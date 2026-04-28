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
from cachetools import TTLCache
from fastapi import APIRouter, Depends, HTTPException

from backend import demo_data
from backend.cache import load_active_struggle_df
from backend.deps import TimeWindow, get_dataframe, get_time_window
from backend.schemas import RagSuggestions
from learning_dashboard import analytics, lab_state, rag

router = APIRouter(prefix="/rag", tags=["rag"])

# Hover-prefetch on a leaderboard fires one /rag/student/{id} per row, then
# clicking opens the panel and refetches. Without a result cache that's an
# OpenAI round-trip on every interaction. Cache the bullet list — not the
# full RagSuggestions, so audience/subject_id stay correct on rebuild.
_RAG_TTL = 600
_student_rag_cache: TTLCache = TTLCache(maxsize=64, ttl=_RAG_TTL)
_question_rag_cache: TTLCache = TTLCache(maxsize=64, ttl=_RAG_TTL)


def invalidate() -> None:
    """Drop both RAG result caches. Called from cache.invalidate()."""
    _student_rag_cache.clear()
    _question_rag_cache.clear()


def _session_id() -> str:
    code = lab_state.read_lab_state().get("session_code")
    return str(code) if code else "default"


@router.get("/student/{student_id}", response_model=RagSuggestions)
async def student_suggestions(
    student_id: str,
    df: pd.DataFrame = Depends(get_dataframe),
    window: TimeWindow = Depends(get_time_window),
) -> RagSuggestions:
    if demo_data.is_active() and demo_data.has_student(student_id):
        mock = demo_data.student_rag(student_id)
        if mock is not None:
            return mock
    if df.empty:
        raise HTTPException(status_code=404, detail="No data loaded.")

    if df[df["user"].astype(str) == student_id].empty:
        raise HTTPException(status_code=404, detail=f"Student {student_id!r} not found.")

    # Match /student/{id} — uses the active leaderboard (improved when enabled,
    # baseline otherwise) and honours the module filter, so the prompt's
    # struggle context lines up with what the page just rendered. Missing rows
    # downgrade to None instead of 404 — generate_assistant_suggestions reads
    # struggle fields with getattr defaults.
    struggle_all = load_active_struggle_df(window.from_, window.to_, window.module)
    if struggle_all.empty:
        struggle_row = None
    else:
        row_sel = struggle_all[struggle_all["user"].astype(str) == student_id]
        struggle_row = row_sel.iloc[0] if not row_sel.empty else None

    session_id = _session_id()
    cache_key = (student_id, window.from_ or "", window.to_ or "", window.module or "", session_id)
    bullets = _student_rag_cache.get(cache_key)
    if bullets is None:
        # No single-flight lock here — `threading.Lock` held across `await`
        # would block the event loop. A concurrent miss for the same key
        # may double-fire OpenAI, which is acceptable.
        bullets = await asyncio.to_thread(
            rag.generate_assistant_suggestions,
            student_id,
            df,
            struggle_row,
            session_id,
        )
        _student_rag_cache[cache_key] = bullets or []
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
    if demo_data.is_active() and demo_data.has_question(question_id):
        mock = demo_data.question_rag(question_id)
        if mock is not None:
            return mock
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
    cache_key = (question_id, session_id)
    bullets = _question_rag_cache.get(cache_key)
    if bullets is None:
        # See note in /student endpoint — no async-unsafe sync lock around the
        # OpenAI call.
        bullets = await asyncio.to_thread(_work)
        _question_rag_cache[cache_key] = bullets or []
    return RagSuggestions(
        audience="question",
        subject_id=question_id,
        bullets=bullets or [],
        session_id=session_id,
    )
