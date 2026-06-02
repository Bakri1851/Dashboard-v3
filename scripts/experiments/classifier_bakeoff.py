"""Classifier bake-off: same data + CV as model_class_bakeoff.py, but
testing classifiers (multinomial logit, RandomForestClassifier,
GradientBoostingClassifier) against the OLS baseline.

Reports two ρ values per classifier:
  - ρ on E[band|x] = sum_b b * P(band=b|x)   (ordinal-preserving)
  - ρ on argmax_b P(band=b|x)                 (discrete, loses tie-breaking)
Also reports linear-weighted κ on the argmax band.

Delete-safe: lives in scripts/experiments/, writes to data/eval/experiments/.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "code2"))

import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import GroupKFold, LeaveOneOut
from sklearn.metrics import cohen_kappa_score
from sklearn.preprocessing import StandardScaler

EVAL = REPO / "data" / "eval"
OUT  = EVAL / "experiments"
OUT.mkdir(parents=True, exist_ok=True)

STRUGGLE_BANDS    = ["On Track", "Minor Issues", "Struggling", "Needs Help"]
DIFFICULTY_BANDS  = ["Easy", "Medium", "Hard", "Very Hard"]
STRUGGLE_SIGNALS  = ["n_hat", "t_hat", "i_norm", "r_norm", "A_norm", "d_hat", "rep_norm"]
DIFFICULTY_SIGNALS = ["c_norm", "t_tilde", "a_tilde", "f_norm", "p_norm"]
IMPROVED_SIGNALS  = ["behavioural_composite", "mastery_gap", "difficulty_adjusted_score"]

STRUGGLE_BAND_INDEX   = {b: i for i, b in enumerate(STRUGGLE_BANDS)}
DIFFICULTY_BAND_INDEX = {b: i for i, b in enumerate(DIFFICULTY_BANDS)}

BAND_VALUES = np.array([0, 1, 2, 3], dtype=float)


def _load(name: str):
    with (EVAL / name).open(encoding="utf-8") as f:
        return json.load(f)


def _build_struggle():
    snaps = _load("snapshots.json")["struggle_snapshots"]
    labels = _load("llm_struggle_labels.json")["labels"]
    matched = [s for s in snaps if s["snapshot_id"] in labels]
    X = np.array([[s["v1_features"][k] for k in STRUGGLE_SIGNALS] for s in matched])
    y = np.array([STRUGGLE_BAND_INDEX[labels[s["snapshot_id"]]["band"]] for s in matched])
    groups = np.array([s["session_id"] for s in matched])
    return X, y, groups


def _build_difficulty():
    qs = _load("snapshots.json")["difficulty_questions"]
    labels = _load("llm_difficulty_labels.json")["labels"]
    matched = [q for q in qs if q["question"] in labels]
    X = np.array([[q["v1_features"][k] for k in DIFFICULTY_SIGNALS] for q in matched])
    y = np.array([DIFFICULTY_BAND_INDEX[labels[q["question"]]["band"]] for q in matched])
    return X, y, None


def _build_improved():
    snaps = _load("snapshots.json")["struggle_snapshots"]
    labels = _load("llm_struggle_labels.json")["labels"]
    matched = [s for s in snaps
               if s["snapshot_id"] in labels and "improved_components" in s
               and s["improved_components"].get("improved_struggle_score") is not None]
    if not matched:
        return None
    X = np.array([[s["improved_components"][k] for k in IMPROVED_SIGNALS] for s in matched])
    y = np.array([STRUGGLE_BAND_INDEX[labels[s["snapshot_id"]]["band"]] for s in matched])
    groups = np.array([s["session_id"] for s in matched])
    return X, y, groups


def _eval_classifier(make_clf, X, y, groups, cv_splits, n_classes=4):
    """Run a classifier across CV folds, pool predictions, return metrics."""
    pooled_expected = np.zeros(len(y))
    pooled_argmax   = np.zeros(len(y), dtype=int)
    for tr, te in cv_splits:
        sc = StandardScaler().fit(X[tr])
        clf = make_clf()
        clf.fit(sc.transform(X[tr]), y[tr])
        proba = clf.predict_proba(sc.transform(X[te]))
        full_proba = np.zeros((proba.shape[0], n_classes))
        for col, c in enumerate(clf.classes_):
            full_proba[:, int(c)] = proba[:, col]
        pooled_expected[te] = full_proba @ BAND_VALUES
        pooled_argmax[te]   = full_proba.argmax(axis=1)
    rho_exp = float(spearmanr(pooled_expected, y).correlation)
    rho_arg = float(spearmanr(pooled_argmax,   y).correlation)
    kappa   = float(cohen_kappa_score(y, pooled_argmax, labels=list(range(n_classes)),
                                       weights="linear"))
    mae     = float(np.mean(np.abs(pooled_argmax - y)))
    return {"rho_expected": rho_exp, "rho_argmax": rho_arg,
            "weighted_kappa": kappa, "mae": mae}


def _eval_ols(X, y, cv_splits):
    pooled = np.zeros(len(y))
    for tr, te in cv_splits:
        sc = StandardScaler().fit(X[tr])
        ols = LinearRegression().fit(sc.transform(X[tr]), y[tr].astype(float))
        pooled[te] = ols.predict(sc.transform(X[te]))
    pred_band = np.clip(np.rint(pooled), 0, 3).astype(int)
    return {"rho_expected": float(spearmanr(pooled, y).correlation),
            "rho_argmax":   float(spearmanr(pred_band, y).correlation),
            "weighted_kappa": float(cohen_kappa_score(y, pred_band, labels=[0,1,2,3],
                                                     weights="linear")),
            "mae": float(np.mean(np.abs(pred_band - y)))}


def _eval_one_target(name, X, y, groups):
    if groups is not None and len(np.unique(groups)) >= 5:
        gkf = GroupKFold(n_splits=5)
        cv_splits = list(gkf.split(X, y, groups))
    else:
        loo = LeaveOneOut()
        cv_splits = list(loo.split(X))

    print(f"\n=== {name} (n={len(y)}, features={X.shape[1]}) ===")
    results = {}

    results["OLS (baseline)"] = _eval_ols(X, y, list(cv_splits))
    print(f"  OLS (baseline):       rho_exp={results['OLS (baseline)']['rho_expected']:+.3f}  "
          f"rho_argmax={results['OLS (baseline)']['rho_argmax']:+.3f}  "
          f"kappa={results['OLS (baseline)']['weighted_kappa']:+.3f}  "
          f"mae={results['OLS (baseline)']['mae']:.3f}")

    classifiers = [
        ("LogisticRegression (multinomial)",
         lambda: LogisticRegression(max_iter=2000, C=1.0, solver="lbfgs")),
        ("RandomForestClassifier (n=200, d=5)",
         lambda: RandomForestClassifier(n_estimators=200, max_depth=5, random_state=42)),
        ("GradientBoostingClassifier (n=200, d=3, lr=0.05)",
         lambda: GradientBoostingClassifier(n_estimators=200, max_depth=3,
                                            learning_rate=0.05, random_state=42)),
    ]
    for clf_name, make in classifiers:
        try:
            m = _eval_classifier(make, X, y, groups, list(cv_splits))
        except Exception as exc:
            print(f"  {clf_name:<50s} FAILED: {exc}")
            results[clf_name] = {"error": str(exc)}
            continue
        results[clf_name] = m
        delta_rho_exp = m["rho_expected"] - results["OLS (baseline)"]["rho_expected"]
        delta_kappa   = m["weighted_kappa"] - results["OLS (baseline)"]["weighted_kappa"]
        print(f"  {clf_name:<50s} rho_exp={m['rho_expected']:+.3f} (Δ {delta_rho_exp:+.3f})  "
              f"rho_argmax={m['rho_argmax']:+.3f}  "
              f"kappa={m['weighted_kappa']:+.3f} (Δ {delta_kappa:+.3f})  "
              f"mae={m['mae']:.3f}")

    return results


def main() -> int:
    all_results = {}

    print("=" * 78)
    Xs, ys, gs = _build_struggle()
    all_results["struggle"] = _eval_one_target("STRUGGLE", Xs, ys, gs)

    print("=" * 78)
    imp = _build_improved()
    if imp is None:
        print("\nIMPROVED-STRUGGLE: improved_components missing from snapshots.json — skipping")
        all_results["improved"] = {"skipped": "improved_components missing"}
    else:
        Xi, yi, gi = imp
        all_results["improved"] = _eval_one_target("IMPROVED-STRUGGLE", Xi, yi, gi)

    print("=" * 78)
    Xd, yd, gd = _build_difficulty()
    all_results["difficulty"] = _eval_one_target("DIFFICULTY", Xd, yd, gd)

    out_path = OUT / "classifier_bakeoff.json"
    out_path.write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    print(f"\nFull numbers written to {out_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
