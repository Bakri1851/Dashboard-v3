"""Phase 4 — Optimise v2 weight vectors via logistic regression.

Three modes share the same training infrastructure (LR + L2 + inner CV for
the L2 strength). The outer CV scheme differs by mode:

  --kind struggle    : 5-fold group K-fold, session as group  (N=1306)
  --kind difficulty  : leave-one-out on questions             (N=72)
  --kind improved    : 5-fold group K-fold (requires snapshot extension)

Run from repo root::

    python scripts/optimise_v2_weights.py --kind struggle
    python scripts/optimise_v2_weights.py --kind difficulty
    python scripts/optimise_v2_weights.py --kind improved   # stub for now

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

# Silence sklearn 1.8 deprecation noise about the `penalty` arg in LogisticRegression
# — the script intentionally pins penalty='l2' for term-by-term v1/v2 comparability,
# and the suggested `l1_ratio=0` replacement is functionally identical.
warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "code2"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import roc_auc_score, brier_score_loss  # noqa: E402
from sklearn.model_selection import GroupKFold, KFold, LeaveOneOut  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from backend import paths  # noqa: E402


STRUGGLE_FEATURE_COLS = ["n_hat", "t_hat", "i_norm", "r_norm", "A_norm", "d_hat", "rep_norm"]
DIFFICULTY_FEATURE_COLS = ["c_norm", "t_tilde", "a_tilde", "f_norm", "p_norm"]
IMPROVED_FEATURE_COLS = ["behavioural_composite", "mastery_gap", "difficulty_adjusted_score"]
DEFAULT_CS = np.logspace(-3, 3, 7).tolist()  # 7 L2-strength candidates
DEFAULT_SEED = 42


# -------------------- Data loading --------------------

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


# -------------------- Coefficient post-processing --------------------

def _unscale_coefs(coefs_std: np.ndarray, scaler: StandardScaler) -> np.ndarray:
    """Convert LR coefficients fit on standardised features back to raw-feature space.

    In standardised space:  logit(p) = b0 + sum(c_i * (x_i - mu_i) / sigma_i)
    In raw space:           logit(p) = b0' + sum(c_i' * x_i)
    where c_i' = c_i / sigma_i.
    """
    return coefs_std / scaler.scale_


def _normalise_to_convex(coefs: np.ndarray) -> np.ndarray:
    """Normalise the raw-space coefficient vector so |w|_1 = 1, preserving sign.

    The v1 hand-set weights sum to 1 (convex combination). Reporting v2 weights
    on the same scale makes the term-by-term comparison interpretable. We use
    L1 normalisation rather than positive-only renormalisation because LR may
    legitimately learn a negative weight on a signal that proxies the wrong
    direction for the target (e.g. low submission count → struggling).
    """
    l1 = float(np.abs(coefs).sum())
    if l1 <= 0:
        return np.full_like(coefs, 1.0 / len(coefs))
    return coefs / l1


# -------------------- Core training loop --------------------

def _inner_cv_best_C(
    X: np.ndarray,
    y: np.ndarray,
    groups: Optional[np.ndarray],
    Cs: list[float],
    n_inner: int = 3,
    seed: int = DEFAULT_SEED,
) -> float:
    """Pick the L2 strength C that maximises mean inner-fold AUC."""
    if groups is not None and len(np.unique(groups)) >= n_inner:
        splitter = GroupKFold(n_splits=n_inner)
        splits = list(splitter.split(X, y, groups))
    else:
        # LOO outer means inner has nothing to group on — use plain KFold
        splitter = KFold(n_splits=min(n_inner, max(2, len(X) // 5)), shuffle=True, random_state=seed)
        splits = list(splitter.split(X, y))

    best_C = Cs[0]
    best_auc = -np.inf
    for C in Cs:
        fold_aucs = []
        for tr, va in splits:
            if len(np.unique(y[tr])) < 2 or len(np.unique(y[va])) < 2:
                continue  # AUC undefined on single-class folds
            sc = StandardScaler().fit(X[tr])
            Xtr, Xva = sc.transform(X[tr]), sc.transform(X[va])
            lr = LogisticRegression(
                penalty="l2", C=C, max_iter=2000, solver="lbfgs", random_state=seed
            )
            lr.fit(Xtr, y[tr])
            prob = lr.predict_proba(Xva)[:, 1]
            fold_aucs.append(roc_auc_score(y[va], prob))
        if not fold_aucs:
            continue
        mean_auc = float(np.mean(fold_aucs))
        if mean_auc > best_auc:
            best_auc = mean_auc
            best_C = C
    return best_C


def _train_one_fold(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    feature_cols: list[str],
    train_groups: Optional[np.ndarray],
    Cs: list[float],
    seed: int = DEFAULT_SEED,
) -> dict:
    """Fit on the outer training fold with inner-CV-selected L2; predict on test."""
    # Guard against single-class training folds (can happen with LOO on heavily
    # skewed targets). Return a stub fold so the run continues — _summarise_folds
    # filters by valid AUC, so a stub fold just doesn't contribute to the headline.
    if len(np.unique(y_train)) < 2:
        return {
            "best_C": float("nan"),
            "auc": float("nan"),
            "brier": float("nan"),
            "n_train": int(len(X_train)),
            "n_test": int(len(X_test)),
            "n_positive_test": int(y_test.sum()),
            "positive_rate_test": float(y_test.mean()) if len(y_test) else 0.0,
            "coefs_raw": {k: float("nan") for k in feature_cols},
            "weights_convex": {k: float("nan") for k in feature_cols},
            "skipped_reason": "single_class_training_fold",
        }
    best_C = _inner_cv_best_C(X_train, y_train, train_groups, Cs, seed=seed)

    scaler = StandardScaler().fit(X_train)
    Xtr_s = scaler.transform(X_train)
    Xte_s = scaler.transform(X_test)
    lr = LogisticRegression(
        penalty="l2", C=best_C, max_iter=2000, solver="lbfgs", random_state=seed
    )
    lr.fit(Xtr_s, y_train)

    prob_test = lr.predict_proba(Xte_s)[:, 1]
    auc = (
        float(roc_auc_score(y_test, prob_test))
        if len(np.unique(y_test)) >= 2
        else float("nan")
    )
    brier = float(brier_score_loss(y_test, prob_test)) if len(y_test) else float("nan")

    raw_coefs = _unscale_coefs(lr.coef_[0], scaler)
    convex = _normalise_to_convex(raw_coefs)
    return {
        "best_C": float(best_C),
        "auc": auc,
        "brier": brier,
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "n_positive_test": int(y_test.sum()),
        "positive_rate_test": float(y_test.mean()) if len(y_test) else 0.0,
        "coefs_raw": dict(zip(feature_cols, [float(c) for c in raw_coefs])),
        "weights_convex": dict(zip(feature_cols, [float(c) for c in convex])),
    }


def _summarise_folds(
    per_fold: list[dict], feature_cols: list[str], n_folds: int
) -> dict:
    valid_aucs = [f["auc"] for f in per_fold if not np.isnan(f["auc"])]
    mean_auc = float(np.mean(valid_aucs)) if valid_aucs else float("nan")
    std_auc = float(np.std(valid_aucs, ddof=1)) if len(valid_aucs) > 1 else 0.0
    if len(valid_aucs) > 1:
        t_crit = stats.t.ppf(0.975, len(valid_aucs) - 1)
        half = t_crit * std_auc / np.sqrt(len(valid_aucs))
        ci = [mean_auc - half, mean_auc + half]
    else:
        ci = [mean_auc, mean_auc]

    valid_folds = [f for f in per_fold if not np.isnan(f["weights_convex"].get(feature_cols[0], float("nan")))]
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
        "auc_mean": mean_auc,
        "auc_std": std_auc,
        "auc_ci95": ci,
        "weights": mean_weights,
        "weights_per_fold_std": std_weights,
        "n_folds_with_valid_auc": len(valid_aucs),
        "best_C_per_fold": [f["best_C"] for f in per_fold],
    }


# -------------------- Mode dispatchers --------------------

def train_struggle(
    snapshots: list[dict],
    labels: dict[str, dict],
    n_folds: int = 5,
    Cs: Optional[list[float]] = None,
    seed: int = DEFAULT_SEED,
) -> dict:
    Cs = Cs or DEFAULT_CS
    matched = [s for s in snapshots if s["snapshot_id"] in labels]
    print(f"struggle: {len(matched)}/{len(snapshots)} snapshots have labels")

    X = np.array([[s["v1_features"][k] for k in STRUGGLE_FEATURE_COLS] for s in matched])
    y = np.array([int(labels[s["snapshot_id"]]["intervene"]) for s in matched])
    groups = np.array([s["session_id"] for s in matched])

    print(f"  X shape: {X.shape}; positive rate: {y.mean():.1%}")
    print(f"  Unique sessions: {len(np.unique(groups))}")

    gkf = GroupKFold(n_splits=n_folds)
    per_fold = []
    for fold_idx, (tr, te) in enumerate(gkf.split(X, y, groups)):
        result = _train_one_fold(
            X[tr], y[tr], X[te], y[te],
            STRUGGLE_FEATURE_COLS, groups[tr], Cs, seed,
        )
        result["fold"] = fold_idx
        per_fold.append(result)
        print(
            f"  fold {fold_idx}: C={result['best_C']:.3g}  AUC={result['auc']:.3f}  "
            f"n_train={result['n_train']}  n_test={result['n_test']}  "
            f"pos_rate={result['positive_rate_test']:.1%}"
        )

    summary = _summarise_folds(per_fold, STRUGGLE_FEATURE_COLS, n_folds)
    return {
        "version": "v2",
        "kind": "struggle",
        "model_class": "LogisticRegression",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "n_samples": int(len(X)),
        "n_folds": n_folds,
        "target": "intervene (binary; LLM second-opinion)",
        "features": STRUGGLE_FEATURE_COLS,
        "cv_scheme": f"GroupKFold(n_splits={n_folds}) with session_id as group",
        "regularisation": "L2 (Ridge); C selected by inner GroupKFold(3) on AUC",
        "Cs_grid": Cs,
        "random_seed": seed,
        **summary,
        "per_fold": per_fold,
    }


def train_difficulty(
    questions: list[dict],
    labels: dict[str, dict],
    Cs: Optional[list[float]] = None,
    seed: int = DEFAULT_SEED,
) -> dict:
    Cs = Cs or DEFAULT_CS
    matched = [q for q in questions if q["question"] in labels]
    print(f"difficulty: {len(matched)}/{len(questions)} questions have labels")

    # Binary target: "very hard" = LLM band == 'Very Hard'.
    # The original {Hard, Very Hard} target produced 98.6% positive rate on
    # this cohort (the LLM judged COA122 questions uniformly hard given the
    # aggregate stats). At 99% positive LOO produces single-class training
    # folds and the LR has nothing to discriminate. "Very Hard only" gives a
    # 76%/24% split — still skewed but trainable. The reframed question is
    # "what distinguishes the very hardest questions from the merely hard?"
    X = np.array([[q["v1_features"][k] for k in DIFFICULTY_FEATURE_COLS] for q in matched])
    y = np.array([
        int(labels[q["question"]]["band"] == "Very Hard") for q in matched
    ])
    print(f"  X shape: {X.shape}; positive rate (Very Hard only): {y.mean():.1%}")

    loo = LeaveOneOut()
    per_fold: list[dict] = []
    for fold_idx, (tr, te) in enumerate(loo.split(X)):
        # LOO has 1 test sample — AUC undefined per-fold; we aggregate predictions
        result = _train_one_fold(
            X[tr], y[tr], X[te], y[te],
            DIFFICULTY_FEATURE_COLS, None, Cs, seed,
        )
        result["fold"] = fold_idx
        per_fold.append(result)

    # LOO: AUC computed on the pooled out-of-fold predictions
    pooled_y = np.array([y[i] for i in range(len(X))])
    pooled_prob: list[float] = []
    for fold_idx, (tr, te) in enumerate(loo.split(X)):
        # Skip folds that were stubbed out (single-class training data); use the
        # class-mean as the prediction so the pooled AUC at least has SOMETHING
        # to score. Stub folds also have NaN coefs so the recompute below
        # would fail.
        if per_fold[fold_idx].get("skipped_reason") is not None:
            pooled_prob.append(float(y[tr].mean()))
            continue
        scaler = StandardScaler().fit(X[tr])
        lr = LogisticRegression(
            penalty="l2", C=per_fold[fold_idx]["best_C"],
            max_iter=2000, solver="lbfgs", random_state=seed,
        )
        Xtr_s = scaler.transform(X[tr])
        Xte_s = scaler.transform(X[te])
        lr.fit(Xtr_s, y[tr])
        pooled_prob.append(float(lr.predict_proba(Xte_s)[0, 1]))

    if len(np.unique(pooled_y)) >= 2:
        pooled_auc = float(roc_auc_score(pooled_y, pooled_prob))
        pooled_brier = float(brier_score_loss(pooled_y, pooled_prob))
    else:
        pooled_auc = float("nan")
        pooled_brier = float("nan")
    print(f"  LOO pooled AUC: {pooled_auc:.3f}  Brier: {pooled_brier:.3f}")

    mean_weights = {
        k: float(np.mean([f["weights_convex"][k] for f in per_fold]))
        for k in DIFFICULTY_FEATURE_COLS
    }
    std_weights = {
        k: float(np.std([f["weights_convex"][k] for f in per_fold], ddof=1))
        for k in DIFFICULTY_FEATURE_COLS
    }

    return {
        "version": "v2",
        "kind": "difficulty",
        "model_class": "LogisticRegression",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "n_samples": int(len(X)),
        "n_folds": len(per_fold),
        "target": "very hard (binary; LLM band == 'Very Hard'). Reframed from the original {Hard, Very Hard} target which gave 98.6% positive on this cohort and crashed LOO with single-class training folds.",
        "features": DIFFICULTY_FEATURE_COLS,
        "cv_scheme": "LeaveOneOut on questions",
        "regularisation": "L2 (Ridge); C selected by inner KFold(3) on AUC",
        "Cs_grid": Cs,
        "random_seed": seed,
        "weights": mean_weights,
        "weights_per_fold_std": std_weights,
        "auc_mean": pooled_auc,
        "auc_std": 0.0,  # single pooled AUC; no per-fold variance
        "auc_ci95": [pooled_auc, pooled_auc],
        "brier_pooled": pooled_brier,
        "best_C_per_fold": [f["best_C"] for f in per_fold],
        # per_fold omitted for difficulty — would be 72 entries; just keep summary
    }


def train_improved(
    snapshots: list[dict],
    labels: dict[str, dict],
    n_folds: int = 5,
    Cs: Optional[list[float]] = None,
    seed: int = DEFAULT_SEED,
) -> dict:
    """Train the 3 blend weights (w_B, w_M, w_D) of the improved-struggle composite.

    Features are the three component scores per snapshot:
      - behavioural_composite (B_s)
      - mastery_gap (M_s)
      - difficulty_adjusted_score (D_s)

    Target is the same binary LLM intervene label as the struggle pass — the
    improved composite is supposed to predict the same actionable signal, so
    we train it against the same target for a clean v1 vs v2 comparison of
    the BLEND weights specifically (not the composite-vs-baseline question,
    which is in scope for Phase 6 evaluation).

    Requires snapshots to carry `improved_components` populated by
    scripts/eval_common.py (the helper compute_improved_components_at_t).
    Snapshots without the field are filtered out — if zero snapshots have
    it, returns a DEFERRED stub identical in shape to the original
    train_improved_stub so the JSON consumer side doesn't break.
    """
    Cs = Cs or DEFAULT_CS

    # Filter snapshots that have BOTH the LLM label AND populated improved_components
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
        # Snapshots haven't been regenerated yet — fall back to the stub shape
        return {
            "version": "v2",
            "kind": "improved",
            "model_class": "LogisticRegression",
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "status": "DEFERRED",
            "reason": (
                "No snapshots have improved_components populated. Run "
                "`python scripts/eval_common.py` to regenerate snapshots "
                "with BKT + IRT component scores per (session, cutoff), "
                "then re-run this script."
            ),
            "weights": {"w_B": 0.45, "w_M": 0.30, "w_D": 0.25},
            "auc_mean": float("nan"),
        }

    X = np.array([[s["improved_components"][k] for k in IMPROVED_FEATURE_COLS] for s in matched])
    y = np.array([int(labels[s["snapshot_id"]]["intervene"]) for s in matched])
    groups = np.array([s["session_id"] for s in matched])

    print(f"  X shape: {X.shape}; positive rate: {y.mean():.1%}")
    print(f"  Unique sessions: {len(np.unique(groups))}")

    gkf = GroupKFold(n_splits=n_folds)
    per_fold = []
    for fold_idx, (tr, te) in enumerate(gkf.split(X, y, groups)):
        result = _train_one_fold(
            X[tr], y[tr], X[te], y[te],
            IMPROVED_FEATURE_COLS, groups[tr], Cs, seed,
        )
        result["fold"] = fold_idx
        per_fold.append(result)
        print(
            f"  fold {fold_idx}: C={result['best_C']:.3g}  AUC={result['auc']:.3f}  "
            f"n_train={result['n_train']}  n_test={result['n_test']}  "
            f"pos_rate={result['positive_rate_test']:.1%}"
        )

    summary = _summarise_folds(per_fold, IMPROVED_FEATURE_COLS, n_folds)
    # Rename keys for v1 comparability (w_B, w_M, w_D)
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
        "model_class": "LogisticRegression",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "n_samples": int(len(X)),
        "n_folds": n_folds,
        "target": "intervene (binary; LLM second-opinion)",
        "features": IMPROVED_FEATURE_COLS,
        "feature_aliases": {"behavioural_composite": "w_B", "mastery_gap": "w_M", "difficulty_adjusted_score": "w_D"},
        "cv_scheme": f"GroupKFold(n_splits={n_folds}) with session_id as group",
        "regularisation": "L2 (Ridge); C selected by inner GroupKFold(3) on AUC",
        "Cs_grid": Cs,
        "random_seed": seed,
        "auc_mean": summary["auc_mean"],
        "auc_std": summary["auc_std"],
        "auc_ci95": summary["auc_ci95"],
        "weights": weights_named,
        "weights_per_fold_std": weights_std_named,
        "weights_by_feature": summary["weights"],
        "weights_per_fold_std_by_feature": summary["weights_per_fold_std"],
        "n_folds_with_valid_auc": summary["n_folds_with_valid_auc"],
        "best_C_per_fold": summary["best_C_per_fold"],
        "per_fold": per_fold,
    }


# -------------------- Main --------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", required=True, choices=["struggle", "difficulty", "improved"])
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--Cs",
        type=float,
        nargs="+",
        default=None,
        help="Override the default L2-strength grid (7 values from 1e-3 to 1e3).",
    )
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    payload = _load_snapshots()
    snapshots = payload.get("struggle_snapshots", [])
    questions = payload.get("difficulty_questions", [])

    if args.kind == "struggle":
        labels = _load_labels("struggle")
        result = train_struggle(
            snapshots, labels, n_folds=args.n_folds, Cs=args.Cs, seed=args.seed
        )
        out = args.out or paths.DATA_DIR / "eval" / "optimised_struggle_weights_v2.json"
    elif args.kind == "difficulty":
        labels = _load_labels("difficulty")
        result = train_difficulty(questions, labels, Cs=args.Cs, seed=args.seed)
        out = args.out or paths.DATA_DIR / "eval" / "optimised_difficulty_weights_v2.json"
    else:  # improved
        labels = _load_labels("struggle")  # same target as struggle pass
        result = train_improved(snapshots, labels, n_folds=args.n_folds, Cs=args.Cs, seed=args.seed)
        out = args.out or paths.DATA_DIR / "eval" / "optimised_improved_weights_v2.json"

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print()
    print(f"Wrote {out}")
    print()

    # Headline summary
    if result.get("status") == "DEFERRED":
        print(f"Status: DEFERRED ({result['kind']})")
        return 0
    print(f"=== {args.kind.upper()} v2 weights ===")
    print(f"  AUC (mean): {result['auc_mean']:.3f}  95% CI: [{result['auc_ci95'][0]:.3f}, {result['auc_ci95'][1]:.3f}]")
    print(f"  N samples:  {result['n_samples']}")
    print(f"  N folds:    {result['n_folds']}")
    print()
    print("  Weights (convex, sum |w|=1):")
    for k, v in result["weights"].items():
        sd = result["weights_per_fold_std"].get(k, 0.0)
        print(f"    {k:<10} {v:+.3f}  (per-fold std: {sd:.3f})")
    print()
    print(f"  Best C per fold: {[round(c, 4) for c in result['best_C_per_fold']]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
