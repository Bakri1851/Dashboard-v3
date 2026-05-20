# analytics.py — shared scoring utilities (UI-independent).
#
# This file used to hold every scoring concern under one roof. During the
# 2026-05-20 split it was carved into five per-concern modules — each now
# imports from this file only for the genuinely shared helpers below:
#
#   incorrectness.py — OpenAI scoring + persistent cache + feedback confidence
#   struggle.py      — 7-signal student struggle + Bayesian shrinkage
#   difficulty.py    — 5-signal question difficulty
#   collab.py        — collaborative-filtering similar-students lookup
#   clustering.py    — TF-IDF + KMeans mistake clustering
#
# What stays here:
#   _get_openai_client       — shared OpenAI client factory (also imported by
#                              rag.py and clustering.py)
#   min_max_normalize        — clamped [0, 1] normalisation; used by struggle
#                              and improved_struggle
#   min_max_normalize_grouped — within-group variant; used by difficulty
#   classify_score           — threshold-band lookup; used by struggle,
#                              difficulty, irt
#   apply_temporal_smoothing — EWMA smoother kept for completeness; not on
#                              any current hot path
import os
from typing import Optional

import pandas as pd
from openai import OpenAI

from . import config


def _get_openai_client() -> OpenAI:
    # Key is sourced from OPENAI_API_KEY in the environment. backend/main.py
    # lifts it out of .secrets/secrets.toml at FastAPI boot.
    key = os.environ.get("OPENAI_API_KEY", "")
    return OpenAI(api_key=key, max_retries=1, timeout=20.0)


# Min-Max Normalization

def min_max_normalize(series: pd.Series) -> pd.Series:
    """(x - min) / (max - min), clamped to [0, 1].

    Returns 0.5 if min == max — the neutral midpoint preserves the feature's
    weight contribution in composite sums when the cohort is degenerate
    (e.g. all students have A_raw=0). Rankings are unchanged either way.
    """
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series(0.5, index=series.index)
    result = (series - min_val) / (max_val - min_val)
    return result.clip(0.0, 1.0)


def min_max_normalize_grouped(
    series: pd.Series,
    groups: Optional[pd.Series],
) -> pd.Series:
    """Min-max normalise within each group label.

    Different modules have different difficulty/workload distributions — a
    CS student's time-on-task is not commensurable with a maths student's.
    Grouping by module before normalisation keeps the rankings meaningful
    when the global leaderboard mixes cohorts.

    A single-group input (or ``groups=None``) is equivalent to
    ``min_max_normalize``. Groups of size 1 or with all-equal values
    return 0.5 for each member (same semantics as the ungrouped helper).
    """
    if groups is None:
        return min_max_normalize(series)
    groups = groups.reindex(series.index)
    out = pd.Series(0.5, index=series.index, dtype=float)
    for _label, idx in groups.groupby(groups, dropna=False).groups.items():
        sub = series.loc[idx]
        out.loc[idx] = min_max_normalize(sub).values
    return out


# Classification Helpers

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


# Temporal Smoothing (Stub — not actively used)

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
