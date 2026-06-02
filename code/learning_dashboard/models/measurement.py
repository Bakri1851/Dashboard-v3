"""Phase 1 — Measurement confidence for AI-derived incorrectness scores."""

import numpy as np
import pandas as pd

from learning_dashboard import analytics, config


def compute_incorrectness_with_confidence(df: pd.DataFrame) -> pd.DataFrame:
    """
    Wrap analytics.compute_incorrectness_column() and add confidence metadata.

    Returns a copy of *df* with three new columns:
        incorrectness            float [0, 1]  (identical to baseline)
        incorrectness_confidence float [0, 1]
        incorrectness_source     str           (always config.OPENAI_MODEL)
    """
    out = df.copy()
    scores = analytics.compute_incorrectness_column(df)
    out["incorrectness"] = scores

    feedbacks = df["ai_feedback"].astype(str).str.strip()
    empty_markers = {"", "nan", "none", "null", "n/a", "na"}
    is_empty = (
        feedbacks.str.lower().isin(empty_markers)
        | df["ai_feedback"].isna()
        | scores.isna()
    )

    lengths = feedbacks.str.len().fillna(0).astype(float)
    length_factor = np.minimum(1.0, lengths / config.MEASUREMENT_CONFIDENCE_MIN_LENGTH)

    safe_scores = scores.fillna(0.5)
    extremity_factor = 2.0 * np.abs(safe_scores - 0.5)

    confidence = (
        config.MEASUREMENT_CONFIDENCE_BASE
        * length_factor
        * (0.5 + 0.5 * extremity_factor)
    )
    confidence = np.clip(confidence, 0.0, 1.0)

    confidence[is_empty] = 0.0

    out["incorrectness_confidence"] = confidence
    out["incorrectness_source"] = config.OPENAI_MODEL
    return out
