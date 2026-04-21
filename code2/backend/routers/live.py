"""Live heartbeat + struggle + difficulty leaderboards.

Endpoints:
    GET /api/live       — hero stats + 24h timeline + level-bucket counts
    GET /api/struggle   — ranked student struggle leaderboard
    GET /api/difficulty — ranked question difficulty leaderboard

All three accept `?from=<iso>&to=<iso>` to filter by submission timestamp.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends

from backend.cache import filter_df, load_active_difficulty_df, load_active_struggle_df
from backend.deps import TimeWindow, get_dataframe, get_time_window
from backend.schemas import (
    LevelBucket,
    LiveDataResponse,
    QuestionDifficulty,
    StudentStruggle,
)

router = APIRouter(tags=["live"])


# ----------------------------------------------------------------
# helpers
# ----------------------------------------------------------------


def _nunique(df: pd.DataFrame, col: str) -> int:
    return int(df[col].nunique()) if col in df.columns and not df.empty else 0


def _bucket_counts(series: pd.Series, order: list[str]) -> list[LevelBucket]:
    counts = series.value_counts().to_dict() if len(series) else {}
    return [LevelBucket(label=lbl, count=int(counts.get(lbl, 0))) for lbl in order]


def _timeline_24h(df: pd.DataFrame) -> list[int]:
    """Hourly submission counts for the last 24h (length 24).

    Always operates on the wall-clock last 24h regardless of the active filter,
    because this is a *heartbeat* chart, not a filtered aggregate."""
    if df.empty or "timestamp" not in df.columns:
        return [0] * 24
    ts = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    now = pd.Timestamp.now(tz="UTC")
    cutoff = now - pd.Timedelta(hours=24)
    recent = ts[(ts >= cutoff) & (ts <= now)].dropna()
    if recent.empty:
        return [0] * 24
    hours_ago = ((now - recent).dt.total_seconds() // 3600).astype(int)
    buckets = np.zeros(24, dtype=int)
    for h in hours_ago:
        idx = 23 - int(h)
        if 0 <= idx < 24:
            buckets[idx] += 1
    return buckets.tolist()


STRUGGLE_ORDER = ["On Track", "Minor Issues", "Struggling", "Needs Help"]
DIFFICULTY_ORDER = ["Easy", "Medium", "Hard", "Very Hard"]


# ----------------------------------------------------------------
# endpoints
# ----------------------------------------------------------------


@router.get("/live", response_model=LiveDataResponse)
def get_live(
    df: pd.DataFrame = Depends(get_dataframe),
    window: TimeWindow = Depends(get_time_window),
) -> LiveDataResponse:
    # Hero stats + buckets reflect the filter window. Timeline stays wall-clock-24h.
    working = filter_df(df, window.from_, window.to_) if window.active else df
    struggle_df = load_active_struggle_df(window.from_, window.to_)
    difficulty_df = load_active_difficulty_df(window.from_, window.to_)

    mean_inc = float(working["incorrectness"].mean()) if "incorrectness" in working.columns and not working.empty else 0.0

    return LiveDataResponse(
        records=int(len(working)),
        last_updated=datetime.now(timezone.utc).isoformat(),
        unique_students=_nunique(working, "user"),
        unique_questions=_nunique(working, "question"),
        unique_modules=_nunique(working, "module"),
        mean_incorrectness=round(mean_inc, 3),
        struggle_buckets=_bucket_counts(struggle_df.get("struggle_level", pd.Series(dtype=str)), STRUGGLE_ORDER),
        difficulty_buckets=_bucket_counts(difficulty_df.get("difficulty_level", pd.Series(dtype=str)), DIFFICULTY_ORDER),
        timeline_24h=_timeline_24h(df),
        error=None,
    )


@router.get("/struggle", response_model=list[StudentStruggle])
def get_struggle(window: TimeWindow = Depends(get_time_window)) -> list[StudentStruggle]:
    s = load_active_struggle_df(window.from_, window.to_)
    if s.empty:
        return []
    s = s.sort_values("struggle_score", ascending=False)
    out: list[StudentStruggle] = []
    for r in s.to_dict("records"):
        out.append(
            StudentStruggle(
                id=str(r["user"]),
                level=str(r.get("struggle_level", "")),
                score=float(r.get("struggle_score", 0.0)),
                submissions=int(r.get("submission_count", 0)),
                recent=float(r.get("recent_incorrectness", 0.0)),
                trend=float(-r.get("d_hat", 0.0)),
            )
        )
    return out


@router.get("/difficulty", response_model=list[QuestionDifficulty])
def get_difficulty(
    df: pd.DataFrame = Depends(get_dataframe),
    window: TimeWindow = Depends(get_time_window),
) -> list[QuestionDifficulty]:
    q = load_active_difficulty_df(window.from_, window.to_)
    if q.empty:
        return []
    q = q.sort_values("difficulty_score", ascending=False)

    # Representative module per question from the (filtered) source df.
    working = filter_df(df, window.from_, window.to_) if window.active else df
    module_lookup: dict[str, str] = {}
    if not working.empty and "question" in working.columns and "module" in working.columns:
        module_lookup = (
            working.drop_duplicates("question").set_index("question")["module"].astype(str).to_dict()
        )

    out: list[QuestionDifficulty] = []
    for r in q.to_dict("records"):
        qid = str(r["question"])
        out.append(
            QuestionDifficulty(
                id=qid,
                level=str(r.get("difficulty_level", "")),
                score=float(r.get("difficulty_score", 0.0)),
                students=int(r.get("unique_students", 0)),
                avgAttempts=float(r.get("avg_attempts", 0.0)),
                module=module_lookup.get(qid, ""),
            )
        )
    return out
