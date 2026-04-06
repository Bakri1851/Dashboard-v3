"""Phase 2 — 1-Parameter Logistic (Rasch) IRT difficulty estimation."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit  # sigmoid

from learning_dashboard import config
from learning_dashboard.analytics import classify_score

# Column schema for the output DataFrame (used for empty-data fallback).
_OUTPUT_COLUMNS = [
    "question",
    "irt_difficulty",
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
    if df.empty or "incorrectness" not in df.columns:
        return pd.DataFrame()

    # Best attempt per student-question pair.
    best = (
        df.groupby(["user", "question"])["incorrectness"]
        .min()
        .reset_index()
    )
    best["correct"] = (best["incorrectness"] < correct_threshold).astype(int)

    matrix = best.pivot(index="user", columns="question", values="correct")

    # Iteratively filter until minimums are met.
    changed = True
    while changed:
        changed = False
        # Drop questions with too few responding students.
        col_counts = matrix.notna().sum(axis=0)
        keep_cols = col_counts[col_counts >= config.IRT_MIN_ATTEMPTS_PER_QUESTION].index
        if len(keep_cols) < len(matrix.columns):
            matrix = matrix[keep_cols]
            changed = True
        # Drop students with too few attempted questions.
        row_counts = matrix.notna().sum(axis=1)
        keep_rows = row_counts[row_counts >= config.IRT_MIN_ATTEMPTS_PER_STUDENT].index
        if len(keep_rows) < len(matrix.index):
            matrix = matrix.loc[keep_rows]
            changed = True

    return matrix


def fit_rasch_model(
    response_matrix: pd.DataFrame,
    max_iter: int = config.IRT_MAX_ITER,
) -> dict:
    """Fit a Rasch (1PL) model via joint MLE.

    Parameters
    ----------
    response_matrix : DataFrame
        Binary student (rows) x question (columns) matrix.  NaN = unobserved.
    max_iter : int
        Maximum L-BFGS-B iterations.

    Returns
    -------
    dict with keys ``difficulty``, ``ability``, ``convergence``,
    ``log_likelihood``.
    """
    students = response_matrix.index.tolist()
    questions = response_matrix.columns.tolist()
    n_students = len(students)
    n_questions = len(questions)

    if n_students == 0 or n_questions == 0:
        return {
            "difficulty": {},
            "ability": {},
            "convergence": False,
            "log_likelihood": 0.0,
        }

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

    def _neg_log_likelihood(params: np.ndarray) -> float:
        theta = params[:n_students]
        b = params[n_students:]
        # Centre abilities for identifiability.
        theta = theta - theta.mean()
        logit = theta[obs_rows] - b[obs_cols]
        p = expit(logit)
        # Clip to avoid log(0).
        p = np.clip(p, 1e-12, 1.0 - 1e-12)
        ll = (obs_vals * np.log(p) + (1.0 - obs_vals) * np.log(1.0 - p)).sum()
        return -ll

    def _gradient(params: np.ndarray) -> np.ndarray:
        theta = params[:n_students]
        b = params[n_students:]
        theta = theta - theta.mean()
        logit = theta[obs_rows] - b[obs_cols]
        p = expit(logit)
        residual = obs_vals - p  # y - p

        grad_theta = np.zeros(n_students)
        grad_b = np.zeros(n_questions)
        np.add.at(grad_theta, obs_rows, residual)
        np.add.at(grad_b, obs_cols, -residual)

        # Negate because we minimise negative log-likelihood.
        return np.concatenate([-grad_theta, -grad_b])

    x0 = np.zeros(n_students + n_questions)
    result = minimize(
        _neg_log_likelihood,
        x0,
        jac=_gradient,
        method="L-BFGS-B",
        options={"maxiter": max_iter, "ftol": 1e-8},
    )

    theta_hat = result.x[:n_students]
    b_hat = result.x[n_students:]
    # Final centring.
    theta_hat = theta_hat - theta_hat.mean()

    return {
        "difficulty": dict(zip(questions, b_hat.tolist())),
        "ability": dict(zip(students, theta_hat.tolist())),
        "convergence": bool(result.success),
        "log_likelihood": float(-result.fun),
    }


def compute_irt_difficulty_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Compute IRT-based difficulty scores for all questions.

    Returns a DataFrame with columns matching ``_OUTPUT_COLUMNS``.
    The ``irt_difficulty`` value is the raw logit-scale ``b_i`` mapped
    to [0, 1] via the sigmoid function so it can be compared with the
    baseline difficulty score and classified using the same threshold
    structure.
    """
    empty = pd.DataFrame(columns=_OUTPUT_COLUMNS)

    if df.empty:
        return empty

    matrix = build_response_matrix(df)
    if matrix.empty:
        return empty

    fit = fit_rasch_model(matrix)
    if not fit["difficulty"]:
        return empty

    rows = []
    for qid, b_raw in fit["difficulty"].items():
        score = float(expit(b_raw))  # map logit → [0, 1]
        level, color = classify_score(score, config.IRT_DIFFICULTY_THRESHOLDS)
        rows.append({
            "question": qid,
            "irt_difficulty": round(score, 4),
            "irt_difficulty_level": level,
            "irt_difficulty_color": color,
        })

    result = pd.DataFrame(rows)
    result = result.sort_values("irt_difficulty", ascending=False).reset_index(drop=True)
    return result
