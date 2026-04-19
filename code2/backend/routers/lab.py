"""Lab-session coordination endpoints.

Every endpoint delegates to `learning_dashboard.lab_state`, which uses a
`FileLock` on `data/lab_session.json` — so all four processes (code/ Streamlit
×2, code2/ Streamlit ×2, this FastAPI) share the same source of truth.

POST endpoints return the fresh `LabState` so React can optimistically refresh
without a separate GET round-trip.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.schemas import (
    AssignRequest,
    AssistantIdRequest,
    JoinRequest,
    JoinResult,
    LabAssignment,
    LabAssistant,
    LabState,
    SetBoolRequest,
    SimpleResult,
    StudentIdRequest,
)
from learning_dashboard import lab_state

router = APIRouter(prefix="/lab", tags=["lab"])


def _to_lab_state(raw: dict) -> LabState:
    assistants = [
        LabAssistant(
            id=aid,
            name=info.get("name", ""),
            joined_at=info.get("joined_at", ""),
            assigned_student=info.get("assigned_student"),
        )
        for aid, info in (raw.get("lab_assistants", {}) or {}).items()
    ]
    assignments = [
        LabAssignment(
            student_id=sid,
            assistant_id=entry.get("assistant_id", ""),
            status=entry.get("status", "helping"),
            assigned_at=entry.get("assigned_at", ""),
            helped_at=entry.get("helped_at"),
        )
        for sid, entry in (raw.get("assignments", {}) or {}).items()
    ]
    return LabState(
        session_code=raw.get("session_code"),
        session_active=bool(raw.get("session_active", False)),
        session_start=raw.get("session_start"),
        generated_at=raw.get("generated_at", ""),
        allow_self_allocation=bool(raw.get("allow_self_allocation", False)),
        lab_assistants=assistants,
        assignments=assignments,
    )


@router.get("/state", response_model=LabState)
def get_state() -> LabState:
    return _to_lab_state(lab_state.read_lab_state())


@router.post("/start", response_model=LabState)
def start() -> LabState:
    lab_state.start_lab_session()
    return _to_lab_state(lab_state.read_lab_state())


@router.post("/end", response_model=LabState)
def end() -> LabState:
    lab_state.end_lab_session()
    return _to_lab_state(lab_state.read_lab_state())


@router.post("/join", response_model=JoinResult)
def join(req: JoinRequest) -> JoinResult:
    ok, assistant_id, err = lab_state.join_session(req.code, req.name)
    return JoinResult(ok=ok, assistant_id=assistant_id, error=err)


@router.post("/leave", response_model=LabState)
def leave(req: AssistantIdRequest) -> LabState:
    ok, err = lab_state.leave_session(req.assistant_id)
    if not ok and err:
        raise HTTPException(status_code=400, detail=err)
    return _to_lab_state(lab_state.read_lab_state())


@router.post("/assign", response_model=LabState)
def assign(req: AssignRequest) -> LabState:
    ok = lab_state.assign_student(req.student_id, req.assistant_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Assignment failed (assistant busy or invalid ids).")
    return _to_lab_state(lab_state.read_lab_state())


@router.post("/self-claim", response_model=LabState)
def self_claim(req: AssignRequest) -> LabState:
    ok, err = lab_state.self_claim_student(req.student_id, req.assistant_id)
    if not ok and err:
        raise HTTPException(status_code=400, detail=err)
    return _to_lab_state(lab_state.read_lab_state())


@router.post("/mark-helped", response_model=LabState)
def mark_helped(req: StudentIdRequest) -> LabState:
    ok = lab_state.mark_student_helped(req.student_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Could not mark helped (no assignment).")
    return _to_lab_state(lab_state.read_lab_state())


@router.post("/unassign", response_model=LabState)
def unassign(req: StudentIdRequest) -> LabState:
    ok = lab_state.unassign_student(req.student_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Could not unassign (no assignment).")
    return _to_lab_state(lab_state.read_lab_state())


@router.post("/remove-assistant", response_model=LabState)
def remove_assistant(req: AssistantIdRequest) -> LabState:
    ok, err = lab_state.remove_assistant(req.assistant_id)
    if not ok and err:
        raise HTTPException(status_code=400, detail=err)
    return _to_lab_state(lab_state.read_lab_state())


@router.post("/allow-self-alloc", response_model=SimpleResult)
def allow_self_alloc(req: SetBoolRequest) -> SimpleResult:
    lab_state.set_allow_self_allocation(req.enabled)
    return SimpleResult(ok=True)
