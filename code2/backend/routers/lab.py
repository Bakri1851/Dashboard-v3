"""Lab-session coordination endpoints.

Every endpoint delegates to `learning_dashboard.lab_state`, which uses a
`FileLock` on `data/lab_session.json` — so all three processes (code/
instructor + mobile, and this FastAPI) share the same source of truth. The
React SPA reads state through this backend, not the file directly.

POST endpoints return the fresh `LabState` so React can optimistically refresh
without a separate GET round-trip.
"""
from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query

from backend.deps import TimeWindow, get_dataframe, get_time_window
from backend.cache import filter_df, invalidate as invalidate_caches
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
    StrugglingQuestionRow,
    StudentIdRequest,
)
from learning_dashboard import analytics, lab_state

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
    invalidate_caches()
    return _to_lab_state(lab_state.read_lab_state())


@router.post("/end", response_model=LabState)
def end() -> LabState:
    lab_state.end_lab_session()
    invalidate_caches()
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


@router.get(
    "/student/{student_id}/struggling-questions",
    response_model=list[StrugglingQuestionRow],
)
def struggling_questions(
    student_id: str,
    limit: int = Query(default=3, ge=1, le=20),
    df: pd.DataFrame = Depends(get_dataframe),
    window: TimeWindow = Depends(get_time_window),
) -> list[StrugglingQuestionRow]:
    """Top-N questions for a student, ranked by mean incorrectness DESC.

    Mirrors `code/learning_dashboard/assistant_app.py:389-398`. The mobile
    lab-assistant portal uses this to tell a helper which questions their
    assigned student is doing worst on.
    """
    if df.empty or "user" not in df.columns:
        return []

    # Default to the active lab session's start when no explicit window is
    # passed — matches the `code/` original which reads
    # `state["session_start"]` in `_load_student_data()`.
    effective_from = window.from_
    effective_to = window.to_
    if not window.active:
        session_start = lab_state.read_lab_state().get("session_start")
        if session_start:
            effective_from = str(session_start)

    working = (
        filter_df(df, effective_from, effective_to)
        if (effective_from or effective_to)
        else df
    )
    student_df = working[working["user"].astype(str) == student_id].copy()
    if student_df.empty:
        return []

    if "incorrectness" not in student_df.columns:
        student_df["incorrectness"] = analytics.compute_incorrectness_column(student_df)

    q_scores = (
        student_df.groupby("question")["incorrectness"]
        .mean()
        .sort_values(ascending=False)
        .head(limit)
    )
    return [
        StrugglingQuestionRow(question=str(q), avg_incorrectness=float(v))
        for q, v in q_scores.items()
    ]
