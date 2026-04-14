# rag.py — RAG pipeline for lab assistant coaching suggestions
#
# Architecture: Dr. Batmaz's hybrid two-layer retrieval (FYP Meeting 3, 2026-04-08).
#   Layer 1 — pandas pre-filter by student_id (SQL concept, pandas implementation)
#   Layer 2 — ChromaDB semantic search with student_id metadata filter
#   Generation — GPT-4o-mini (via shared _get_openai_client()) → 2–3 bullet points
#
# chromadb and sentence-transformers are optional; if either is missing the entire
# module degrades gracefully — generate_assistant_suggestions returns [] silently.
#
# Cache pattern mirrors _incorrectness_cache in analytics.py.

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

from learning_dashboard import config
from learning_dashboard import paths
from learning_dashboard.analytics import _get_openai_client

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level state (mirrors _incorrectness_cache in analytics.py:26)
# ---------------------------------------------------------------------------
_suggestion_cache: dict[str, list[str]] = {}
_cached_session_id: str | None = None
_cached_row_count: int = 0
_collection: Any = None  # chromadb.Collection once built


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_lazy_import_warned: bool = False


def _lazy_import() -> tuple[Any, Any]:
    """Try to import chromadb and SentenceTransformer. Returns (chromadb, SentenceTransformer)
    or (None, None) if either dependency is missing."""
    global _lazy_import_warned
    try:
        import chromadb  # noqa: PLC0415
        from sentence_transformers import SentenceTransformer  # noqa: PLC0415
        return chromadb, SentenceTransformer
    except ImportError as exc:
        if not _lazy_import_warned:
            logger.warning(
                "RAG suggestions disabled — missing optional dependency: %s. "
                "Install chromadb and sentence-transformers to enable.",
                exc,
            )
            _lazy_import_warned = True
        return None, None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_rag_collection(df: Any, session_id: str) -> Any:
    """Build (or reuse) a ChromaDB collection for the current session.

    Rebuild guard: returns the cached collection unchanged when session_id and
    row count match — avoids recomputing embeddings on every 5-second refresh.

    Returns None if chromadb/sentence-transformers are not installed or on error.
    """
    global _collection, _cached_session_id, _cached_row_count

    # Rebuild guard
    if (
        _collection is not None
        and session_id == _cached_session_id
        and len(df) == _cached_row_count
    ):
        return _collection

    chromadb_mod, SentenceTransformer = _lazy_import()
    if chromadb_mod is None:
        return None

    try:
        client = chromadb_mod.PersistentClient(path=str(paths.rag_chroma_dir()))

        collection_name = f"session_{session_id}"

        # If session changed, delete the old collection to prevent stale cross-session bleed
        if session_id != _cached_session_id:
            try:
                client.delete_collection(name=collection_name)
            except Exception:
                pass  # collection didn't exist yet — fine

        collection = client.get_or_create_collection(name=collection_name)

        # Build document lists from the dataframe
        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict] = []

        for i, row in enumerate(df.itertuples(index=False)):
            question = getattr(row, "question", "") or ""
            student_answer = getattr(row, "student_answer", "") or ""
            ai_feedback = getattr(row, "ai_feedback", "") or ""
            student_id = getattr(row, "user", "") or ""
            incorrectness = float(getattr(row, "incorrectness", 0.0) or 0.0)

            ids.append(f"{session_id}_{i}")
            documents.append(f"{question} | {student_answer} | {ai_feedback}")
            metadatas.append({
                "student_id": str(student_id),
                "question": str(question),
                "incorrectness": incorrectness,
            })

        if not documents:
            return None

        # Compute embeddings
        model = SentenceTransformer(config.RAG_EMBEDDING_MODEL)
        embeddings = model.encode(documents, show_progress_bar=False).tolist()

        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

        _collection = collection
        _cached_session_id = session_id
        _cached_row_count = len(df)
        return _collection

    except Exception as exc:
        logger.warning("RAG build_rag_collection failed: %s", exc)
        return None


def generate_assistant_suggestions(
    student_id: str,
    df: Any,
    struggle_row: Any,
    session_id: str,
) -> list[str]:
    """Generate 2–3 coaching bullet points for the assigned student.

    Returns [] silently on any error — never breaks the UI.
    Cached per student_id within a session; cleared on session change via clear_suggestion_cache().
    """
    # Cache hit
    if student_id in _suggestion_cache:
        return _suggestion_cache[student_id]

    try:
        # Layer 1 — pre-filter by student_id
        student_df = df[df["user"] == student_id]
        if len(student_df) < config.RAG_MIN_SUBMISSIONS:
            return []

        # Build (or reuse) collection
        collection = build_rag_collection(df, session_id)
        if collection is None:
            return []

        # Build query from the top-incorrectness question's latest ai_feedback
        top_question_series = (
            student_df.groupby("question")["incorrectness"]
            .mean()
            .sort_values(ascending=False)
        )
        if top_question_series.empty:
            return []

        top_question = top_question_series.index[0]
        top_question_rows = student_df[student_df["question"] == top_question].sort_values(
            "timestamp", ascending=False
        )
        query_text: str = ""
        if not top_question_rows.empty:
            query_text = str(top_question_rows.iloc[0].get("ai_feedback", "") or "")
        if not query_text:
            query_text = str(top_question)

        # Layer 2 — ChromaDB semantic search filtered by student_id
        results = collection.query(
            query_texts=[query_text],
            n_results=config.RAG_SUGGESTION_MAX_RESULTS,
            where={"student_id": str(student_id)},
        )

        retrieved_docs: list[str] = results.get("documents", [[]])[0] or []
        retrieved_metas: list[dict] = results.get("metadatas", [[]])[0] or []

        # Sort by incorrectness descending so worst errors appear first in the prompt
        paired = sorted(
            zip(retrieved_docs, retrieved_metas),
            key=lambda x: x[1].get("incorrectness", 0.0),
            reverse=True,
        )
        sorted_docs = [d for d, _ in paired]

        # Build struggle context
        struggle_score: float = 0.0
        struggle_label: str = "Unknown"
        try:
            struggle_score = float(getattr(struggle_row, "struggle_score", 0.0) or 0.0)
            struggle_label = str(getattr(struggle_row, "struggle_label", "Unknown") or "Unknown")
        except Exception:
            pass

        # Top-3 questions by incorrectness for the prompt
        top3 = (
            student_df.groupby("question")["incorrectness"]
            .mean()
            .sort_values(ascending=False)
            .head(3)
        )
        top3_lines = "\n".join(
            f"  - {q}: {v:.0%} incorrect" for q, v in top3.items()
        )

        snippets = "\n".join(f"  [{i+1}] {doc}" for i, doc in enumerate(sorted_docs))

        system_msg = (
            "You are advising a lab assistant on how to help a student. "
            "Be concise and practical."
        )
        user_msg = (
            f"Student struggle score: {struggle_score:.2f} ({struggle_label})\n"
            f"Top questions by incorrectness:\n{top3_lines}\n\n"
            f"Retrieved Q&A snippets (worst first):\n{snippets}\n\n"
            "Return a JSON array of 2 or 3 short bullet strings (max 15 words each) "
            "on what to check or discuss with this student. No prose outside the array."
        )

        client = _get_openai_client()
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content.strip()
        parsed = json.loads(raw)

        # Accept {"bullets": [...]} or a bare array
        if isinstance(parsed, list):
            bullets = [str(b) for b in parsed if b]
        elif isinstance(parsed, dict):
            for key in ("bullets", "suggestions", "items", "result"):
                if key in parsed and isinstance(parsed[key], list):
                    bullets = [str(b) for b in parsed[key] if b]
                    break
            else:
                bullets = [str(v) for v in parsed.values() if isinstance(v, str) and v]
        else:
            bullets = []

        bullets = bullets[:3]  # never more than 3

        _suggestion_cache[student_id] = bullets
        return bullets

    except Exception as exc:
        logger.debug("RAG generate_assistant_suggestions failed for %s: %s", student_id, exc)
        return []


def clear_suggestion_cache() -> None:
    """Clear all module-level RAG state. Call when session_id changes."""
    global _suggestion_cache, _cached_session_id, _cached_row_count, _collection
    _suggestion_cache = {}
    _cached_session_id = None
    _cached_row_count = 0
    _collection = None
