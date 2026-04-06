"""
Phase 4 — Improved struggle model (mastery-aware, difficulty-adjusted).

Combines three signal groups:
  1. Behavioral composite  (weight 0.45)
  2. Mastery gap           (weight 0.30) — BKT mastery vs recent performance
  3. Difficulty-adjusted   (weight 0.25) — failing easy questions is worse

Graceful degradation: unavailable signal groups redistribute their weight
to the behavioral composite.
"""

from __future__ import annotations

import pandas as pd

from learning_dashboard import analytics, config


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def compute_improved_struggle_scores(
    df: pd.DataFrame,
    mastery_summary: pd.DataFrame | None = None,
    irt_difficulty: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Return a struggle DataFrame compatible with the baseline schema.

    Extra diagnostic columns: ``behavioral_composite``, ``mastery_gap``,
    ``difficulty_adjusted_score``.
    """
    _columns = [
        "user", "struggle_score", "struggle_level", "struggle_color",
        "behavioral_composite", "mastery_gap", "difficulty_adjusted_score",
    ]

    if df.empty:
        return pd.DataFrame(columns=_columns)

    work = df.copy()
    if "incorrectness" not in work.columns:
        work["incorrectness"] = analytics.compute_incorrectness_column(work)

    # --- Determine effective weights with graceful degradation ---
    w_beh = config.IMPROVED_STRUGGLE_WEIGHT_BEHAVIORAL
    w_mg = config.IMPROVED_STRUGGLE_WEIGHT_MASTERY_GAP
    w_da = config.IMPROVED_STRUGGLE_WEIGHT_DIFFICULTY_ADJ

    has_mastery = mastery_summary is not None and not mastery_summary.empty
    has_irt = irt_difficulty is not None and not irt_difficulty.empty

    if not has_mastery:
        w_beh += w_mg
        w_mg = 0.0
    if not has_irt:
        w_beh += w_da
        w_da = 0.0

    # --- Per-student behavioral signals ---
    rows: list[dict] = []
    grouped = work.groupby("user")

    for user, group in grouped:
        n = len(group)

        a_raw = analytics.compute_recent_incorrectness(group)
        d_raw = analytics._compute_slope(group)

        unique_q = group["question"].nunique()
        r_hat = 1.0 - (unique_q / n) if n > 0 else 0.0

        # Exact-answer repetition rate
        total_repeat = 0
        for _q, q_group in group.groupby("question"):
            answers = q_group.sort_values("timestamp")["student_answer"].tolist()
            seen: set[str] = set()
            for ans in answers:
                cleaned = str(ans).strip()
                if cleaned in seen:
                    total_repeat += 1
                else:
                    seen.add(cleaned)
        rep_hat = total_repeat / n if n > 0 else 0.0

        rows.append({
            "user": user,
            "n": n,
            "A_raw": a_raw,
            "d_raw": d_raw,
            "r_hat": r_hat,
            "rep_hat": rep_hat,
        })

    result = pd.DataFrame(rows)

    if result.empty:
        return pd.DataFrame(columns=_columns)

    # Min-max normalize trajectory slope across students
    result["d_hat"] = analytics.min_max_normalize(result["d_raw"])

    # Behavioral composite: equal weight across the 4 sub-signals
    result["behavioral_composite"] = (
        (result["A_raw"] + result["r_hat"] + result["d_hat"] + result["rep_hat"]) / 4.0
    ).clip(0.0, 1.0)

    # --- Mastery gap ---
    result["mastery_gap"] = 0.0
    if has_mastery:
        result = result.merge(
            mastery_summary[["user", "mean_mastery"]],
            on="user",
            how="left",
        )
        result["mean_mastery"] = result["mean_mastery"].fillna(0.0)
        # recent_performance ≈ how correct the student is recently
        recent_perf = 1.0 - result["A_raw"]
        result["mastery_gap"] = (result["mean_mastery"] - recent_perf).clip(lower=0.0)
        result.drop(columns=["mean_mastery"], inplace=True)

    # --- Difficulty-adjusted score ---
    result["difficulty_adjusted_score"] = 0.0
    if has_irt:
        result["difficulty_adjusted_score"] = _compute_difficulty_adjusted(
            work, result, irt_difficulty
        )

    # --- Weighted combination ---
    result["struggle_score"] = (
        w_beh * result["behavioral_composite"]
        + w_mg * result["mastery_gap"]
        + w_da * result["difficulty_adjusted_score"]
    ).clip(0.0, 1.0)

    # Bayesian shrinkage toward class mean
    s_mean = result["struggle_score"].mean()
    w_n = result["n"] / (result["n"] + config.SHRINKAGE_K)
    result["struggle_score"] = (
        w_n * result["struggle_score"] + (1.0 - w_n) * s_mean
    ).clip(0.0, 1.0)

    # Min-max normalize so scores spread across the full threshold range.
    # Without this, raw scores cluster in a narrow band and all students
    # land in the same category.
    result["struggle_score"] = analytics.min_max_normalize(result["struggle_score"])

    # Classify
    levels_colors = result["struggle_score"].apply(
        lambda s: analytics.classify_score(s, config.STRUGGLE_THRESHOLDS)
    )
    result["struggle_level"] = levels_colors.apply(lambda x: x[0])
    result["struggle_color"] = levels_colors.apply(lambda x: x[1])

    result = result.sort_values("struggle_score", ascending=False).reset_index(drop=True)

    return result[_columns]


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

def _compute_difficulty_adjusted(
    work: pd.DataFrame,
    result: pd.DataFrame,
    irt_difficulty: pd.DataFrame,
) -> pd.Series:
    """Per-student difficulty-adjusted score from recent submissions.

    For each student's last ``RECENT_SUBMISSION_COUNT`` submissions, compute
    ``incorrectness * (1 - normalized_irt_difficulty)`` and take the mean.
    Failing easy questions yields a higher score.
    """
    # Normalize IRT difficulty to [0, 1] across available questions
    irt_norm = irt_difficulty[["question", "irt_difficulty"]].copy()
    irt_norm["norm_diff"] = analytics.min_max_normalize(irt_norm["irt_difficulty"])

    scores: dict[str, float] = {}
    for user, group in work.groupby("user"):
        recent = (
            group.sort_values("timestamp", ascending=False)
            .head(config.RECENT_SUBMISSION_COUNT)
        )
        merged = recent.merge(irt_norm[["question", "norm_diff"]], on="question", how="left")
        merged["norm_diff"] = merged["norm_diff"].fillna(0.5)  # unknown difficulty → neutral
        vals = merged["incorrectness"] * (1.0 - merged["norm_diff"])
        scores[user] = float(vals.mean()) if len(vals) > 0 else 0.0

    return result["user"].map(scores).fillna(0.0).clip(0.0, 1.0)
