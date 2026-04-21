"""GET / POST / DELETE `/api/settings`.

`GET` returns the immutable config snapshot (weights, thresholds) alongside
the live runtime flags (sounds, CF, auto-refresh, model selectors, BKT params).
`POST` merges a partial dict into `runtime_config` and invalidates the
analytics caches so the next request recomputes with the new flags.
`POST /reset` reverts to defaults.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend import cache as backend_cache, runtime_config
from backend.schemas import (
    BKTParameters,
    DifficultyWeights,
    RuntimeSettings,
    Settings,
    StruggleWeights,
    Thresholds,
)
from learning_dashboard import config

router = APIRouter(tags=["settings"])


def _to_runtime_settings(rc: runtime_config.RuntimeConfig) -> RuntimeSettings:
    return RuntimeSettings(
        sounds_enabled=rc.sounds_enabled,
        auto_refresh=rc.auto_refresh,
        refresh_interval=rc.refresh_interval,
        cf_enabled=rc.cf_enabled,
        cf_threshold=rc.cf_threshold,
        struggle_model=rc.struggle_model,
        difficulty_model=rc.difficulty_model,
        bkt=BKTParameters(
            p_init=rc.bkt_p_init,
            p_learn=rc.bkt_p_learn,
            p_guess=rc.bkt_p_guess,
            p_slip=rc.bkt_p_slip,
            mastery_threshold=rc.bkt_mastery_threshold,
        ),
    )


def _build_settings() -> Settings:
    rc = runtime_config.get()
    return Settings(
        cache_ttl=config.CACHE_TTL,
        correct_threshold=config.CORRECT_THRESHOLD,
        smoothing_alpha=config.SMOOTHING_ALPHA,
        struggle_weights=StruggleWeights(
            n=config.STRUGGLE_WEIGHT_N,
            t=config.STRUGGLE_WEIGHT_T,
            i=config.STRUGGLE_WEIGHT_I,
            r=config.STRUGGLE_WEIGHT_R,
            a=config.STRUGGLE_WEIGHT_A,
            d=config.STRUGGLE_WEIGHT_D,
            rep=config.STRUGGLE_WEIGHT_REP,
        ),
        difficulty_weights=DifficultyWeights(
            c=config.DIFFICULTY_WEIGHT_C,
            t=config.DIFFICULTY_WEIGHT_T,
            a=config.DIFFICULTY_WEIGHT_A,
            f=config.DIFFICULTY_WEIGHT_F,
            p=config.DIFFICULTY_WEIGHT_P,
        ),
        thresholds=Thresholds(
            struggle=config.STRUGGLE_THRESHOLDS,
            difficulty=config.DIFFICULTY_THRESHOLDS,
        ),
        bkt=BKTParameters(
            p_init=rc.bkt_p_init,
            p_learn=rc.bkt_p_learn,
            p_guess=rc.bkt_p_guess,
            p_slip=rc.bkt_p_slip,
            mastery_threshold=rc.bkt_mastery_threshold,
        ),
        leaderboard_max_items=config.LEADERBOARD_MAX_ITEMS,
        runtime=_to_runtime_settings(rc),
    )


@router.get("/settings", response_model=Settings)
def get_settings() -> Settings:
    return _build_settings()


@router.post("/settings", response_model=Settings)
def post_settings(partial: dict[str, Any]) -> Settings:
    """Accept any subset of runtime keys. Ignores unknown fields silently.

    Flushes analytics caches on every update so the next `/api/live`,
    `/api/struggle`, etc. reflects the new flags (BKT params, model choice,
    CF threshold, etc. — any of which can change leaderboard output).
    """
    runtime_config.update(partial)
    backend_cache.invalidate()
    return _build_settings()


@router.post("/settings/reset", response_model=Settings)
def reset_settings() -> Settings:
    runtime_config.reset()
    backend_cache.invalidate()
    return _build_settings()
