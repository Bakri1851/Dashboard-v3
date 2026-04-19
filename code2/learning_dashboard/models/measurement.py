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
    # Treat common null markers and whitespace-only strings as empty.
    empty_markers = {"", "nan", "none", "null", "n/a", "na"}
    is_empty = (
        feedbacks.str.lower().isin(empty_markers)
        | df["ai_feedback"].isna()
        | scores.isna()  # L7: NaN score from upstream → no valid measurement
    )

    # Length factor: ramps linearly from 0 to 1 over MIN_LENGTH characters
    lengths = feedbacks.str.len().fillna(0).astype(float)
    length_factor = np.minimum(1.0, lengths / config.MEASUREMENT_CONFIDENCE_MIN_LENGTH)

    # Extremity factor: 0.0 at score=0.5, 1.0 at score=0 or 1.
    # By design, mid-range incorrectness produces lower confidence — we are
    # least certain about borderline answers. This is a confidence valley,
    # not a bug. Fill NaN scores with 0.5 so extremity is 0 before is_empty
    # zeroes them out below.
    safe_scores = scores.fillna(0.5)
    extremity_factor = 2.0 * np.abs(safe_scores - 0.5)

    # Combined confidence: base * length * (0.5 + 0.5 * extremity)
    # The 0.5+0.5*extremity term ensures valid feedback with mid-range scores
    # still gets at least half the base confidence rather than dropping to zero.
    confidence = (
        config.MEASUREMENT_CONFIDENCE_BASE
        * length_factor
        * (0.5 + 0.5 * extremity_factor)
    )
    confidence = np.clip(confidence, 0.0, 1.0)

    # Empty/null feedback → confidence 0.0 (the 0.5 default is a prior, not a measurement)
    confidence[is_empty] = 0.0

    out["incorrectness_confidence"] = confidence
    out["incorrectness_source"] = config.OPENAI_MODEL
    return out
