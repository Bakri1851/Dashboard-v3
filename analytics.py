# analytics.py — Scoring calculations (UI-independent)
from typing import Optional

import numpy as np
import pandas as pd

import config


# Incorrectness Estimation from AI Feedback

def estimate_incorrectness(feedback: Optional[str]) -> float:
    """
    Keyword-based heuristic on AI feedback text.
    Returns float in [0, 1] where 0=correct, 1=completely incorrect.
    Rules applied in order — first match wins.
    """
    # Rule 1: empty / null
    if not feedback or not str(feedback).strip():
        return config.INCORRECTNESS_EMPTY

    text = str(feedback).lower()

    positive_count = sum(1 for kw in config.POSITIVE_KEYWORDS if kw in text)
    negative_count = sum(1 for kw in config.NEGATIVE_KEYWORDS if kw in text)
    partial_count = sum(1 for kw in config.PARTIAL_KEYWORDS if kw in text)

    # Rule 2: only positive
    if positive_count > 0 and negative_count == 0 and partial_count == 0:
        return config.INCORRECTNESS_ONLY_POSITIVE

    # Rule 3: only negative
    if negative_count > 0 and positive_count == 0 and partial_count == 0:
        return config.INCORRECTNESS_ONLY_NEGATIVE

    # Rule 4: any partial
    if partial_count > 0:
        return config.INCORRECTNESS_PARTIAL

    # Rule 5: more positive than negative
    if positive_count > negative_count:
        return config.INCORRECTNESS_MORE_POSITIVE

    # Rule 6: more negative than positive
    if negative_count > positive_count:
        return config.INCORRECTNESS_MORE_NEGATIVE

    # Rule 7: otherwise
    return config.INCORRECTNESS_DEFAULT


def compute_incorrectness_column(df: pd.DataFrame) -> pd.Series:
    """Apply estimate_incorrectness to the ai_feedback column."""
    return df["ai_feedback"].apply(estimate_incorrectness)


# Min-Max Normalization

def min_max_normalize(series: pd.Series) -> pd.Series:
    """(x - min) / (max - min), clamped to [0, 1]. Returns 0 if min == max."""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series(0.0, index=series.index)
    result = (series - min_val) / (max_val - min_val)
    return result.clip(0.0, 1.0)


# -----------------------------------------------------------------
# Recent Incorrectness (A_raw)
# -----------------------------------------------------------------

def compute_recent_incorrectness(student_submissions: pd.DataFrame) -> float:
    """
    Last N submissions (most recent first), weighted by RECENT_WEIGHTS.
    If fewer than N, renormalize active weights to sum to 1.0.
    """
    recent = (
        student_submissions.sort_values("timestamp", ascending=False)
        .head(config.RECENT_SUBMISSION_COUNT)
    )
    scores = recent["incorrectness"].tolist()
    n_actual = len(scores)

    if n_actual == 0:
        return 0.0

    weights = config.RECENT_WEIGHTS[:n_actual]
    weight_sum = sum(weights)
    if weight_sum > 0:
        weights = [w / weight_sum for w in weights]

    return sum(w * s for w, s in zip(weights, scores))


# -----------------------------------------------------------------
# Classification Helpers
# -----------------------------------------------------------------

def classify_score(
    score: float,
    thresholds: list[tuple[float, float, str, str]],
) -> tuple[str, str]:
    """Return (label, color) for the matching threshold range."""
    for i, (low, high, label, color) in enumerate(thresholds):
        if i == len(thresholds) - 1:
            if low <= score <= high:
                return label, color
        else:
            if low <= score < high:
                return label, color
    return thresholds[-1][2], thresholds[-1][3]


# -----------------------------------------------------------------
# Student Struggle Score
# -----------------------------------------------------------------

def compute_student_struggle_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute struggle scores for all students in the DataFrame.
    Returns a DataFrame with one row per student.
    """
    if df.empty:
        return pd.DataFrame(columns=[
            "user", "submission_count", "time_active_min", "n_hat", "t_hat",
            "e_hat", "f_hat", "A_raw", "struggle_score", "struggle_level",
            "struggle_color", "error_rate_pct", "recent_incorrectness",
        ])

    work = df.copy()
    if "incorrectness" not in work.columns:
        work["incorrectness"] = compute_incorrectness_column(work)

    rows = []
    grouped = work.groupby("user")

    for user, group in grouped:
        n = len(group)

        # Time active (minutes from first to last submission)
        if n > 1:
            t = (group["timestamp"].max() - group["timestamp"].min()).total_seconds() / 60.0
        else:
            t = 0.0

        # Error rate: submissions with incorrectness > threshold / total
        e_hat = (group["incorrectness"] > config.CORRECT_THRESHOLD).sum() / n

        # Feedback rate: non-empty AI feedback in single pass (Bug #2 fix)
        has_feedback = group["ai_feedback"].notna() & (group["ai_feedback"].astype(str).str.strip() != "")
        f_hat = has_feedback.sum() / n

        # Recent incorrectness (A_raw)
        a_raw = compute_recent_incorrectness(group)

        rows.append({
            "user": user,
            "submission_count": n,
            "time_active_min": round(t, 2),
            "n_raw": n,
            "t_raw": t,
            "e_hat": e_hat,
            "f_hat": f_hat,
            "A_raw": a_raw,
        })

    result = pd.DataFrame(rows)

    # Min-max normalize n and t across all students
    result["n_hat"] = min_max_normalize(result["n_raw"])
    result["t_hat"] = min_max_normalize(result["t_raw"])

    # Compute S_raw
    result["struggle_score"] = (
        config.STRUGGLE_WEIGHT_N * result["n_hat"]
        + config.STRUGGLE_WEIGHT_T * result["t_hat"]
        + config.STRUGGLE_WEIGHT_E * result["e_hat"]
        + config.STRUGGLE_WEIGHT_F * result["f_hat"]
        + config.STRUGGLE_WEIGHT_A * result["A_raw"]
    ).clip(0.0, 1.0)

    # Classify
    levels_colors = result["struggle_score"].apply(
        lambda s: classify_score(s, config.STRUGGLE_THRESHOLDS)
    )
    result["struggle_level"] = levels_colors.apply(lambda x: x[0])
    result["struggle_color"] = levels_colors.apply(lambda x: x[1])

    # Convenience columns
    result["error_rate_pct"] = (result["e_hat"] * 100).round(1)
    result["recent_incorrectness"] = result["A_raw"].round(3)

    # Sort descending by score
    result = result.sort_values("struggle_score", ascending=False).reset_index(drop=True)

    return result


# -----------------------------------------------------------------
# Question Difficulty Score
# -----------------------------------------------------------------

def compute_question_difficulty_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute difficulty scores for all questions in the DataFrame.
    Returns a DataFrame with one row per question.
    """
    if df.empty:
        return pd.DataFrame(columns=[
            "question", "total_attempts", "unique_students", "avg_attempts",
            "c_tilde", "t_tilde", "a_tilde", "f_tilde",
            "difficulty_score", "difficulty_level", "difficulty_color",
            "incorrect_rate_pct",
        ])

    work = df.copy()
    if "incorrectness" not in work.columns:
        work["incorrectness"] = compute_incorrectness_column(work)

    rows = []
    grouped = work.groupby("question")

    for question, group in grouped:
        total_attempts = len(group)
        unique_students = group["user"].nunique()

        # c_tilde: incorrect rate
        correct_count = (group["incorrectness"] < config.CORRECT_THRESHOLD).sum()
        c_tilde = 1.0 - (correct_count / total_attempts) if total_attempts > 0 else 0.0

        # t_raw: avg time per student (only students with 2+ attempts)
        time_values = []
        for _user, user_group in group.groupby("user"):
            if len(user_group) >= 2:
                t_student = (
                    user_group["timestamp"].max() - user_group["timestamp"].min()
                ).total_seconds() / 60.0
                time_values.append(t_student)
        t_raw = np.mean(time_values) if time_values else 0.0

        # a_raw: avg attempts per student
        a_raw = total_attempts / unique_students if unique_students > 0 else 0.0

        # f_tilde: average incorrectness across all attempts
        f_tilde = group["incorrectness"].mean()

        rows.append({
            "question": question,
            "total_attempts": total_attempts,
            "unique_students": unique_students,
            "avg_attempts": round(a_raw, 2),
            "c_tilde": c_tilde,
            "t_raw": t_raw,
            "a_raw": a_raw,
            "f_tilde": f_tilde,
        })

    result = pd.DataFrame(rows)

    # Min-max normalize t_raw and a_raw
    result["t_tilde"] = min_max_normalize(result["t_raw"])
    result["a_tilde"] = min_max_normalize(result["a_raw"])

    # Compute D_raw
    result["difficulty_score"] = (
        config.DIFFICULTY_WEIGHT_C * result["c_tilde"]
        + config.DIFFICULTY_WEIGHT_T * result["t_tilde"]
        + config.DIFFICULTY_WEIGHT_A * result["a_tilde"]
        + config.DIFFICULTY_WEIGHT_F * result["f_tilde"]
    ).clip(0.0, 1.0)

    # Classify
    levels_colors = result["difficulty_score"].apply(
        lambda s: classify_score(s, config.DIFFICULTY_THRESHOLDS)
    )
    result["difficulty_level"] = levels_colors.apply(lambda x: x[0])
    result["difficulty_color"] = levels_colors.apply(lambda x: x[1])

    # Convenience columns
    result["incorrect_rate_pct"] = (result["c_tilde"] * 100).round(1)

    # Sort descending by score
    result = result.sort_values("difficulty_score", ascending=False).reset_index(drop=True)

    return result


# -----------------------------------------------------------------
# Temporal Smoothing (Stub — not actively used)
# -----------------------------------------------------------------

def apply_temporal_smoothing(
    s_raw: float,
    s_previous: Optional[float],
    alpha: float = config.SMOOTHING_ALPHA,
) -> float:
    """
    S_t = (1 - alpha) * S_previous + alpha * S_raw
    Returns s_raw if s_previous is None (first computation).
    """
    if s_previous is None:
        return s_raw
    return (1 - alpha) * s_previous + alpha * s_raw
