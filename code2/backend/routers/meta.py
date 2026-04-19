"""GET /api/meta/academic-periods and /api/meta/filter-presets.

Metadata endpoints used by the sidebar filter panel. Neither hits the
analytics pipeline — cheap to call, no caching needed.
"""
from __future__ import annotations

from fastapi import APIRouter

from backend.schemas import AcademicPeriod, FilterPreset
from learning_dashboard import academic_calendar

router = APIRouter(prefix="/meta", tags=["meta"])


_PRESETS: list[FilterPreset] = [
    FilterPreset(id="all", label="All Time"),
    FilterPreset(id="live", label="Live Session"),
    FilterPreset(id="today", label="Today"),
    FilterPreset(id="past_hour", label="Past Hour"),
    FilterPreset(id="past_24h", label="Past 24H"),
    FilterPreset(id="current_week", label="Current Week"),
    FilterPreset(id="last_week", label="Last Week"),
    FilterPreset(id="custom", label="Custom", needs_custom=True),
]


@router.get("/filter-presets", response_model=list[FilterPreset])
def filter_presets() -> list[FilterPreset]:
    return _PRESETS


@router.get("/academic-periods", response_model=list[AcademicPeriod])
def academic_periods() -> list[AcademicPeriod]:
    out: list[AcademicPeriod] = []
    for start_date, end_date, label in academic_calendar.ACADEMIC_PERIODS:
        out.append(
            AcademicPeriod(
                label=str(label),
                start_date=start_date.isoformat() if hasattr(start_date, "isoformat") else str(start_date),
                end_date=end_date.isoformat() if hasattr(end_date, "isoformat") else str(end_date),
            )
        )
    return out
