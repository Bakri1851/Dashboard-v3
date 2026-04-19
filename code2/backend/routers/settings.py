"""GET /api/settings — expose the current backend tuning constants (read-only).

POST support is deliberately not implemented yet: mutating weights live would
invalidate the 5-min analytics cache on every request and produce confusing
comparisons. For the defence demo, Settings is a visible inventory of the
configuration rather than a live control panel.
"""
from __future__ import annotations

from fastapi import APIRouter

from backend.schemas import (
    BKTParameters,
    DifficultyWeights,
    Settings,
    StruggleWeights,
    Thresholds,
)
from learning_dashboard import config

router = APIRouter(tags=["settings"])


@router.get("/settings", response_model=Settings)
def get_settings() -> Settings:
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
            p_init=config.BKT_P_INIT,
            p_learn=config.BKT_P_LEARN,
            p_guess=config.BKT_P_GUESS,
            p_slip=config.BKT_P_SLIP,
            mastery_threshold=config.BKT_MASTERY_THRESHOLD,
        ),
        leaderboard_max_items=config.LEADERBOARD_MAX_ITEMS,
    )
