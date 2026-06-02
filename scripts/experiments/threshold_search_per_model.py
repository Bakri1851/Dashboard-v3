"""Per-model threshold search — adds threshold sets for improved-struggle
and IRT-difficulty (which currently share STRUGGLE_THRESHOLDS /
DIFFICULTY_THRESHOLDS with their baseline-composite siblings).

Minimal-imports variant: json + numpy + csv only, manual κ + manual CV
splitters. Designed to run under Windows memory pressure where the full
scipy/sklearn stack fails to load.

IRT difficulty scores are lifted from data/eval/comparison_difficulty_pairs.csv
(written by notebooks/model_comparison.ipynb on its last run) to avoid
re-fitting the 2PL model in-process.

Merges results into data/eval/experiments/threshold_search_cv.json under
the new keys `struggle_improved` and `difficulty_irt`.
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


def fast_kappa(y_true: np.ndarray, y_pred: np.ndarray) -> float:
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


def to_band(score: np.ndarray, c1: float, c2: float, c3: float) -> np.ndarray:
    out = np.zeros(score.shape, dtype=int)
    out[score >= c1] = 1
    out[score >= c2] = 2
    out[score >= c3] = 3
    return out


def search_cutpoints(score, y, lo, hi, step):
    grid = np.round(np.arange(lo, hi + step, step), 4)
    best = (-2.0, None)
    for c1, c2, c3 in product(grid, grid, grid):
        if not (c1 < c2 < c3):
            continue
        k = fast_kappa(y, to_band(score, c1, c2, c3))
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
        k = fast_kappa(y, to_band(score, c1, c2, c3))
        if k > best[0]:
            best = (k, (float(c1), float(c2), float(c3)))
    return best


def group_kfold_5(groups: np.ndarray):
    """Tiny GroupKFold(5): 5 contiguous group-index slices, no shuffling.
    Matches sklearn's GroupKFold deterministically enough for our needs.
    """
    unique = np.array(sorted(set(groups.tolist())))
    fold_assign = {g: i % 5 for i, g in enumerate(unique)}
    fold_of = np.array([fold_assign[g] for g in groups])
    for f in range(5):
        te_mask = fold_of == f
        yield np.where(~te_mask)[0], np.where(te_mask)[0]


def leave_one_out(n: int):
    for i in range(n):
        te = np.array([i])
        tr = np.array([j for j in range(n) if j != i])
        yield tr, te


def cv_eval(score, y, groups, lo, hi, step, name, baseline_cuts):
    print(f"\n--- {name} (n={len(y)}, range=[{score.min():.3f}, {score.max():.3f}]) ---")
    base_k = fast_kappa(y, to_band(score, *baseline_cuts))
    print(f"  baseline κ @ {baseline_cuts}: {base_k:+.4f}")
    splits = list(group_kfold_5(groups)) if groups is not None else list(leave_one_out(len(y)))
    pooled = np.zeros_like(y)
    fold_cuts = []
    fold_train_k = []
    for tr, te in splits:
        train_k, cuts = search_cutpoints(score[tr], y[tr], lo, hi, step)
        fold_cuts.append(cuts)
        fold_train_k.append(train_k)
        pooled[te] = to_band(score[te], *cuts)
    cv_k = fast_kappa(y, pooled)
    print(f"  CV-pooled κ:  {cv_k:+.4f}  (Δ over baseline = {cv_k - base_k:+.4f})")
    arr = np.array(fold_cuts)
    print(f"  per-fold cuts (n={len(splits)}): "
          f"c1 mean={arr[:,0].mean():.3f}±{arr[:,0].std():.3f}, "
          f"c2 mean={arr[:,1].mean():.3f}±{arr[:,1].std():.3f}, "
          f"c3 mean={arr[:,2].mean():.3f}±{arr[:,2].std():.3f}")
    return {
        "baseline_cutpoints": list(baseline_cuts),
        "baseline_kappa": float(base_k),
        "cv_pooled_kappa": float(cv_k),
        "cv_pooled_delta_kappa": float(cv_k - base_k),
        "fold_cutpoints": [list(c) for c in fold_cuts],
        "fold_train_kappa": [float(k) for k in fold_train_k],
        "cv_cutpoint_means": arr.mean(axis=0).tolist(),
        "cv_cutpoint_stds":  arr.std(axis=0).tolist(),
    }


def main() -> int:
    print("=" * 78)
    print("PER-MODEL THRESHOLD SEARCH (new sets only)")
    print("  + struggle_improved (BKT+IRT [0,1])")
    print("  + difficulty_irt    (Rasch 1PL b_raw, scaled to [0,1])")
    print("=" * 78)

    snaps = json.loads((EVAL / "snapshots.json").read_text(encoding="utf-8"))["struggle_snapshots"]
    llm_s = json.loads((EVAL / "llm_struggle_labels.json").read_text(encoding="utf-8"))["labels"]
    matched = [s for s in snaps
               if s["snapshot_id"] in llm_s
               and (s.get("improved_components") or {}).get("improved_struggle_score") is not None]
    imp_score = np.array([float(s["improved_components"]["improved_struggle_score"]) for s in matched])
    y_imp     = np.array([STRUGGLE_BAND_INDEX[llm_s[s["snapshot_id"]]["band"]] for s in matched])
    groups    = np.array([s["session_id"] for s in matched])
    print(f"struggle improved: {len(matched)} matched snapshots (with improved_components + label)")

    res_imp = cv_eval(imp_score, y_imp, groups, 0.0, 1.0, 0.025,
                     "struggle IMPROVED [0,1] (BKT+IRT blend) — GroupKFold(5)",
                     (0.2, 0.35, 0.5))

    pairs_path = EVAL / "comparison_difficulty_pairs.csv"
    if not pairs_path.exists():
        print(f"\nFAIL: {pairs_path.relative_to(REPO)} not found — "
              f"run notebooks/model_comparison.ipynb first to generate IRT scores")
        return 1

    rows = list(csv.DictReader(pairs_path.open(encoding="utf-8")))
    irt_score = np.array([float(r["irt_score"]) for r in rows])
    y_irt     = np.array([DIFFICULTY_BAND_INDEX[r["llm_band"]] for r in rows if r["llm_band"]])
    rows_l = [r for r in rows if r["llm_band"]]
    irt_score = np.array([float(r["irt_score"]) for r in rows_l])
    y_irt     = np.array([DIFFICULTY_BAND_INDEX[r["llm_band"]] for r in rows_l])
    print(f"\ndifficulty IRT: {len(rows_l)} questions (with IRT fit + LLM label)")

    res_irt = cv_eval(irt_score, y_irt, None, 0.0, 1.0, 0.025,
                     "difficulty IRT [0,1] (Rasch scaled) — LOO",
                     (0.35, 0.5, 0.75))

    cv_path = OUT / "threshold_search_cv.json"
    existing = json.loads(cv_path.read_text(encoding="utf-8")) if cv_path.exists() else {}
    existing["struggle_improved"] = res_imp
    existing["difficulty_irt"]    = res_irt
    cv_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    print(f"\nWritten merged results to {cv_path.relative_to(REPO)}")

    print()
    print("=" * 78)
    print("SUMMARY — all 6 model threshold sets, CV-trained vs hand-set")
    print("=" * 78)
    print(f"{'model':<32s}  {'hand-set κ':>10s}  {'CV-trained κ':>14s}  {'Δ':>7s}")
    print(f"{'-'*32}  {'-'*10}  {'-'*14}  {'-'*7}")
    for key, label in [
        ("struggle_v1",       "struggle  baseline composite"),
        ("struggle_improved", "struggle  improved (BKT+IRT) ★ NEW"),
        ("struggle_v2",       "struggle  v2 OLS [0,3]"),
        ("difficulty_v1",     "difficulty baseline composite"),
        ("difficulty_irt",    "difficulty IRT Rasch        ★ NEW"),
        ("difficulty_v2",     "difficulty v2 OLS [0,3]"),
    ]:
        r = existing.get(key)
        if not r: continue
        bk = r["baseline_kappa"]
        ck = r["cv_pooled_kappa"]
        print(f"{label:<32s}  {bk:>+10.4f}  {ck:>+14.4f}  {ck - bk:>+7.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
