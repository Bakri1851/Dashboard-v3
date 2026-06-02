"""Side experiment (escalation): re-label ALL 1306 struggle snapshots + 72
difficulty questions with full GPT-4o, using identical prompts to
scripts/eval_label.py. NEVER overwrites canonical labels — writes only to
data/eval/experiments/.

Cost estimate: ~$4-5 OpenAI spend. ~15-20 min wallclock.

Idempotent: if either output JSON already has a label for a snapshot, that
label is reused on re-run; only missing snapshots get fresh API calls. Safe
to interrupt + resume.

Outputs:
  data/eval/experiments/full_relabel_struggle_gpt4o.json   (1306 snapshots)
  data/eval/experiments/full_relabel_difficulty_gpt4o.json (72 questions)
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "code2"))
sys.path.insert(0, str(REPO / "scripts"))

SECRETS_PATH = REPO / ".secrets" / "secrets.toml"
if SECRETS_PATH.exists():
    line_re = re.compile(r'^\s*([A-Z_][A-Z0-9_]*)\s*=\s*"([^"]*)"\s*$')
    for line in SECRETS_PATH.read_text(encoding="utf-8").splitlines():
        m = line_re.match(line)
        if m and m.group(1) not in os.environ:
            os.environ[m.group(1)] = m.group(2)

from eval_label import _struggle_prompt, _difficulty_prompt, _call_openai  # noqa: E402
import backend.config as bk_config  # noqa: E402

EVAL = REPO / "data" / "eval"
OUT = EVAL / "experiments"
OUT.mkdir(parents=True, exist_ok=True)

MODEL = "gpt-4o"
BATCH_STRUGGLE = 5
BATCH_DIFFICULTY = 5


def _load_existing(out_path: Path) -> dict:
    if out_path.exists():
        return json.loads(out_path.read_text(encoding="utf-8")).get("labels", {})
    return {}


def _save(out_path: Path, kind: str, labels: dict):
    out_path.write_text(
        json.dumps({
            "ran_at": datetime.now(timezone.utc).isoformat(),
            "model": MODEL,
            "schema_version": 2,
            "kind": kind,
            "n_labeled": len(labels),
            "labels": labels,
        }, indent=2, default=str),
        encoding="utf-8",
    )


def relabel_kind(kind: str, items: list[dict], id_key: str, prompt_fn, batch_size: int):
    out_path = OUT / f"full_relabel_{kind}_gpt4o.json"
    existing = _load_existing(out_path)
    to_label = [it for it in items if it[id_key] not in existing]
    if not to_label:
        print(f"  {kind}: all {len(items)} already labelled — nothing to do.")
        return existing

    print(f"  {kind}: {len(existing)} already labelled, {len(to_label)} to do "
          f"({len(items)} total)")

    n_batches = (len(to_label) + batch_size - 1) // batch_size
    t0 = time.time()
    save_every = 10  # batches

    labels = dict(existing)
    for bi in range(0, len(to_label), batch_size):
        batch = to_label[bi:bi + batch_size]
        prompt = prompt_fn(batch)
        try:
            results = _call_openai(prompt, len(batch), kind)
        except Exception as e:
            print(f"    Batch {bi // batch_size + 1}/{n_batches} FAILED: {e}", file=sys.stderr)
            continue
        if results is None:
            continue
        for item, result in zip(batch, results):
            labels[item[id_key]] = {
                "intervene": result.get("intervene"),
                "band": result.get("band"),
                "reason": result.get("reason", ""),
                "model": MODEL,
            }
        if (bi // batch_size) % save_every == 0:
            _save(out_path, kind, labels)

        done = len(labels) - len(existing)
        elapsed = time.time() - t0
        rate = done / elapsed if elapsed > 0 else 0
        eta = (len(to_label) - done) / rate if rate > 0 else 0
        if (bi // batch_size) % 5 == 0:
            print(f"    Batch {bi // batch_size + 1}/{n_batches}: "
                  f"{done}/{len(to_label)} new ({elapsed:.0f}s, ETA {eta:.0f}s)")

    _save(out_path, kind, labels)
    print(f"  {kind}: wrote {out_path.name} ({len(labels)} total labels)")
    return labels


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skip-difficulty", action="store_true",
                    help="Only relabel struggle (cheaper iteration)")
    ap.add_argument("--skip-struggle", action="store_true",
                    help="Only relabel difficulty")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    snap_blob = json.loads((EVAL / "snapshots.json").read_text(encoding="utf-8"))
    snapshots = snap_blob.get("struggle_snapshots", [])
    questions = snap_blob.get("difficulty_questions", [])

    n_struggle_batches = (len(snapshots) + BATCH_STRUGGLE - 1) // BATCH_STRUGGLE
    n_difficulty_batches = (len(questions) + BATCH_DIFFICULTY - 1) // BATCH_DIFFICULTY
    cost_struggle = n_struggle_batches * 0.015
    cost_difficulty = n_difficulty_batches * 0.015
    print(f"Inputs: {len(snapshots)} struggle snapshots + {len(questions)} difficulty questions")
    print(f"Cost estimate:")
    print(f"  struggle:   ~${cost_struggle:.2f}  ({n_struggle_batches} batches of {BATCH_STRUGGLE})")
    print(f"  difficulty: ~${cost_difficulty:.2f}  ({n_difficulty_batches} batches of {BATCH_DIFFICULTY})")
    print(f"  TOTAL:      ~${cost_struggle + cost_difficulty:.2f}")
    print()

    if args.dry_run:
        print("DRY RUN — no API calls made.")
        return 0

    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set.", file=sys.stderr)
        return 1

    original_model = bk_config.OPENAI_MODEL
    bk_config.OPENAI_MODEL = MODEL
    print(f"OpenAI model: {bk_config.OPENAI_MODEL}")
    print()

    try:
        if not args.skip_struggle:
            print("=== STRUGGLE ===")
            relabel_kind("struggle", snapshots, "snapshot_id",
                         _struggle_prompt, BATCH_STRUGGLE)
            print()
        if not args.skip_difficulty:
            print("=== DIFFICULTY ===")
            relabel_kind("difficulty", questions, "question",
                         _difficulty_prompt, BATCH_DIFFICULTY)
    finally:
        bk_config.OPENAI_MODEL = original_model

    return 0


if __name__ == "__main__":
    sys.exit(main())
