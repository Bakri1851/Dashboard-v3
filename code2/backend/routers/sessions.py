"""Sessions router — GET list, POST save (retroactive), DELETE by id.

`POST /api/sessions/save` builds a session record from the current time-
filter window (supplied by the frontend) and delegates to
`data_loader.save_session_record`. The Streamlit `build_session_record_from_state`
helper is Streamlit-only because it reads `st.session_state` — here the same
shape is assembled from plain POST arguments.

`DELETE /api/sessions/{id}` delegates to `data_loader.delete_session_record`.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.schemas import SavedSession
from learning_dashboard import data_loader

router = APIRouter(tags=["sessions"])


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
