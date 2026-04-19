"""TTL-cached data + analytics loader for the FastAPI path.

The raw DataFrame and the derived struggle / difficulty tables are all cached
with the same TTL so the expensive fetch + analytics pass only runs once per
window, not on every endpoint call.
"""
from __future__ import annotations

import pandas as pd
from cachetools import TTLCache, cached

from learning_dashboard import analytics, config, data_loader

_EMPTY_DF = pd.DataFrame(
    columns=[
        "module",
        "question",
        "timestamp",
        "student_answer",
        "ai_feedback",
        "session",
        "user",
    ]
)

# Raw data TTL matches the Streamlit app (fresh submissions matter for pollers).
# Analytics outputs get a much longer TTL because a full recompute takes ~2 min
# on 34k records × 203 students — users wait < 250 ms inside the window.
_ANALYTICS_TTL = 300  # seconds

_df_cache: TTLCache = TTLCache(maxsize=1, ttl=config.CACHE_TTL)
_struggle_cache: TTLCache = TTLCache(maxsize=1, ttl=_ANALYTICS_TTL)
_difficulty_cache: TTLCache = TTLCache(maxsize=1, ttl=_ANALYTICS_TTL)


@cached(_df_cache)
def load_dataframe() -> tuple[pd.DataFrame, str]:
    """Fetch + parse + normalise raw API data. Returns (df, error_msg)."""
    try:
        raw = data_loader.fetch_raw_data_uncached()
    except Exception as e:
        return _EMPTY_DF.copy(), f"API connection failed: {type(e).__name__} - {e}"

    fmt = data_loader.detect_format(raw)
    if fmt == "json":
        try:
            records = data_loader.parse_json_response(raw)
        except Exception as json_error:
            try:
                records = data_loader.parse_xml_response(raw)
            except Exception as xml_error:
                return (
                    _EMPTY_DF.copy(),
                    "Unable to parse API response as JSON or XML: "
                    f"{type(json_error).__name__}, {type(xml_error).__name__}",
                )
    else:
        try:
            records = data_loader.parse_xml_response(raw)
        except Exception as e:
            return _EMPTY_DF.copy(), f"XML parse failed: {type(e).__name__} - {e}"

    df = data_loader.normalize_and_clean(records)
    return df, ""


@cached(_struggle_cache)
def load_struggle_df() -> pd.DataFrame:
    """Compute + cache the full struggle leaderboard."""
    df, _ = load_dataframe()
    return analytics.compute_student_struggle_scores(df)


@cached(_difficulty_cache)
def load_difficulty_df() -> pd.DataFrame:
    """Compute + cache the full difficulty leaderboard."""
    df, _ = load_dataframe()
    return analytics.compute_question_difficulty_scores(df)


def invalidate() -> None:
    """Drop all caches — used by POST endpoints that mutate state."""
    _df_cache.clear()
    _struggle_cache.clear()
    _difficulty_cache.clear()
