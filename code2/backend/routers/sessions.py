"""GET /api/sessions — list previously saved lab sessions (read-only).

Writes are Streamlit-only today because `build_session_record_from_state`
pulls from `st.session_state`. When the React UI needs to persist sessions
directly, add a POST endpoint that accepts the record shape built client-side.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter

from backend.schemas import SavedSession
from learning_dashboard import data_loader

router = APIRouter(tags=["sessions"])


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
