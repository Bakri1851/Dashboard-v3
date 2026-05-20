"""Phase 1 — Measurement confidence for AI-derived incorrectness scores.

Confidence formula lives in ``incorrectness.compute_feedback_confidence`` so the
struggle pipeline and this public wrapper share a single definition.
"""

import pandas as pd

from .. import config, incorrectness


def compute_incorrectness_with_confidence(df: pd.DataFrame) -> pd.DataFrame:
    """
    Wrap incorrectness.compute_incorrectness_column() and add confidence metadata.

    Returns a copy of *df* with three new columns:
        incorrectness            float [0, 1]  (identical to baseline)
        incorrectness_confidence float [0, 1]
        incorrectness_source     str           (always config.OPENAI_MODEL)
    """
    out = df.copy()
    scores = incorrectness.compute_incorrectness_column(df)
    out["incorrectness"] = scores

    feedbacks = df["ai_feedback"] if "ai_feedback" in df.columns else pd.Series("", index=df.index)
    out["incorrectness_confidence"] = incorrectness.compute_feedback_confidence(feedbacks, scores)
    out["incorrectness_source"] = config.OPENAI_MODEL
    return out
