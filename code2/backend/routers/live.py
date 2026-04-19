"""Live heartbeat + struggle + difficulty leaderboards.

Endpoints:
    GET /api/live       — hero stats + 24h timeline + level-bucket counts
    GET /api/struggle   — ranked student struggle leaderboard
    GET /api/difficulty — ranked question difficulty leaderboard
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends

from backend.cache import load_difficulty_df, load_struggle_df
from backend.deps import get_dataframe
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
    """Count per-label occurrences in a series, preserving `order`."""
    counts = series.value_counts().to_dict() if len(series) else {}
    return [LevelBucket(label=lbl, count=int(counts.get(lbl, 0))) for lbl in order]


def _timeline_24h(df: pd.DataFrame) -> list[int]:
    """Hourly submission counts for the last 24h (length 24)."""
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
def get_live(df: pd.DataFrame = Depends(get_dataframe)) -> LiveDataResponse:
    struggle_df = load_struggle_df()
    difficulty_df = load_difficulty_df()

    mean_inc = float(df["incorrectness"].mean()) if "incorrectness" in df.columns and not df.empty else 0.0

    return LiveDataResponse(
        records=int(len(df)),
        last_updated=datetime.now(timezone.utc).isoformat(),
        unique_students=_nunique(df, "user"),
        unique_questions=_nunique(df, "question"),
        unique_modules=_nunique(df, "module"),
        mean_incorrectness=round(mean_inc, 3),
        struggle_buckets=_bucket_counts(struggle_df.get("struggle_level", pd.Series(dtype=str)), STRUGGLE_ORDER),
        difficulty_buckets=_bucket_counts(difficulty_df.get("difficulty_level", pd.Series(dtype=str)), DIFFICULTY_ORDER),
        timeline_24h=_timeline_24h(df),
        error=None,
    )


@router.get("/struggle", response_model=list[StudentStruggle])
def get_struggle() -> list[StudentStruggle]:
    s = load_struggle_df()
    if s.empty:
        return []
    s = s.sort_values("struggle_score", ascending=False)
    out: list[StudentStruggle] = []
    for _, r in s.iterrows():
        out.append(
            StudentStruggle(
                id=str(r["user"]),
                level=str(r.get("struggle_level", "")),
                score=float(r.get("struggle_score", 0.0)),
                submissions=int(r.get("submission_count", 0)),
                recent=float(r.get("recent_incorrectness", 0.0)),
                # d_hat is the normalised improvement slope; flip sign so that
                # negative d_hat (getting worse) reads as a negative trend.
                trend=float(-r.get("d_hat", 0.0)),
            )
        )
    return out


@router.get("/difficulty", response_model=list[QuestionDifficulty])
def get_difficulty(df: pd.DataFrame = Depends(get_dataframe)) -> list[QuestionDifficulty]:
    q = load_difficulty_df()
    if q.empty:
        return []
    q = q.sort_values("difficulty_score", ascending=False)

    # Look up one representative module per question from the source df.
    module_lookup: dict[str, str] = {}
    if not df.empty and "question" in df.columns and "module" in df.columns:
        module_lookup = (
            df.drop_duplicates("question").set_index("question")["module"].astype(str).to_dict()
        )

    out: list[QuestionDifficulty] = []
    for _, r in q.iterrows():
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
