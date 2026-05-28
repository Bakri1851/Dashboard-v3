"""Brute-force κ-maximising threshold search for v1 score → band mapping.

Tests whether the hand-set thresholds in code2/backend/config.py
(STRUGGLE_THRESHOLDS, DIFFICULTY_THRESHOLDS) leave linear-weighted κ on the
table compared to thresholds chosen to maximise band-classification κ
against the LLM 4-band labels.

Also tests v2 OLS-output rounding cutpoints (default 0.5 / 1.5 / 2.5) for
the same κ-maximisation question.

Delete-safe: writes only to data/eval/experiments/.
"""
from __future__ import annotations
import json
import sys
from itertools import product
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "code2"))

import numpy as np
from sklearn.metrics import cohen_kappa_score

EVAL = REPO / "data" / "eval"
OUT  = EVAL / "experiments"
OUT.mkdir(parents=True, exist_ok=True)

STRUGGLE_BANDS    = ["On Track", "Minor Issues", "Struggling", "Needs Help"]
DIFFICULTY_BANDS  = ["Easy", "Medium", "Hard", "Very Hard"]
STRUGGLE_BAND_INDEX   = {b: i for i, b in enumerate(STRUGGLE_BANDS)}
DIFFICULTY_BAND_INDEX = {b: i for i, b in enumerate(DIFFICULTY_BANDS)}


def _load(name: str):
    with (EVAL / name).open(encoding="utf-8") as f:
        return json.load(f)


def thresholds_to_band(score: np.ndarray, cutpoints: tuple) -> np.ndarray:
    """Map continuous score to band index 0..3 using 3 cutpoints (low → high)."""
    c1, c2, c3 = cutpoints
    out = np.zeros_like(score, dtype=int)
    out[score >= c1] = 1
    out[score >= c2] = 2
    out[score >= c3] = 3
    return out


def kappa_for_cutpoints(score, y_true, cutpoints):
    pred = thresholds_to_band(score, cutpoints)
    return cohen_kappa_score(y_true, pred, labels=[0, 1, 2, 3], weights="linear")


def brute_force_search(score, y_true, lo: float, hi: float, step: float,
                       label: str):
    """Coarse grid + fine local search around the coarse best."""
    grid = np.round(np.arange(lo, hi + step, step), 4)
    best = (-1.0, None)
    for c1, c2, c3 in product(grid, grid, grid):
        if not (c1 < c2 < c3):
            continue
        k = kappa_for_cutpoints(score, y_true, (c1, c2, c3))
        if k > best[0]:
            best = (k, (c1, c2, c3))
    # Refine around the coarse best with a finer grid
    coarse_best = best[1]
    fine_step = step / 5
    fine_grid_extent = step * 1.5
    c1s = np.round(np.arange(coarse_best[0] - fine_grid_extent,
                             coarse_best[0] + fine_grid_extent + fine_step,
                             fine_step), 4)
    c2s = np.round(np.arange(coarse_best[1] - fine_grid_extent,
                             coarse_best[1] + fine_grid_extent + fine_step,
                             fine_step), 4)
    c3s = np.round(np.arange(coarse_best[2] - fine_grid_extent,
                             coarse_best[2] + fine_grid_extent + fine_step,
                             fine_step), 4)
    for c1, c2, c3 in product(c1s, c2s, c3s):
        if not (c1 < c2 < c3) or c1 < lo or c3 > hi:
            continue
        k = kappa_for_cutpoints(score, y_true, (c1, c2, c3))
        if k > best[0]:
            best = (k, (c1, c2, c3))
    print(f"  [{label}] best κ={best[0]:+.4f} at cutpoints {best[1]}")
    return best


def baseline_kappa(score, y_true, cutpoints, label):
    k = kappa_for_cutpoints(score, y_true, cutpoints)
    print(f"  [{label}] baseline κ={k:+.4f} at cutpoints {cutpoints}")
    return k


def main() -> int:
    print("=" * 78)
    print("STRUGGLE — v1 [0,1] composite score → 4-band classification")
    print("=" * 78)

    snaps = _load("snapshots.json")["struggle_snapshots"]
    labels_s = _load("llm_struggle_labels.json")["labels"]
    matched_s = [s for s in snaps if s["snapshot_id"] in labels_s]
    v1_score = np.array([s["v1_struggle_score"] for s in matched_s])
    y_s      = np.array([STRUGGLE_BAND_INDEX[labels_s[s["snapshot_id"]]["band"]] for s in matched_s])
    print(f"  n={len(matched_s)} matched snapshots")
    print(f"  v1 score range: [{v1_score.min():.3f}, {v1_score.max():.3f}]")
    print(f"  y band dist:    {dict(zip(*np.unique(y_s, return_counts=True)))}")

    baseline_kappa(v1_score, y_s, (0.2, 0.35, 0.5), "hand-set")
    best_v1_struggle = brute_force_search(v1_score, y_s, 0.0, 1.0, 0.025, "grid")

    # Also test v2: OLS output is in [0, 3] band-index space.
    print()
    print("STRUGGLE — v2 OLS output [0,3] → 4-band rounding")
    pred_v2 = _load("pooled_predictions_v2.json")["v2_struggle"]["pred"]
    # pooled_predictions ordering matches matched_s only IF the notebook's
    # rederive_struggle_v2 iterated snapshots in the same order. Sanity-check:
    pooled_y = np.array(_load("pooled_predictions_v2.json")["v2_struggle"]["y"])
    if np.array_equal(pooled_y, y_s):
        v2_score = np.array(pred_v2)
        print(f"  v2 OLS range: [{v2_score.min():.3f}, {v2_score.max():.3f}]")
        baseline_kappa(v2_score, y_s, (0.5, 1.5, 2.5), "natural-round")
        brute_force_search(v2_score, y_s, 0.0, 3.0, 0.05, "grid")
    else:
        print("  pooled_y mismatch with derived y — re-run notebook to refresh.")

    print()
    print("=" * 78)
    print("DIFFICULTY — v1 [0,1] composite score → 4-band classification")
    print("=" * 78)

    qs = _load("snapshots.json")["difficulty_questions"]
    labels_d = _load("llm_difficulty_labels.json")["labels"]
    matched_d = [q for q in qs if q["question"] in labels_d]
    v1_diff = np.array([q["v1_difficulty_score"] for q in matched_d])
    y_d     = np.array([DIFFICULTY_BAND_INDEX[labels_d[q["question"]]["band"]] for q in matched_d])
    print(f"  n={len(matched_d)} matched questions")
    print(f"  v1 score range: [{v1_diff.min():.3f}, {v1_diff.max():.3f}]")
    print(f"  y band dist:    {dict(zip(*np.unique(y_d, return_counts=True)))}")

    baseline_kappa(v1_diff, y_d, (0.35, 0.5, 0.75), "hand-set")
    best_v1_difficulty = brute_force_search(v1_diff, y_d, 0.0, 1.0, 0.025, "grid")

    # v2 difficulty: pull pooled predictions directly
    print()
    print("DIFFICULTY — v2 OLS output [0,3] → 4-band rounding")
    opt_d = _load("optimised_difficulty_weights_v2.json")
    pred_v2_d = np.array(opt_d["pooled_predictions"])
    pooled_y_d = np.array(opt_d["pooled_y"])
    if np.array_equal(pooled_y_d, y_d):
        print(f"  v2 OLS range: [{pred_v2_d.min():.3f}, {pred_v2_d.max():.3f}]")
        baseline_kappa(pred_v2_d, y_d, (0.5, 1.5, 2.5), "natural-round")
        brute_force_search(pred_v2_d, y_d, 0.0, 3.0, 0.05, "grid")
    else:
        print("  pooled_y_d mismatch — bail.")

    out = {
        "struggle_v1_hand_set": {"cutpoints": (0.2, 0.35, 0.5),
                                  "kappa": kappa_for_cutpoints(v1_score, y_s, (0.2, 0.35, 0.5))},
        "struggle_v1_optimal":  {"cutpoints": list(best_v1_struggle[1]),
                                  "kappa": best_v1_struggle[0]},
        "difficulty_v1_hand_set": {"cutpoints": (0.35, 0.5, 0.75),
                                    "kappa": kappa_for_cutpoints(v1_diff, y_d, (0.35, 0.5, 0.75))},
        "difficulty_v1_optimal":  {"cutpoints": list(best_v1_difficulty[1]),
                                    "kappa": best_v1_difficulty[0]},
    }
    out_path = OUT / "threshold_search.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nWritten to {out_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
