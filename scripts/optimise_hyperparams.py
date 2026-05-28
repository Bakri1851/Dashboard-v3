"""Phase 4d — Bayesian hyperparam optimisation via Optuna (TPE sampler).

Two TPE studies, one per cheap-to-evaluate scalar hyperparam:

1. **shrinkage_k** — integer in {0..50}. Objective: 5-fold session-grouped CV
   **Spearman ρ** of v1 struggle model (with K applied as Bayesian-shrinkage
   pull toward cohort class mean) against the LLM's 4-band rating.

2. **cf_threshold** — float in [0.4, 0.9]. Objective: 5-fold session-grouped
   CV **Spearman ρ** of CF scores (cosine k-NN over the 5 normalised features)
   against the same 4-band rating.

Both studies use TPE (Tree-structured Parzen Estimator); 50 trials each;
fixed random seed for reproducibility. Cached snapshot features mean no
model refits per trial — each trial is sub-100 ms (K) or sub-2 s (CF).

**Target**: 4-band rating (`On Track`=0, `Minor Issues`=1,
`Struggling`=2, `Needs Help`=3) — the same target the v2 weight scripts use.
The binary `intervene` flag is NOT used as the optimisation target because
the dashboard makes no automatic alert/allocation decision.

**Deferred (would each need ~30 min of BKT/IRT refits per trial):**
- BKT priors (p_init, p_learn, p_guess, p_slip)
- BKT mastery threshold

Output: ``data/eval/optimised_hyperparams_v2.json`` with best values, best
Spearman ρs, full per-trial trajectories, and a comparison against v1
defaults (K=5, τ=0.7).

Run from repo root::

    python scripts/optimise_hyperparams.py
    python scripts/optimise_hyperparams.py --n-trials 100   # more trials
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import warnings
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "code2"))

import numpy as np  # noqa: E402
import optuna  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402
from sklearn.model_selection import GroupKFold  # noqa: E402

from backend import collab, config, paths  # noqa: E402

warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")
optuna.logging.set_verbosity(optuna.logging.WARNING)  # quiet per-trial chatter
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s")
logger = logging.getLogger("optimise_hyperparams")

STRUGGLE_SIGNALS = ["n_hat", "t_hat", "i_norm", "r_norm", "A_norm", "d_hat", "rep_norm"]
CF_FEATURES = collab.CF_FEATURES  # ["n_hat", "t_hat", "i_norm", "A_norm", "d_hat"]
V1_K = config.SHRINKAGE_K_DEFAULT
V1_TAU = 0.7
DEFAULT_N_TRIALS = 50
DEFAULT_SEED = 42

# 4-band target encoded as integer index 0-3 (matches optimise_v2_weights.py)
STRUGGLE_BAND_INDEX = {
    "On Track": 0,
    "Minor Issues": 1,
    "Struggling": 2,
    "Needs Help": 3,
}


# -------------------- Data loaders --------------------

def _load_jsons() -> tuple[list[dict], dict[str, dict]]:
    snap_path = paths.DATA_DIR / "eval" / "snapshots.json"
    lab_path = paths.DATA_DIR / "eval" / "llm_struggle_labels.json"
    if not snap_path.exists():
        raise FileNotFoundError(f"{snap_path} missing — run scripts/eval_common.py first")
    if not lab_path.exists():
        raise FileNotFoundError(f"{lab_path} missing — run scripts/eval_label.py --mode struggle first")
    snapshots = json.loads(snap_path.read_text(encoding="utf-8")).get("struggle_snapshots", [])
    labels = json.loads(lab_path.read_text(encoding="utf-8")).get("labels", {})
    return snapshots, labels


def _build_matched(snapshots: list[dict], labels: dict[str, dict]) -> dict[str, Any]:
    """Filter snapshots to those with LLM labels; build the per-fold index arrays."""
    matched = [s for s in snapshots if s["snapshot_id"] in labels]
    y = np.array([STRUGGLE_BAND_INDEX[labels[s["snapshot_id"]]["band"]] for s in matched])
    groups = np.array([s["session_id"] for s in matched])

    # Cohort grouping for shrinkage class-mean + CF cohort-relative similarity
    cohorts: dict[tuple[str, str], list[int]] = defaultdict(list)
    for idx, s in enumerate(matched):
        cohorts[(s["session_id"], s["t"])].append(idx)

    gkf = GroupKFold(n_splits=5)
    fold_splits = list(gkf.split(np.zeros(len(matched)), y, groups))

    band_counts = {b: int(np.sum(y == STRUGGLE_BAND_INDEX[b])) for b in STRUGGLE_BAND_INDEX}
    print(f"  matched: {len(matched)} snapshots")
    print(f"  cohorts: {len(cohorts)}")
    print(f"  sessions: {len(np.unique(groups))}")
    print(f"  mean band: {y.mean():.2f}; band counts: {band_counts}")
    return {"matched": matched, "y": y, "groups": groups, "cohorts": cohorts, "fold_splits": fold_splits}


# -------------------- Score recomputation --------------------

# v1 weights (hardcoded from config — same values, but explicit so the script
# is self-contained and would still work if config.py drifted).
V1_W = {
    "n_hat":    config.STRUGGLE_WEIGHT_N,
    "t_hat":    config.STRUGGLE_WEIGHT_T,
    "i_norm":   config.STRUGGLE_WEIGHT_I,
    "r_norm":   config.STRUGGLE_WEIGHT_R,
    "A_norm":   config.STRUGGLE_WEIGHT_A,
    "d_hat":    config.STRUGGLE_WEIGHT_D,
    "rep_norm": config.STRUGGLE_WEIGHT_REP,
}


def _raw_struggle(s: dict) -> float:
    raw = sum(V1_W[k] * s["v1_features"][k] for k in STRUGGLE_SIGNALS)
    return float(np.clip(raw, 0.0, 1.0))


def score_with_k(data: dict, K: int) -> np.ndarray:
    """Recompute v1 struggle scores under shrinkage K. Vectorised over cohorts.

    score = w_n · raw + (1 − w_n) · cohort_mean,  where  w_n = n / (n + K)
    """
    matched = data["matched"]
    preds = np.zeros(len(matched))
    raws = np.array([_raw_struggle(s) for s in matched])
    for member_indices in data["cohorts"].values():
        cohort_raws = raws[member_indices]
        cohort_mean = float(cohort_raws.mean())
        for idx in member_indices:
            n = matched[idx]["context"]["n_submissions_so_far"]
            w_n = n / (n + K) if (n + K) > 0 else 0.0
            preds[idx] = float(np.clip(w_n * raws[idx] + (1 - w_n) * cohort_mean, 0.0, 1.0))
    return preds


def score_with_tau(data: dict, tau: float) -> np.ndarray:
    """Compute CF scores cohort-by-cohort at the given similarity threshold."""
    matched = data["matched"]
    preds = np.zeros(len(matched))
    raws = np.array([_raw_struggle(s) for s in matched])
    for member_indices in data["cohorts"].values():
        rows = []
        for idx in member_indices:
            s = matched[idx]
            row = {"user": s["user"], "struggle_score": raws[idx]}
            for col in CF_FEATURES:
                row[col] = s["v1_features"][col]
            rows.append(row)
        cohort_df = pd.DataFrame(rows)
        cf_series, _diag = collab.compute_cf_struggle_scores(cohort_df, threshold=tau, k=3)
        # cf_series is indexed by cohort_df row positions
        for i, idx in enumerate(member_indices):
            preds[idx] = float(np.clip(cf_series.iloc[i], 0.0, 1.0))
    return preds


# -------------------- CV scoring --------------------

def cv_spearman(data: dict, preds: np.ndarray) -> tuple[float, list[float]]:
    """Mean Spearman ρ across 5 session-grouped folds + the per-fold list.

    ρ measures rank correlation between predicted score and band index
    — exactly the ranking quality the dashboard's leaderboard surfaces.
    """
    y = data["y"]
    fold_rhos = []
    for _tr, te in data["fold_splits"]:
        if len(np.unique(y[te])) < 2 or len(te) < 2:
            continue
        rho = spearmanr(preds[te], y[te]).correlation
        if rho is None or np.isnan(rho):
            continue
        fold_rhos.append(float(rho))
    return float(np.mean(fold_rhos)) if fold_rhos else float("nan"), fold_rhos


# -------------------- Optuna objectives --------------------

def make_k_objective(data: dict):
    def objective(trial: optuna.Trial) -> float:
        K = trial.suggest_int("shrinkage_k", 0, 50)
        preds = score_with_k(data, K)
        mean_rho, fold_rhos = cv_spearman(data, preds)
        trial.set_user_attr("fold_rhos", fold_rhos)
        return mean_rho
    return objective


def make_tau_objective(data: dict):
    def objective(trial: optuna.Trial) -> float:
        tau = trial.suggest_float("cf_threshold", 0.4, 0.9)
        preds = score_with_tau(data, tau)
        mean_rho, fold_rhos = cv_spearman(data, preds)
        trial.set_user_attr("fold_rhos", fold_rhos)
        return mean_rho
    return objective


# -------------------- Main --------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-trials", type=int, default=DEFAULT_N_TRIALS,
                        help="Trials per study (default 50; more = better quality, longer wallclock).")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--out", type=Path,
                        default=paths.DATA_DIR / "eval" / "optimised_hyperparams_v2.json")
    args = parser.parse_args()

    print("Loading snapshots + LLM labels...")
    snapshots, labels = _load_jsons()
    print(f"  total snapshots: {len(snapshots)}; total LLM labels: {len(labels)}")
    print()

    print("Building fold splits + cohorts...")
    data = _build_matched(snapshots, labels)
    print()

    # ---- Baseline: v1 defaults ----
    print(f"Baseline Spearman ρ at v1 defaults (K={V1_K}, τ={V1_TAU})...")
    base_k_preds = score_with_k(data, V1_K)
    base_k_rho, base_k_folds = cv_spearman(data, base_k_preds)
    print(f"  shrinkage K={V1_K} → CV ρ = {base_k_rho:+.4f}  (folds: {[round(r, 3) for r in base_k_folds]})")
    base_t_preds = score_with_tau(data, V1_TAU)
    base_t_rho, base_t_folds = cv_spearman(data, base_t_preds)
    print(f"  CF τ={V1_TAU}    → CV ρ = {base_t_rho:+.4f}  (folds: {[round(r, 3) for r in base_t_folds]})")
    print()

    # ---- Optuna study 1: shrinkage_k ----
    print(f"Optuna TPE study 1/2: shrinkage_k ({args.n_trials} trials)...")
    study_k = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=args.seed),
        study_name="shrinkage_k",
    )
    study_k.optimize(make_k_objective(data), n_trials=args.n_trials, show_progress_bar=False)
    best_k = study_k.best_params["shrinkage_k"]
    best_k_rho = study_k.best_value
    print(f"  best K = {best_k}  CV ρ = {best_k_rho:+.4f}  (Δ vs v1: {best_k_rho - base_k_rho:+.4f})")
    print()

    # ---- Optuna study 2: cf_threshold ----
    print(f"Optuna TPE study 2/2: cf_threshold ({args.n_trials} trials)...")
    study_t = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=args.seed),
        study_name="cf_threshold",
    )
    study_t.optimize(make_tau_objective(data), n_trials=args.n_trials, show_progress_bar=False)
    best_t = study_t.best_params["cf_threshold"]
    best_t_rho = study_t.best_value
    print(f"  best τ = {best_t:.3f}  CV ρ = {best_t_rho:+.4f}  (Δ vs v1: {best_t_rho - base_t_rho:+.4f})")
    print()

    # ---- Compile + persist ----
    payload = {
        "version": "v2",
        "kind": "hyperparams",
        "method": "Optuna TPE sampler",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "n_trials_per_study": args.n_trials,
        "random_seed": args.seed,
        "cv_scheme": "GroupKFold(n_splits=5) with session_id as group; same fold split as the v2 weight scripts",
        "target": (
            "4-band rating (LLM second-opinion). "
            "On Track=0, Minor Issues=1, Struggling=2, Needs Help=3. "
            "Objective: maximise mean per-fold Spearman ρ."
        ),
        "metric": "Spearman ρ (rank correlation between predicted score and band index)",
        "n_samples": len(data["matched"]),

        "best_values": {
            "shrinkage_k": int(best_k),
            "cf_threshold": float(best_t),
            # Defaults preserved for hyperparams we did NOT optimise — the
            # runtime_config boot overlay (RuntimeConfig.defaults) seeds the
            # scalar sliders from the full set; the trained v2 values are the
            # unconditional deployed default.
            "bkt_p_init":           config.BKT_P_INIT,
            "bkt_p_learn":          config.BKT_P_LEARN,
            "bkt_p_guess":          config.BKT_P_GUESS,
            "bkt_p_slip":           config.BKT_P_SLIP,
            "bkt_mastery_threshold": config.BKT_MASTERY_THRESHOLD,
        },
        "best_rhos": {
            "shrinkage_k_best":  float(best_k_rho),
            "cf_threshold_best": float(best_t_rho),
        },
        "v1_baseline_rhos": {
            "shrinkage_k_at_default":  float(base_k_rho),
            "cf_threshold_at_default": float(base_t_rho),
            "default_k":   V1_K,
            "default_tau": V1_TAU,
        },
        "deltas": {
            "shrinkage_k":  float(best_k_rho - base_k_rho),
            "cf_threshold": float(best_t_rho - base_t_rho),
        },
        "studies": {
            "shrinkage_k": {
                "n_trials": len(study_k.trials),
                "best_trial_number": study_k.best_trial.number,
                "trials": [
                    {
                        "number": t.number,
                        "value": t.value,
                        "params": t.params,
                        "fold_rhos": t.user_attrs.get("fold_rhos", []),
                        "state": str(t.state),
                    }
                    for t in study_k.trials
                ],
            },
            "cf_threshold": {
                "n_trials": len(study_t.trials),
                "best_trial_number": study_t.best_trial.number,
                "trials": [
                    {
                        "number": t.number,
                        "value": t.value,
                        "params": t.params,
                        "fold_rhos": t.user_attrs.get("fold_rhos", []),
                        "state": str(t.state),
                    }
                    for t in study_t.trials
                ],
            },
        },
        "deferred": ["bkt_p_init", "bkt_p_learn", "bkt_p_guess", "bkt_p_slip", "bkt_mastery_threshold"],
        "deferred_reason": (
            "Each BKT hyperparam trial would require refitting BKT per (session, "
            "cutoff) — ~30 min per study at our N. Skipped to keep Phase 4d "
            "wallclock under 5 min. Reported in §5.4 as 'BKT priors held at "
            "config defaults; only directly-tunable scalars (K, τ) optimised'."
        ),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {args.out}")
    print()
    print("=== HEADLINE (Spearman ρ vs 4-band) ===")
    print(f"  shrinkage_k:  best={best_k}  ρ={best_k_rho:+.4f}  (Δ vs v1 K={V1_K}: {best_k_rho - base_k_rho:+.4f})")
    print(f"  cf_threshold: best={best_t:.3f}  ρ={best_t_rho:+.4f}  (Δ vs v1 τ={V1_TAU}: {best_t_rho - base_t_rho:+.4f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
