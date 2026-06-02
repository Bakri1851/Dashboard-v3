"""Side experiment: bake-off of regression model classes for the v2 training.

Investigates whether OLS (current baseline) is actually the best choice, or
whether a regularised linear model (Ridge / Lasso / ElasticNet) or a non-linear
model (Random Forest / Gradient Boosting) gives meaningfully better Spearman ρ
against the LLM's 4-band rating.

Same data + CV splits as scripts/optimise_v2_weights.py. Outputs land in
data/eval/experiments/ — fully isolated from the canonical evaluation pipeline.
Delete-safe: `rm -rf scripts/experiments/ data/eval/experiments/` wipes the
experiment entirely without touching anything else.

Run from repo root::

    python scripts/experiments/model_class_bakeoff.py

Output:
    data/eval/experiments/model_class_bakeoff.json   — full per-fold numbers
    data/eval/experiments/model_class_bakeoff.md     — human-readable summary
"""
from __future__ import annotations
import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

warnings.filterwarnings("ignore")

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "code2"))

import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
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

MODELS = [
    ("OLS (baseline)",       lambda: LinearRegression()),
    ("Ridge alpha=0.1",      lambda: Ridge(alpha=0.1)),
    ("Ridge alpha=1.0",      lambda: Ridge(alpha=1.0)),
    ("Ridge alpha=10.0",     lambda: Ridge(alpha=10.0)),
    ("Lasso alpha=0.01",     lambda: Lasso(alpha=0.01, max_iter=5000)),
    ("ElasticNet a=0.01",    lambda: ElasticNet(alpha=0.01, l1_ratio=0.5, max_iter=5000)),
    ("RandomForest",         lambda: RandomForestRegressor(n_estimators=200, max_depth=5, random_state=42, n_jobs=-1)),
    ("GradientBoosting",     lambda: GradientBoostingRegressor(n_estimators=200, max_depth=3, learning_rate=0.05, random_state=42)),
]


def cv_rho(make_model, X, y, splits) -> dict:
    rhos = []
    for tr, te in splits:
        if len(np.unique(y[tr])) < 2 or len(te) < 2 or len(np.unique(y[te])) < 2:
            continue
        sc = StandardScaler().fit(X[tr])
        m = make_model()
        m.fit(sc.transform(X[tr]), y[tr].astype(float))
        pred = m.predict(sc.transform(X[te]))
        rho = stats.spearmanr(pred, y[te]).correlation
        if rho is None or np.isnan(rho):
            continue
        rhos.append(float(rho))
    if not rhos:
        return {"mean": float("nan"), "std": float("nan"), "per_fold": []}
    return {
        "mean": float(np.mean(rhos)),
        "std": float(np.std(rhos, ddof=1)) if len(rhos) > 1 else 0.0,
        "per_fold": rhos,
    }


def loo_pooled_rho(make_model, X, y) -> dict:
    loo = LeaveOneOut()
    pred_pool = []
    y_pool = []
    for tr, te in loo.split(X):
        if len(np.unique(y[tr])) < 2:
            pred_pool.append(float(y[tr].mean()))
            y_pool.append(int(y[te][0]))
            continue
        sc = StandardScaler().fit(X[tr])
        m = make_model()
        m.fit(sc.transform(X[tr]), y[tr].astype(float))
        pred_pool.append(float(m.predict(sc.transform(X[te]))[0]))
        y_pool.append(int(y[te][0]))
    rho = stats.spearmanr(pred_pool, y_pool).correlation
    return {
        "pooled_rho": float(rho) if rho is not None and not np.isnan(rho) else float("nan"),
        "n_predictions": len(pred_pool),
    }


def run_all():
    snap_blob = json.loads((EVAL / "snapshots.json").read_text(encoding="utf-8"))
    snapshots = snap_blob.get("struggle_snapshots", [])
    questions = snap_blob.get("difficulty_questions", [])
    llm_struggle = json.loads((EVAL / "llm_struggle_labels.json").read_text(encoding="utf-8"))["labels"]
    llm_difficulty = json.loads((EVAL / "llm_difficulty_labels.json").read_text(encoding="utf-8"))["labels"]

    report = {
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "purpose": (
            "Side experiment to test whether OLS (current v2 baseline) is the best regression model "
            "class against the 4-band target, or whether regularised linear / non-linear alternatives "
            "give meaningfully better Spearman ρ. NO canonical artefacts modified."
        ),
        "results": {},
    }

    matched_s = [s for s in snapshots if s["snapshot_id"] in llm_struggle]
    X_s = np.array([[s["v1_features"][k] for k in STRUGGLE_SIGNALS] for s in matched_s])
    y_s = np.array([STRUGGLE_BAND_IDX[llm_struggle[s["snapshot_id"]]["band"]] for s in matched_s])
    groups_s = np.array([s["session_id"] for s in matched_s])
    splits_s = list(GroupKFold(n_splits=5).split(X_s, y_s, groups_s))
    print("=" * 78)
    print(f"STRUGGLE  N={len(matched_s)}  features={len(STRUGGLE_SIGNALS)}  CV=GroupKFold(5)")
    print("=" * 78)
    print(f"{'model':<22s} {'mean rho':>10s} {'std':>8s}   per-fold rho")
    struggle_results = {}
    for name, make in MODELS:
        r = cv_rho(make, X_s, y_s, splits_s)
        struggle_results[name] = r
        per_fold = " ".join(f"{v:+.3f}" for v in r["per_fold"])
        print(f"{name:<22s} {r['mean']:+.4f}   {r['std']:.3f}   [{per_fold}]")
    report["results"]["struggle"] = {
        "n_samples": len(matched_s),
        "n_features": len(STRUGGLE_SIGNALS),
        "cv_scheme": "GroupKFold(5) session-grouped",
        "models": struggle_results,
    }

    matched_d = [q for q in questions if q["question"] in llm_difficulty]
    X_d = np.array([[q["v1_features"][k] for k in DIFFICULTY_SIGNALS] for q in matched_d])
    y_d = np.array([DIFFICULTY_BAND_IDX[llm_difficulty[q["question"]]["band"]] for q in matched_d])
    print()
    print("=" * 78)
    print(f"DIFFICULTY  N={len(matched_d)}  features={len(DIFFICULTY_SIGNALS)}  CV=LeaveOneOut (pooled rho)")
    print("=" * 78)
    print(f"{'model':<22s} {'pooled rho':>12s}")
    difficulty_results = {}
    for name, make in MODELS:
        r = loo_pooled_rho(make, X_d, y_d)
        difficulty_results[name] = r
        print(f"{name:<22s} {r['pooled_rho']:+.4f}")
    report["results"]["difficulty"] = {
        "n_samples": len(matched_d),
        "n_features": len(DIFFICULTY_SIGNALS),
        "cv_scheme": "LeaveOneOut on questions (pooled OOF Spearman rho)",
        "models": difficulty_results,
    }

    matched_i = [
        s for s in snapshots
        if s["snapshot_id"] in llm_struggle
        and s.get("improved_components")
        and "behavioural_composite" in s["improved_components"]
    ]
    X_i = np.array([[s["improved_components"][k] for k in IMPROVED_SIGNALS] for s in matched_i])
    y_i = np.array([STRUGGLE_BAND_IDX[llm_struggle[s["snapshot_id"]]["band"]] for s in matched_i])
    groups_i = np.array([s["session_id"] for s in matched_i])
    splits_i = list(GroupKFold(n_splits=5).split(X_i, y_i, groups_i))
    print()
    print("=" * 78)
    print(f"IMPROVED-STRUGGLE  N={len(matched_i)}  features={len(IMPROVED_SIGNALS)}  CV=GroupKFold(5)")
    print("=" * 78)
    print(f"{'model':<22s} {'mean rho':>10s} {'std':>8s}   per-fold rho")
    improved_results = {}
    for name, make in MODELS:
        r = cv_rho(make, X_i, y_i, splits_i)
        improved_results[name] = r
        per_fold = " ".join(f"{v:+.3f}" for v in r["per_fold"])
        print(f"{name:<22s} {r['mean']:+.4f}   {r['std']:.3f}   [{per_fold}]")
    report["results"]["improved_struggle"] = {
        "n_samples": len(matched_i),
        "n_features": len(IMPROVED_SIGNALS),
        "cv_scheme": "GroupKFold(5) session-grouped",
        "models": improved_results,
    }

    return report


def write_markdown_summary(report, out_path: Path) -> None:
    lines = []
    A = lines.append
    A("# Model-class bake-off results")
    A("")
    A(f"_Ran at {report['ran_at']}_")
    A("")
    A(report["purpose"])
    A("")
    A("All metrics: Spearman ρ against the LLM 4-band rating, using identical CV splits to `scripts/optimise_v2_weights.py`. Higher is better.")
    A("")

    for kind, header in [
        ("struggle", "Struggle (n=1306, 7 features, 5-fold GroupKFold by session)"),
        ("difficulty", "Difficulty (n=72, 5 features, LOO — pooled ρ)"),
        ("improved_struggle", "Improved-struggle (n=1306, 3 features, 5-fold GroupKFold by session)"),
    ]:
        kr = report["results"][kind]
        A(f"## {header}")
        A("")
        if kind == "difficulty":
            A("| Model | Pooled ρ |")
            A("|---|---|")
            baseline = kr["models"]["OLS (baseline)"]["pooled_rho"]
            for name, r in kr["models"].items():
                val = r["pooled_rho"]
                delta = val - baseline
                marker = " 🟢" if delta > 0.005 else (" 🔴" if delta < -0.005 else "")
                star = " **★**" if name == "OLS (baseline)" else ""
                A(f"| {name}{star} | {val:+.3f} (Δ {delta:+.3f}){marker} |")
        else:
            A("| Model | Mean ρ | Std | Δ vs OLS |")
            A("|---|---|---|---|")
            baseline = kr["models"]["OLS (baseline)"]["mean"]
            for name, r in kr["models"].items():
                val = r["mean"]
                delta = val - baseline
                marker = " 🟢" if delta > 0.005 else (" 🔴" if delta < -0.005 else "")
                star = " **★**" if name == "OLS (baseline)" else ""
                A(f"| {name}{star} | {val:+.3f} | {r['std']:.3f} | {delta:+.3f}{marker} |")
        A("")

    A("## Verdict heuristic")
    A("")
    A("- **🟢** = improves ρ by > +0.005 vs the OLS baseline (i.e. measurably better)")
    A("- **🔴** = degrades ρ by > 0.005 vs OLS (worse)")
    A("- **★** = the current canonical v2 baseline (`scripts/optimise_v2_weights.py`)")
    A("- No marker = within ±0.005 of OLS (effectively tied)")
    A("")
    A("Trade-off reminder for the non-linear models (RandomForest, GradientBoosting): better Spearman ρ here does NOT mean we should swap to them as the v2 model. They produce no per-feature signed weights, so the §5.4 v1↔v2 weight-comparison story cannot apply to them. Use them as a CEILING REFERENCE only — \"the best non-linear model achieves X; OLS gets Y; we're within Z of the achievable ceiling\".")
    A("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = run_all()

    json_path = OUT / "model_class_bakeoff.json"
    md_path = OUT / "model_class_bakeoff.md"
    json_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    write_markdown_summary(report, md_path)

    print()
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
