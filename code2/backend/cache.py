"""TTL-cached data + analytics loader for the FastAPI path.

The raw DataFrame is filter-independent (one fetch covers all time windows).
The derived struggle / difficulty tables ARE filter-dependent, so they are
keyed by `(from_iso, to_iso)` and the cache holds up to 8 distinct windows
(a reasonable upper bound for a single interactive session that flips
between "Today / Past Hour / Current Week / Custom").
"""
from __future__ import annotations

from typing import Optional

import pandas as pd
from cachetools import TTLCache, cached

from learning_dashboard import analytics, config, data_loader
from learning_dashboard.models import improved_struggle

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

# Raw-data TTL matches the Streamlit app (fresh submissions matter).
# Analytics TTL is larger — the full recompute is expensive (~2 min on 34k
# records × 203 students). A filter window can happily live for 5 minutes.
_ANALYTICS_TTL = 300  # seconds
_IMPROVED_TTL = 600   # seconds — IRT+BKT fits are the most expensive path

_df_cache: TTLCache = TTLCache(maxsize=1, ttl=config.CACHE_TTL)
# maxsize=16 covers a full day of window flips (Today / Past Hour / Current
# Week / Custom × live-session toggles) without eviction thrash.
_struggle_cache: TTLCache = TTLCache(maxsize=16, ttl=_ANALYTICS_TTL)
_difficulty_cache: TTLCache = TTLCache(maxsize=16, ttl=_ANALYTICS_TTL)
_improved_cache: TTLCache = TTLCache(maxsize=4, ttl=_IMPROVED_TTL)
# CF diagnostics derive from struggle_df + threshold; mirror the analytics TTL.
_cf_cache: TTLCache = TTLCache(maxsize=16, ttl=_ANALYTICS_TTL)


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

    # Pre-compute the incorrectness column once at load time so downstream
    # endpoints (question.py, student.py, rag.py) don't each re-derive it on
    # every request. Guarded so a missing OpenAI key / transient API failure
    # doesn't break the whole load; endpoints will recompute on demand.
    if not df.empty and "ai_feedback" in df.columns and "incorrectness" not in df.columns:
        try:
            df["incorrectness"] = analytics.compute_incorrectness_column(df)
        except Exception:
            pass

    return df, ""


def filter_df(
    df: pd.DataFrame,
    from_: Optional[str] = None,
    to_: Optional[str] = None,
) -> pd.DataFrame:
    """Slice by ISO-timestamp window. Returns the input unchanged when both
    bounds are None. Missing/unparseable timestamps are dropped when filtering."""
    if (not from_ and not to_) or df.empty or "timestamp" not in df.columns:
        return df
    ts = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    mask = ts.notna()
    if from_:
        try:
            mask &= ts >= pd.Timestamp(from_).tz_convert("UTC") if pd.Timestamp(from_).tzinfo else ts >= pd.Timestamp(from_, tz="UTC")
        except Exception:
            pass
    if to_:
        try:
            mask &= ts <= pd.Timestamp(to_).tz_convert("UTC") if pd.Timestamp(to_).tzinfo else ts <= pd.Timestamp(to_, tz="UTC")
        except Exception:
            pass
    return df[mask].copy()


def _window_key(from_: Optional[str], to_: Optional[str]) -> tuple[str, str]:
    return (from_ or "", to_ or "")


def load_struggle_df(from_: Optional[str] = None, to_: Optional[str] = None) -> pd.DataFrame:
    """Compute + cache the struggle leaderboard for the given window."""
    key = _window_key(from_, to_)
    if key in _struggle_cache:
        return _struggle_cache[key]
    df, _ = load_dataframe()
    sliced = filter_df(df, from_, to_) if (from_ or to_) else df
    result = analytics.compute_student_struggle_scores(sliced)
    _struggle_cache[key] = result
    return result


def load_difficulty_df(from_: Optional[str] = None, to_: Optional[str] = None) -> pd.DataFrame:
    """Compute + cache the difficulty leaderboard for the given window."""
    key = _window_key(from_, to_)
    if key in _difficulty_cache:
        return _difficulty_cache[key]
    df, _ = load_dataframe()
    sliced = filter_df(df, from_, to_) if (from_ or to_) else df
    result = analytics.compute_question_difficulty_scores(sliced)
    _difficulty_cache[key] = result
    return result


def load_improved_struggle_df(
    from_: Optional[str] = None, to_: Optional[str] = None
) -> pd.DataFrame:
    """Compute + cache improved (IRT + BKT) struggle scores for the window.

    The underlying fit is the most expensive path in the app — cache hits save
    tens of seconds per repeat visit to the Model Comparison view."""
    key = _window_key(from_, to_)
    if key in _improved_cache:
        return _improved_cache[key]
    df, _ = load_dataframe()
    sliced = filter_df(df, from_, to_) if (from_ or to_) else df
    try:
        result = improved_struggle.compute_improved_struggle_scores(sliced)
    except Exception:
        result = pd.DataFrame()
    _improved_cache[key] = result
    return result


def invalidate() -> None:
    """Drop all caches — called by POST endpoints that mutate settings/weights."""
    _df_cache.clear()
    _struggle_cache.clear()
    _difficulty_cache.clear()
    _improved_cache.clear()
    _cf_cache.clear()
