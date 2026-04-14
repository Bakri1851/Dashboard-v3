# rag.py

**Path:** `code/learning_dashboard/rag.py`
**Folder:** [[learning_dashboard]]

> Retrieval-augmented generation pipeline that produces short coaching suggestions for lab assistants (per-student) and instructors (per-mistake-cluster).

## Responsibilities

- Build a per-session ChromaDB collection of student submissions with embeddings from `sentence-transformers` (`all-MiniLM-L6-v2`, local, no API cost).
- Execute a two-layer retrieval: pandas pre-filter by `student_id`, then semantic search for the most relevant submissions.
- Generate 2–3 bullet coaching suggestions via OpenAI `gpt-4o-mini` given the retrieved context.
- Provide a separate cluster-suggestion path that generates instructor-facing feedback for a mistake cluster from [[analytics]].
- Cache suggestions keyed by session + student / cluster, with clear-cache helpers for when data refreshes.
- Degrade gracefully: all optional dependencies are loaded via `_lazy_import()`; absence disables RAG rather than crashing.

## Key functions / classes

- `build_rag_collection(df, session_id)` — builds or returns the per-session Chroma collection.
- `generate_assistant_suggestions(df, student_id, session_id, ...)` — per-student coaching bullets.
- `generate_cluster_suggestions(cluster, question_id, session_id, ...)` — cluster-level coaching bullets.
- `clear_suggestion_cache()` · `clear_cluster_suggestion_cache()`
- `_extract_bullets(parsed)` — normalises the LLM response into a bullet list.

## Dependencies

- Lazy: `chromadb`, `sentence_transformers`.
- Eager: `openai`, `pandas`.
- Imports [[config]] for RAG settings and [[paths]] for `rag_chroma_dir()`.
- Consumed by [[assistant_app]] (per-student) and [[views]] / [[components]] (per-cluster).

## Related notes

- [[Phase 9 RAG Suggested Feedback for Question Clusters]]
- [[ChromaDB]] · [[Sentence-Transformers]] (candidate library notes)
