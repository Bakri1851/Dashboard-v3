---
tags: [assistant-app, rag, meeting3]
date: 2026-04-08
status: ✅ Implemented
source: FYP Meeting 3 — Dr. Batmaz
---

# RAG Architecture

## Concept: Dr. Batmaz's Hybrid Design

Hybrid RAG combining structured pre-filtering with ChromaDB vector search.
Described as "very innovative" — fewer pipeline steps than standard RAG.
![[Pasted image 20260414004425.png]]

### Layer 1 — Structured Pre-filter

```python
student_df = df[df["user"] == student_id]
```

Conceptually the "SQL" step from Dr. Batmaz's design. Implemented as a pandas filter since the session data is already in-memory; the SQL framing is retained in the dissertation as the architectural concept.

### Layer 2 — ChromaDB Vector Search

- Embed: Q&A data, AI feedback strings, incorrectness scores
- Metadata filters: `student_id`, `question`, `incorrectness`
- Flow: pre-filter → ChromaDB semantic search → LLM recommendation
- Store: `chromadb.PersistentClient` at `data/rag_chroma/`
- Collection naming: `session_{session_id}`
- Embedding model: `all-MiniLM-L6-v2` (sentence-transformers, local, no API cost)

See [[rag.py — RAG Engine and ChromaDB Interface]] for implementation.

## Reference Videos (watched)

- https://youtu.be/QSW2L8dkaZk
- https://youtu.be/cm2Ze2n9lxw

## Credit

Dr. Batmaz designed this architecture — must be acknowledged in dissertation.

## Completed Actions

- [x] Install chromadb, add to requirements.txt
- [x] Build pre-filter layer from session data (pandas `df[df["user"] == student_id]`)
- [x] Build ChromaDB collection, embed Q&A + feedback strings
- [x] Wire LLM recommendation output (GPT-4o-mini, 2–3 bullet points)
- [ ] Write dissertation justification
- [ ] Add RAG + ChromaDB literature review subsection
