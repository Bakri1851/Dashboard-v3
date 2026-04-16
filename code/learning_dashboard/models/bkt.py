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
