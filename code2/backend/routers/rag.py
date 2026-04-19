"""GET /api/rag/student/{id} and /api/rag/question/{id} — coaching suggestions.

Both flavours wrap `learning_dashboard.rag`, which swallows all errors into an
empty list so the UI never breaks if ChromaDB / sentence-transformers / OpenAI
are unavailable. The handlers are `async` and execute the blocking RAG work in
a worker thread — required because first-time `build_rag_collection` can take
minutes (downloads the sentence-transformers model, embeds 34k records) and
would otherwise starve the FastAPI event loop.

The session_id cache-key is taken from the live lab session (falling back to
a stable "default" when no session is active).
"""
from __future__ import annotations

import asyncio

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException

from backend.cache import load_struggle_df
from backend.deps import get_dataframe
from backend.schemas import RagSuggestions
from learning_dashboard import analytics, lab_state, rag

router = APIRouter(prefix="/rag", tags=["rag"])


def _session_id() -> str:
    code = lab_state.read_lab_state().get("session_code")
    return str(code) if code else "default"


@router.get("/student/{student_id}", response_model=RagSuggestions)
async def student_suggestions(
    student_id: str,
    df: pd.DataFrame = Depends(get_dataframe),
) -> RagSuggestions:
    if df.empty:
        raise HTTPException(status_code=404, detail="No data loaded.")

    struggle_all = load_struggle_df()
    row_sel = struggle_all[struggle_all["user"].astype(str) == student_id]
    if row_sel.empty:
        raise HTTPException(status_code=404, detail=f"Student {student_id!r} not found.")
    struggle_row = row_sel.iloc[0]

    session_id = _session_id()
    bullets = await asyncio.to_thread(
        rag.generate_assistant_suggestions,
        student_id,
        df,
        struggle_row,
        session_id,
    )
    return RagSuggestions(
        audience="student",
        subject_id=student_id,
        bullets=bullets or [],
        session_id=session_id,
    )


@router.get("/question/{question_id}", response_model=RagSuggestions)
async def question_suggestions(
    question_id: str,
    df: pd.DataFrame = Depends(get_dataframe),
) -> RagSuggestions:
    if df.empty:
        raise HTTPException(status_code=404, detail="No data loaded.")

    q_df = df[df["question"].astype(str) == question_id].copy()
    if q_df.empty:
        raise HTTPException(status_code=404, detail=f"Question {question_id!r} not found.")

    def _work() -> list[str]:
        local = q_df
        if "incorrectness" not in local.columns:
            local["incorrectness"] = analytics.compute_incorrectness_column(local)
        try:
            clusters = analytics.cluster_question_mistakes(local, question_id) or []
        except Exception:
            clusters = []
        try:
            return rag.generate_cluster_suggestions(question_id, df, clusters, session_id) or []
        except Exception:
            return []

    session_id = _session_id()
    bullets = await asyncio.to_thread(_work)
    return RagSuggestions(
        audience="question",
        subject_id=question_id,
        bullets=bullets or [],
        session_id=session_id,
    )
