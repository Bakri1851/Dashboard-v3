"""Phase 4 — Optimise v2 weight vectors via ordinary least-squares linear regression.

Three modes share the same training infrastructure. The outer CV scheme differs
by mode:

  --kind struggle    : 5-fold group K-fold, session as group  (N=1306)
  --kind difficulty  : leave-one-out on questions             (N=72)
  --kind improved    : 5-fold group K-fold (requires snapshot extension)

**Target**: the LLM's 4-band rating (`On Track`=0, `Minor Issues`=1,
`Struggling`=2, `Needs Help`=3 for struggle; analogous `Easy ... Very Hard` for
difficulty). This matches what the dashboard surfaces — a ranked leaderboard
mapped to bands — rather than the binary "intervene now?" decision the
system does NOT automatically make.

**Model class**: ordinary least squares (`sklearn.linear_model.LinearRegression`).
No regularisation. Coefficients are interpretable as "expected change in band
index per unit feature".

**Metrics**: Spearman ρ (rank quality) + linear-weighted Cohen's κ (band
agreement) + MAE (mean absolute band-distance error). AUC + Brier are not used
— neither is meaningful for a continuous regression on a band target.

Run from repo root::

    python scripts/optimise_v2_weights.py --kind struggle
    python scripts/optimise_v2_weights.py --kind difficulty
    python scripts/optimise_v2_weights.py --kind improved

Outputs written under ``data/eval/``::

    optimised_struggle_weights_v2.json
    optimised_difficulty_weights_v2.json
    optimised_improved_weights_v2.json
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "code2"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402
from sklearn.linear_model import LinearRegression  # noqa: E402
from sklearn.metrics import cohen_kappa_score, mean_absolute_error  # noqa: E402
from sklearn.model_selection import GroupKFold, LeaveOneOut  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from backend import paths  # noqa: E402


STRUGGLE_FEATURE_COLS = ["n_hat", "t_hat", "i_norm", "r_norm", "A_norm", "d_hat", "rep_norm"]
DIFFICULTY_FEATURE_COLS = ["c_norm", "t_tilde", "a_tilde", "f_norm", "p_norm"]
IMPROVED_FEATURE_COLS = ["behavioural_composite", "mastery_gap", "difficulty_adjusted_score"]
DEFAULT_SEED = 42

STRUGGLE_BAND_INDEX = {
    "On Track": 0,
    "Minor Issues": 1,
    "Struggling": 2,
    "Needs Help": 3,
}
DIFFICULTY_BAND_INDEX = {
    "Easy": 0,
    "Medium": 1,
    "Hard": 2,
    "Very Hard": 3,
}
N_BANDS = 4
TARGET_DESCRIPTION = (
    "4-band rating (LLM second-opinion). "
    "Struggle: On Track=0, Minor Issues=1, Struggling=2, Needs Help=3. "
    "Difficulty: Easy=0, Medium=1, Hard=2, Very Hard=3."
)


def _load_snapshots() -> dict:
    path = paths.DATA_DIR / "eval" / "snapshots.json"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing. Run scripts/eval_common.py first.")
    return json.loads(path.read_text(encoding="utf-8"))


def _load_labels(kind: str) -> dict[str, dict]:
    path = paths.DATA_DIR / "eval" / f"llm_{kind}_labels.json"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} missing. Run `scripts/eval_label.py --mode {kind}` first."
        )
    blob = json.loads(path.read_text(encoding="utf-8"))
    return blob.get("labels", {})


def _unscale_coefs(coefs_std: np.ndarray, scaler: StandardScaler) -> np.ndarray:
    """Convert OLS coefficients fit on standardised features back to raw-feature space.

    Standardised:  y = b0 + sum(c_i * (x_i - mu_i) / sigma_i)
    Raw:           y = b0' + sum(c_i' * x_i),  where  c_i' = c_i / sigma_i.
    """
    return coefs_std / scaler.scale_


def _normalise_to_convex(coefs: np.ndarray) -> np.ndarray:
    """L1-normalise the raw-space coefficient vector so |w|_1 = 1, preserving sign.

    The v1 hand-set weights sum to 1 (convex combination). Reporting v2 weights
    on the same scale makes the term-by-term v1 vs v2 comparison interpretable.
    L1 rather than positive-only renormalisation because OLS may legitimately
    learn a negative weight on a signal that proxies the wrong direction for
    severity (e.g. low submission count → struggling).
    """
    l1 = float(np.abs(coefs).sum())
    if l1 <= 0:
        return np.full_like(coefs, 1.0 / len(coefs))
    return coefs / l1


def _pred_to_band(pred: np.ndarray) -> np.ndarray:
    """Round + clip continuous OLS prediction to a valid band index in {0..3}."""
    return np.clip(np.rint(pred), 0, N_BANDS - 1).astype(int)


def _fold_metrics(y_true: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    """Spearman ρ on raw predictions + linear-weighted κ + MAE on rounded bands."""
    if len(y_true) < 2 or len(np.unique(y_true)) < 2:
        return {
            "spearman_rho": float("nan"),
            "weighted_kappa": float("nan"),
            "mae": float("nan"),
            "mae_continuous": float("nan"),
        }
    rho = float(stats.spearmanr(pred, y_true).correlation)
    pred_band = _pred_to_band(pred)
    try:
        kappa = float(cohen_kappa_score(y_true, pred_band, weights="linear"))
    except ValueError:
        kappa = float("nan")
    return {
        "spearman_rho": rho if not np.isnan(rho) else float("nan"),
        "weighted_kappa": kappa,
        "mae": float(mean_absolute_error(y_true, pred_band)),
        "mae_continuous": float(np.mean(np.abs(pred - y_true))),
    }


def _train_one_fold(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    feature_cols: list[str],
    seed: int = DEFAULT_SEED,
) -> dict:
    """Fit OLS on the outer training fold; predict on test; return per-fold metrics."""
    if len(np.unique(y_train)) < 2:
        return {
            "spearman_rho": float("nan"),
            "weighted_kappa": float("nan"),
            "mae": float("nan"),
            "mae_continuous": float("nan"),
            "n_train": int(len(X_train)),
            "n_test": int(len(X_test)),
            "y_test_mean": float(y_test.mean()) if len(y_test) else 0.0,
            "y_test_std": float(y_test.std()) if len(y_test) else 0.0,
            "coefs_raw": {k: float("nan") for k in feature_cols},
            "weights_convex": {k: float("nan") for k in feature_cols},
            "skipped_reason": "single_target_value_training_fold",
        }

    scaler = StandardScaler().fit(X_train)
    Xtr_s = scaler.transform(X_train)
    Xte_s = scaler.transform(X_test)

    lr = LinearRegression()
    lr.fit(Xtr_s, y_train.astype(float))
    pred_test = lr.predict(Xte_s)

    metrics = _fold_metrics(y_test, pred_test)
    raw_coefs = _unscale_coefs(lr.coef_, scaler)
    convex = _normalise_to_convex(raw_coefs)
    return {
        **metrics,
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "y_test_mean": float(y_test.mean()) if len(y_test) else 0.0,
        "y_test_std": float(y_test.std()) if len(y_test) else 0.0,
        "coefs_raw": dict(zip(feature_cols, [float(c) for c in raw_coefs])),
        "weights_convex": dict(zip(feature_cols, [float(c) for c in convex])),
    }


def _summarise_folds(per_fold: list[dict], feature_cols: list[str], n_folds: int) -> dict:
    """Mean / std / 95% CI across the per-fold Spearman ρ + weighted κ + MAE."""
    valid_rhos = [f["spearman_rho"] for f in per_fold if not np.isnan(f["spearman_rho"])]
    valid_kappas = [f["weighted_kappa"] for f in per_fold if not np.isnan(f["weighted_kappa"])]
    valid_maes = [f["mae"] for f in per_fold if not np.isnan(f["mae"])]

    def _agg(values: list[float]) -> tuple[float, float, list[float], int]:
        if not values:
            return float("nan"), float("nan"), [float("nan"), float("nan")], 0
        mean = float(np.mean(values))
        std = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
        if len(values) > 1:
            t_crit = stats.t.ppf(0.975, len(values) - 1)
            half = t_crit * std / np.sqrt(len(values))
            ci = [mean - half, mean + half]
        else:
            ci = [mean, mean]
        return mean, std, ci, len(values)

    rho_mean, rho_std, rho_ci, n_valid = _agg(valid_rhos)
    kappa_mean, kappa_std, kappa_ci, _ = _agg(valid_kappas)
    mae_mean, mae_std, mae_ci, _ = _agg(valid_maes)

    valid_folds = [
        f for f in per_fold
        if not np.isnan(f["weights_convex"].get(feature_cols[0], float("nan")))
    ]
    mean_weights = {
        k: float(np.mean([f["weights_convex"][k] for f in valid_folds]))
        if valid_folds
        else float("nan")
        for k in feature_cols
    }
    std_weights = {
        k: float(np.std([f["weights_convex"][k] for f in valid_folds], ddof=1))
        if len(valid_folds) > 1
        else 0.0
        for k in feature_cols
    }
    return {
        "spearman_rho_mean": rho_mean,
        "spearman_rho_std": rho_std,
        "spearman_rho_ci95": rho_ci,
        "weighted_kappa_mean": kappa_mean,
        "weighted_kappa_std": kappa_std,
        "weighted_kappa_ci95": kappa_ci,
        "mae_mean": mae_mean,
        "mae_std": mae_std,
        "mae_ci95": mae_ci,
        "weights": mean_weights,
        "weights_per_fold_std": std_weights,
        "n_folds_with_valid_rho": n_valid,
    }


def train_struggle(
    snapshots: list[dict],
    labels: dict[str, dict],
    n_folds: int = 5,
    seed: int = DEFAULT_SEED,
) -> dict:
    matched = [s for s in snapshots if s["snapshot_id"] in labels]
    print(f"struggle: {len(matched)}/{len(snapshots)} snapshots have labels")

    X = np.array([[s["v1_features"][k] for k in STRUGGLE_FEATURE_COLS] for s in matched])
    y = np.array([STRUGGLE_BAND_INDEX[labels[s["snapshot_id"]]["band"]] for s in matched])
    groups = np.array([s["session_id"] for s in matched])

    band_counts = {b: int(np.sum(y == STRUGGLE_BAND_INDEX[b])) for b in STRUGGLE_BAND_INDEX}
    print(f"  X shape: {X.shape}; y mean band: {y.mean():.2f}; band counts: {band_counts}")
    print(f"  Unique sessions: {len(np.unique(groups))}")

    gkf = GroupKFold(n_splits=n_folds)
    per_fold = []
    for fold_idx, (tr, te) in enumerate(gkf.split(X, y, groups)):
        result = _train_one_fold(
            X[tr], y[tr], X[te], y[te],
            STRUGGLE_FEATURE_COLS, seed,
        )
        result["fold"] = fold_idx
        per_fold.append(result)
        print(
            f"  fold {fold_idx}: ρ={result['spearman_rho']:+.3f}  "
            f"κ={result['weighted_kappa']:+.3f}  MAE={result['mae']:.3f}  "
            f"n_train={result['n_train']}  n_test={result['n_test']}"
        )

    summary = _summarise_folds(per_fold, STRUGGLE_FEATURE_COLS, n_folds)
    return {
        "version": "v2",
        "kind": "struggle",
        "model_class": "LinearRegression",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "n_samples": int(len(X)),
        "n_folds": n_folds,
        "target": TARGET_DESCRIPTION,
        "target_band_index": STRUGGLE_BAND_INDEX,
        "features": STRUGGLE_FEATURE_COLS,
        "cv_scheme": f"GroupKFold(n_splits={n_folds}) with session_id as group",
        "regularisation": "None (OLS — pure ordinary least squares)",
        "random_seed": seed,
        **summary,
        "per_fold": per_fold,
    }


def train_difficulty(
    questions: list[dict],
    labels: dict[str, dict],
    seed: int = DEFAULT_SEED,
) -> dict:
    matched = [q for q in questions if q["question"] in labels]
    print(f"difficulty: {len(matched)}/{len(questions)} questions have labels")

    X = np.array([[q["v1_features"][k] for k in DIFFICULTY_FEATURE_COLS] for q in matched])
    y = np.array([DIFFICULTY_BAND_INDEX[labels[q["question"]]["band"]] for q in matched])
    band_counts = {b: int(np.sum(y == DIFFICULTY_BAND_INDEX[b])) for b in DIFFICULTY_BAND_INDEX}
    print(f"  X shape: {X.shape}; y mean band: {y.mean():.2f}; band counts: {band_counts}")

    loo = LeaveOneOut()
    per_fold: list[dict] = []
    pooled_pred: list[float] = []
    pooled_y: list[int] = []
    for fold_idx, (tr, te) in enumerate(loo.split(X)):
        result = _train_one_fold(
            X[tr], y[tr], X[te], y[te],
            DIFFICULTY_FEATURE_COLS, seed,
        )
        result["fold"] = fold_idx
        per_fold.append(result)
        if result.get("skipped_reason") is None:
            scaler = StandardScaler().fit(X[tr])
            lr = LinearRegression()
            lr.fit(scaler.transform(X[tr]), y[tr].astype(float))
            pred = float(lr.predict(scaler.transform(X[te]))[0])
        else:
            pred = float(y[tr].mean()) if len(tr) else 0.0
        pooled_pred.append(pred)
        pooled_y.append(int(y[te][0]))

    pooled_pred_arr = np.array(pooled_pred)
    pooled_y_arr = np.array(pooled_y)
    pooled_metrics = _fold_metrics(pooled_y_arr, pooled_pred_arr)
    print(
        f"  LOO pooled: ρ={pooled_metrics['spearman_rho']:+.3f}  "
        f"κ={pooled_metrics['weighted_kappa']:+.3f}  "
        f"MAE={pooled_metrics['mae']:.3f}"
    )

    valid_folds = [
        f for f in per_fold
        if not np.isnan(f["weights_convex"].get(DIFFICULTY_FEATURE_COLS[0], float("nan")))
    ]
    mean_weights = {
        k: float(np.mean([f["weights_convex"][k] for f in valid_folds]))
        for k in DIFFICULTY_FEATURE_COLS
    } if valid_folds else {k: float("nan") for k in DIFFICULTY_FEATURE_COLS}
    std_weights = {
        k: float(np.std([f["weights_convex"][k] for f in valid_folds], ddof=1))
        if len(valid_folds) > 1
        else 0.0
        for k in DIFFICULTY_FEATURE_COLS
    }

    return {
        "version": "v2",
        "kind": "difficulty",
        "model_class": "LinearRegression",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "n_samples": int(len(X)),
        "n_folds": len(per_fold),
        "target": TARGET_DESCRIPTION,
        "target_band_index": DIFFICULTY_BAND_INDEX,
        "features": DIFFICULTY_FEATURE_COLS,
        "cv_scheme": "LeaveOneOut on questions; pooled metrics over OOF predictions",
        "regularisation": "None (OLS — pure ordinary least squares)",
        "random_seed": seed,
        "weights": mean_weights,
        "weights_per_fold_std": std_weights,
        "spearman_rho_mean": pooled_metrics["spearman_rho"],
        "spearman_rho_std": 0.0,
        "spearman_rho_ci95": [pooled_metrics["spearman_rho"], pooled_metrics["spearman_rho"]],
        "weighted_kappa_mean": pooled_metrics["weighted_kappa"],
        "weighted_kappa_std": 0.0,
        "weighted_kappa_ci95": [pooled_metrics["weighted_kappa"], pooled_metrics["weighted_kappa"]],
        "mae_mean": pooled_metrics["mae"],
        "mae_std": 0.0,
        "mae_ci95": [pooled_metrics["mae"], pooled_metrics["mae"]],
        "pooled_predictions": pooled_pred,
        "pooled_y": pooled_y,
    }


def train_improved(
    snapshots: list[dict],
    labels: dict[str, dict],
    n_folds: int = 5,
    seed: int = DEFAULT_SEED,
) -> dict:
    """Train the 3 model weights (w_B, w_M, w_D) of the improved-struggle model.

    Features are the three component scores per snapshot. Target is the same
    4-band struggle rating as the struggle pass — the improved model
    is supposed to predict the same band severity, so we train it against
    the same target for a clean v1 vs v2 comparison of the MODEL weights.

    Requires snapshots to carry `improved_components` populated by
    scripts/eval_common.py (the helper compute_improved_components_at_t).
    """
    matched = [
        s for s in snapshots
        if s["snapshot_id"] in labels
        and s.get("improved_components")
        and "behavioural_composite" in s["improved_components"]
    ]
    print(
        f"improved: {len(matched)}/{len(snapshots)} snapshots have labels + "
        f"improved_components (the rest are filtered)"
    )

    if not matched:
        return {
            "version": "v2",
            "kind": "improved",
            "model_class": "LinearRegression",
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "status": "DEFERRED",
            "reason": (
                "No snapshots have improved_components populated. Run "
                "`python scripts/eval_common.py` to regenerate snapshots "
                "with BKT + IRT component scores per (session, cutoff), "
                "then re-run this script."
            ),
            "weights": {"w_B": 0.45, "w_M": 0.30, "w_D": 0.25},
            "spearman_rho_mean": float("nan"),
        }

    X = np.array([[s["improved_components"][k] for k in IMPROVED_FEATURE_COLS] for s in matched])
    y = np.array([STRUGGLE_BAND_INDEX[labels[s["snapshot_id"]]["band"]] for s in matched])
    groups = np.array([s["session_id"] for s in matched])

    band_counts = {b: int(np.sum(y == STRUGGLE_BAND_INDEX[b])) for b in STRUGGLE_BAND_INDEX}
    print(f"  X shape: {X.shape}; y mean band: {y.mean():.2f}; band counts: {band_counts}")
    print(f"  Unique sessions: {len(np.unique(groups))}")

    gkf = GroupKFold(n_splits=n_folds)
    per_fold = []
    for fold_idx, (tr, te) in enumerate(gkf.split(X, y, groups)):
        result = _train_one_fold(
            X[tr], y[tr], X[te], y[te],
            IMPROVED_FEATURE_COLS, seed,
        )
        result["fold"] = fold_idx
        per_fold.append(result)
        print(
            f"  fold {fold_idx}: ρ={result['spearman_rho']:+.3f}  "
            f"κ={result['weighted_kappa']:+.3f}  MAE={result['mae']:.3f}  "
            f"n_train={result['n_train']}  n_test={result['n_test']}"
        )

    summary = _summarise_folds(per_fold, IMPROVED_FEATURE_COLS, n_folds)
    weights_named = {
        "w_B": summary["weights"]["behavioural_composite"],
        "w_M": summary["weights"]["mastery_gap"],
        "w_D": summary["weights"]["difficulty_adjusted_score"],
    }
    weights_std_named = {
        "w_B": summary["weights_per_fold_std"]["behavioural_composite"],
        "w_M": summary["weights_per_fold_std"]["mastery_gap"],
        "w_D": summary["weights_per_fold_std"]["difficulty_adjusted_score"],
    }

    return {
        "version": "v2",
        "kind": "improved",
        "model_class": "LinearRegression",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "n_samples": int(len(X)),
        "n_folds": n_folds,
        "target": TARGET_DESCRIPTION,
        "target_band_index": STRUGGLE_BAND_INDEX,
        "features": IMPROVED_FEATURE_COLS,
        "feature_aliases": {
            "behavioural_composite": "w_B",
            "mastery_gap": "w_M",
            "difficulty_adjusted_score": "w_D",
        },
        "cv_scheme": f"GroupKFold(n_splits={n_folds}) with session_id as group",
        "regularisation": "None (OLS — pure ordinary least squares)",
        "random_seed": seed,
        "spearman_rho_mean": summary["spearman_rho_mean"],
        "spearman_rho_std": summary["spearman_rho_std"],
        "spearman_rho_ci95": summary["spearman_rho_ci95"],
        "weighted_kappa_mean": summary["weighted_kappa_mean"],
        "weighted_kappa_std": summary["weighted_kappa_std"],
        "weighted_kappa_ci95": summary["weighted_kappa_ci95"],
        "mae_mean": summary["mae_mean"],
        "mae_std": summary["mae_std"],
        "mae_ci95": summary["mae_ci95"],
        "weights": weights_named,
        "weights_per_fold_std": weights_std_named,
        "weights_by_feature": summary["weights"],
        "weights_per_fold_std_by_feature": summary["weights_per_fold_std"],
        "n_folds_with_valid_rho": summary["n_folds_with_valid_rho"],
        "per_fold": per_fold,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", required=True, choices=["struggle", "difficulty", "improved"])
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    payload = _load_snapshots()
    snapshots = payload.get("struggle_snapshots", [])
    questions = payload.get("difficulty_questions", [])

    if args.kind == "struggle":
        labels = _load_labels("struggle")
        result = train_struggle(snapshots, labels, n_folds=args.n_folds, seed=args.seed)
        out = args.out or paths.DATA_DIR / "eval" / "optimised_struggle_weights_v2.json"
    elif args.kind == "difficulty":
        labels = _load_labels("difficulty")
        result = train_difficulty(questions, labels, seed=args.seed)
        out = args.out or paths.DATA_DIR / "eval" / "optimised_difficulty_weights_v2.json"
    else:  # improved
        labels = _load_labels("struggle")
        result = train_improved(snapshots, labels, n_folds=args.n_folds, seed=args.seed)
        out = args.out or paths.DATA_DIR / "eval" / "optimised_improved_weights_v2.json"

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print()
    print(f"Wrote {out}")
    print()

    if result.get("status") == "DEFERRED":
        print(f"Status: DEFERRED ({result['kind']})")
        return 0
    print(f"=== {args.kind.upper()} v2 weights (OLS on 4-band) ===")
    print(f"  Spearman ρ: {result['spearman_rho_mean']:+.3f}  "
          f"95% CI: [{result['spearman_rho_ci95'][0]:+.3f}, {result['spearman_rho_ci95'][1]:+.3f}]")
    print(f"  Weighted κ: {result['weighted_kappa_mean']:+.3f}  "
          f"95% CI: [{result['weighted_kappa_ci95'][0]:+.3f}, {result['weighted_kappa_ci95'][1]:+.3f}]")
    print(f"  MAE (band): {result['mae_mean']:.3f}  "
          f"95% CI: [{result['mae_ci95'][0]:.3f}, {result['mae_ci95'][1]:.3f}]")
    print(f"  N samples:  {result['n_samples']}")
    print(f"  N folds:    {result['n_folds']}")
    print()
    print("  Weights (convex, sum |w|=1):")
    for k, v in result["weights"].items():
        sd = result["weights_per_fold_std"].get(k, 0.0)
        print(f"    {k:<10} {v:+.3f}  (per-fold std: {sd:.3f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
