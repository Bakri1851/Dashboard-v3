"""TTL-cached data + analytics loader for the FastAPI path.

The raw DataFrame is filter-independent (one fetch covers all time windows).
The derived struggle / difficulty tables ARE filter-dependent, so they are
keyed by `(from_iso, to_iso)` and the cache holds up to 8 distinct windows
(a reasonable upper bound for a single interactive session that flips
between "Today / Past Hour / Current Week / Custom").
"""
from __future__ import annotations

import logging
import threading
from typing import Optional

import pandas as pd
from cachetools import TTLCache

from backend import config, data_loader, difficulty, incorrectness, lab_classes, struggle
from backend.models import bkt, improved_struggle, irt

logger = logging.getLogger("backend.cache")

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

_ANALYTICS_TTL = 900  # seconds
_IMPROVED_TTL = 600   # seconds

_df_cache: TTLCache = TTLCache(maxsize=1, ttl=config.CACHE_TTL)
_struggle_cache: TTLCache = TTLCache(maxsize=16, ttl=_ANALYTICS_TTL)
_difficulty_cache: TTLCache = TTLCache(maxsize=16, ttl=_ANALYTICS_TTL)
_improved_cache: TTLCache = TTLCache(maxsize=4, ttl=_IMPROVED_TTL)
_irt_difficulty_cache: TTLCache = TTLCache(maxsize=4, ttl=_IMPROVED_TTL)
_cf_cache: TTLCache = TTLCache(maxsize=16, ttl=_ANALYTICS_TTL)

_df_lock = threading.Lock()
_struggle_lock = threading.Lock()
_difficulty_lock = threading.Lock()
_improved_lock = threading.Lock()
_irt_difficulty_lock = threading.Lock()


def load_dataframe() -> tuple[pd.DataFrame, str]:
    """Fetch + parse + normalise raw API data. Returns (df, error_msg)."""
    cached = _df_cache.get("df")
    if cached is not None:
        return cached
    with _df_lock:
        cached = _df_cache.get("df")
        if cached is not None:
            return cached
        result = _load_dataframe_uncached()
        _df_cache["df"] = result
        return result


def _load_dataframe_uncached() -> tuple[pd.DataFrame, str]:
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

    df = data_loader.normalise_and_clean(records)

    if not df.empty:
        try:
            df = lab_classes.tag_records(df)
        except Exception as e:
            logger.warning("lab_classes.tag_records raised: %s", e)

    if not df.empty and "ai_feedback" in df.columns and "incorrectness" not in df.columns:
        try:
            df["incorrectness"] = incorrectness.compute_incorrectness_column(df, score_new=False)
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


def _window_key(
    from_: Optional[str], to_: Optional[str], module: Optional[str] = None
) -> tuple[str, str, str]:
    return (from_ or "", to_ or "", module or "")


def _slice_df(
    df: pd.DataFrame,
    from_: Optional[str],
    to_: Optional[str],
    module: Optional[str],
) -> pd.DataFrame:
    """Apply time + module filters in order. Either may be None."""
    out = filter_df(df, from_, to_) if (from_ or to_) else df
    if module:
        out = data_loader.filter_by_module(out, module)
    return out


def load_struggle_df(
    from_: Optional[str] = None,
    to_: Optional[str] = None,
    module: Optional[str] = None,
) -> pd.DataFrame:
    """Compute + cache the struggle leaderboard for the given window + module.

    Uses the trained v2 weights + the runtime shrinkage_k (seeded from the
    Optuna-tuned v2 value) unconditionally — the trained model is the deployed
    system. The hand-set v1 weights survive only as `config.py` constants for
    the offline evaluation comparison.
    """
    from backend import runtime_config as _rc_mod

    rc = _rc_mod.get()
    key = _window_key(from_, to_, module)
    if key in _struggle_cache:
        return _struggle_cache[key]
    with _struggle_lock:
        if key in _struggle_cache:
            return _struggle_cache[key]
        df, _ = load_dataframe()
        sliced = _slice_df(df, from_, to_, module)
        weights = struggle._load_v2_weights()
        result = struggle.compute_student_struggle_scores(
            sliced, weights=weights, shrinkage_k=rc.shrinkage_k
        )
        _struggle_cache[key] = result
        return result


def load_difficulty_df(
    from_: Optional[str] = None,
    to_: Optional[str] = None,
    module: Optional[str] = None,
) -> pd.DataFrame:
    """Compute + cache the difficulty leaderboard for the given window + module.

    Uses the trained v2 weights unconditionally — the trained model is the
    deployed system. The hand-set v1 weights survive only as `config.py`
    constants for the offline evaluation comparison.
    """
    key = _window_key(from_, to_, module)
    if key in _difficulty_cache:
        return _difficulty_cache[key]
    with _difficulty_lock:
        if key in _difficulty_cache:
            return _difficulty_cache[key]
        df, _ = load_dataframe()
        sliced = _slice_df(df, from_, to_, module)
        weights = difficulty._load_v2_weights()
        result = difficulty.compute_question_difficulty_scores(sliced, weights=weights)
        _difficulty_cache[key] = result
        return result


def load_improved_struggle_df(
    from_: Optional[str] = None,
    to_: Optional[str] = None,
    module: Optional[str] = None,
) -> pd.DataFrame:
    """Compute + cache improved (IRT + BKT) struggle scores for the window.

    BKT mastery is computed inline with the runtime-configured parameters so
    that the Settings sliders (p_init, p_learn, p_guess, p_slip) actually
    shape the output. The cache key is the window only — runtime-param
    changes go through `POST /api/settings` which calls `invalidate()`."""
    from backend import runtime_config as _rc_mod

    key = _window_key(from_, to_, module)
    if key in _improved_cache:
        return _improved_cache[key]
    with _improved_lock:
        if key in _improved_cache:
            return _improved_cache[key]
        df, _ = load_dataframe()
        sliced = _slice_df(df, from_, to_, module)
        rc = _rc_mod.get()
        at_defaults = (
            rc.bkt_p_init == config.BKT_P_INIT
            and rc.bkt_p_learn == config.BKT_P_LEARN
            and rc.bkt_p_guess == config.BKT_P_GUESS
            and rc.bkt_p_slip == config.BKT_P_SLIP
        )
        per_skill = bkt.get_fitted_params() if at_defaults else None
        mix_weights = improved_struggle._load_v2_weights()
        try:
            mastery_df = bkt.compute_all_mastery(
                sliced,
                p_init=rc.bkt_p_init,
                p_learn=rc.bkt_p_learn,
                p_guess=rc.bkt_p_guess,
                p_slip=rc.bkt_p_slip,
                per_skill_params=per_skill,
            )
            mastery_summary = (
                bkt.compute_student_mastery_summary(mastery_df)
                if not mastery_df.empty
                else None
            )
            irt_model = load_irt_model(from_, to_, module)
            irt_diff_full = irt_model.get("difficulty_df", pd.DataFrame())
            irt_ability = irt_model.get("ability_df", pd.DataFrame())
            result = improved_struggle.compute_improved_struggle_scores(
                sliced,
                mastery_summary=mastery_summary,
                irt_difficulty=irt_diff_full if not irt_diff_full.empty else None,
                irt_ability=irt_ability if not irt_ability.empty else None,
                mix_weights=mix_weights,
            )
        except Exception:
            logger.warning(
                "improved_struggle.compute_improved_struggle_scores failed for "
                "window=(%s, %s) rows=%d — caching empty result",
                from_, to_, len(sliced),
                exc_info=True,
            )
            result = pd.DataFrame()
        _improved_cache[key] = result
        return result


def load_irt_model(
    from_: Optional[str] = None,
    to_: Optional[str] = None,
    module: Optional[str] = None,
) -> dict:
    """Compute + cache the full IRT fit (difficulty + discrimination + ability).

    Caches under the same window key as ``load_irt_difficulty_df`` so a
    back-to-back ``difficulty`` and ``abilities`` lookup only fits once.
    """
    key = _window_key(from_, to_, module)
    cached = _irt_difficulty_cache.get(key)
    if isinstance(cached, dict):
        return cached
    with _irt_difficulty_lock:
        cached = _irt_difficulty_cache.get(key)
        if isinstance(cached, dict):
            return cached
        df, _ = load_dataframe()
        sliced = _slice_df(df, from_, to_, module)
        try:
            model = irt.compute_irt_model(sliced)
        except Exception:
            logger.warning(
                "irt.compute_irt_model failed for window=(%s, %s) rows=%d — "
                "caching empty result",
                from_, to_, len(sliced),
                exc_info=True,
            )
            model = {
                "difficulty_df": pd.DataFrame(),
                "ability_df": pd.DataFrame(columns=["user", "theta"]),
                "convergence": False,
                "log_likelihood": 0.0,
            }
        if model["difficulty_df"].empty:
            logger.info(
                "IRT fit returned empty for window=(%s, %s) rows=%d — likely "
                "too few eligible attempts after min-count + separation filter.",
                from_, to_, len(sliced),
            )
        _irt_difficulty_cache[key] = model
        return model


def load_irt_difficulty_df(
    from_: Optional[str] = None,
    to_: Optional[str] = None,
    module: Optional[str] = None,
) -> pd.DataFrame:
    """Compute + cache IRT question-difficulty scores for the window.

    Projection of ``load_irt_model`` — returns only the question-level df
    with the public ``_OUTPUT_COLUMNS`` schema (drops the internal b_raw).
    """
    model = load_irt_model(from_, to_, module)
    diff = model.get("difficulty_df", pd.DataFrame())
    if diff.empty:
        return pd.DataFrame()
    cols = [c for c in diff.columns if c != "b_raw"]
    return diff[cols].copy()


def load_irt_ability_df(
    from_: Optional[str] = None,
    to_: Optional[str] = None,
    module: Optional[str] = None,
) -> pd.DataFrame:
    """Per-student θ for the window. Shares the cache with load_irt_model."""
    return load_irt_model(from_, to_, module).get("ability_df", pd.DataFrame())


def load_active_struggle_df(
    from_: Optional[str] = None,
    to_: Optional[str] = None,
    module: Optional[str] = None,
) -> pd.DataFrame:
    """Return the struggle leaderboard for the currently-selected model.

    Dispatches on `runtime_config.struggle_model`:
      - "improved": BKT-mastery + IRT-weighted struggle (honours BKT sliders)
      - anything else: baseline behavioural composite

    When improved is active, baseline's ancillary columns
    (`submission_count`, `recent_incorrectness`, `d_hat`, `n_hat`, `t_hat`,
    etc.) are merged onto each user so downstream endpoints see a single
    superset schema regardless of model — `struggle_score`/`struggle_level`
    come from improved, row-level diagnostics from baseline. Ordering is
    preserved from the improved result (score desc).

    Graceful fallback: if the improved fit returns empty (sparse data,
    single-class outcomes), fall through to the baseline so downstream
    endpoints never see an empty leaderboard when data exists.
    """
    from backend import runtime_config as _rc_mod

    if _rc_mod.get().struggle_model == "improved":
        improved_df = load_improved_struggle_df(from_, to_, module)
        if not improved_df.empty:
            baseline_df = load_struggle_df(from_, to_, module)
            if not baseline_df.empty and "user" in baseline_df.columns:
                ancillary = [
                    c for c in baseline_df.columns
                    if c not in improved_df.columns and c != "user"
                ]
                if ancillary:
                    improved_df = improved_df.merge(
                        baseline_df[["user"] + ancillary],
                        on="user",
                        how="left",
                    )
            return improved_df
    return load_struggle_df(from_, to_, module)


def load_active_difficulty_df(
    from_: Optional[str] = None,
    to_: Optional[str] = None,
    module: Optional[str] = None,
) -> pd.DataFrame:
    """Return the difficulty leaderboard for the currently-selected model.

    Dispatches on `runtime_config.difficulty_model`:
      - "irt": Rasch 1PL b_i estimates (column-renamed to the baseline schema)
      - anything else: baseline behavioural composite
    The column-rename keeps callers (live.py, student.py) agnostic to which
    model produced the row — they always read `difficulty_score` /
    `difficulty_level`.
    """
    from backend import runtime_config as _rc_mod

    if _rc_mod.get().difficulty_model == "irt":
        df = load_irt_difficulty_df(from_, to_, module)
        if not df.empty and "irt_difficulty" in df.columns:
            return df.rename(
                columns={
                    "irt_difficulty": "difficulty_score",
                    "irt_difficulty_level": "difficulty_level",
                }
            )
    return load_difficulty_df(from_, to_, module)


def invalidate() -> None:
    """Drop all caches — called by POST endpoints that mutate settings/weights."""
    _df_cache.clear()
    _struggle_cache.clear()
    _difficulty_cache.clear()
    _improved_cache.clear()
    _irt_difficulty_cache.clear()
    _cf_cache.clear()
    try:
        from backend.routers import analysis as _analysis_router
        _analysis_router.invalidate()
    except Exception:
        pass
    try:
        from backend.routers import rag as _rag_router
        _rag_router.invalidate()
    except Exception:
        pass
