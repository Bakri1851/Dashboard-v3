"""CV-validated threshold search.

Mirrors scripts/experiments/threshold_search.py but refits the cutpoints
INSIDE each CV fold:
  - struggle: GroupKFold(5) by session_id (same scheme as v2 OLS training)
  - difficulty: LeaveOneOut (same scheme as v2 OLS training, n=72)

For each held-out fold, the brute-force κ-maximising search runs on the
TRAIN fold only, then those trained cutpoints are applied to predict the
TEST fold's bands. We pool test-fold predictions across folds and compute
the honest out-of-sample κ.

Also reports per-fold cutpoint stability: if the trained cutpoints vary
wildly between folds, the gain is overfit.

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
import pandas as pd
from sklearn.metrics import cohen_kappa_score
from sklearn.model_selection import GroupKFold, LeaveOneOut

_W4 = np.abs(np.arange(4)[:, None] - np.arange(4)[None, :]).astype(np.float64)


def fast_kappa(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Linear-weighted Cohen's κ for 4-class integer arrays.

    Equivalent to sklearn.metrics.cohen_kappa_score(weights='linear',
    labels=[0,1,2,3]) but ~50× faster because it skips dispatch overhead.
    """
    cm = np.zeros((4, 4), dtype=np.int64)
    np.add.at(cm, (y_true, y_pred), 1)
    n = cm.sum()
    if n == 0:
        return 0.0
    row = cm.sum(axis=1).astype(np.float64)
    col = cm.sum(axis=0).astype(np.float64)
    expected = np.outer(row, col) / n
    num = float((_W4 * cm).sum())
    den = float((_W4 * expected).sum())
    return 1.0 - num / den if den > 0 else 0.0

EVAL = REPO / "data" / "eval"
OUT  = EVAL / "experiments"
OUT.mkdir(parents=True, exist_ok=True)

STRUGGLE_BANDS    = ["On Track", "Minor Issues", "Struggling", "Needs Help"]
DIFFICULTY_BANDS  = ["Easy", "Medium", "Hard", "Very Hard"]
STRUGGLE_BAND_INDEX   = {b: i for i, b in enumerate(STRUGGLE_BANDS)}
DIFFICULTY_BAND_INDEX = {b: i for i, b in enumerate(DIFFICULTY_BANDS)}


def _load(name):
    with (EVAL / name).open(encoding="utf-8") as f:
        return json.load(f)


def to_band(score: np.ndarray, c1: float, c2: float, c3: float) -> np.ndarray:
    out = np.zeros(score.shape, dtype=int)
    out[score >= c1] = 1
    out[score >= c2] = 2
    out[score >= c3] = 3
    return out


def search_cutpoints(score: np.ndarray, y: np.ndarray,
                     lo: float, hi: float, step: float):
    grid = np.round(np.arange(lo, hi + step, step), 4)
    best = (-2.0, None)
    for c1, c2, c3 in product(grid, grid, grid):
        if not (c1 < c2 < c3):
            continue
        pred = to_band(score, c1, c2, c3)
        k = fast_kappa(y, pred)
        if k > best[0]:
            best = (k, (float(c1), float(c2), float(c3)))
    c1b, c2b, c3b = best[1]
    fs = step / 5
    ext = step * 1.5
    c1s = np.round(np.arange(max(lo, c1b - ext), min(hi, c1b + ext) + fs, fs), 4)
    c2s = np.round(np.arange(max(lo, c2b - ext), min(hi, c2b + ext) + fs, fs), 4)
    c3s = np.round(np.arange(max(lo, c3b - ext), min(hi, c3b + ext) + fs, fs), 4)
    for c1, c2, c3 in product(c1s, c2s, c3s):
        if not (c1 < c2 < c3):
            continue
        pred = to_band(score, c1, c2, c3)
        k = fast_kappa(y, pred)
        if k > best[0]:
            best = (k, (float(c1), float(c2), float(c3)))
    return best


def cv_threshold_eval(score, y, groups, lo, hi, step, name, baseline_cutpoints):
    """Run CV-validated threshold search and return pooled metrics."""
    print(f"\n--- {name} (n={len(y)}, range=[{score.min():.3f}, {score.max():.3f}]) ---")
    base_kappa = fast_kappa(y, to_band(score, *baseline_cutpoints))
    print(f"  baseline κ @ {baseline_cutpoints}: {base_kappa:+.4f}")

    if groups is not None:
        cv = list(GroupKFold(n_splits=5).split(score, y, groups))
    else:
        cv = list(LeaveOneOut().split(score))

    pooled_pred = np.zeros_like(y)
    fold_cuts = []
    fold_train_kappa = []
    for fold_idx, (tr, te) in enumerate(cv):
        train_kappa, cuts = search_cutpoints(score[tr], y[tr], lo, hi, step)
        fold_cuts.append(cuts)
        fold_train_kappa.append(train_kappa)
        pooled_pred[te] = to_band(score[te], *cuts)
        if groups is None and fold_idx < 3:
            continue
    cv_kappa = fast_kappa(y, pooled_pred)
    print(f"  CV-pooled κ:  {cv_kappa:+.4f}  (Δ over baseline = {cv_kappa - base_kappa:+.4f})")

    cuts_arr = np.array(fold_cuts)
    cut_means = cuts_arr.mean(axis=0)
    cut_stds  = cuts_arr.std(axis=0)
    print(f"  per-fold cutpoints (n_folds={len(fold_cuts)}):")
    print(f"    c1: mean={cut_means[0]:.3f}  std={cut_stds[0]:.3f}  range=[{cuts_arr[:,0].min():.3f}, {cuts_arr[:,0].max():.3f}]")
    print(f"    c2: mean={cut_means[1]:.3f}  std={cut_stds[1]:.3f}  range=[{cuts_arr[:,1].min():.3f}, {cuts_arr[:,1].max():.3f}]")
    print(f"    c3: mean={cut_means[2]:.3f}  std={cut_stds[2]:.3f}  range=[{cuts_arr[:,2].min():.3f}, {cuts_arr[:,2].max():.3f}]")
    print(f"  per-fold train κ: mean={np.mean(fold_train_kappa):+.4f}  std={np.std(fold_train_kappa):.4f}")

    return {
        "baseline_cutpoints": list(baseline_cutpoints),
        "baseline_kappa": float(base_kappa),
        "cv_pooled_kappa": float(cv_kappa),
        "cv_pooled_delta_kappa": float(cv_kappa - base_kappa),
        "fold_cutpoints": [list(c) for c in fold_cuts],
        "fold_train_kappa": [float(k) for k in fold_train_kappa],
        "cv_cutpoint_means": cut_means.tolist(),
        "cv_cutpoint_stds":  cut_stds.tolist(),
    }


def main() -> int:
    print("=" * 78)
    print("STRUGGLE — GroupKFold(5) by session_id, brute-force κ-search per fold")
    print("=" * 78)

    snaps = _load("snapshots.json")["struggle_snapshots"]
    labels_s = _load("llm_struggle_labels.json")["labels"]
    matched_s = [s for s in snaps if s["snapshot_id"] in labels_s]
    v1_score = np.array([s["v1_struggle_score"] for s in matched_s])
    y_s      = np.array([STRUGGLE_BAND_INDEX[labels_s[s["snapshot_id"]]["band"]] for s in matched_s])
    groups_s = np.array([s["session_id"] for s in matched_s])

    pooled = _load("pooled_predictions_v2.json")["v2_struggle"]
    v2_score = np.array(pooled["pred"])
    assert np.array_equal(np.array(pooled["y"]), y_s), "pooled_y mismatch"

    matched_imp = [s for s in matched_s
                   if (s.get("improved_components") or {}).get("improved_struggle_score") is not None]
    imp_score = np.array([s["improved_components"]["improved_struggle_score"] for s in matched_imp])
    y_imp     = np.array([STRUGGLE_BAND_INDEX[labels_s[s["snapshot_id"]]["band"]] for s in matched_imp])
    groups_imp = np.array([s["session_id"] for s in matched_imp])

    results = {}
    results["struggle_v1"] = cv_threshold_eval(
        v1_score, y_s, groups_s, 0.0, 1.0, 0.025, "struggle v1 [0,1] (baseline composite)", (0.2, 0.35, 0.5))
    results["struggle_v2"] = cv_threshold_eval(
        v2_score, y_s, groups_s, 0.0, 3.0, 0.05, "struggle v2 [0,3] (OLS band-index)", (0.5, 1.5, 2.5))
    results["struggle_improved"] = cv_threshold_eval(
        imp_score, y_imp, groups_imp, 0.0, 1.0, 0.025,
        "struggle IMPROVED [0,1] (BKT+IRT) — currently shares STRUGGLE_THRESHOLDS with baseline",
        (0.2, 0.35, 0.5))

    print()
    print("=" * 78)
    print("DIFFICULTY — LeaveOneOut, brute-force κ-search per held-out question")
    print("=" * 78)

    qs = _load("snapshots.json")["difficulty_questions"]
    labels_d = _load("llm_difficulty_labels.json")["labels"]
    matched_d = [q for q in qs if q["question"] in labels_d]
    v1_diff = np.array([q["v1_difficulty_score"] for q in matched_d])
    y_d     = np.array([DIFFICULTY_BAND_INDEX[labels_d[q["question"]]["band"]] for q in matched_d])

    opt_d = _load("optimised_difficulty_weights_v2.json")
    v2_diff = np.array(opt_d["pooled_predictions"])
    assert np.array_equal(np.array(opt_d["pooled_y"]), y_d), "pooled_y_d mismatch"

    results["difficulty_v1"] = cv_threshold_eval(
        v1_diff, y_d, None, 0.0, 1.0, 0.025, "difficulty v1 [0,1] LOO (baseline composite)", (0.35, 0.5, 0.75))
    results["difficulty_v2"] = cv_threshold_eval(
        v2_diff, y_d, None, 0.0, 3.0, 0.05, "difficulty v2 [0,3] LOO (OLS band-index)", (0.5, 1.5, 2.5))

    from backend.models.irt import compute_irt_model
    subs_df = pd.read_parquet(EVAL / "submissions.parquet")
    print(f"  fitting 2PL on {len(subs_df):,} submissions for IRT thresholds...")
    irt_model = compute_irt_model(subs_df)
    irt_df = irt_model["difficulty_df"].copy()
    b_raw = irt_df["b_raw"].astype(float).values
    b_min, b_max = float(b_raw.min()), float(b_raw.max())
    irt_df["irt_score"] = (b_raw - b_min) / (b_max - b_min) if b_max > b_min else 0.5
    q_col = "question" if "question" in irt_df.columns else irt_df.columns[0]
    irt_lookup = dict(zip(irt_df[q_col].astype(str), irt_df["irt_score"].astype(float)))
    matched_irt = [q for q in matched_d if q["question"] in irt_lookup]
    irt_score = np.array([irt_lookup[q["question"]] for q in matched_irt])
    y_irt     = np.array([DIFFICULTY_BAND_INDEX[labels_d[q["question"]]["band"]] for q in matched_irt])
    print(f"  IRT-difficulty overlap with eval cohort: {len(matched_irt)} of {len(matched_d)} questions")
    results["difficulty_irt"] = cv_threshold_eval(
        irt_score, y_irt, None, 0.0, 1.0, 0.025,
        "difficulty IRT [0,1] LOO (Rasch 1PL, scaled) — currently shares DIFFICULTY_THRESHOLDS",
        (0.35, 0.5, 0.75))

    try:
        in_sample = _load("experiments/threshold_search.json")
        print()
        print("=" * 78)
        print("OVERFITTING DIAGNOSTIC (in-sample vs CV)")
        print("=" * 78)
        comparisons = [
            ("struggle_v1",   "struggle_v1_optimal",   "struggle_v1_hand_set"),
            ("difficulty_v1", "difficulty_v1_optimal", "difficulty_v1_hand_set"),
        ]
        for cv_key, ins_key, base_key in comparisons:
            base_k = in_sample[base_key]["kappa"]
            ins_k  = in_sample[ins_key]["kappa"]
            cv_k   = results[cv_key]["cv_pooled_kappa"]
            print(f"  {cv_key}: hand-set κ={base_k:+.4f}  in-sample-trained κ={ins_k:+.4f}  "
                  f"CV-trained κ={cv_k:+.4f}  (CV - hand-set = {cv_k - base_k:+.4f})")
    except FileNotFoundError:
        pass

    out_path = OUT / "threshold_search_cv.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nWritten to {out_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
