---
tags: [rag, architecture, chromadb, phase9, meeting3]
status: ✅ Implemented
date: 2026-04-14
source: FYP Meeting 3 — Dr. Batmaz (2026-04-08)
---

# RAG Pipeline — Two-Layer Retrieval

**Architecture designed by Dr. Batmaz** (FYP Meeting 3, 2026-04-08) — must be credited in the dissertation. See [[RAG Architecture]] for the original design note and diagram.

![[Pasted image 20260414004425.png]]

---

## Pipeline overview

```
Student assigned
       │
       ▼
Layer 1: pandas pre-filter
  df[df["user"] == student_id]
  → student_df (this student's rows only)
       │
       ▼
Layer 2: ChromaDB semantic search
  collection.query(
      query_texts=[top_incorrectness_ai_feedback],
      n_results=RAG_SUGGESTION_MAX_RESULTS,
      where={"student_id": student_id}
  )
  → top-k Q&A chunks, sorted by incorrectness
       │
       ▼
Generation: GPT-4o-mini
  System: "You are advising a lab assistant..."
  User: struggle score + level + top-3 question incorrectness
        + retrieved Q&A snippets (worst first)
  → JSON array of 2–3 bullets (≤15 words each)
       │
       ▼
Cached in _suggestion_cache[student_id]
+ st.session_state["cached_suggestions"][student_id]
       │
       ▼
Rendered in assistant app as "Suggested Focus Areas"
```

---

## Layer 1 — Structured pre-filter

Dr. Batmaz framed this as a SQL step:

```sql
SELECT ... FROM session_logs WHERE student_id = ?
```

In this codebase there is no SQL store; the session data is already a pandas DataFrame. The implementation is:

```python
student_df = df[df["user"] == student_id]
```

The SQL concept is retained in the dissertation as the architectural framing; the pandas filter is the concrete realisation.

---

## Layer 2 — ChromaDB vector search

One collection per session, named `session_{session_id}`, stored in `data/rag_chroma/` via `chromadb.PersistentClient`.

Each document: `"{question} | {student_answer} | {ai_feedback}"`

Metadata per document:
- `student_id` — enables the `where=` privacy filter
- `question` — for display and grouping
- `incorrectness` — used to sort retrieved chunks before passing to the LLM

Embedding model: `all-MiniLM-L6-v2` (sentence-transformers, local, ~90 MB first-run download, no API cost).

---

## Generation

GPT-4o-mini, temperature 0, `response_format={"type": "json_object"}`. Returns a JSON array of 2–3 bullet strings, each ≤15 words.

Reuses `_get_openai_client()` from `analytics.py` — not duplicated.

---

## Cache behaviour

- Module-level: `_suggestion_cache: dict[str, list[str]]` in `rag.py`
- Session-level: `st.session_state["cached_suggestions"]`
- Both cleared on session change via `rag.clear_suggestion_cache()`
- Result: OpenAI is called exactly once per student assignment per session; auto-refresh hits the cache

---

## Related notes

- [[RAG Architecture]] — original design note (Dr. Batmaz)
- [[rag.py — RAG Engine and ChromaDB Interface]] — implementation
- [[ChromaDB]] — library reference
- [[Suggested Focus Areas Panel]] — UI
