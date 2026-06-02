"""Re-fit the DEPLOYED band thresholds on the v2-OLS [0,1] composite.

Calibration fix (2026-05-27): config.py shipped STRUGGLE_THRESHOLDS /
DIFFICULTY_THRESHOLDS were fit on the v1 *baseline* composite, but the deployed
system feeds the *v2 trained-OLS* composite through them. The v2 composite is
compressed (struggle scores ~[0, 0.62], mean 0.24), so the baseline thresholds
classified ~99% of snapshots below "Needs Help".

This re-fits the cutpoints on the actual deployed composite:
    score = clip( sum(v2_weights_k * normalised_signal_k), 0, 1 )
(the score the dashboard classifies; struggle's downstream Bayesian shrinkage
is a low-n smoothing whose class-mean is computed over the full live cohort and
is therefore not reproducible from the stratified eval sample — we fit on the
reproducible composite, the dominant term).

Same constrained CV machinery as threshold_search_constrained.py:
GroupKFold(5) by session for struggle, LOO for difficulty; c1 >= train P5;
every band >= 10% of the [0,1] range. Writes the new cutpoints +
diagnostics to data/eval/experiments/threshold_search_v2composite.json.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

THIS = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS))
from threshold_search_constrained import (  # noqa: E402
    STRUGGLE_BAND_INDEX, DIFFICULTY_BAND_INDEX,
    fast_kappa, to_band, search_constrained, group_kfold_5, leave_one_out,
)


def cv_eval_floored(score, y, groups, lo, hi, step, name, baseline_cuts, min_width):
    """Constrained CV, but the On Track band is ALSO floored at min_width.

    threshold_search_constrained only floors c1 at the train-fold P5, which is
    0 for the v2 composite (>=5% of scores clip to exactly 0) -> the lowest band
    collapses to empty. We enforce c1 >= max(P5, min_width) so every band,
    including On Track, keeps >= 10% of the [0,1] range, matching the handoff's
    stated constrained intent (prevent the lowest band collapsing)."""
    print(f"\n--- {name} ---")
    print(f"  n={len(y)}  score range=[{score.min():.3f}, {score.max():.3f}]  min_width={min_width}")
    score_max = float(score.max())
    base_k = fast_kappa(y, to_band(score, *baseline_cuts))
    print(f"  baseline (current config) kappa @ {baseline_cuts}: {base_k:+.4f}")
    splits = list(group_kfold_5(groups)) if groups is not None else list(leave_one_out(len(y)))
    pooled = np.zeros_like(y)
    fold_cuts, fold_train_k = [], []
    for tr, te in splits:
        min_c1 = max(float(np.percentile(score[tr], 5)), min_width)
        train_k, cuts = search_constrained(score[tr], y[tr], lo, hi, step, min_c1, score_max, min_width)
        fold_cuts.append(cuts)
        fold_train_k.append(train_k)
        pooled[te] = to_band(score[te], *cuts)
    cv_k = fast_kappa(y, pooled)
    arr = np.array(fold_cuts)
    print(f"  constrained CV-pooled kappa: {cv_k:+.4f}  (delta over current = {cv_k - base_k:+.4f})")
    print(f"  per-fold cuts: c1={arr[:,0].mean():.3f}+/-{arr[:,0].std():.3f}  "
          f"c2={arr[:,1].mean():.3f}+/-{arr[:,1].std():.3f}  c3={arr[:,2].mean():.3f}+/-{arr[:,2].std():.3f}")
    return {
        "baseline_cutpoints": list(baseline_cuts),
        "baseline_kappa": float(base_k),
        "constrained_cv_kappa": float(cv_k),
        "constrained_delta_kappa": float(cv_k - base_k),
        "min_width": float(min_width),
        "c1_floor": "max(train P5, min_width)",
        "fold_cutpoints": [list(c) for c in fold_cuts],
        "fold_train_kappa": [float(k) for k in fold_train_k],
        "cv_cutpoint_means": arr.mean(axis=0).tolist(),
        "cv_cutpoint_stds": arr.std(axis=0).tolist(),
    }

REPO = THIS.parent.parent
EVAL = REPO / "data" / "eval"
OUT = EVAL / "experiments"

STRUGGLE_SIGNALS = ["n_hat", "t_hat", "i_norm", "r_norm", "A_norm", "d_hat", "rep_norm"]
DIFFICULTY_SIGNALS = ["c_norm", "t_tilde", "a_tilde", "f_norm", "p_norm"]


def composite(features: dict, weights: dict, signals) -> float:
    return min(max(sum(weights[k] * features[k] for k in signals), 0.0), 1.0)


def main() -> int:
    print("=" * 78)
    print("RE-FIT DEPLOYED THRESHOLDS ON THE v2-OLS [0,1] COMPOSITE")
    print("=" * 78)

    blob = json.loads((EVAL / "snapshots.json").read_text(encoding="utf-8"))
    snaps = blob["struggle_snapshots"]
    qs = blob["difficulty_questions"]
    llm_s = json.loads((EVAL / "llm_struggle_labels.json").read_text(encoding="utf-8"))["labels"]
    llm_d = json.loads((EVAL / "llm_difficulty_labels.json").read_text(encoding="utf-8"))["labels"]
    w_s = json.loads((EVAL / "optimised_struggle_weights_v2.json").read_text(encoding="utf-8"))["weights"]
    w_d = json.loads((EVAL / "optimised_difficulty_weights_v2.json").read_text(encoding="utf-8"))["weights"]

    matched_s = [s for s in snaps if s["snapshot_id"] in llm_s]
    score_s = np.array([composite(s["v1_features"], w_s, STRUGGLE_SIGNALS) for s in matched_s])
    y_s = np.array([STRUGGLE_BAND_INDEX[llm_s[s["snapshot_id"]]["band"]] for s in matched_s])
    groups_s = np.array([s["session_id"] for s in matched_s])

    matched_d = [q for q in qs if q["question"] in llm_d]
    score_d = np.array([composite(q["v1_features"], w_d, DIFFICULTY_SIGNALS) for q in matched_d])
    y_d = np.array([DIFFICULTY_BAND_INDEX[llm_d[q["question"]]["band"]] for q in matched_d])

    results = {}
    results["struggle_v2composite"] = cv_eval_floored(
        score_s, y_s, groups_s, 0.0, 1.0, 0.02,
        "struggle v2 [0,1] composite (deployed)", (0.315, 0.505, 0.605), min_width=0.10)
    results["difficulty_v2composite"] = cv_eval_floored(
        score_d, y_d, None, 0.0, 1.0, 0.02,
        "difficulty v2 [0,1] composite (deployed) LOO", (0.363, 0.463, 0.587), min_width=0.10)

    out_path = OUT / "threshold_search_v2composite.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path.relative_to(REPO)}")

    print("\n" + "=" * 78)
    print("PROPOSED config.py cutpoints (CV-mean, rounded to 3 dp):")
    for key, label in [("struggle_v2composite", "STRUGGLE"), ("difficulty_v2composite", "DIFFICULTY")]:
        cm = results[key]["cv_cutpoint_means"]
        print(f"  {label}: ({cm[0]:.3f}, {cm[1]:.3f}, {cm[2]:.3f})   "
              f"constrained CV kappa = {results[key]['constrained_cv_kappa']:+.4f} "
              f"(baseline {results[key]['baseline_kappa']:+.4f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
