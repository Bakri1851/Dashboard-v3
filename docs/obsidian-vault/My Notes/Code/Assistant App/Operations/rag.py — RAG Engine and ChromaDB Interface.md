---
tags: [rag, assistant-app, chromadb, openai, phase9]
status: ✅ Implemented
date: 2026-04-14
community: Assistant App
---

# rag.py — RAG Engine and ChromaDB Interface

New module implementing Dr. Batmaz's hybrid two-layer RAG pipeline for Phase 9. Generates 2–3 coaching bullet points for lab assistants, grounded in the assigned student's submission history.

See [[RAG Architecture]] for the architectural design credit.

---

## Overview

- **Location:** `code/learning_dashboard/rag.py`
- **Purpose:** Build and query a ChromaDB collection of Q&A + feedback embeddings; call GPT-4o-mini to produce assistant coaching suggestions
- **Dependencies:** `chromadb`, `sentence-transformers` (both optional — graceful no-op if missing)
- **Reuses:** `_get_openai_client()` from `analytics.py` (not duplicated)

---

## Module-level state

Mirrors `_incorrectness_cache` pattern in [[analytics.py — Scoring Engine]]:

```python
_suggestion_cache: dict[str, list[str]] = {}   # keyed by student_id
_cached_session_id: str | None = None
_cached_row_count: int = 0
_collection = None  # chromadb.Collection once built
```

---

## Functions

### `_lazy_import() -> tuple[chromadb | None, SentenceTransformer | None]`

Tries to import `chromadb` and `sentence_transformers`. Returns `(None, None)` with a one-time warning log if either is missing. Entire RAG pipeline no-ops silently in that case.

### `build_rag_collection(df, session_id) -> Collection | None`

Builds (or reuses) a ChromaDB collection for the current session.

- **Rebuild guard:** returns cached collection unchanged if `session_id` and `len(df)` match — avoids recomputing embeddings on every 5-second auto-refresh
- **Storage:** `chromadb.PersistentClient` at `data/rag_chroma/` (via `paths.rag_chroma_dir()`)
- **Collection name:** `session_{session_id}`
- **Document format:** `"{question} | {student_answer} | {ai_feedback}"`
- **Metadata per doc:** `student_id`, `question`, `incorrectness`
- **Embeddings:** `SentenceTransformer("all-MiniLM-L6-v2").encode(documents)`

### `generate_assistant_suggestions(student_id, df, struggle_row, session_id) -> list[str]`

Main entry point called from `assistant_app.py`.

1. Cache hit → return immediately
2. **Layer 1:** `df[df["user"] == student_id]` — restrict to this student only
3. If < `RAG_MIN_SUBMISSIONS` (2) rows → return `[]`
4. Build/reuse collection via `build_rag_collection`
5. **Layer 2:** `collection.query(where={"student_id": student_id}, n_results=RAG_SUGGESTION_MAX_RESULTS)`
6. Sort results by `incorrectness` descending
7. Prompt GPT-4o-mini with struggle metrics + snippets → parse JSON array
8. Cache and return up to 3 bullets; return `[]` on any exception

### `clear_suggestion_cache() -> None`

Resets all module state. Called from `assistant_app.py` when `session_id` changes.

---

## Error handling

- Missing deps → `_lazy_import` returns `(None, None)`, all functions return `[]`
- OpenAI failure / malformed JSON → broad `except Exception` → return `[]`
- Never raises — UI never breaks

---

## Related notes

- [[RAG Architecture]] — Dr. Batmaz's design (must credit in dissertation)
- [[RAG Pipeline - Two-Layer Retrieval]] — pipeline detail
- [[ChromaDB]] — library reference
- [[Suggested Focus Areas Panel]] — UI where suggestions appear
- [[analytics.py — Scoring Engine]] — `_get_openai_client` reused here
