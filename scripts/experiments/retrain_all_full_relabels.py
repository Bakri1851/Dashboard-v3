"""Companion to full_relabel_gpt4o.py.

Once the full GPT-4o relabel is complete, this script:

  1. Loads the new full struggle + difficulty labels (test folder only).
  2. Re-trains all 3 OLS models (struggle, difficulty, improved-struggle) +
     re-runs the Optuna hyperparam study with Spearman ρ objective.
  3. Compares headline metrics (ρ, weighted κ, MAE) to the canonical run.
  4. Writes a single comparison JSON + markdown summary to test folder only.

NEVER overwrites any canonical artefact.

Reads:
  data/eval/snapshots.json
  data/eval/llm_struggle_labels.json   (canonical 4o-mini labels — read-only)
  data/eval/llm_difficulty_labels.json (canonical 4o-mini labels — read-only)
  data/eval/optimised_struggle_weights_v2.json   (canonical ρ — read-only)
  data/eval/optimised_difficulty_weights_v2.json (canonical ρ — read-only)
  data/eval/optimised_improved_weights_v2.json   (canonical ρ — read-only)
  data/eval/optimised_hyperparams_v2.json        (canonical ρ — read-only)
  data/eval/experiments/full_relabel_struggle_gpt4o.json
  data/eval/experiments/full_relabel_difficulty_gpt4o.json

Writes:
  data/eval/experiments/full_relabel_comparison.json
  data/eval/experiments/full_relabel_comparison.md
"""
from __future__ import annotations
import json
import sys
import warnings
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

warnings.filterwarnings("ignore")

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "code2"))

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import cohen_kappa_score, mean_absolute_error
from sklearn.model_selection import GroupKFold, LeaveOneOut
from sklearn.preprocessing import StandardScaler

EVAL = REPO / "data" / "eval"
OUT = EVAL / "experiments"
OUT.mkdir(parents=True, exist_ok=True)

STRUGGLE_SIGNALS = ["n_hat", "t_hat", "i_norm", "r_norm", "A_norm", "d_hat", "rep_norm"]
DIFFICULTY_SIGNALS = ["c_norm", "t_tilde", "a_tilde", "f_norm", "p_norm"]
IMPROVED_SIGNALS = ["behavioural_composite", "mastery_gap", "difficulty_adjusted_score"]
STRUGGLE_BAND_IDX = {"On Track": 0, "Minor Issues": 1, "Struggling": 2, "Needs Help": 3}
DIFFICULTY_BAND_IDX = {"Easy": 0, "Medium": 1, "Hard": 2, "Very Hard": 3}


def _fold_metrics(y_true, pred):
    if len(y_true) < 2:
        return float("nan"), float("nan"), float("nan")
    rho = stats.spearmanr(pred, y_true).correlation
    pred_band = np.clip(np.rint(pred), 0, 3).astype(int)
    try:
        kappa = cohen_kappa_score(y_true, pred_band, weights="linear")
    except ValueError:
        kappa = float("nan")
    mae = mean_absolute_error(y_true, pred_band)
    return float(rho), float(kappa), float(mae)


def train_ols_grouped(X, y, groups, n_folds=5):
    gkf = GroupKFold(n_splits=n_folds)
    fold_rhos, fold_kappas, fold_maes = [], [], []
    for tr, te in gkf.split(X, y, groups):
        if len(np.unique(y[tr])) < 2:
            continue
        sc = StandardScaler().fit(X[tr])
        m = LinearRegression()
        m.fit(sc.transform(X[tr]), y[tr].astype(float))
        pred = m.predict(sc.transform(X[te]))
        rho, kappa, mae = _fold_metrics(y[te], pred)
        if rho is not None and not np.isnan(rho):
            fold_rhos.append(rho)
            fold_kappas.append(kappa)
            fold_maes.append(mae)
    return {
        "n_samples": int(len(y)),
        "rho_mean": float(np.mean(fold_rhos)) if fold_rhos else float("nan"),
        "rho_std": float(np.std(fold_rhos, ddof=1)) if len(fold_rhos) > 1 else 0.0,
        "rho_per_fold": fold_rhos,
        "kappa_mean": float(np.mean(fold_kappas)) if fold_kappas else float("nan"),
        "mae_mean": float(np.mean(fold_maes)) if fold_maes else float("nan"),
    }


def train_ols_loo(X, y):
    loo = LeaveOneOut()
    pred = []
    for tr, te in loo.split(X):
        if len(np.unique(y[tr])) < 2:
            pred.append(float(y[tr].mean()))
            continue
        sc = StandardScaler().fit(X[tr])
        m = LinearRegression()
        m.fit(sc.transform(X[tr]), y[tr].astype(float))
        pred.append(float(m.predict(sc.transform(X[te]))[0]))
    pred = np.array(pred)
    rho, kappa, mae = _fold_metrics(y, pred)
    return {"n_samples": int(len(y)), "rho_mean": rho, "kappa_mean": kappa, "mae_mean": mae}


def main() -> int:
    snap_blob = json.loads((EVAL / "snapshots.json").read_text(encoding="utf-8"))
    snapshots = snap_blob.get("struggle_snapshots", [])
    questions = snap_blob.get("difficulty_questions", [])

    canon_struggle = json.loads((EVAL / "llm_struggle_labels.json").read_text(encoding="utf-8"))["labels"]
    canon_difficulty = json.loads((EVAL / "llm_difficulty_labels.json").read_text(encoding="utf-8"))["labels"]

    new_s_path = OUT / "full_relabel_struggle_gpt4o.json"
    new_d_path = OUT / "full_relabel_difficulty_gpt4o.json"
    if not new_s_path.exists() or not new_d_path.exists():
        print(f"ERROR: full_relabel JSONs missing. Run full_relabel_gpt4o.py first.", file=sys.stderr)
        return 1
    new_struggle = json.loads(new_s_path.read_text(encoding="utf-8"))["labels"]
    new_difficulty = json.loads(new_d_path.read_text(encoding="utf-8"))["labels"]
    print(f"Labels loaded: canonical struggle {len(canon_struggle)}, "
          f"new struggle {len(new_struggle)}; "
          f"canonical difficulty {len(canon_difficulty)}, "
          f"new difficulty {len(new_difficulty)}")
    print()

    results = {"ran_at": datetime.now(timezone.utc).isoformat(), "models": {}}

    print("=" * 70 + "\nSTRUGGLE\n" + "=" * 70)
    for name, lbls in [("canonical (4o-mini)", canon_struggle), ("new (4o-full)", new_struggle)]:
        matched = [s for s in snapshots if s["snapshot_id"] in lbls]
        X = np.array([[s["v1_features"][k] for k in STRUGGLE_SIGNALS] for s in matched])
        y = np.array([STRUGGLE_BAND_IDX[lbls[s["snapshot_id"]]["band"]] for s in matched])
        groups = np.array([s["session_id"] for s in matched])
        res = train_ols_grouped(X, y, groups)
        results["models"].setdefault("struggle", {})[name] = res
        print(f"  {name:<22s} N={res['n_samples']:>5d}  ρ={res['rho_mean']:+.4f}  "
              f"κ={res['kappa_mean']:+.4f}  MAE={res['mae_mean']:.3f}  "
              f"folds={[round(r, 3) for r in res['rho_per_fold']]}")

    print("\n" + "=" * 70 + "\nDIFFICULTY\n" + "=" * 70)
    for name, lbls in [("canonical (4o-mini)", canon_difficulty), ("new (4o-full)", new_difficulty)]:
        matched = [q for q in questions if q["question"] in lbls]
        X = np.array([[q["v1_features"][k] for k in DIFFICULTY_SIGNALS] for q in matched])
        y = np.array([DIFFICULTY_BAND_IDX[lbls[q["question"]]["band"]] for q in matched])
        res = train_ols_loo(X, y)
        results["models"].setdefault("difficulty", {})[name] = res
        print(f"  {name:<22s} N={res['n_samples']:>3d}  ρ={res['rho_mean']:+.4f}  "
              f"κ={res['kappa_mean']:+.4f}  MAE={res['mae_mean']:.3f}")

    print("\n" + "=" * 70 + "\nIMPROVED-STRUGGLE\n" + "=" * 70)
    for name, lbls in [("canonical (4o-mini)", canon_struggle), ("new (4o-full)", new_struggle)]:
        matched = [
            s for s in snapshots
            if s["snapshot_id"] in lbls
            and s.get("improved_components")
            and "behavioural_composite" in s["improved_components"]
        ]
        X = np.array([[s["improved_components"][k] for k in IMPROVED_SIGNALS] for s in matched])
        y = np.array([STRUGGLE_BAND_IDX[lbls[s["snapshot_id"]]["band"]] for s in matched])
        groups = np.array([s["session_id"] for s in matched])
        res = train_ols_grouped(X, y, groups)
        results["models"].setdefault("improved_struggle", {})[name] = res
        print(f"  {name:<22s} N={res['n_samples']:>5d}  ρ={res['rho_mean']:+.4f}  "
              f"κ={res['kappa_mean']:+.4f}  MAE={res['mae_mean']:.3f}  "
              f"folds={[round(r, 3) for r in res['rho_per_fold']]}")

    print("\n" + "=" * 70 + "\nDELTAS (new − canonical)\n" + "=" * 70)
    print(f"  {'Model':<20s} {'canon ρ':>10s} {'new ρ':>10s} {'Δρ':>10s}")
    for kind in ["struggle", "difficulty", "improved_struggle"]:
        c = results["models"][kind]["canonical (4o-mini)"]["rho_mean"]
        n = results["models"][kind]["new (4o-full)"]["rho_mean"]
        print(f"  {kind:<20s} {c:+.4f}    {n:+.4f}    {n - c:+.4f}")

    (OUT / "full_relabel_comparison.json").write_text(
        json.dumps(results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {OUT / 'full_relabel_comparison.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
