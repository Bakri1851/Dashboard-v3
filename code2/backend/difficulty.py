# difficulty.py — 5-signal baseline question difficulty score with within-module normalisation.
#
# Carved out of the old analytics.py during the 2026-05-20 split.
# Holds `compute_question_difficulty_scores` — the only public symbol.
#
# Depends on `incorrectness.compute_incorrectness_column` for the per-row
# scoring and on `analytics.{min_max_normalise_grouped, classify_score}`
# for the shared normalisation and band-labelling helpers.
import numpy as np
import pandas as pd

from . import config
from .analytics import classify_score, min_max_normalise_grouped
from .incorrectness import compute_incorrectness_column


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

        # Module attribution: questions belong to exactly one module, so
        # group["module"].iloc[0] is canonical. Used for within-module
        # normalisation — see compute_student_struggle_scores.
        if "module" in group.columns:
            question_module = str(group["module"].iloc[0]) if len(group) else ""
        else:
            question_module = ""

        rows.append({
            "question": question,
            "module": question_module,
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

    # Min-max normalise every composite input so configured weights match
    # effective weights. Raw rates (c_tilde, f_tilde, p_tilde) are retained
    # for display (incorrect_rate_pct); _norm columns feed the weighted sum.
    # Grouped by module — a "hard" CS question is not commensurable with a
    # "hard" maths question when both appear on the global leaderboard.
    modules = result["module"] if "module" in result.columns else None
    result["t_tilde"] = min_max_normalise_grouped(result["t_raw"], modules)
    result["a_tilde"] = min_max_normalise_grouped(result["a_raw"], modules)
    result["c_norm"] = min_max_normalise_grouped(result["c_tilde"], modules)
    result["f_norm"] = min_max_normalise_grouped(result["f_tilde"], modules)
    result["p_norm"] = min_max_normalise_grouped(result["p_tilde"], modules)

    # Compute D_raw
    result["difficulty_score"] = (
        config.DIFFICULTY_WEIGHT_C * result["c_norm"]
        + config.DIFFICULTY_WEIGHT_T * result["t_tilde"]
        + config.DIFFICULTY_WEIGHT_A * result["a_tilde"]
        + config.DIFFICULTY_WEIGHT_F * result["f_norm"]
        + config.DIFFICULTY_WEIGHT_P * result["p_norm"]
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
