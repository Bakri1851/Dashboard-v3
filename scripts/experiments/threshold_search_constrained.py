"""Constrained CV threshold search — all 6 model sets, but with two
guardrails added to the brute-force κ-max:

  * `min_c1` = train-fold 5th percentile of score → forces the lowest band
    to capture ≥5% of training samples. Stops the `c1 = 0` collapse where
    the lowest band ('On Track' / 'Easy') goes empty just because the
    cohort happens to have few/no truly-low-severity entities.

  * `min_width` per band → no band thinner than 10% of the score range
    (0.10 in [0,1] space, 0.30 in [0,3] space). Stops trained bands
    becoming so narrow they're degenerate.

Lower κ than the unconstrained search by design — the point is to produce
thresholds that survive a new cohort with a different label distribution,
rather than overfit to this cohort's class imbalance.

Minimal imports (json + numpy + csv) so it runs under Windows memory
pressure where scipy/sklearn DLL loads fail. v2 OLS scores lifted from
pooled_predictions_v2.json + optimised_difficulty_weights_v2.json. IRT
scores lifted from comparison_difficulty_pairs.csv. fast_kappa reused
from threshold_search_cv.py (inlined here to keep this self-contained).

Merges into data/eval/experiments/threshold_search_cv.json under
`*_constrained` keys alongside the existing unconstrained ones.
"""
from __future__ import annotations
import csv
import json
import sys
from itertools import product
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
EVAL = REPO / "data" / "eval"
OUT  = EVAL / "experiments"

import numpy as np

STRUGGLE_BAND_INDEX   = {"On Track": 0, "Minor Issues": 1, "Struggling": 2, "Needs Help": 3}
DIFFICULTY_BAND_INDEX = {"Easy": 0, "Medium": 1, "Hard": 2, "Very Hard": 3}

_W4 = np.abs(np.arange(4)[:, None] - np.arange(4)[None, :]).astype(np.float64)


def fast_kappa(y_true, y_pred):
    cm = np.zeros((4, 4), dtype=np.int64)
    np.add.at(cm, (y_true, y_pred), 1)
    n = cm.sum()
    if n == 0: return 0.0
    row = cm.sum(axis=1).astype(np.float64)
    col = cm.sum(axis=0).astype(np.float64)
    expected = np.outer(row, col) / n
    num = float((_W4 * cm).sum())
    den = float((_W4 * expected).sum())
    return 1.0 - num / den if den > 0 else 0.0


def to_band(score, c1, c2, c3):
    out = np.zeros(score.shape, dtype=int)
    out[score >= c1] = 1
    out[score >= c2] = 2
    out[score >= c3] = 3
    return out


def search_constrained(score, y, lo, hi, step, min_c1, score_max, min_width):
    """Grid search with cutpoint constraints applied as skip filters."""
    grid = np.round(np.arange(lo, hi + step, step), 4)
    best = (-2.0, None)
    for c1, c2, c3 in product(grid, grid, grid):
        if not (c1 < c2 < c3): continue
        if c1 < min_c1: continue
        if (c2 - c1) < min_width: continue
        if (c3 - c2) < min_width: continue
        if (score_max - c3) < min_width: continue
        k = fast_kappa(y, to_band(score, c1, c2, c3))
        if k > best[0]:
            best = (k, (float(c1), float(c2), float(c3)))
    if best[1] is None:
        # No combo satisfied constraints — fall back to relaxed min_width
        for c1, c2, c3 in product(grid, grid, grid):
            if not (c1 < c2 < c3): continue
            if c1 < min_c1: continue
            k = fast_kappa(y, to_band(score, c1, c2, c3))
            if k > best[0]:
                best = (k, (float(c1), float(c2), float(c3)))
    # Refine around the coarse best
    c1b, c2b, c3b = best[1]
    fs = step / 5
    ext = step * 1.5
    c1s = np.round(np.arange(max(lo, c1b - ext), min(hi, c1b + ext) + fs, fs), 4)
    c2s = np.round(np.arange(max(lo, c2b - ext), min(hi, c2b + ext) + fs, fs), 4)
    c3s = np.round(np.arange(max(lo, c3b - ext), min(hi, c3b + ext) + fs, fs), 4)
    for c1, c2, c3 in product(c1s, c2s, c3s):
        if not (c1 < c2 < c3): continue
        if c1 < min_c1: continue
        if (c2 - c1) < min_width or (c3 - c2) < min_width: continue
        if (score_max - c3) < min_width: continue
        k = fast_kappa(y, to_band(score, c1, c2, c3))
        if k > best[0]:
            best = (k, (float(c1), float(c2), float(c3)))
    return best


def group_kfold_5(groups):
    unique = np.array(sorted(set(groups.tolist())))
    fold_assign = {g: i % 5 for i, g in enumerate(unique)}
    fold_of = np.array([fold_assign[g] for g in groups])
    for f in range(5):
        te_mask = fold_of == f
        yield np.where(~te_mask)[0], np.where(te_mask)[0]


def leave_one_out(n):
    for i in range(n):
        te = np.array([i])
        tr = np.array([j for j in range(n) if j != i])
        yield tr, te


def cv_eval_constrained(score, y, groups, lo, hi, step, name, baseline_cuts,
                         min_width, c1_percentile=5):
    """Run constrained CV. min_c1 per fold = train-fold's `c1_percentile`-th
    percentile of score. Reports unconstrained baseline for sanity."""
    print(f"\n--- {name} ---")
    print(f"  n={len(y)}  score range=[{score.min():.3f}, {score.max():.3f}]  "
          f"min_width={min_width}  c1≥train P{c1_percentile}")
    score_max = float(score.max())
    base_k = fast_kappa(y, to_band(score, *baseline_cuts))
    print(f"  baseline κ @ {baseline_cuts}: {base_k:+.4f}")

    splits = list(group_kfold_5(groups)) if groups is not None else list(leave_one_out(len(y)))
    pooled = np.zeros_like(y)
    fold_cuts = []
    fold_train_k = []
    fold_min_c1 = []
    for tr, te in splits:
        min_c1 = float(np.percentile(score[tr], c1_percentile))
        fold_min_c1.append(min_c1)
        train_k, cuts = search_constrained(
            score[tr], y[tr], lo, hi, step, min_c1, score_max, min_width)
        fold_cuts.append(cuts)
        fold_train_k.append(train_k)
        pooled[te] = to_band(score[te], *cuts)
    cv_k = fast_kappa(y, pooled)
    print(f"  constrained CV-pooled κ:  {cv_k:+.4f}  (Δ over hand-set = {cv_k - base_k:+.4f})")
    arr = np.array(fold_cuts)
    print(f"  per-fold cuts: c1 mean={arr[:,0].mean():.3f}±{arr[:,0].std():.3f}  "
          f"c2 mean={arr[:,1].mean():.3f}±{arr[:,1].std():.3f}  "
          f"c3 mean={arr[:,2].mean():.3f}±{arr[:,2].std():.3f}")
    print(f"  per-fold min_c1 (5th pctile): mean={np.mean(fold_min_c1):.3f}")
    return {
        "baseline_cutpoints": list(baseline_cuts),
        "baseline_kappa": float(base_k),
        "constrained_cv_kappa": float(cv_k),
        "constrained_delta_kappa": float(cv_k - base_k),
        "min_width": float(min_width),
        "c1_percentile_floor": c1_percentile,
        "fold_cutpoints": [list(c) for c in fold_cuts],
        "fold_train_kappa": [float(k) for k in fold_train_k],
        "fold_min_c1": [float(m) for m in fold_min_c1],
        "cv_cutpoint_means": arr.mean(axis=0).tolist(),
        "cv_cutpoint_stds":  arr.std(axis=0).tolist(),
    }


def main() -> int:
    print("=" * 78)
    print("CONSTRAINED CV THRESHOLD SEARCH — all 6 model sets")
    print(" constraints: c1 ≥ train P5  AND  every band ≥ min_width wide")
    print("=" * 78)

    snaps = json.loads((EVAL / "snapshots.json").read_text(encoding="utf-8"))["struggle_snapshots"]
    llm_s = json.loads((EVAL / "llm_struggle_labels.json").read_text(encoding="utf-8"))["labels"]
    matched_s = [s for s in snaps if s["snapshot_id"] in llm_s]
    v1_score = np.array([float(s["v1_struggle_score"]) for s in matched_s])
    y_s      = np.array([STRUGGLE_BAND_INDEX[llm_s[s["snapshot_id"]]["band"]] for s in matched_s])
    groups_s = np.array([s["session_id"] for s in matched_s])

    pooled_v2 = json.loads((EVAL / "pooled_predictions_v2.json").read_text(encoding="utf-8"))["v2_struggle"]
    v2_score = np.array(pooled_v2["pred"])
    assert np.array_equal(np.array(pooled_v2["y"]), y_s), "pooled_y mismatch"

    matched_imp = [s for s in matched_s
                   if (s.get("improved_components") or {}).get("improved_struggle_score") is not None]
    imp_score = np.array([float(s["improved_components"]["improved_struggle_score"]) for s in matched_imp])
    y_imp     = np.array([STRUGGLE_BAND_INDEX[llm_s[s["snapshot_id"]]["band"]] for s in matched_imp])
    groups_imp = np.array([s["session_id"] for s in matched_imp])

    qs = json.loads((EVAL / "snapshots.json").read_text(encoding="utf-8"))["difficulty_questions"]
    llm_d = json.loads((EVAL / "llm_difficulty_labels.json").read_text(encoding="utf-8"))["labels"]
    matched_d = [q for q in qs if q["question"] in llm_d]
    v1_diff = np.array([float(q["v1_difficulty_score"]) for q in matched_d])
    y_d     = np.array([DIFFICULTY_BAND_INDEX[llm_d[q["question"]]["band"]] for q in matched_d])

    opt_d = json.loads((EVAL / "optimised_difficulty_weights_v2.json").read_text(encoding="utf-8"))
    v2_diff = np.array(opt_d["pooled_predictions"])
    assert np.array_equal(np.array(opt_d["pooled_y"]), y_d), "pooled_y_d mismatch"

    pairs_path = EVAL / "comparison_difficulty_pairs.csv"
    rows_l = [r for r in csv.DictReader(pairs_path.open(encoding="utf-8")) if r["llm_band"]]
    irt_score = np.array([float(r["irt_score"]) for r in rows_l])
    y_irt     = np.array([DIFFICULTY_BAND_INDEX[r["llm_band"]] for r in rows_l])

    results = {}
    results["struggle_v1_constrained"] = cv_eval_constrained(
        v1_score, y_s, groups_s, 0.0, 1.0, 0.025,
        "struggle v1 [0,1] baseline composite", (0.2, 0.35, 0.5), min_width=0.10)
    results["struggle_improved_constrained"] = cv_eval_constrained(
        imp_score, y_imp, groups_imp, 0.0, 1.0, 0.025,
        "struggle IMPROVED [0,1] (BKT+IRT)", (0.2, 0.35, 0.5), min_width=0.10)
    results["struggle_v2_constrained"] = cv_eval_constrained(
        v2_score, y_s, groups_s, 0.0, 3.0, 0.05,
        "struggle v2 [0,3] OLS", (0.5, 1.5, 2.5), min_width=0.30)
    results["difficulty_v1_constrained"] = cv_eval_constrained(
        v1_diff, y_d, None, 0.0, 1.0, 0.025,
        "difficulty v1 [0,1] baseline composite LOO", (0.35, 0.5, 0.75), min_width=0.10)
    results["difficulty_irt_constrained"] = cv_eval_constrained(
        irt_score, y_irt, None, 0.0, 1.0, 0.025,
        "difficulty IRT [0,1] LOO", (0.35, 0.5, 0.75), min_width=0.10)
    results["difficulty_v2_constrained"] = cv_eval_constrained(
        v2_diff, y_d, None, 0.0, 3.0, 0.05,
        "difficulty v2 [0,3] OLS LOO", (0.5, 1.5, 2.5), min_width=0.30)

    cv_path = OUT / "threshold_search_cv.json"
    existing = json.loads(cv_path.read_text(encoding="utf-8")) if cv_path.exists() else {}
    existing.update(results)
    cv_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    print(f"\nMerged into {cv_path.relative_to(REPO)}")

    print()
    print("=" * 92)
    print("SUMMARY — hand-set κ vs unconstrained-CV κ vs constrained-CV κ")
    print("=" * 92)
    print(f"{'model':<36s}  {'hand-set':>9s}  {'unconstr':>9s}  {'constr':>9s}  {'Δ unc':>7s}  {'Δ con':>7s}")
    print(f"{'-'*36}  {'-'*9}  {'-'*9}  {'-'*9}  {'-'*7}  {'-'*7}")
    pairs = [
        ("struggle_v1",       "struggle  baseline composite"),
        ("struggle_improved", "struggle  improved (BKT+IRT)"),
        ("struggle_v2",       "struggle  v2 OLS [0,3]"),
        ("difficulty_v1",     "difficulty baseline composite"),
        ("difficulty_irt",    "difficulty IRT Rasch"),
        ("difficulty_v2",     "difficulty v2 OLS [0,3]"),
    ]
    for key, label in pairs:
        bk = existing.get(key, {}).get("baseline_kappa")
        uk = existing.get(key, {}).get("cv_pooled_kappa")
        ck = existing.get(f"{key}_constrained", {}).get("constrained_cv_kappa")
        if bk is None: continue
        line = f"{label:<36s}  {bk:>+9.4f}  "
        line += f"{uk:>+9.4f}  " if uk is not None else f"{'—':>9s}  "
        line += f"{ck:>+9.4f}  " if ck is not None else f"{'—':>9s}  "
        line += f"{(uk - bk):>+7.4f}  " if uk is not None else f"{'—':>7s}  "
        line += f"{(ck - bk):>+7.4f}" if ck is not None else f"{'—':>7s}"
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
