"""Side experiment: re-label 150 stratified snapshots with GPT-4o (full model,
not mini) using the EXACT SAME prompt as scripts/eval_label.py. Hypothesis:
GPT-4o produces less noisy labels than gpt-4o-mini, lifting the κ vs human
agreement and (downstream) the OLS Spearman ρ.

NEVER overwrites the canonical `data/eval/llm_struggle_labels.json` — outputs
only to `data/eval/experiments/relabel_subset_gpt4o.json`.

Strategy: pick 150 snapshots, 37–38 per band (stratified). Includes the 50
author-self-labelled snapshots so we can compute a head-to-head κ between
4o-mini and 4o against the same human reference.

Cost: ~$2-3 in OpenAI spend; ~3-5 min wallclock.

Run from repo root::

    python scripts/experiments/relabel_subset_gpt4o.py
    python scripts/experiments/relabel_subset_gpt4o.py --n 50   # smaller pilot
    python scripts/experiments/relabel_subset_gpt4o.py --dry-run  # print cost estimate only
"""
from __future__ import annotations
import argparse
import json
import os
import re
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "code2"))

# Load .secrets/secrets.toml if present (same pattern as eval_label.py)
SECRETS_PATH = REPO / ".secrets" / "secrets.toml"
if SECRETS_PATH.exists():
    line_re = re.compile(r'^\s*([A-Z_][A-Z0-9_]*)\s*=\s*"([^"]*)"\s*$')
    for line in SECRETS_PATH.read_text(encoding="utf-8").splitlines():
        m = line_re.match(line)
        if m and m.group(1) not in os.environ:
            os.environ[m.group(1)] = m.group(2)

# Reuse the exact prompt helper from scripts/eval_label.py so the comparison is
# apples-to-apples (only the OpenAI model changes).
sys.path.insert(0, str(REPO / "scripts"))
from eval_label import _struggle_prompt, _call_openai  # noqa: E402

from backend.analytics import _get_openai_client  # noqa: E402

EVAL = REPO / "data" / "eval"
OUT = EVAL / "experiments"
OUT.mkdir(parents=True, exist_ok=True)

# Override model for this experiment ONLY (does not touch config.py)
RELABEL_MODEL = "gpt-4o"   # full GPT-4o, not 4o-mini
BATCH = 5                   # smaller batch than 4o-mini (longer context per call)


def _stratified_sample(snapshots, labels, n_per_band, self_label_ids=None, seed=42):
    """Pick n_per_band snapshots from each of the 4 bands.

    If self_label_ids is provided, ALL snapshots whose id is in that set are
    force-included (so we can do head-to-head κ vs the human reference);
    additional stratified picks fill the rest of each band up to n_per_band.
    """
    rng = random.Random(seed)
    self_label_ids = self_label_ids or set()
    by_band = {b: [] for b in ["On Track", "Minor Issues", "Struggling", "Needs Help"]}
    for s in snapshots:
        sid = s["snapshot_id"]
        if sid not in labels:
            continue
        band = labels[sid]["band"]
        if band in by_band:
            by_band[band].append(s)
    picked = []
    for band, pool in by_band.items():
        rng.shuffle(pool)
        forced = [s for s in pool if s["snapshot_id"] in self_label_ids]
        rest = [s for s in pool if s["snapshot_id"] not in self_label_ids]
        target = max(n_per_band, len(forced))
        chosen = forced + rest[: max(0, target - len(forced))]
        picked.extend(chosen)
        print(f"  {band}: pool={len(pool)}, forced(self-label)={len(forced)}, "
              f"final={len(chosen)}")
    return picked


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=150,
                    help="Total snapshots to re-label (split evenly across 4 bands)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print cost estimate; no API calls")
    args = ap.parse_args()

    # Load canonical inputs (read-only)
    snaps = json.loads((EVAL / "snapshots.json").read_text(encoding="utf-8"))["struggle_snapshots"]
    labels = json.loads((EVAL / "llm_struggle_labels.json").read_text(encoding="utf-8"))["labels"]
    self_labels_path = EVAL / "self_labels.json"
    self_labels = {}
    if self_labels_path.exists():
        self_labels = json.loads(self_labels_path.read_text(encoding="utf-8")).get("labels", {})

    print(f"Loaded {len(snaps)} snapshots, {len(labels)} existing 4o-mini labels, "
          f"{len(self_labels)} author self-labels")
    print()

    n_per_band = args.n // 4
    print(f"Stratified sample target: {n_per_band} per band, {n_per_band*4} total")
    print(f"  (all author self-labels force-included for head-to-head κ comparison)")
    picked = _stratified_sample(snaps, labels, n_per_band, self_label_ids=set(self_labels.keys()))
    print(f"Picked {len(picked)} snapshots total")

    # Prioritise overlap with author self-labels for direct κ comparison
    self_ids = set(self_labels.keys())
    overlap = [s for s in picked if s["snapshot_id"] in self_ids]
    print(f"  → {len(overlap)} overlap with author self-labels (head-to-head κ available)")
    print()

    # Cost estimate: GPT-4o is ~$2.50 per 1M input tokens, ~$10 per 1M output.
    # Each snapshot prompt is ~1000 tokens; output is ~50 tokens. With batch=5,
    # each call is ~5000 input + 250 output = $0.0125 + $0.0025 = ~$0.015/call.
    # 150 snapshots / 5 per batch = 30 calls → ~$0.45. Conservative ~$1-2 ceiling.
    n_batches = (len(picked) + BATCH - 1) // BATCH
    est_cost = n_batches * 0.015
    print(f"Estimated cost: ~${est_cost:.2f} ({n_batches} API calls, batch={BATCH})")
    if args.dry_run:
        print("DRY RUN — no API calls made.")
        return 0

    # Sanity-check API key
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        print("ERROR: OPENAI_API_KEY not set; cannot call OpenAI.", file=sys.stderr)
        return 1

    # Monkeypatch the model used by _call_openai
    import backend.config as bk_config
    original_model = bk_config.OPENAI_MODEL
    bk_config.OPENAI_MODEL = RELABEL_MODEL
    print(f"OpenAI model: {bk_config.OPENAI_MODEL} (was {original_model})")
    print()

    relabels = {}
    t0 = time.time()
    for bi in range(0, len(picked), BATCH):
        batch = picked[bi:bi + BATCH]
        prompt = _struggle_prompt(batch)
        try:
            results = _call_openai(prompt, len(batch), "struggle")
        except Exception as e:
            print(f"  Batch {bi//BATCH + 1}/{n_batches} FAILED: {e}", file=sys.stderr)
            continue
        if results is None:
            print(f"  Batch {bi//BATCH + 1}/{n_batches} returned None — skipping")
            continue
        for snap, result in zip(batch, results):
            relabels[snap["snapshot_id"]] = {
                "intervene": result.get("intervene"),
                "band": result.get("band"),
                "reason": result.get("reason", ""),
                "model": RELABEL_MODEL,
            }
        elapsed = time.time() - t0
        done = len(relabels)
        rate = done / elapsed if elapsed > 0 else 0
        eta = (len(picked) - done) / rate if rate > 0 else 0
        print(f"  Batch {bi//BATCH + 1}/{n_batches}: {done}/{len(picked)} done "
              f"({elapsed:.0f}s elapsed, ETA {eta:.0f}s)")

    # Restore canonical model (defensive — script ends anyway)
    bk_config.OPENAI_MODEL = original_model

    out_path = OUT / "relabel_subset_gpt4o.json"
    payload = {
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "model": RELABEL_MODEL,
        "schema_version": 2,
        "n_relabeled": len(relabels),
        "stratification": "stratified random across 4 bands; includes author self-label overlap",
        "purpose": (
            "Re-label a 150-snapshot subset with full GPT-4o (not 4o-mini) to test "
            "whether label quality is the ρ ceiling. Compare κ vs author self-labels "
            "(head-to-head 4o-mini vs 4o); then re-train OLS with merged labels and "
            "compare Spearman ρ vs the canonical run."
        ),
        "labels": relabels,
    }
    out_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print()
    print(f"Wrote {out_path}")
    print(f"Re-labeled {len(relabels)}/{len(picked)} snapshots.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
