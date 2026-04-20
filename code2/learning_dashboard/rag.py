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
import threading
from typing import TYPE_CHECKING, Any

from cachetools import TTLCache

from learning_dashboard import config
from learning_dashboard import paths
from learning_dashboard.analytics import _get_openai_client

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level state (mirrors _incorrectness_cache in analytics.py:26)
# ---------------------------------------------------------------------------
# 10-minute TTL bounds staleness for long lab sessions; maxsize=256 covers a
# full cohort of students and questions without unbounded growth.
_suggestion_cache: TTLCache = TTLCache(maxsize=256, ttl=600)
_cluster_suggestion_cache: TTLCache = TTLCache(maxsize=256, ttl=600)
_cached_session_id: str | None = None
_cached_row_count: int = 0
_cached_latest_ts: str = ""
_collection: Any = None  # chromadb.Collection once built
_sentence_model: Any = None  # SentenceTransformer singleton — load once per process

# Single-flight guard around build_rag_collection(). The first build on cold
# start takes 60-120s (sentence-transformers download + embedding); without
# this lock, concurrent requests each kick off their own rebuild and
# saturate the FastAPI threadpool.
_build_lock = threading.Lock()
# Count-drift tolerance for skipping the re-embed. The persistent ChromaDB
# store may be a few rows behind the live dataframe (new submissions since
# last rebuild); a 10% tolerance avoids a 60-120s re-embed for routine drift
# while still triggering a rebuild on a genuine dataset change.
_FAST_PATH_DRIFT_TOLERANCE = 0.10


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

_COLLECTION_NAME = "submissions"


def _sample_for_rag(df: Any) -> Any:
    """Reduce the embedding corpus with a stratified per-ISO-week sample.

    Keeps up to ``config.RAG_SAMPLE_PER_WEEK`` rows from each ISO-year-week
    bucket using a fixed seed. Rows without a parseable timestamp fall into a
    single sentinel bucket. Returns ``df`` unchanged when sampling is disabled
    (cap <= 0) or the corpus is already below the cap.
    """
    import pandas as _pd  # noqa: PLC0415
    cap = int(getattr(config, "RAG_SAMPLE_PER_WEEK", 0) or 0)
    if cap <= 0 or "timestamp" not in df.columns or len(df) <= cap:
        return df
    ts = _pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    iso = ts.dt.isocalendar()
    week_key = (
        iso["year"].astype("string").fillna("NA")
        + "-W"
        + iso["week"].astype("string").fillna("00")
    )
    week_key.index = df.index  # align for groupby-by-series
    seed = int(getattr(config, "RAG_SAMPLE_SEED", 42))
    sampled = (
        df.groupby(week_key, group_keys=False, sort=False)
          .apply(lambda g: g.sample(n=min(len(g), cap), random_state=seed))
    )
    return sampled


def build_rag_collection(df: Any, session_id: str) -> Any:
    """Build (or reuse) the ChromaDB collection for current submissions.

    Rebuild guard: row count + max(timestamp) — the embedded documents and
    metadata don't depend on session_id (it isn't in the text or any filter
    field), so starting a new lab session no longer forces a 30–60s re-embed.

    `session_id` is accepted for backwards compatibility and recorded for
    diagnostics, but does NOT invalidate the cached collection.

    Returns None if chromadb/sentence-transformers are not installed or on error.
    """
    global _collection, _cached_session_id, _cached_row_count, _cached_latest_ts

    # In-memory cache hit: always reuse the collection once built. Minor drift
    # from new submissions is acceptable — the embeddings are still semantically
    # valid, and a 60-120s re-embed on a user request is not.
    if _collection is not None:
        _cached_session_id = session_id
        return _collection

    try:
        latest_ts = str(df["timestamp"].max()) if "timestamp" in df.columns else ""
    except Exception:
        latest_ts = ""

    chromadb_mod, SentenceTransformer = _lazy_import()
    if chromadb_mod is None:
        return None

    # Non-blocking lock: if another thread (usually the startup prewarm) is
    # already doing the 60-120s first-time embed, don't pile up behind it.
    # User requests return None fast and get real results next click once
    # prewarm finishes and populates `_collection`.
    if not _build_lock.acquire(blocking=False):
        logger.info("RAG: build already in progress; returning None so the request doesn't hang")
        return None
    try:
        if _collection is not None:
            _cached_session_id = session_id
            return _collection

        try:
            client = chromadb_mod.PersistentClient(path=str(paths.rag_chroma_dir()))
            collection = client.get_or_create_collection(name=_COLLECTION_NAME)

            # Stratify the embedding corpus so the first-time build fits in
            # tens of seconds on CPU. The rest of the app still uses the full
            # df — this only affects which rows land in ChromaDB.
            sampled_df = _sample_for_rag(df)

            # Fast path on process restart: compare the persistent count
            # against the SAMPLED size (that's what we embedded last time),
            # not the full df. 10% drift tolerance absorbs minor variation.
            try:
                existing = collection.count()
            except Exception:
                existing = 0
            n = len(sampled_df)
            drift_ok = (
                existing > 0
                and n > 0
                and abs(existing - n) / max(1, n) <= _FAST_PATH_DRIFT_TOLERANCE
            )
            if drift_ok:
                logger.info(
                    "RAG fast-path: reusing persistent collection (existing=%d, sampled=%d, full=%d)",
                    existing,
                    n,
                    len(df),
                )
                _collection = collection
                _cached_session_id = session_id
                _cached_row_count = existing
                _cached_latest_ts = latest_ts
                return _collection

            ids: list[str] = []
            documents: list[str] = []
            metadatas: list[dict] = []

            for i, row in enumerate(sampled_df.itertuples(index=False)):
                question = getattr(row, "question", "") or ""
                student_answer = getattr(row, "student_answer", "") or ""
                ai_feedback = getattr(row, "ai_feedback", "") or ""
                student_id = getattr(row, "user", "") or ""
                incorrectness = float(getattr(row, "incorrectness", 0.0) or 0.0)

                ids.append(f"row_{i}")
                documents.append(f"{question} | {student_answer} | {ai_feedback}")
                metadatas.append({
                    "student_id": str(student_id),
                    "question": str(question),
                    "incorrectness": incorrectness,
                })

            if not documents:
                return None

            global _sentence_model
            if _sentence_model is None:
                logger.info("RAG: loading sentence-transformers model %s", config.RAG_EMBEDDING_MODEL)
                _sentence_model = SentenceTransformer(config.RAG_EMBEDDING_MODEL)
            logger.info(
                "RAG: embedding %d sampled rows (full df=%d) — this prints a progress bar to stderr",
                len(documents),
                len(df),
            )
            embeddings = _sentence_model.encode(documents, show_progress_bar=True, batch_size=32).tolist()

            # ChromaDB imposes a per-call upsert limit (~5461 items). Chunk so
            # larger sampled corpora still write successfully.
            UPSERT_CHUNK = 5000
            total = len(ids)
            for start in range(0, total, UPSERT_CHUNK):
                end = min(start + UPSERT_CHUNK, total)
                collection.upsert(
                    ids=ids[start:end],
                    embeddings=embeddings[start:end],
                    documents=documents[start:end],
                    metadatas=metadatas[start:end],
                )
            logger.info("RAG: upserted %d rows in %d chunk(s)", total, (total + UPSERT_CHUNK - 1) // UPSERT_CHUNK)

            _collection = collection
            _cached_session_id = session_id
            _cached_row_count = len(sampled_df)
            _cached_latest_ts = latest_ts
            return _collection

        except Exception as exc:
            logger.warning("RAG build_rag_collection failed: %s", exc)
            return None
    finally:
        _build_lock.release()


def _extract_bullets(parsed: Any) -> list[str]:
    """Pull a list of short strings out of whatever shape OpenAI returned.

    `response_format={"type": "json_object"}` forces a dict wrapper, and the
    model chooses the key name (bullets / advice / feedback / etc.), so we
    accept any key whose value is a list of strings. Falls back to flattening
    nested lists/dicts if needed.
    """
    if isinstance(parsed, list):
        return [str(b).strip() for b in parsed if isinstance(b, (str, int, float)) and str(b).strip()]

    if isinstance(parsed, dict):
        # First: any value that is a list of short-ish things
        for value in parsed.values():
            if isinstance(value, list) and value:
                items = [str(v).strip() for v in value if isinstance(v, (str, int, float)) and str(v).strip()]
                if items:
                    return items
        # Next: any value that is itself a dict containing a list (one level of nesting)
        for value in parsed.values():
            if isinstance(value, dict):
                nested = _extract_bullets(value)
                if nested:
                    return nested
        # Last resort: treat all string values as bullets
        return [str(v).strip() for v in parsed.values() if isinstance(v, str) and v.strip()]

    return []


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
            timeout=15.0,
        )

        raw = response.choices[0].message.content.strip()
        parsed = json.loads(raw)

        bullets = _extract_bullets(parsed)
        bullets = bullets[:3]  # never more than 3

        _suggestion_cache[student_id] = bullets
        return bullets

    except Exception:
        logger.exception("RAG generate_assistant_suggestions failed for %s", student_id)
        return []


def generate_cluster_suggestions(
    question_id: str,
    df: Any,
    clusters: list[dict],
    session_id: str,
) -> list[str]:
    """Generate 2–3 pedagogical bullets for an instructor viewing a clustered question.

    Audience is the instructor: focus on misconception diagnosis and corrective class-wide
    feedback, not one-on-one tutoring. Reuses the shared ChromaDB collection built for the
    student-side RAG, filtered on the `question` metadata key.

    Returns [] silently on any error. Cached per question_id within a session; cleared on
    session change via clear_cluster_suggestion_cache().
    """
    if question_id in _cluster_suggestion_cache:
        return _cluster_suggestion_cache[question_id]

    if not clusters:
        return []

    try:
        question_df = df[df["question"] == question_id]
        if len(question_df) < config.RAG_MIN_SUBMISSIONS:
            return []

        collection = build_rag_collection(df, session_id)
        if collection is None:
            return []

        top_clusters = clusters[:3]
        query_text = f"{question_id} " + " ".join(
            (c.get("example_answers") or [""])[0] for c in top_clusters
        )

        results = collection.query(
            query_texts=[query_text],
            n_results=config.RAG_SUGGESTION_MAX_RESULTS,
            where={"question": str(question_id)},
        )
        retrieved_docs: list[str] = results.get("documents", [[]])[0] or []

        cluster_lines = []
        for i, c in enumerate(top_clusters, 1):
            examples = "; ".join((c.get("example_answers") or [])[:2])
            cluster_lines.append(
                f"  [{i}] {c.get('label', '?')} — {c.get('count', 0)} students "
                f"({c.get('percent_of_wrong', 0):.0f}% of wrong). Examples: {examples}"
            )
        clusters_block = "\n".join(cluster_lines)
        snippets = "\n".join(f"  - {d}" for d in retrieved_docs)

        system_msg = (
            "You advise a university instructor on how to correct common misconceptions "
            "about a specific question. Focus on teaching adjustments and corrective "
            "feedback to give the class — not one-on-one tutoring."
        )
        user_msg = (
            f"Question: {question_id}\n\n"
            f"Mistake clusters (top 3):\n{clusters_block}\n\n"
            f"Retrieved Q&A snippets:\n{snippets}\n\n"
            "Return a JSON array of 2 or 3 short bullet strings (max 15 words each) "
            "with pedagogical advice: what misconception each cluster reveals and what "
            "feedback or follow-up the instructor should give. No prose outside the array."
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
            timeout=15.0,
        )
        raw = response.choices[0].message.content.strip()
        parsed = json.loads(raw)

        bullets = _extract_bullets(parsed)
        bullets = bullets[:3]
        _cluster_suggestion_cache[question_id] = bullets
        return bullets

    except Exception as exc:
        logger.warning("RAG generate_cluster_suggestions failed for %s: %s", question_id, exc, exc_info=True)
        return []


def clear_suggestion_cache() -> None:
    """Clear cached coaching bullets. Call when session_id changes — keeps the
    embedded ChromaDB collection intact (its content doesn't depend on the
    session) so a new lab session doesn't pay the 30–60s re-embed cost."""
    global _cached_session_id
    _suggestion_cache.clear()
    _cached_session_id = None


def clear_cluster_suggestion_cache() -> None:
    """Clear the per-question RAG cache. Call when session_id changes."""
    _cluster_suggestion_cache.clear()
