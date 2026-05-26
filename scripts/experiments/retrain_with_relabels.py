"""Side experiment companion to relabel_subset_gpt4o.py.

Two evaluations:

  1. Cohen's κ head-to-head on the 50 author-self-labelled snapshots:
       human  ↔  gpt-4o-mini  (canonical labels)
       human  ↔  gpt-4o-full  (new labels)
     If the new κ is higher, GPT-4o is a less noisy rater than 4o-mini.

  2. Re-train OLS struggle weights with a merged label set
     (gpt-4o-full overrides 4o-mini wherever a new label exists, otherwise the
     4o-mini label is retained). Compare Spearman ρ vs the canonical run
     (ρ +0.573) using identical CV splits.

Reads:
  data/eval/snapshots.json           (read-only)
  data/eval/llm_struggle_labels.json (read-only — canonical 4o-mini labels)
  data/eval/self_labels.json         (read-only)
  data/eval/experiments/relabel_subset_gpt4o.json (the new 4o labels)

Writes:
  data/eval/experiments/retrain_relabel_comparison.json
  data/eval/experiments/retrain_relabel_comparison.md
"""
from __future__ import annotations
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "code2"))

import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import cohen_kappa_score, mean_absolute_error
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler

EVAL = REPO / "data" / "eval"
OUT = EVAL / "experiments"

STRUGGLE_SIGNALS = ["n_hat", "t_hat", "i_norm", "r_norm", "A_norm", "d_hat", "rep_norm"]
STRUGGLE_BAND_IDX = {"On Track": 0, "Minor Issues": 1, "Struggling": 2, "Needs Help": 3}


def _train_struggle_ols(snapshots, labels):
    """Mirror scripts/optimise_v2_weights.py struggle training; return summary dict."""
    matched = [s for s in snapshots if s["snapshot_id"] in labels]
    X = np.array([[s["v1_features"][k] for k in STRUGGLE_SIGNALS] for s in matched])
    y = np.array([STRUGGLE_BAND_IDX[labels[s["snapshot_id"]]["band"]] for s in matched])
    groups = np.array([s["session_id"] for s in matched])

    gkf = GroupKFold(n_splits=5)
    fold_rhos, fold_kappas, fold_maes = [], [], []
    for tr, te in gkf.split(X, y, groups):
        sc = StandardScaler().fit(X[tr])
        lr = LinearRegression()
        lr.fit(sc.transform(X[tr]), y[tr].astype(float))
        pred = lr.predict(sc.transform(X[te]))
        rho = stats.spearmanr(pred, y[te]).correlation
        pred_band = np.clip(np.rint(pred), 0, 3).astype(int)
        try:
            kappa = cohen_kappa_score(y[te], pred_band, weights="linear")
        except ValueError:
            kappa = float("nan")
        mae = mean_absolute_error(y[te], pred_band)
        if rho is not None and not np.isnan(rho):
            fold_rhos.append(float(rho))
            fold_kappas.append(float(kappa))
            fold_maes.append(float(mae))
    return {
        "n_samples": len(matched),
        "n_folds_with_rho": len(fold_rhos),
        "rho_mean": float(np.mean(fold_rhos)) if fold_rhos else float("nan"),
        "rho_std": float(np.std(fold_rhos, ddof=1)) if len(fold_rhos) > 1 else 0.0,
        "rho_per_fold": fold_rhos,
        "kappa_mean": float(np.mean(fold_kappas)) if fold_kappas else float("nan"),
        "mae_mean": float(np.mean(fold_maes)) if fold_maes else float("nan"),
    }


def _kappa_head_to_head(human_labels, llm_labels_a, llm_labels_b, label_a, label_b):
    """Compute κ between human and each LLM on the OVERLAPPING ids."""
    shared = [sid for sid in human_labels if sid in llm_labels_a and sid in llm_labels_b]
    if not shared:
        return None
    human_band = np.array([STRUGGLE_BAND_IDX[human_labels[s]["band"]] for s in shared])
    a_band     = np.array([STRUGGLE_BAND_IDX[llm_labels_a[s]["band"]] for s in shared])
    b_band     = np.array([STRUGGLE_BAND_IDX[llm_labels_b[s]["band"]] for s in shared])
    return {
        "n_shared": len(shared),
        f"kappa_human_vs_{label_a}_unweighted":         float(cohen_kappa_score(human_band, a_band)),
        f"kappa_human_vs_{label_a}_linear_weighted":    float(cohen_kappa_score(human_band, a_band, weights="linear")),
        f"kappa_human_vs_{label_a}_quadratic_weighted": float(cohen_kappa_score(human_band, a_band, weights="quadratic")),
        f"kappa_human_vs_{label_b}_unweighted":         float(cohen_kappa_score(human_band, b_band)),
        f"kappa_human_vs_{label_b}_linear_weighted":    float(cohen_kappa_score(human_band, b_band, weights="linear")),
        f"kappa_human_vs_{label_b}_quadratic_weighted": float(cohen_kappa_score(human_band, b_band, weights="quadratic")),
        f"agreement_exact_human_vs_{label_a}": float(np.mean(human_band == a_band)),
        f"agreement_exact_human_vs_{label_b}": float(np.mean(human_band == b_band)),
        f"agreement_within_1_human_vs_{label_a}": float(np.mean(np.abs(human_band - a_band) <= 1)),
        f"agreement_within_1_human_vs_{label_b}": float(np.mean(np.abs(human_band - b_band) <= 1)),
    }


def main() -> int:
    snaps = json.loads((EVAL / "snapshots.json").read_text(encoding="utf-8"))["struggle_snapshots"]
    canonical = json.loads((EVAL / "llm_struggle_labels.json").read_text(encoding="utf-8"))["labels"]
    self_labels = json.loads((EVAL / "self_labels.json").read_text(encoding="utf-8"))["labels"]
    relabel_path = OUT / "relabel_subset_gpt4o.json"
    relabel = json.loads(relabel_path.read_text(encoding="utf-8"))["labels"]

    print(f"Loaded: {len(snaps)} snapshots, "
          f"{len(canonical)} canonical 4o-mini labels, "
          f"{len(self_labels)} author self-labels, "
          f"{len(relabel)} new 4o-full labels.")
    print()

    # Build the merged label set: 4o-full overrides 4o-mini where available
    merged = dict(canonical)
    n_overridden = 0
    for sid, lbl in relabel.items():
        if sid in merged:
            n_overridden += 1
        merged[sid] = lbl
    print(f"Merged labels: {len(merged)} total ({n_overridden} overridden from 4o-mini → 4o)")
    print()

    # ---- κ head-to-head (on the self-labelled subset) ----
    print("=" * 70)
    print("Cohen's κ: human ↔ 4o-mini   vs   human ↔ 4o-full")
    print(f"(on the {len(self_labels)} author-self-labelled snapshots)")
    print("=" * 70)
    kappa = _kappa_head_to_head(self_labels, canonical, relabel, "4o_mini", "4o_full")
    if kappa is None:
        print("No shared snapshots — skipping κ comparison")
    else:
        print(f"  n shared: {kappa['n_shared']}")
        print()
        print(f"  {'Metric':<28s} {'4o-mini':>10s} {'4o-full':>10s}  {'Δ':>8s}")
        for metric in ["unweighted", "linear_weighted", "quadratic_weighted"]:
            a = kappa[f"kappa_human_vs_4o_mini_{metric}"]
            b = kappa[f"kappa_human_vs_4o_full_{metric}"]
            print(f"  κ ({metric}):".ljust(28) + f" {a:>+10.3f} {b:>+10.3f}  {b-a:>+8.3f}")
        for metric in ["agreement_exact", "agreement_within_1"]:
            a = kappa[f"{metric}_human_vs_4o_mini"]
            b = kappa[f"{metric}_human_vs_4o_full"]
            print(f"  {metric}:".ljust(28) + f" {a:>10.1%} {b:>10.1%}  {b-a:>+8.1%}")
    print()

    # ---- Retraining: canonical vs merged ----
    print("=" * 70)
    print("OLS struggle re-training: canonical vs merged labels")
    print("(same GroupKFold(5) splits, same feature set, same model)")
    print("=" * 70)
    canon_res = _train_struggle_ols(snaps, canonical)
    merged_res = _train_struggle_ols(snaps, merged)
    print(f"  {'Metric':<22s} {'Canonical (4o-mini only)':>26s} {'Merged (4o-mini + 4o)':>22s}  {'Δ':>8s}")
    for key, label in [("rho_mean", "Spearman ρ"),
                       ("kappa_mean", "Weighted κ (band)"),
                       ("mae_mean", "MAE (band)")]:
        a, b = canon_res[key], merged_res[key]
        delta = b - a
        print(f"  {label:<22s} {a:>+26.4f} {b:>+22.4f}  {delta:>+8.4f}")
    print(f"  {'Per-fold ρ (canon)':<22s} {[round(r, 3) for r in canon_res['rho_per_fold']]}")
    print(f"  {'Per-fold ρ (merged)':<22s} {[round(r, 3) for r in merged_res['rho_per_fold']]}")
    print()

    report = {
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "Test whether re-labelling 148 stratified snapshots with GPT-4o (vs 4o-mini) lifts (a) κ vs human, (b) downstream OLS Spearman ρ.",
        "kappa_head_to_head": kappa,
        "training_canonical": canon_res,
        "training_merged": merged_res,
        "deltas": {
            "rho":   merged_res["rho_mean"]   - canon_res["rho_mean"],
            "kappa": merged_res["kappa_mean"] - canon_res["kappa_mean"],
            "mae":   merged_res["mae_mean"]   - canon_res["mae_mean"],
        },
    }
    (OUT / "retrain_relabel_comparison.json").write_text(
        json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {OUT / 'retrain_relabel_comparison.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
