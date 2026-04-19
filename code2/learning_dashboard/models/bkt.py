"""Phase 3 — Bayesian Knowledge Tracing (BKT) mastery estimation.

Standard BKT with 4 parameters per skill (question = skill):
    P(L_0)  prior probability of knowing the skill
    P(T)    probability of learning on each opportunity
    P(G)    probability of guessing correctly without knowing
    P(S)    probability of slipping (wrong answer despite knowing)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.metrics import roc_auc_score

from learning_dashboard import config

_MASTERY_COLUMNS = ["user", "question", "mastery", "n_attempts"]
_SUMMARY_COLUMNS = [
    "user",
    "mean_mastery",
    "min_mastery",
    "mastered_count",
    "total_questions",
]


def bkt_update(
    p_mastery: float,
    correct: bool,
    p_guess: float = config.BKT_P_GUESS,
    p_slip: float = config.BKT_P_SLIP,
    p_learn: float = config.BKT_P_LEARN,
) -> float:
    """Single BKT HMM update step.  Returns P(L_{t+1})."""
    if correct:
        p_obs = p_mastery * (1.0 - p_slip) + (1.0 - p_mastery) * p_guess
        if p_obs < 1e-12:
            p_obs = 1e-12
        p_posterior = p_mastery * (1.0 - p_slip) / p_obs
    else:
        p_obs = p_mastery * p_slip + (1.0 - p_mastery) * (1.0 - p_guess)
        if p_obs < 1e-12:
            p_obs = 1e-12
        p_posterior = p_mastery * p_slip / p_obs

    p_next = p_posterior + (1.0 - p_posterior) * p_learn
    return float(np.clip(p_next, 0.0, 1.0))


def compute_student_mastery(
    student_df: pd.DataFrame,
    p_init: float = config.BKT_P_INIT,
    p_learn: float = config.BKT_P_LEARN,
    p_guess: float = config.BKT_P_GUESS,
    p_slip: float = config.BKT_P_SLIP,
) -> dict[str, float]:
    """Replay one student's chronological submissions and return final mastery per question.

    ``student_df`` must contain columns ``question``, ``timestamp``, and
    ``incorrectness``, sorted by ``timestamp`` ascending.
    """
    if student_df.empty:
        return {}

    if "timestamp" in student_df.columns:
        student_df = student_df.sort_values("timestamp", ascending=True, kind="mergesort")

    mastery: dict[str, float] = {}
    for _, row in student_df.iterrows():
        qid = row["question"]
        correct = row["incorrectness"] < config.CORRECT_THRESHOLD
        mastery[qid] = bkt_update(
            mastery.get(qid, p_init), correct, p_guess, p_slip, p_learn
        )
    return mastery


def compute_all_mastery(
    df: pd.DataFrame,
    p_init: float = config.BKT_P_INIT,
    p_learn: float = config.BKT_P_LEARN,
    p_guess: float = config.BKT_P_GUESS,
    p_slip: float = config.BKT_P_SLIP,
) -> pd.DataFrame:
    """Per-student, per-question mastery for the entire dataset.

    Returns DataFrame with columns: user, question, mastery, n_attempts.
    """
    empty = pd.DataFrame(columns=_MASTERY_COLUMNS)
    required = {"user", "question", "timestamp", "incorrectness"}
    if df.empty or not required.issubset(df.columns):
        return empty

    # BKT is a sequential HMM; replay order determines the posterior.
    # Sort with a secondary key so submissions at identical timestamps
    # (bulk imports, same-second posts) replay in a deterministic order.
    ordered = df.sort_values(
        ["timestamp", "question"], ascending=True, kind="mergesort"
    )

    attempt_counts = ordered.groupby(["user", "question"]).size()
    rows: list[dict] = []

    for user, group in ordered.groupby("user", sort=False):
        for qid, p in compute_student_mastery(
            group, p_init=p_init, p_learn=p_learn, p_guess=p_guess, p_slip=p_slip
        ).items():
            rows.append(
                {
                    "user": user,
                    "question": qid,
                    "mastery": round(p, 6),
                    "n_attempts": int(attempt_counts.loc[(user, qid)]),
                }
            )

    return pd.DataFrame(rows) if rows else empty


def _build_sequences(df: pd.DataFrame) -> list[np.ndarray]:
    """Per-(user, question) binary correctness sequences, in temporal order.

    Uses the same ``[timestamp, question]`` mergesort ordering as
    ``compute_all_mastery`` so the fit sees the exact same sequences as
    inference.  Returns an empty list when required columns are missing.
    """
    required = {"user", "question", "timestamp", "incorrectness"}
    if df.empty or not required.issubset(df.columns):
        return []

    ordered = df.sort_values(
        ["timestamp", "question"], ascending=True, kind="mergesort"
    )
    correct = (ordered["incorrectness"] < config.CORRECT_THRESHOLD).astype(np.int8).to_numpy()
    users = ordered["user"].to_numpy()
    questions = ordered["question"].to_numpy()

    sequences: dict[tuple, list[int]] = {}
    for u, q, c in zip(users, questions, correct):
        sequences.setdefault((u, q), []).append(int(c))
    return [np.asarray(seq, dtype=np.int8) for seq in sequences.values()]


def _walk_and_score(
    sequences: list[np.ndarray],
    p_init: float,
    p_learn: float,
    p_guess: float,
    p_slip: float,
) -> tuple[float, np.ndarray, np.ndarray]:
    """Single pass over all sequences.

    Returns ``(log_likelihood, predictions, actuals)`` where ``predictions[i]``
    is the model's P(correct) for the i-th attempt *before* the attempt was
    observed, and ``actuals[i]`` is the observed 0/1 correctness.  The sum of
    ``log P(observed | history)`` across attempts is the forward-algorithm
    log-likelihood of the data under the BKT HMM.
    """
    n_obs = sum(len(s) for s in sequences)
    predictions = np.empty(n_obs, dtype=np.float64)
    actuals = np.empty(n_obs, dtype=np.int8)
    log_lik = 0.0

    idx = 0
    eps = 1e-12
    for seq in sequences:
        mastery = float(p_init)
        for c in seq:
            p_correct = mastery * (1.0 - p_slip) + (1.0 - mastery) * p_guess
            predictions[idx] = p_correct
            actuals[idx] = c
            idx += 1

            p_obs = p_correct if c else (1.0 - p_correct)
            if p_obs < eps:
                p_obs = eps
            log_lik += float(np.log(p_obs))

            # Bayes update + transition — identical to bkt_update().
            if c:
                p_posterior = mastery * (1.0 - p_slip) / p_obs
            else:
                p_posterior = mastery * p_slip / p_obs
            mastery = p_posterior + (1.0 - p_posterior) * p_learn
            if mastery > 1.0:
                mastery = 1.0
            elif mastery < 0.0:
                mastery = 0.0

    return log_lik, predictions, actuals


def fit_bkt_parameters(
    df: pd.DataFrame,
    initial_params: tuple[float, float, float, float] | None = None,
    max_iter: int | None = None,
    min_observations: int | None = None,
) -> dict:
    """Fit a single global (P(L_0), P(T), P(G), P(S)) by maximum likelihood.

    Uses the forward algorithm for the 2-state BKT HMM and L-BFGS-B with
    bounds ``[(0,1), (0,1), (0,0.5), (0,0.5)]`` to enforce the standard
    identifiability constraint (P(G) + P(S) < 1).

    Returns a dict with keys:
        p_init, p_learn, p_guess, p_slip  — fitted parameters
        log_likelihood                     — data log-likelihood at the fit
        auc                                — ROC-AUC on next-attempt correctness
        convergence                        — bool from scipy
        n_observations                     — number of attempts used
        message                            — scipy convergence message

    If ``df`` has fewer than ``min_observations`` attempts, returns the current
    defaults with ``convergence=False`` and a message explaining why.
    """
    if max_iter is None:
        max_iter = getattr(config, "BKT_FIT_MAX_ITER", 200)
    if min_observations is None:
        min_observations = getattr(config, "BKT_FIT_MIN_OBSERVATIONS", 50)

    sequences = _build_sequences(df)
    n_observations = sum(len(s) for s in sequences)

    result_stub = {
        "p_init": config.BKT_P_INIT,
        "p_learn": config.BKT_P_LEARN,
        "p_guess": config.BKT_P_GUESS,
        "p_slip": config.BKT_P_SLIP,
        "log_likelihood": 0.0,
        "auc": float("nan"),
        "convergence": False,
        "n_observations": n_observations,
        "message": "",
    }

    if n_observations < min_observations:
        result_stub["message"] = (
            f"Too few observations ({n_observations} < {min_observations}) — "
            "retaining current parameters."
        )
        return result_stub

    # Refuse to fit when every attempt is graded the same way.  With one class
    # the log-likelihood surface is maximised at a bounds corner where every
    # prediction is 1 (LL = 0), AUC is undefined, and the fitted parameters
    # carry no information about learning dynamics.
    all_outcomes = np.concatenate([seq for seq in sequences])
    if len(np.unique(all_outcomes)) < 2:
        only_class = "correct" if int(all_outcomes[0]) == 1 else "incorrect"
        threshold = config.CORRECT_THRESHOLD
        lines = [
            f"All {n_observations} attempts in the current view were graded "
            f"{only_class} (threshold: incorrectness < {threshold:g}). "
            "BKT cannot identify learning from a single-class dataset."
        ]
        if "incorrectness" in df.columns:
            inc = df["incorrectness"].dropna()
            if not inc.empty:
                n_fallback = int((inc == 0.5).sum())
                n_below = int((inc < 0.5).sum())
                n_above = int((inc > 0.5).sum())
                lines.append(
                    f"Incorrectness distribution — at 0.5 (OpenAI fallback / "
                    f"empty feedback): {n_fallback}; < 0.5: {n_below}; "
                    f"> 0.5: {n_above}. min={inc.min():.2f}, "
                    f"median={inc.median():.2f}, max={inc.max():.2f}."
                )
                if n_fallback >= 0.8 * len(inc):
                    lines.append(
                        "Most rows are at the 0.5 fallback — likely cause: "
                        "empty ai_feedback or OpenAI scoring failing silently. "
                        "Check the Streamlit console for 'OpenAI batch call failed' "
                        "warnings and verify .streamlit/secrets.toml has a valid "
                        "OPENAI_API_KEY."
                    )
                elif n_below == 0 and n_above > 0:
                    lines.append(
                        f"OpenAI is scoring, but no row falls below {threshold:g}. "
                        "Consider lowering config.CORRECT_THRESHOLD to capture "
                        "partial-credit answers, or widen the time/module filter."
                    )
                else:
                    lines.append("Try widening the time/module filter.")
        result_stub["message"] = " ".join(lines)
        return result_stub

    if initial_params is None:
        initial_params = (
            config.BKT_P_INIT,
            config.BKT_P_LEARN,
            config.BKT_P_GUESS,
            config.BKT_P_SLIP,
        )

    def _neg_log_likelihood(params: np.ndarray) -> float:
        p_init, p_learn, p_guess, p_slip = params
        ll, _, _ = _walk_and_score(sequences, p_init, p_learn, p_guess, p_slip)
        return -ll

    bounds = [(0.0, 1.0), (0.0, 1.0), (0.0, 0.5), (0.0, 0.5)]
    opt = minimize(
        _neg_log_likelihood,
        x0=np.asarray(initial_params, dtype=np.float64),
        method="L-BFGS-B",
        bounds=bounds,
        options={"maxiter": max_iter, "ftol": 1e-8},
    )

    p_init, p_learn, p_guess, p_slip = (float(v) for v in opt.x)
    final_ll, predictions, actuals = _walk_and_score(
        sequences, p_init, p_learn, p_guess, p_slip
    )

    try:
        auc = (
            float(roc_auc_score(actuals, predictions))
            if len(np.unique(actuals)) >= 2
            else float("nan")
        )
    except (ValueError, TypeError):
        auc = float("nan")

    message = opt.message if isinstance(opt.message, str) else str(opt.message)

    return {
        "p_init": p_init,
        "p_learn": p_learn,
        "p_guess": p_guess,
        "p_slip": p_slip,
        "log_likelihood": float(final_ll),
        "auc": auc,
        "convergence": bool(opt.success),
        "n_observations": n_observations,
        "message": message,
    }


def compute_student_mastery_summary(
    mastery_df: pd.DataFrame,
) -> pd.DataFrame:
    """Per-student aggregate mastery statistics.

    Accepts the output of ``compute_all_mastery`` to avoid recomputation.
    Returns DataFrame with columns: user, mean_mastery, min_mastery,
    mastered_count, total_questions.
    """
    empty = pd.DataFrame(columns=_SUMMARY_COLUMNS)
    if mastery_df.empty:
        return empty

    threshold = config.BKT_MASTERY_THRESHOLD
    summary = (
        mastery_df.groupby("user")
        .agg(
            mean_mastery=("mastery", "mean"),
            min_mastery=("mastery", "min"),
            mastered_count=("mastery", lambda x: int((x >= threshold).sum())),
            total_questions=("mastery", "size"),
        )
        .reset_index()
    )
    summary["mean_mastery"] = summary["mean_mastery"].round(4)
    summary["min_mastery"] = summary["min_mastery"].round(4)
    return summary
