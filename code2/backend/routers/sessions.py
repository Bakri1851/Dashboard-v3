"""Sessions router — GET list, POST save (retroactive), DELETE by id,
GET progression.

`POST /api/sessions/save` builds a session record from the current time-
filter window (supplied by the frontend) and delegates to
`data_loader.save_session_record`.

`DELETE /api/sessions/{id}` delegates to `data_loader.delete_session_record`.

`GET /api/sessions/{id}/progression` replays the session as a series of
time-bucket snapshots so the frontend can show how it evolved — not just
the end state.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.cache import filter_df, load_dataframe
from backend.schemas import (
    LevelBucket,
    ProgressionPoint,
    SavedSession,
    SessionProgression,
)
from learning_dashboard import analytics, data_loader

router = APIRouter(tags=["sessions"])

STRUGGLE_ORDER = ["On Track", "Minor Issues", "Struggling", "Needs Help"]
DIFFICULTY_ORDER = ["Easy", "Medium", "Hard", "Very Hard"]


class SaveSessionRequest(BaseModel):
    name: str
    start_time: str      # ISO-8601
    end_time: str        # ISO-8601
    module_filter: str | None = None
    dashboard_view: str | None = None
    time_filter_preset: str | None = None


def _parse_dt(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None


def _as_saved_session(r: dict) -> SavedSession:
    start = _parse_dt(r.get("start_time") or r.get("start"))
    end = _parse_dt(r.get("end_time") or r.get("end"))
    duration = None
    if start and end:
        duration = max(0.0, (end - start).total_seconds() / 60.0)
    return SavedSession(
        id=str(r.get("id", "")),
        name=str(r.get("name", "Untitled session")),
        start_time=start.isoformat() if start else None,
        end_time=end.isoformat() if end else None,
        duration_minutes=duration,
        students=r.get("students") or r.get("student_count"),
        flagged=r.get("flagged") or r.get("needs_help_count"),
        module_filter=r.get("secondary_module_filter") or r.get("module_filter"),
    )


@router.get("/sessions", response_model=list[SavedSession])
def list_sessions() -> list[SavedSession]:
    raw = data_loader.load_saved_sessions()
    return [_as_saved_session(r) for r in raw if isinstance(r, dict)]


@router.post("/sessions/save", response_model=SavedSession)
def save_session(req: SaveSessionRequest) -> SavedSession:
    """Retroactive save — builds a record from the frontend's current filter
    window and persists it through `data_loader.save_session_record`."""
    record = {
        "id": uuid.uuid4().hex,
        "name": req.name,
        "start_time": req.start_time,
        "end_time": req.end_time,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "dashboard_view": req.dashboard_view or "In Class View",
        "secondary_module_filter": req.module_filter or "All",
        "time_filter_preset": req.time_filter_preset or "Custom",
    }
    try:
        data_loader.save_session_record(record)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Save failed: {type(e).__name__} - {e}")
    return _as_saved_session(record)


@router.delete("/sessions/{session_id}", response_model=list[SavedSession])
def delete_session(session_id: str) -> list[SavedSession]:
    ok = data_loader.delete_session_record(session_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Session {session_id!r} not found.")
    return list_sessions()


def _find_session(session_id: str) -> dict:
    for r in data_loader.load_saved_sessions():
        if isinstance(r, dict) and str(r.get("id", "")) == session_id:
            return r
    raise HTTPException(status_code=404, detail=f"Session {session_id!r} not found.")


def _bucket_counts(series: pd.Series, order: list[str]) -> list[LevelBucket]:
    counts = series.value_counts().to_dict() if len(series) else {}
    return [LevelBucket(label=lbl, count=int(counts.get(lbl, 0))) for lbl in order]


@router.get("/sessions/{session_id}/progression", response_model=SessionProgression)
def get_session_progression(
    session_id: str,
    buckets: int = Query(default=20, ge=3, le=60, description="Number of time buckets to generate."),
) -> SessionProgression:
    """Replay a saved session as `buckets` time-bucket snapshots.

    Each snapshot is the analytics state as of that bucket's end time — i.e.
    the struggle and difficulty leaderboards computed over all submissions
    up to `t_end`. The frontend draws the stacked-area progression from
    this series.
    """
    record = _find_session(session_id)
    session_meta = _as_saved_session(record)

    start = _parse_dt(record.get("start_time"))
    end = _parse_dt(record.get("end_time"))
    if start is None or end is None or end <= start:
        raise HTTPException(
            status_code=400,
            detail="Session has invalid or missing start/end timestamps.",
        )

    df, err = load_dataframe()
    if df.empty:
        raise HTTPException(status_code=503, detail=err or "No data available.")

    window_df = filter_df(df, start.isoformat(), end.isoformat())
    if window_df.empty or "timestamp" not in window_df.columns:
        return SessionProgression(session=session_meta, bucket_minutes=0.0, points=[])

    duration_s = (end - start).total_seconds()
    bucket_s = max(duration_s / buckets, 60.0)  # never finer than 1 minute
    bucket_minutes = round(bucket_s / 60.0, 2)

    ts = pd.to_datetime(window_df["timestamp"], errors="coerce", utc=True)
    working = window_df.assign(_ts=ts).dropna(subset=["_ts"])
    start_utc = pd.Timestamp(start).tz_convert("UTC") if pd.Timestamp(start).tzinfo else pd.Timestamp(start, tz="UTC")

    points: list[ProgressionPoint] = []
    for i in range(1, buckets + 1):
        t_end = start_utc + pd.Timedelta(seconds=bucket_s * i)
        slice_df = working[working["_ts"] <= t_end].drop(columns=["_ts"])
        if slice_df.empty:
            points.append(
                ProgressionPoint(
                    t_end=t_end.isoformat(),
                    cumulative_submissions=0,
                    cumulative_students=0,
                    mean_incorrectness=0.0,
                    struggle_buckets=[LevelBucket(label=lbl, count=0) for lbl in STRUGGLE_ORDER],
                    difficulty_buckets=[LevelBucket(label=lbl, count=0) for lbl in DIFFICULTY_ORDER],
                    needs_help_ids=[],
                )
            )
            continue

        try:
            struggle_df = analytics.compute_student_struggle_scores(slice_df)
        except Exception:
            struggle_df = pd.DataFrame()
        try:
            difficulty_df = analytics.compute_question_difficulty_scores(slice_df)
        except Exception:
            difficulty_df = pd.DataFrame()

        mean_inc = (
            float(slice_df["incorrectness"].mean())
            if "incorrectness" in slice_df.columns and not slice_df.empty
            else 0.0
        )

        needs_help_ids: list[str] = []
        if not struggle_df.empty and "struggle_level" in struggle_df.columns:
            needs_help_ids = [
                str(u) for u in struggle_df.loc[
                    struggle_df["struggle_level"] == "Needs Help", "user"
                ].tolist()
            ]

        points.append(
            ProgressionPoint(
                t_end=t_end.isoformat(),
                cumulative_submissions=int(len(slice_df)),
                cumulative_students=int(slice_df["user"].nunique()) if "user" in slice_df.columns else 0,
                mean_incorrectness=round(mean_inc, 3),
                struggle_buckets=_bucket_counts(
                    struggle_df.get("struggle_level", pd.Series(dtype=str)), STRUGGLE_ORDER
                ),
                difficulty_buckets=_bucket_counts(
                    difficulty_df.get("difficulty_level", pd.Series(dtype=str)), DIFFICULTY_ORDER
                ),
                needs_help_ids=needs_help_ids,
            )
        )

    return SessionProgression(
        session=session_meta,
        bucket_minutes=bucket_minutes,
        points=points,
    )
