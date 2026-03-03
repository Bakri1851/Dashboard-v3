# analytics.py — Scoring calculations (UI-independent)
import json
import math
from typing import Optional

import numpy as np
import pandas as pd
from openai import OpenAI

import config


# Incorrectness Estimation via OpenAI

_incorrectness_cache: dict[str, float] = {}


def _call_openai_batch(feedbacks: list[str]) -> list[float]:
    """
    Send a batch of feedback texts to OpenAI and return incorrectness scores [0, 1].
    Returns [0.5] * len(feedbacks) on any error.
    """
    numbered = "\n".join(f"{i + 1}. {text}" for i, text in enumerate(feedbacks))
    prompt = (
        "You are scoring student answers based on AI tutor feedback.\n"
        "For each numbered feedback text below, return a JSON array of floats "
        "from 0.0 (fully correct) to 1.0 (fully incorrect).\n"
        "Return ONLY the JSON array, nothing else.\n\n"
        f"Feedbacks:\n{numbered}"
    )
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        scores = json.loads(response.choices[0].message.content.strip())
        if isinstance(scores, list) and len(scores) == len(feedbacks):
            return [float(max(0.0, min(1.0, s))) for s in scores]
    except Exception:
        pass
    return [0.5] * len(feedbacks)


def estimate_incorrectness(feedback: Optional[str]) -> float:
    """Score a single feedback string via OpenAI. Returns float in [0, 1]."""
    if not feedback or not str(feedback).strip():
        return 0.5
    key = str(feedback).strip()
    if key not in _incorrectness_cache:
        _incorrectness_cache[key] = _call_openai_batch([key])[0]
    return _incorrectness_cache[key]


def compute_incorrectness_column(df: pd.DataFrame) -> pd.Series:
    """
    Score all ai_feedback values via OpenAI, batched for efficiency.
    Results are cached in-process to avoid repeat API calls across reruns.
    Empty/null feedback → 0.5 without an API call.
    """
    feedbacks = df["ai_feedback"].astype(str).str.strip()

    # Collect unique non-empty texts not yet cached
    uncached = [t for t in feedbacks.unique() if t and t not in _incorrectness_cache]

    # Fetch in batches
    for i in range(0, len(uncached), config.OPENAI_BATCH_SIZE):
        batch = uncached[i : i + config.OPENAI_BATCH_SIZE]
        scores = _call_openai_batch(batch)
        _incorrectness_cache.update(zip(batch, scores))

    return feedbacks.map(lambda t: _incorrectness_cache.get(t, 0.5))


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
    Last N submissions (most recent first), weighted by exponential time decay.
    w_i = exp(-lambda * delta_t_i) where delta_t_i = seconds since submission i.
    Weights are normalised to sum to 1.0.
    Falls back to equal weights if all timestamps are identical.
    """
    recent = (
        student_submissions.sort_values("timestamp", ascending=False)
        .head(config.RECENT_SUBMISSION_COUNT)
    )
    scores = recent["incorrectness"].tolist()
    n_actual = len(scores)

    if n_actual == 0:
        return 0.0

    timestamps = recent["timestamp"].tolist()
    t_now = timestamps[0]  # most recent after descending sort
    lam = math.log(2) / config.DECAY_HALFLIFE_SECONDS

    raw_weights = [
        math.exp(-lam * max(0.0, (t_now - ts).total_seconds()))
        for ts in timestamps
    ]
    weight_sum = sum(raw_weights)

    # Equal-weight fallback if all timestamps are identical (e.g. bulk import)
    if weight_sum <= 0 or all(w == raw_weights[0] for w in raw_weights):
        return sum(scores) / n_actual

    weights = [w / weight_sum for w in raw_weights]
    return sum(w * s for w, s in zip(weights, scores))


# -----------------------------------------------------------------
# Improvement Trajectory Helper
# -----------------------------------------------------------------

def _compute_slope(student_submissions: pd.DataFrame) -> float:
    """
    Linear regression slope of incorrectness vs. submission order (oldest=0).
    Positive slope = getting worse; negative = improving.
    Returns 0.0 if fewer than 2 submissions.
    """
    sorted_subs = student_submissions.sort_values("timestamp", ascending=True)
    scores = sorted_subs["incorrectness"].tolist()
    n = len(scores)
    if n < 2:
        return 0.0
    slope = np.polyfit(range(n), scores, 1)[0]
    return float(slope)


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
            "i_hat", "r_hat", "rep_hat", "A_raw", "d_hat", "struggle_score",
            "struggle_level", "struggle_color", "mean_incorrectness_pct",
            "recent_incorrectness",
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

        # Mean incorrectness: continuous gradient, no binary threshold
        i_hat = group["incorrectness"].mean()

        # Retry rate: fraction of submissions that are repeats of an already-attempted question
        unique_q = group["question"].nunique()
        r_hat = 1.0 - (unique_q / n) if n > 0 else 0.0

        # Recent incorrectness (A_raw)
        a_raw = compute_recent_incorrectness(group)

        # Improvement trajectory: linear slope of incorrectness over submission order
        d_raw = _compute_slope(group)

        # Answer repetition rate: fraction of submissions that exactly repeat
        # a previously submitted answer on the same question (exact match after strip).
        total_repeat_submissions = 0
        for _q, q_group in group.groupby("question"):
            answers = q_group.sort_values("timestamp")["student_answer"].tolist()
            seen: set[str] = set()
            for ans in answers:
                cleaned = str(ans).strip()
                if cleaned in seen:
                    total_repeat_submissions += 1
                else:
                    seen.add(cleaned)
        rep_hat = total_repeat_submissions / n if n > 0 else 0.0

        rows.append({
            "user": user,
            "submission_count": n,
            "time_active_min": round(t, 2),
            "n_raw": n,
            "t_raw": t,
            "i_hat": i_hat,
            "r_hat": r_hat,
            "A_raw": a_raw,
            "d_raw": d_raw,
            "rep_hat": rep_hat,
        })

    result = pd.DataFrame(rows)

    # Min-max normalize n, t, and trajectory slope across all students
    result["n_hat"] = min_max_normalize(result["n_raw"])
    result["t_hat"] = min_max_normalize(result["t_raw"])
    result["d_hat"] = min_max_normalize(result["d_raw"])  # positive = getting worse

    # Compute S_raw
    result["struggle_score"] = (
        config.STRUGGLE_WEIGHT_N * result["n_hat"]
        + config.STRUGGLE_WEIGHT_T * result["t_hat"]
        + config.STRUGGLE_WEIGHT_I * result["i_hat"]
        + config.STRUGGLE_WEIGHT_R * result["r_hat"]
        + config.STRUGGLE_WEIGHT_A * result["A_raw"]
        + config.STRUGGLE_WEIGHT_D * result["d_hat"]
        + config.STRUGGLE_WEIGHT_REP * result["rep_hat"]
    ).clip(0.0, 1.0)

    # Bayesian shrinkage: pull low-n scores toward the class mean to reduce noise.
    # w_n = n / (n + K) → students with few submissions are shrunk more strongly.
    s_class_mean = result["struggle_score"].mean()
    w_n = result["n_raw"] / (result["n_raw"] + config.SHRINKAGE_K)
    result["struggle_score"] = (
        w_n * result["struggle_score"] + (1 - w_n) * s_class_mean
    ).clip(0.0, 1.0)

    # Classify
    levels_colors = result["struggle_score"].apply(
        lambda s: classify_score(s, config.STRUGGLE_THRESHOLDS)
    )
    result["struggle_level"] = levels_colors.apply(lambda x: x[0])
    result["struggle_color"] = levels_colors.apply(lambda x: x[1])

    # Convenience columns
    result["mean_incorrectness_pct"] = (result["i_hat"] * 100).round(1)
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
            "c_tilde", "t_tilde", "a_tilde", "f_tilde", "p_tilde",
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

        # t_raw: avg time per student (all students; 1-attempt students contribute 0)
        time_values = []
        for _user, user_group in group.groupby("user"):
            if len(user_group) >= 2:
                t_student = (
                    user_group["timestamp"].max() - user_group["timestamp"].min()
                ).total_seconds() / 60.0
            else:
                t_student = 0.0
            time_values.append(t_student)
        t_raw = np.mean(time_values) if time_values else 0.0

        # a_raw: avg attempts per student
        a_raw = total_attempts / unique_students if unique_students > 0 else 0.0

        # f_tilde: average incorrectness across all attempts
        f_tilde = group["incorrectness"].mean()

        # p_tilde: first-attempt failure rate
        first_attempts = group.sort_values("timestamp").groupby("user").first().reset_index()
        failed_first = (first_attempts["incorrectness"] >= config.CORRECT_THRESHOLD).sum()
        p_tilde = failed_first / unique_students if unique_students > 0 else 0.0

        rows.append({
            "question": question,
            "total_attempts": total_attempts,
            "unique_students": unique_students,
            "avg_attempts": round(a_raw, 2),
            "c_tilde": c_tilde,
            "t_raw": t_raw,
            "a_raw": a_raw,
            "f_tilde": f_tilde,
            "p_tilde": p_tilde,
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
        + config.DIFFICULTY_WEIGHT_P * result["p_tilde"]
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
