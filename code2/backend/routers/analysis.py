"""GET /api/analysis — aggregate stats for the Data Analysis view."""
from __future__ import annotations

import threading

import pandas as pd
from cachetools import TTLCache
from fastapi import APIRouter, Depends

from backend.cache import filter_df
from backend.deps import TimeWindow, get_dataframe, get_time_window
from backend.routers._timeline import hour_of_day_distribution
from backend.schemas import (
    AnalysisStats,
    ModuleBreakdown,
    TopQuestionRow,
    UserActivityRow,
    WeekActivityCell,
)
from learning_dashboard import academic_calendar

router = APIRouter(tags=["analysis"])

# /api/analysis iterates the full df several times per call. The view isn't
# live-polled, but the same window is hit repeatedly when the user scrolls
# between panels. Cache the response by `(from, to, module)` so a re-render
# is instant.
_ANALYSIS_TTL = 300
_analysis_cache: TTLCache = TTLCache(maxsize=8, ttl=_ANALYSIS_TTL)
_analysis_lock = threading.Lock()


def invalidate() -> None:
    """Drop the analysis result cache. Called from cache.invalidate() so
    settings POSTs that clear other caches clear this one too."""
    _analysis_cache.clear()


def _timeline_stats(df: pd.DataFrame) -> tuple[list[int], int, int]:
    """Hour-of-day buckets + peak hour/count over filtered df.

    The timeline is a filtered aggregate (hour-of-day 00..23), not wall-clock
    last-24h, so it respects whatever filter produced `df`. Peak stats are
    derived from the same vector so chart and stats cannot disagree."""
    buckets = hour_of_day_distribution(df)
    peak_hour = max(range(24), key=lambda h: buckets[h])
    return buckets, int(peak_hour), int(buckets[peak_hour])


_DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _top_questions(df: pd.DataFrame, limit: int = 15) -> list[TopQuestionRow]:
    if df.empty or "question" not in df.columns:
        return []
    g = df.groupby("question")
    top = g.agg(
        attempts=("question", "size"),
        unique_students=("user", "nunique"),
    ).sort_values("attempts", ascending=False).head(limit)
    mod_lookup = df.drop_duplicates("question").set_index("question")["module"].astype(str).to_dict() if "module" in df.columns else {}
    out: list[TopQuestionRow] = []
    for r in top.reset_index().to_dict("records"):
        qid = str(r["question"])
        students = int(r["unique_students"])
        attempts = int(r["attempts"])
        out.append(
            TopQuestionRow(
                question=qid,
                module=mod_lookup.get(qid, ""),
                attempts=attempts,
                unique_students=students,
                avg_attempts=round(attempts / students, 2) if students else 0.0,
            )
        )
    return out


def _user_activity(df: pd.DataFrame, limit: int = 20) -> list[UserActivityRow]:
    if df.empty or "user" not in df.columns:
        return []
    ts = pd.to_datetime(df["timestamp"], errors="coerce", utc=True) if "timestamp" in df.columns else None
    work = df.assign(_ts=ts) if ts is not None else df.assign(_ts=None)
    g = work.groupby("user")
    agg = g.agg(
        submissions=("user", "size"),
        unique_questions=("question", "nunique"),
        first_ts=("_ts", "min"),
        last_ts=("_ts", "max"),
    ).sort_values("submissions", ascending=False).head(limit)
    out: list[UserActivityRow] = []
    for r in agg.reset_index().to_dict("records"):
        out.append(
            UserActivityRow(
                user=str(r["user"]),
                submissions=int(r["submissions"]),
                unique_questions=int(r["unique_questions"]),
                first_submission=r["first_ts"].isoformat() if pd.notna(r["first_ts"]) else None,
                last_submission=r["last_ts"].isoformat() if pd.notna(r["last_ts"]) else None,
            )
        )
    return out


def _activity_by_week(df: pd.DataFrame) -> list[WeekActivityCell]:
    """Counts keyed by (academic period label, day-of-week) — feeds a heatmap."""
    if df.empty or "timestamp" not in df.columns:
        return []
    ts = pd.to_datetime(df["timestamp"], errors="coerce", utc=True).dropna()
    if ts.empty:
        return []

    # For each ts, ask the academic calendar for its label; skip missing.
    cells: dict[tuple[str, int], int] = {}
    for t in ts:
        label = academic_calendar.get_academic_period(t.date())
        if not label:
            continue
        dow = int(t.weekday())
        key = (str(label), dow)
        cells[key] = cells.get(key, 0) + 1

    out: list[WeekActivityCell] = []
    for (label, dow), count in cells.items():
        out.append(
            WeekActivityCell(
                week_label=label,
                day_index=dow,
                day_label=_DAY_LABELS[dow] if 0 <= dow < 7 else str(dow),
                count=count,
            )
        )
    # Sort for stable order
    out.sort(key=lambda c: (c.week_label, c.day_index))
    return out


@router.get("/analysis", response_model=AnalysisStats)
def get_analysis(
    df: pd.DataFrame = Depends(get_dataframe),
    window: TimeWindow = Depends(get_time_window),
) -> AnalysisStats:
    cache_key = (window.from_ or "", window.to_ or "", window.module or "")
    cached = _analysis_cache.get(cache_key)
    if cached is not None:
        return cached
    with _analysis_lock:
        cached = _analysis_cache.get(cache_key)
        if cached is not None:
            return cached
        result = _compute_analysis(df, window)
        _analysis_cache[cache_key] = result
        return result


def _compute_analysis(df: pd.DataFrame, window: TimeWindow) -> AnalysisStats:
    df = filter_df(df, window.from_, window.to_) if window.active else df
    if df.empty:
        return AnalysisStats(
            total_records=0, unique_students=0, unique_questions=0, modules=0,
            peak_hour=0, peak_hour_count=0,
            avg_attempts_per_question=0.0, avg_session_minutes=0.0,
            module_breakdown=[], timeline_24h=[0] * 24,
            top_questions=[], user_activity=[], activity_by_week=[],
        )

    timeline, peak_hour, peak_count = _timeline_stats(df)

    # Module breakdown
    module_breakdown: list[ModuleBreakdown] = []
    if "module" in df.columns:
        for mod, g in df.groupby("module"):
            module_breakdown.append(
                ModuleBreakdown(
                    module=str(mod),
                    submissions=int(len(g)),
                    unique_students=int(g["user"].nunique()) if "user" in g else 0,
                )
            )
        module_breakdown.sort(key=lambda m: -m.submissions)

    # Avg attempts per question
    q_counts = df.groupby("question").size() if "question" in df.columns else pd.Series(dtype=int)
    avg_attempts = float(q_counts.mean()) if not q_counts.empty else 0.0

    # Avg session length per student (time between first and last submission)
    avg_session_minutes = 0.0
    if "timestamp" in df.columns and "user" in df.columns:
        ts = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
        ddf = df.assign(_ts=ts).dropna(subset=["_ts"])
        if not ddf.empty:
            spans = ddf.groupby("user")["_ts"].agg(lambda s: (s.max() - s.min()).total_seconds() / 60.0)
            avg_session_minutes = float(spans.mean())

    return AnalysisStats(
        total_records=int(len(df)),
        unique_students=int(df["user"].nunique()) if "user" in df.columns else 0,
        unique_questions=int(df["question"].nunique()) if "question" in df.columns else 0,
        modules=int(df["module"].nunique()) if "module" in df.columns else 0,
        peak_hour=peak_hour,
        peak_hour_count=peak_count,
        avg_attempts_per_question=round(avg_attempts, 2),
        avg_session_minutes=round(avg_session_minutes, 1),
        module_breakdown=module_breakdown,
        timeline_24h=timeline,
        top_questions=_top_questions(df),
        user_activity=_user_activity(df),
        activity_by_week=_activity_by_week(df),
    )
