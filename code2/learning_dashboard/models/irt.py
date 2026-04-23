"""Phase 2 — 2-Parameter Logistic (2PL) IRT difficulty + discrimination.

Upgrade from 1PL Rasch: each question gets both a difficulty ``b_j`` and a
discrimination ``a_j``. Non-discriminating items (``a_j`` near 0) can be
flagged as bad questions. The likelihood is::

    P(correct | θ_i, a_j, b_j) = sigmoid(a_j · (θ_i − b_j))

Identifiability: mean(θ) = 0 (centring) AND mean(log a) = 0 (geomean(a) = 1).
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit  # sigmoid

from learning_dashboard import config
from learning_dashboard.analytics import classify_score

logger = logging.getLogger("learning_dashboard.irt")

# Column schema for the output DataFrame (used for empty-data fallback).
# irt_discrimination is the 2PL ``a_j`` (positive; 1.0 = Rasch-equivalent).
_OUTPUT_COLUMNS = [
    "question",
    "irt_difficulty",
    "irt_discrimination",
    "irt_difficulty_level",
    "irt_difficulty_color",
]


def build_response_matrix(
    df: pd.DataFrame,
    correct_threshold: float = config.CORRECT_THRESHOLD,
) -> pd.DataFrame:
    """Build a binary student x question response matrix.

    For each student-question pair the *best* attempt (lowest incorrectness)
    is selected.  A response is coded 1 (correct) when
    ``incorrectness < correct_threshold``, else 0.

    Rows and columns with fewer than the configured minimums are dropped.
    """
    if df.empty:
        logger.info("build_response_matrix: df is empty")
        return pd.DataFrame()
    if "incorrectness" not in df.columns:
        logger.info(
            "build_response_matrix: missing 'incorrectness' column (have: %s)",
            list(df.columns),
        )
        return pd.DataFrame()

    # Best attempt per student-question pair.
    best = (
        df.groupby(["user", "question"])["incorrectness"]
        .min()
        .reset_index()
    )
    best["correct"] = (best["incorrectness"] < correct_threshold).astype(int)

    matrix = best.pivot(index="user", columns="question", values="correct")
    logger.info(
        "build_response_matrix: initial matrix %d students x %d questions "
        "(correct_rate=%.3f, threshold=%.2f)",
        matrix.shape[0], matrix.shape[1],
        float(best["correct"].mean()) if len(best) else 0.0,
        correct_threshold,
    )

    # Iteratively filter until minimums are met AND no single-class
    # (all-correct / all-wrong) rows or columns remain. Single-class patterns
    # make Rasch MLE unbounded (θ or b → ±∞), so L-BFGS-B drifts to a bounds
    # corner and the gradient vanishes. Dropping them is the standard fix.
    changed = True
    passes = 0
    while changed:
        changed = False
        passes += 1
        shape_before = matrix.shape
        # Drop questions with too few responding students.
        col_counts = matrix.notna().sum(axis=0)
        keep_cols = col_counts[col_counts >= config.IRT_MIN_ATTEMPTS_PER_QUESTION].index
        dropped_min_q = len(matrix.columns) - len(keep_cols)
        if dropped_min_q:
            matrix = matrix[keep_cols]
            changed = True
        # Drop students with too few attempted questions.
        row_counts = matrix.notna().sum(axis=1)
        keep_rows = row_counts[row_counts >= config.IRT_MIN_ATTEMPTS_PER_STUDENT].index
        dropped_min_s = len(matrix.index) - len(keep_rows)
        if dropped_min_s:
            matrix = matrix.loc[keep_rows]
            changed = True
        if matrix.empty:
            logger.info(
                "build_response_matrix: empty after min-attempts pass %d "
                "(dropped %d questions < %d responses, %d students < %d responses)",
                passes, dropped_min_q, config.IRT_MIN_ATTEMPTS_PER_QUESTION,
                dropped_min_s, config.IRT_MIN_ATTEMPTS_PER_STUDENT,
            )
            break
        # Drop single-class questions (all students answered the same way).
        col_nunique = matrix.apply(lambda s: s.dropna().nunique(), axis=0)
        keep_cols = col_nunique[col_nunique >= 2].index
        dropped_sep_q = len(matrix.columns) - len(keep_cols)
        if dropped_sep_q:
            matrix = matrix[keep_cols]
            changed = True
        # Drop single-class students (answered all their questions the same way).
        row_nunique = matrix.apply(lambda s: s.dropna().nunique(), axis=1)
        keep_rows = row_nunique[row_nunique >= 2].index
        dropped_sep_s = len(matrix.index) - len(keep_rows)
        if dropped_sep_s:
            matrix = matrix.loc[keep_rows]
            changed = True
        logger.info(
            "build_response_matrix pass %d: %s → %s "
            "(dropped: min-attempts q=%d s=%d, separable q=%d s=%d)",
            passes, shape_before, matrix.shape,
            dropped_min_q, dropped_min_s, dropped_sep_q, dropped_sep_s,
        )

    logger.info("build_response_matrix: final matrix %s after %d pass(es)", matrix.shape, passes)
    return matrix


def fit_2pl_model(
    response_matrix: pd.DataFrame,
    max_iter: int = config.IRT_MAX_ITER,
) -> dict:
    """Fit a 2PL IRT model via joint MLE.

    Likelihood: ``P(correct | θ_i, a_j, b_j) = sigmoid(a_j · (θ_i − b_j))``.

    Parameter vector is laid out as ``[θ (n_students), b (n_questions),
    log_a (n_questions)]`` — ``log_a`` keeps ``a`` strictly positive without
    box constraints. Identifiability: both ``θ`` and ``log_a`` are
    mean-centred at every call (equivalent to ``mean(θ)=0`` and
    ``geomean(a)=1``).

    Returns dict with keys ``difficulty``, ``discrimination``, ``ability``,
    ``convergence``, ``log_likelihood``.
    """
    students = response_matrix.index.tolist()
    questions = response_matrix.columns.tolist()
    n_students = len(students)
    n_questions = len(questions)

    empty_result = {
        "difficulty": {},
        "discrimination": {},
        "ability": {},
        "convergence": False,
        "log_likelihood": 0.0,
    }

    if n_students == 0 or n_questions == 0:
        return empty_result

    # Observed (row, col, value) triples — skip NaN.
    obs_rows, obs_cols, obs_vals = [], [], []
    values = response_matrix.values
    for i in range(n_students):
        for j in range(n_questions):
            v = values[i, j]
            if not np.isnan(v):
                obs_rows.append(i)
                obs_cols.append(j)
                obs_vals.append(v)
    obs_rows = np.array(obs_rows, dtype=int)
    obs_cols = np.array(obs_cols, dtype=int)
    obs_vals = np.array(obs_vals, dtype=float)

    # Defense in depth: build_response_matrix already drops single-class rows
    # and columns, but if callers pass a hand-constructed matrix we still
    # refuse to fit a single-class dataset — the MLE is unbounded.
    if obs_vals.size == 0 or np.unique(obs_vals).size < 2:
        return empty_result

    # Index slices into the flat parameter vector.
    sl_theta = slice(0, n_students)
    sl_b = slice(n_students, n_students + n_questions)
    sl_log_a = slice(n_students + n_questions, n_students + 2 * n_questions)

    def _unpack(params: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        theta = params[sl_theta] - params[sl_theta].mean()
        b = params[sl_b]
        log_a = params[sl_log_a] - params[sl_log_a].mean()  # geomean(a) = 1
        a = np.exp(log_a)
        return theta, b, a

    def _neg_log_likelihood(params: np.ndarray) -> float:
        theta, b, a = _unpack(params)
        logit = a[obs_cols] * (theta[obs_rows] - b[obs_cols])
        p = expit(logit)
        p = np.clip(p, 1e-12, 1.0 - 1e-12)
        ll = (obs_vals * np.log(p) + (1.0 - obs_vals) * np.log(1.0 - p)).sum()
        return -ll

    def _gradient(params: np.ndarray) -> np.ndarray:
        theta, b, a = _unpack(params)
        a_obs = a[obs_cols]
        diff = theta[obs_rows] - b[obs_cols]
        logit = a_obs * diff
        p = expit(logit)
        residual = obs_vals - p  # y − p

        grad_theta = np.zeros(n_students)
        grad_b = np.zeros(n_questions)
        grad_log_a = np.zeros(n_questions)

        # ∂ log L / ∂ θ_i   = Σ_j  a_j · (y − p)
        np.add.at(grad_theta, obs_rows, a_obs * residual)
        # ∂ log L / ∂ b_j   = −a_j · Σ_i (y − p)
        np.add.at(grad_b, obs_cols, -a_obs * residual)
        # ∂ log L / ∂ log_a = a_j · (θ − b) · (y − p)
        np.add.at(grad_log_a, obs_cols, a_obs * diff * residual)

        # Project through the mean-centering used in _unpack.
        grad_theta = grad_theta - grad_theta.mean()
        grad_log_a = grad_log_a - grad_log_a.mean()

        return np.concatenate([-grad_theta, -grad_b, -grad_log_a])

    # Warm start at Rasch: θ=0, b=0, log_a=0 (a=1 uniform).
    x0 = np.zeros(n_students + 2 * n_questions)
    # Box-bound log_a to keep a in [~0.007, ~148] — stops the optimiser from
    # blowing up on degenerate items where discrimination is near-zero and
    # the Hessian is flat. The bound is on the raw parameter; the effective
    # log_a seen by the likelihood is the mean-centred version (for
    # geomean(a)=1), which can exceed these bounds after centering. A wider
    # raw-parameter bound reduces the chance that the optimiser parks a
    # parameter on the boundary and loses gradient information.
    bounds = (
        [(None, None)] * n_students
        + [(None, None)] * n_questions
        + [(-5.0, 5.0)] * n_questions
    )
    result = minimize(
        _neg_log_likelihood,
        x0,
        jac=_gradient,
        method="L-BFGS-B",
        bounds=bounds,
        options={"maxiter": max_iter, "ftol": 1e-8},
    )

    theta_hat, b_hat, a_hat = _unpack(result.x)

    return {
        "difficulty": dict(zip(questions, b_hat.tolist())),
        "discrimination": dict(zip(questions, a_hat.tolist())),
        "ability": dict(zip(students, theta_hat.tolist())),
        "convergence": bool(result.success),
        "log_likelihood": float(-result.fun),
    }


# Backwards-compat alias — callers that asked for "Rasch" get the 2PL fit.
fit_rasch_model = fit_2pl_model


def compute_irt_model(df: pd.DataFrame) -> dict:
    """Fit 2PL once and return both question- and student-level outputs.

    Returns a dict with:
        ``difficulty_df``: columns matching ``_OUTPUT_COLUMNS`` + raw logit b
        ``ability_df``: columns ``[user, theta]`` — θ on the logit scale
        ``convergence``: bool
        ``log_likelihood``: float

    Both dataframes are empty when the fit fails or there's insufficient data.
    """
    empty_q = pd.DataFrame(columns=_OUTPUT_COLUMNS + ["b_raw"])
    empty_a = pd.DataFrame(columns=["user", "theta"])
    empty_result = {
        "difficulty_df": empty_q,
        "ability_df": empty_a,
        "convergence": False,
        "log_likelihood": 0.0,
    }

    if df.empty:
        return empty_result

    matrix = build_response_matrix(df)
    if matrix.empty:
        return empty_result

    fit = fit_2pl_model(matrix)
    if not fit["difficulty"]:
        return empty_result

    q_rows = []
    for qid, b_raw in fit["difficulty"].items():
        score = float(expit(b_raw))  # map logit → [0, 1]
        level, color = classify_score(score, config.IRT_DIFFICULTY_THRESHOLDS)
        q_rows.append({
            "question": qid,
            "irt_difficulty": round(score, 4),
            "irt_discrimination": round(float(fit["discrimination"].get(qid, 1.0)), 4),
            "irt_difficulty_level": level,
            "irt_difficulty_color": color,
            "b_raw": float(b_raw),
        })
    difficulty_df = (
        pd.DataFrame(q_rows)
        .sort_values("irt_difficulty", ascending=False)
        .reset_index(drop=True)
    )

    ability_df = pd.DataFrame(
        [{"user": u, "theta": float(t)} for u, t in fit["ability"].items()]
    )

    return {
        "difficulty_df": difficulty_df,
        "ability_df": ability_df,
        "convergence": bool(fit["convergence"]),
        "log_likelihood": float(fit["log_likelihood"]),
    }


def compute_irt_difficulty_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Compute IRT-based difficulty scores for all questions.

    Returns a DataFrame with columns matching ``_OUTPUT_COLUMNS``.
    The ``irt_difficulty`` value is the raw logit-scale ``b_j`` mapped
    to [0, 1] via the sigmoid function so it can be compared with the
    baseline difficulty score and classified using the same threshold
    structure. ``irt_discrimination`` carries the 2PL ``a_j`` — values near
    0 indicate non-discriminating (often "bad") items.
    """
    model = compute_irt_model(df)
    df_out = model["difficulty_df"]
    if df_out.empty:
        return pd.DataFrame(columns=_OUTPUT_COLUMNS)
    # Drop the internal b_raw column — only consumed by compute_irt_model.
    return df_out[_OUTPUT_COLUMNS].copy()


def compute_irt_abilities(df: pd.DataFrame) -> pd.DataFrame:
    """Return per-student θ for the given window.

    Convenience wrapper around ``compute_irt_model``. Returns a DataFrame
    with columns ``[user, theta]`` (empty when the fit fails).
    """
    return compute_irt_model(df)["ability_df"]
