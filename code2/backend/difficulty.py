# difficulty.py — 5-signal baseline question difficulty score with within-module normalisation.
#
# Carved out of the old analytics.py during the 2026-05-20 split.
# Holds `compute_question_difficulty_scores` — the only public symbol.
#
# Depends on `incorrectness.compute_incorrectness_column` for the per-row
# scoring and on `analytics.{min_max_normalise_grouped, classify_score}`
# for the shared normalisation and band-labelling helpers.
#
# Phase 5: `compute_question_difficulty_scores` accepts an optional `weights`
# override (mirrors the pattern in struggle.py); `_load_v2_weights` reads the
# trained JSON with graceful fallback to v1.
import json
import logging
from typing import Optional

import numpy as np
import pandas as pd

from . import config
from .analytics import classify_score, min_max_normalise_grouped
from .incorrectness import compute_incorrectness_column

logger = logging.getLogger(__name__)


def _load_v2_weights() -> Optional[dict[str, float]]:
    """Read data/eval/optimised_difficulty_weights_v2.json. Returns the
    5-element weight dict or None if missing/malformed."""
    path = config.DIFFICULTY_WEIGHTS_V2_PATH
    if not path.exists():
        logger.info("v2 difficulty weights file not found at %s; falling back to v1", path)
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("v2 difficulty weights load failed (%s): %s", type(exc).__name__, exc)
        return None
    if payload.get("model_class") != "LogisticRegression":
        logger.warning(
            "v2 difficulty weights model_class=%r != LogisticRegression; refusing",
            payload.get("model_class"),
        )
        return None
    weights = payload.get("weights")
    if not isinstance(weights, dict):
        return None
    expected_keys = {"c_norm", "t_tilde", "a_tilde", "f_norm", "p_norm"}
    if not expected_keys.issubset(weights.keys()):
        logger.warning(
            "v2 difficulty weights missing keys: have %s, need %s",
            set(weights.keys()), expected_keys,
        )
        return None
    return {k: float(v) for k, v in weights.items() if k in expected_keys}


def compute_question_difficulty_scores(
    df: pd.DataFrame,
    weights: Optional[dict[str, float]] = None,
) -> pd.DataFrame:
    """
    Compute difficulty scores for all questions in the DataFrame.
    Returns a DataFrame with one row per question.

    Parameters
    ----------
    df : DataFrame of submissions to score.
    weights : optional dict with keys ``{c_norm, t_tilde, a_tilde, f_norm,
        p_norm}`` — when provided, overrides v1 ``config.DIFFICULTY_WEIGHT_*``.
        The trained v2 weights from ``_load_v2_weights()`` are passed through
        by ``cache.load_difficulty_df`` on every request (the deployed default).
        v2 weights may be negative; the .clip(0, 1) handles out-of-range.
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

    # Compute D_raw. Use v2 weights if provided, else fall back to v1 hand-set.
    if weights is None:
        w_c = config.DIFFICULTY_WEIGHT_C
        w_t = config.DIFFICULTY_WEIGHT_T
        w_a = config.DIFFICULTY_WEIGHT_A
        w_f = config.DIFFICULTY_WEIGHT_F
        w_p = config.DIFFICULTY_WEIGHT_P
    else:
        w_c = weights.get("c_norm", config.DIFFICULTY_WEIGHT_C)
        w_t = weights.get("t_tilde", config.DIFFICULTY_WEIGHT_T)
        w_a = weights.get("a_tilde", config.DIFFICULTY_WEIGHT_A)
        w_f = weights.get("f_norm", config.DIFFICULTY_WEIGHT_F)
        w_p = weights.get("p_norm", config.DIFFICULTY_WEIGHT_P)

    result["difficulty_score"] = (
        w_c * result["c_norm"]
        + w_t * result["t_tilde"]
        + w_a * result["a_tilde"]
        + w_f * result["f_norm"]
        + w_p * result["p_norm"]
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
