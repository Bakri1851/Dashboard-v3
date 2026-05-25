"""Phase 3 — GPT-4o-mini second-opinion labelling for struggle + difficulty.

Mirrors ``code2/backend/incorrectness.py``'s pattern: shared OpenAI client
factory, disk-persisted JSON cache, model-versioned invalidation, save
debounce, batched calls with JSON response parsing. The mirror is deliberate
so all OpenAI traffic in this project behaves consistently (retries, cache
invalidation, model upgrades).

Modes::

    python scripts/eval_label.py --mode struggle    # label 1306 struggle snapshots
    python scripts/eval_label.py --mode difficulty  # label 72 difficulty questions
    python scripts/eval_label.py --mode self-label  # CLI: Human labels 50 struggle snapshots
    python scripts/eval_label.py --mode kappa       # Cohen's kappa: Human vs LLM on shared 50

All modes are idempotent — cached labels are reused on re-run; only the
uncached subset is sent to the API. The cache discards itself on
``OPENAI_MODEL`` change so accidental model upgrades don't mix scores.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import threading
import time
from collections import Counter
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "code2"))


def _load_secrets() -> None:
    """Read .secrets/secrets.toml and populate os.environ.

    Mirrors how Streamlit's secrets are surfaced to V2's `_get_openai_client`
    which reads from os.environ. We never overwrite an existing env var, so
    `$env:OPENAI_API_KEY=...` set at the shell still wins.
    """
    secrets_path = REPO_ROOT / ".secrets" / "secrets.toml"
    if not secrets_path.exists():
        return
    line_re = re.compile(r'^\s*([A-Z_][A-Z0-9_]*)\s*=\s*"([^"]*)"\s*$')
    try:
        for line in secrets_path.read_text(encoding="utf-8").splitlines():
            m = line_re.match(line)
            if m:
                key, value = m.group(1), m.group(2)
                if key and value and key not in os.environ:
                    os.environ[key] = value
    except OSError:
        pass


_load_secrets()

from backend import config, paths  # noqa: E402
from backend.analytics import _get_openai_client  # noqa: E402

logger = logging.getLogger("eval_label")
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s")


SCHEMA_VERSION = 2  # v2: 4-band ordinal scale matching the dashboard (was 1-5 integer)
SAVE_DEBOUNCE_S = 30.0
BATCH_SIZE_STRUGGLE = 5
BATCH_SIZE_DIFFICULTY = 5
REQUEST_TIMEOUT_S = 30.0

STRUGGLE_BANDS = ["On Track", "Minor Issues", "Struggling", "Needs Help"]
BAND_INDEX = {b: i for i, b in enumerate(STRUGGLE_BANDS)}
BAND_BY_SHORTCUT = {
    "1": "On Track", "t": "On Track", "on track": "On Track",
    "2": "Minor Issues", "m": "Minor Issues", "minor issues": "Minor Issues", "minor": "Minor Issues",
    "3": "Struggling", "s": "Struggling", "struggling": "Struggling",
    "4": "Needs Help", "n": "Needs Help", "needs help": "Needs Help", "needs": "Needs Help",
}

DIFFICULTY_BANDS = ["Easy", "Medium", "Hard", "Very Hard"]
DIFF_INDEX = {b: i for i, b in enumerate(DIFFICULTY_BANDS)}


# -------------------- Cache layer (mirrors incorrectness.py) --------------------

def _cache_path(kind: str) -> Path:
    eval_dir = paths.DATA_DIR / "eval"
    eval_dir.mkdir(parents=True, exist_ok=True)
    return eval_dir / f"llm_{kind}_labels.json"


def _load_cache(kind: str) -> dict[str, dict]:
    path = _cache_path(kind)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("cache load failed for %s (%s): %s", kind, type(exc).__name__, exc)
        return {}
    if not isinstance(payload, dict):
        return {}
    if payload.get("model") != config.OPENAI_MODEL:
        logger.info(
            "cache on disk was built for model=%r; current=%r — discarding",
            payload.get("model"), config.OPENAI_MODEL,
        )
        return {}
    if payload.get("schema_version") != SCHEMA_VERSION:
        logger.info(
            "cache schema_version=%r != %r — discarding",
            payload.get("schema_version"), SCHEMA_VERSION,
        )
        return {}
    labels = payload.get("labels")
    if not isinstance(labels, dict):
        return {}
    logger.info("cache: loaded %d %s labels from disk", len(labels), kind)
    return labels


_save_lock = threading.Lock()
_last_save_ts: dict[str, float] = {}


def _save_cache(kind: str, cache: dict[str, dict], *, force: bool = False) -> None:
    global _last_save_ts
    with _save_lock:
        now = time.monotonic()
        last = _last_save_ts.get(kind, 0.0)
        if not force and (now - last) < SAVE_DEBOUNCE_S:
            return
        _last_save_ts[kind] = now
        snapshot = dict(cache)
    payload = {
        "model": config.OPENAI_MODEL,
        "schema_version": SCHEMA_VERSION,
        "labels": snapshot,
    }
    path = _cache_path(kind)
    try:
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        tmp.replace(path)
    except OSError as exc:
        logger.warning("cache save failed for %s: %s", kind, exc)


# -------------------- Prompt construction --------------------

def _struggle_prompt(snapshots: list[dict]) -> str:
    """Build a batch-prompt asking the LLM to label N struggle snapshots."""
    parts = [
        "You are a teaching assistant observing students during a programming lab.",
        "Each numbered block below describes one (student, moment-in-time) snapshot.",
        "Based on the submission evidence alone, give two judgements:",
        "  1. Would you walk over to help this student right now? (binary)",
        "  2. Which struggle band best describes them right now? (4-band ordinal)",
        "",
        "The four struggle bands match the deployed dashboard's classification:",
        '  "On Track"      — clearly progressing, few or recoverable errors',
        '  "Minor Issues"  — some errors but recovering on their own',
        '  "Struggling"    — sustained difficulty, slow progress',
        '  "Needs Help"    — stuck or abandoned, unlikely to recover without intervention',
        "",
        "For EACH snapshot, output one JSON object with EXACTLY these keys:",
        '  {"intervene": true|false, "band": "On Track"|"Minor Issues"|"Struggling"|"Needs Help", "reason": "<= 20 word justification"}',
        "",
        f"Return a JSON ARRAY of exactly {len(snapshots)} objects in the same order as the snapshots.",
        "Return ONLY the JSON array, no surrounding text.",
        "",
        "Snapshots:",
    ]
    for i, snap in enumerate(snapshots, 1):
        ctx = snap.get("context", {})
        trail = ctx.get("recent_trail", [])
        parts.append(f"\n=== Snapshot {i} (id: {snap['snapshot_id'][:60]}) ===")
        parts.append(f"Time into session: {snap['t_minutes_into_session']} min")
        parts.append(
            f"Submissions so far: {ctx.get('n_submissions_so_far')} "
            f"across {ctx.get('n_unique_questions_so_far')} unique questions"
        )
        parts.append(f"Mean incorrectness so far: {ctx.get('mean_incorrectness_so_far'):.2f}")
        parts.append(f"Recent incorrectness (EWMA): {ctx.get('recent_incorrectness_ewma'):.2f}")
        parts.append(f"Time active: {ctx.get('time_active_min')} min")
        if trail:
            parts.append("Recent submission trail (most recent first):")
            for j, sub in enumerate(trail[:8], 1):
                ans = sub.get("answer_excerpt", "")[:120]
                fb = sub.get("feedback_excerpt", "")[:150]
                parts.append(
                    f"  {j}. [{sub.get('timestamp', '')[:19]}] "
                    f"Q={sub.get('question', '')[:30]}  "
                    f"inc={sub.get('incorrectness', 0):.2f}"
                )
                if ans:
                    parts.append(f"     Answer: {ans}")
                if fb:
                    parts.append(f"     Feedback: {fb}")
        else:
            parts.append("Recent submission trail: (empty)")
    return "\n".join(parts)


def _difficulty_prompt(questions: list[dict]) -> str:
    """Build a batch-prompt asking the LLM to rate N question difficulties."""
    parts = [
        "You are an instructor judging the difficulty of programming questions",
        "based on observed student performance on them.",
        "",
        "The four difficulty bands match the deployed dashboard's classification:",
        '  "Easy"      — most students solve quickly on first or second attempt',
        '  "Medium"    — moderate retries; majority eventually solve',
        '  "Hard"      — many retries; significant failure rate',
        '  "Very Hard" — very few solve; high failure rate even with multiple attempts',
        "",
        "For EACH numbered question, output one JSON object with EXACTLY these keys:",
        '  {"band": "Easy"|"Medium"|"Hard"|"Very Hard", "reason": "<= 20 word justification"}',
        "",
        f"Return a JSON ARRAY of exactly {len(questions)} objects in the same order.",
        "Return ONLY the JSON array.",
        "",
        "Questions:",
    ]
    for i, q in enumerate(questions, 1):
        v1 = q.get("v1_features", {})
        parts.append(f"\n=== Question {i} (id: {q['question'][:60]}) ===")
        parts.append(
            f"Total attempts: {q['total_attempts']} across "
            f"{q['unique_students']} unique students"
        )
        parts.append(f"Avg attempts per student: {q['avg_attempts']:.2f}")
        parts.append(f"Incorrect-attempt rate: {q['incorrect_rate_pct']:.1f}%")
        parts.append("Aggregate signals (normalised 0-1):")
        parts.append(f"  Incorrect rate (c_norm):           {v1.get('c_norm', 0):.2f}")
        parts.append(f"  Mean time per student (t_tilde):   {v1.get('t_tilde', 0):.2f}")
        parts.append(f"  Mean attempts per student (a_tilde):{v1.get('a_tilde', 0):.2f}")
        parts.append(f"  Mean incorrectness (f_norm):       {v1.get('f_norm', 0):.2f}")
        parts.append(f"  First-attempt failure rate (p_norm):{v1.get('p_norm', 0):.2f}")
    return "\n".join(parts)


# -------------------- JSON parsing (mirrors incorrectness.py) --------------------

_JSON_ARRAY_RE = re.compile(r"\[.*\]", re.DOTALL)


def _parse_label_array(text: str, expected_len: int, kind: str) -> Optional[list[dict]]:
    if not text:
        return None
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z0-9]*\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()
    candidates = [cleaned]
    match = _JSON_ARRAY_RE.search(cleaned)
    if match and match.group(0) != cleaned:
        candidates.append(match.group(0))
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except (json.JSONDecodeError, ValueError):
            continue
        if not isinstance(parsed, list) or len(parsed) != expected_len:
            continue
        out: list[dict] = []
        ok = True
        for item in parsed:
            if not isinstance(item, dict):
                ok = False
                break
            if kind == "struggle":
                band = item.get("band")
                intervene = item.get("intervene")
                if not isinstance(intervene, bool) or band not in STRUGGLE_BANDS:
                    ok = False
                    break
                out.append({
                    "intervene": bool(intervene),
                    "band": band,
                    "reason": str(item.get("reason", ""))[:200],
                })
            else:  # difficulty
                band = item.get("band")
                if band not in DIFFICULTY_BANDS:
                    ok = False
                    break
                out.append({
                    "band": band,
                    "reason": str(item.get("reason", ""))[:200],
                })
        if ok:
            return out
    return None


# -------------------- OpenAI batch call (mirrors incorrectness.py) --------------------

def _call_openai(prompt: str, expected_len: int, kind: str) -> Optional[list[dict]]:
    try:
        client = _get_openai_client()
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            timeout=REQUEST_TIMEOUT_S,
        )
    except Exception as exc:
        logger.warning("OpenAI call failed (%s): %s", type(exc).__name__, exc)
        return None
    raw = (response.choices[0].message.content or "") if response.choices else ""
    parsed = _parse_label_array(raw, expected_len, kind)
    if parsed is None:
        logger.warning(
            "Response did not parse as %d %s labels; raw[:200]=%r",
            expected_len, kind, raw[:200],
        )
    return parsed


# -------------------- Labelling drivers --------------------

def label_struggle_snapshots(
    snapshots: list[dict], batch_size: int = BATCH_SIZE_STRUGGLE
) -> dict[str, dict]:
    cache = _load_cache("struggle")
    uncached = [s for s in snapshots if s["snapshot_id"] not in cache]
    logger.info(
        "struggle: total=%d  cached=%d  scoring_this_run=%d",
        len(snapshots), len(snapshots) - len(uncached), len(uncached),
    )
    if not uncached:
        return cache

    batches_attempted = batches_succeeded = added = 0
    for i in range(0, len(uncached), batch_size):
        batch = uncached[i : i + batch_size]
        batches_attempted += 1
        prompt = _struggle_prompt(batch)
        results = _call_openai(prompt, len(batch), "struggle")
        if results is None:
            continue
        for snap, label in zip(batch, results):
            cache[snap["snapshot_id"]] = {
                **label,
                "snapshot_id": snap["snapshot_id"],
            }
            added += 1
        batches_succeeded += 1
        if batches_succeeded % 5 == 0:
            logger.info(
                "  progress: %d/%d batches, %d labels added",
                batches_succeeded, batches_attempted, added,
            )
            _save_cache("struggle", cache)

    _save_cache("struggle", cache, force=True)
    logger.info(
        "struggle: batches_attempted=%d batches_succeeded=%d labels_added=%d cache_size=%d",
        batches_attempted, batches_succeeded, added, len(cache),
    )
    return cache


def label_difficulty_questions(
    questions: list[dict], batch_size: int = BATCH_SIZE_DIFFICULTY
) -> dict[str, dict]:
    cache = _load_cache("difficulty")
    uncached = [q for q in questions if q["question"] not in cache]
    logger.info(
        "difficulty: total=%d  cached=%d  scoring_this_run=%d",
        len(questions), len(questions) - len(uncached), len(uncached),
    )
    if not uncached:
        return cache

    batches_attempted = batches_succeeded = added = 0
    for i in range(0, len(uncached), batch_size):
        batch = uncached[i : i + batch_size]
        batches_attempted += 1
        prompt = _difficulty_prompt(batch)
        results = _call_openai(prompt, len(batch), "difficulty")
        if results is None:
            continue
        for q, label in zip(batch, results):
            cache[q["question"]] = {
                **label,
                "question": q["question"],
            }
            added += 1
        batches_succeeded += 1
        if batches_succeeded % 5 == 0:
            _save_cache("difficulty", cache)

    _save_cache("difficulty", cache, force=True)
    logger.info(
        "difficulty: batches_attempted=%d batches_succeeded=%d labels_added=%d cache_size=%d",
        batches_attempted, batches_succeeded, added, len(cache),
    )
    return cache


# -------------------- Self-label CLI --------------------

def self_label_cli(snapshots: list[dict], n: int = 50, seed: int = 42) -> dict[str, dict]:
    import numpy as np

    self_path = paths.DATA_DIR / "eval" / "self_labels.json"
    self_path.parent.mkdir(parents=True, exist_ok=True)
    existing: dict[str, dict] = {}
    if self_path.exists():
        try:
            payload = json.loads(self_path.read_text(encoding="utf-8"))
            on_disk_version = payload.get("schema_version")
            if on_disk_version != SCHEMA_VERSION:
                print(
                    f"self_labels.json schema_version={on_disk_version!r} != current "
                    f"{SCHEMA_VERSION} — discarding {len(payload.get('labels', {}))} old labels."
                )
            else:
                existing = payload.get("labels", {})
                print(f"Found existing {self_path.name} with {len(existing)} entries. Resuming.")
        except Exception as exc:
            print(f"Could not read {self_path.name} ({type(exc).__name__}): {exc}. Starting fresh.")
            existing = {}

    rng = np.random.default_rng(seed)
    pool_idx = rng.choice(len(snapshots), size=min(n, len(snapshots)), replace=False)
    selection = [snapshots[int(i)] for i in pool_idx]
    todo = [s for s in selection if s["snapshot_id"] not in existing]
    if not todo:
        print(f"All {n} snapshots already labelled.")
        return existing

    print(f"\nWill ask you to label {len(todo)} snapshots (of {n} target). Type 'q' to save and quit.")
    print("Press Ctrl+C at any time to save progress and exit.\n")

    try:
        for i, snap in enumerate(todo, 1):
            ctx = snap.get("context", {})
            trail = ctx.get("recent_trail", [])
            print("=" * 80)
            print(f"[{i}/{len(todo)}]  snapshot_id: {snap['snapshot_id']}")
            print(f"  Session: {snap['session_name']}")
            print(f"  Time into session: {snap['t_minutes_into_session']} min")
            print(
                f"  Submissions so far: {ctx.get('n_submissions_so_far')}  "
                f"unique questions: {ctx.get('n_unique_questions_so_far')}"
            )
            print(f"  Mean incorrectness: {ctx.get('mean_incorrectness_so_far'):.2f}")
            print(f"  Recent EWMA:        {ctx.get('recent_incorrectness_ewma'):.2f}")
            print(f"  v1 score: {snap['v1_struggle_score']:.2f}  ({snap['v1_struggle_level']})")
            print()
            print(f"  Recent trail (up to 5 most recent):")
            for j, sub in enumerate(trail[:5], 1):
                print(f"    {j}. [{sub.get('timestamp', '')[:19]}]  Q={sub.get('question', '')[:50]}  "
                      f"inc={sub.get('incorrectness', 0):.2f}")
                ans = sub.get('answer_excerpt', '')
                fb = sub.get('feedback_excerpt', '')
                if ans:
                    print(f"       Answer:")
                    for line in ans.replace('<br>', '\n').splitlines():
                        print(f"         {line}")
                if fb:
                    print(f"       Feedback:")
                    for line in fb.replace('<br>', '\n').splitlines():
                        print(f"         {line}")
            print()

            while True:
                resp = input("  Intervene? [y/n/q]: ").strip().lower()
                if resp == "q":
                    raise KeyboardInterrupt
                if resp in ("y", "n"):
                    break
                print("    (y for yes, n for no, q to save+quit)")

            band: Optional[str] = None
            while band is None:
                band_str = input(
                    "  Band [1=On Track, 2=Minor Issues, 3=Struggling, 4=Needs Help, q=quit]: "
                ).strip().lower()
                if band_str == "q":
                    raise KeyboardInterrupt
                band = BAND_BY_SHORTCUT.get(band_str)
                if band is None:
                    print("    (1/2/3/4 or t/m/s/n or full band name; q to save+quit)")

            existing[snap["snapshot_id"]] = {
                "snapshot_id": snap["snapshot_id"],
                "intervene": resp == "y",
                "band": band,
                "labelled_by": "user",
            }
            # save after every label so a Ctrl+C doesn't lose progress
            self_path.write_text(
                json.dumps({"schema_version": SCHEMA_VERSION, "labels": existing}, indent=2),
                encoding="utf-8",
            )
            print(f"  saved.  ({len(existing)} total)")
            print()

    except KeyboardInterrupt:
        print()
        print(f"\nSaved {len(existing)} self-labels to {self_path}.")

    return existing


def cohen_kappa_report() -> None:
    from sklearn.metrics import cohen_kappa_score  # type: ignore[import-untyped]

    self_path = paths.DATA_DIR / "eval" / "self_labels.json"
    self_path.parent.mkdir(parents=True, exist_ok=True)
    if not self_path.exists():
        print("No self_labels.json yet. Run `--mode self-label` first.")
        return
    self_blob = json.loads(self_path.read_text(encoding="utf-8"))
    self_labels = self_blob.get("labels", {})

    llm_cache = _load_cache("struggle")
    shared = sorted(set(self_labels.keys()) & set(llm_cache.keys()))
    if not shared:
        print(f"No overlap between self_labels (n={len(self_labels)}) and llm cache (n={len(llm_cache)}).")
        return

    human_intervene = [int(self_labels[k]["intervene"]) for k in shared]
    llm_intervene = [int(llm_cache[k]["intervene"]) for k in shared]
    human_band = [self_labels[k]["band"] for k in shared]
    llm_band = [llm_cache[k]["band"] for k in shared]
    human_band_idx = [BAND_INDEX[b] for b in human_band]
    llm_band_idx = [BAND_INDEX[b] for b in llm_band]

    kappa_intervene = cohen_kappa_score(human_intervene, llm_intervene)
    kappa_band = cohen_kappa_score(human_band_idx, llm_band_idx, weights="linear")
    kappa_band_quad = cohen_kappa_score(human_band_idx, llm_band_idx, weights="quadratic")

    print(f"\nCohen's kappa over shared n={len(shared)} snapshots:")
    print(f"  intervene (binary):           kappa = {kappa_intervene:.3f}")
    print(f"  band (linear weights):        kappa = {kappa_band:.3f}")
    print(f"  band (quadratic weights):     kappa = {kappa_band_quad:.3f}")

    # Agreement breakdown
    agree_intervene = sum(1 for b, l in zip(human_intervene, llm_intervene) if b == l)
    agree_band_exact = sum(1 for b, l in zip(human_band, llm_band) if b == l)
    agree_band_within1 = sum(
        1 for b, l in zip(human_band_idx, llm_band_idx) if abs(b - l) <= 1
    )
    print()
    print(f"  intervene exact agreement:    {agree_intervene}/{len(shared)} ({agree_intervene/len(shared):.1%})")
    print(f"  band exact agreement:         {agree_band_exact}/{len(shared)} ({agree_band_exact/len(shared):.1%})")
    print(f"  band within 1 step agreement: {agree_band_within1}/{len(shared)} ({agree_band_within1/len(shared):.1%})")

    # Distribution check
    print()
    print(f"  Human intervene rate: {sum(human_intervene)}/{len(shared)} ({sum(human_intervene)/len(shared):.1%})")
    print(f"  LLM intervene rate:   {sum(llm_intervene)}/{len(shared)} ({sum(llm_intervene)/len(shared):.1%})")
    print(f"  Human band distribution: {dict(Counter(human_band))}")
    print(f"  LLM   band distribution: {dict(Counter(llm_band))}")

    # Persist the numbers so they survive across runs and feed §5.4 prose
    report_path = paths.DATA_DIR / "eval" / "kappa_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_payload = {
        "model": config.OPENAI_MODEL,
        "schema_version": SCHEMA_VERSION,
        "n_shared": len(shared),
        "kappa_intervene_unweighted": float(kappa_intervene),
        "kappa_band_linear_weighted": float(kappa_band),
        "kappa_band_quadratic_weighted": float(kappa_band_quad),
        "exact_agreement": {
            "intervene": {
                "count": agree_intervene, "rate": agree_intervene / len(shared)
            },
            "band": {
                "count": agree_band_exact, "rate": agree_band_exact / len(shared)
            },
        },
        "within_1_band_agreement": {
            "count": agree_band_within1,
            "rate": agree_band_within1 / len(shared),
        },
        "distributions": {
            "human_intervene_rate": sum(human_intervene) / len(shared),
            "llm_intervene_rate": sum(llm_intervene) / len(shared),
            "human_band": dict(Counter(human_band)),
            "llm_band": dict(Counter(llm_band)),
        },
        "shared_snapshot_ids": shared,
    }
    report_path.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")
    print()
    print(f"Saved to {report_path}")


# -------------------- Main --------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        required=True,
        choices=["struggle", "difficulty", "self-label", "kappa", "all"],
        help="Which labelling pass to run.",
    )
    parser.add_argument("--snapshots", type=Path, default=paths.DATA_DIR / "eval" / "snapshots.json")
    parser.add_argument("--n-self", type=int, default=50, help="Number of snapshots to self-label (self-label mode).")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE_STRUGGLE)
    args = parser.parse_args()

    if not args.snapshots.exists():
        print(f"ERROR: {args.snapshots} not found. Run scripts/eval_common.py first.")
        return 1

    payload = json.loads(args.snapshots.read_text(encoding="utf-8"))
    snapshots = payload.get("struggle_snapshots", [])
    questions = payload.get("difficulty_questions", [])
    print(f"Loaded {len(snapshots)} struggle snapshots + {len(questions)} difficulty questions from {args.snapshots}")
    print(f"OpenAI model: {config.OPENAI_MODEL}")
    print()

    if args.mode in ("struggle", "all"):
        label_struggle_snapshots(snapshots, batch_size=args.batch_size)

    if args.mode in ("difficulty", "all"):
        label_difficulty_questions(questions, batch_size=args.batch_size)

    if args.mode == "self-label":
        self_label_cli(snapshots, n=args.n_self, seed=args.seed)

    if args.mode in ("kappa", "all"):
        cohen_kappa_report()

    return 0


if __name__ == "__main__":
    sys.exit(main())
