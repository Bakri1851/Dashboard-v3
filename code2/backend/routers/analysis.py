"""GET /api/analysis — aggregate stats for the Data Analysis view."""
from __future__ import annotations

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends

from backend.deps import get_dataframe
from backend.schemas import AnalysisStats, ModuleBreakdown

router = APIRouter(tags=["analysis"])


def _timeline_24h(df: pd.DataFrame) -> tuple[list[int], int, int]:
    """Hourly counts for the last 24h → (buckets, peak_hour_of_day, peak_count)."""
    if df.empty or "timestamp" not in df.columns:
        return [0] * 24, 0, 0
    ts = pd.to_datetime(df["timestamp"], errors="coerce", utc=True).dropna()
    if ts.empty:
        return [0] * 24, 0, 0
    now = pd.Timestamp.now(tz="UTC")
    cutoff = now - pd.Timedelta(hours=24)
    recent = ts[(ts >= cutoff) & (ts <= now)]
    buckets = np.zeros(24, dtype=int)
    if not recent.empty:
        hours_ago = ((now - recent).dt.total_seconds() // 3600).astype(int)
        for h in hours_ago:
            idx = 23 - int(h)
            if 0 <= idx < 24:
                buckets[idx] += 1
    # Peak hour-of-day across entire dataset (more stable than last-24h spike)
    hod_counts = ts.dt.hour.value_counts()
    peak_hour = int(hod_counts.idxmax()) if not hod_counts.empty else 0
    peak_count = int(hod_counts.max()) if not hod_counts.empty else 0
    return buckets.tolist(), peak_hour, peak_count


@router.get("/analysis", response_model=AnalysisStats)
def get_analysis(df: pd.DataFrame = Depends(get_dataframe)) -> AnalysisStats:
    if df.empty:
        return AnalysisStats(
            total_records=0, unique_students=0, unique_questions=0, modules=0,
            peak_hour=0, peak_hour_count=0,
            avg_attempts_per_question=0.0, avg_session_minutes=0.0,
            module_breakdown=[], timeline_24h=[0] * 24,
        )

    timeline, peak_hour, peak_count = _timeline_24h(df)

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
    )
