---
tags: [assistant-app, rag, placeholder, meeting3]
date: 2026-04-08
status: 🔲 Placeholder — not yet implemented
source: FYP Meeting 3 — Dr. Batmaz
---

# RAG Architecture

> ⚠️ **Placeholder** — Not yet implemented.
> Recorded from Meeting 3 (2026-04-08) for planning purposes only.

## Concept: Dr. Batmaz's Hybrid Design

Hybrid RAG combining SQL structured retrieval with ChromaDB vector search.
Described as "very innovative" — fewer pipeline steps than standard RAG.

### Layer 1 — SQL Pre-filter (planned)

```sql
SELECT ... FROM session_logs WHERE student_id = ? LIMIT 10
```

### Layer 2 — ChromaDB Vector Search (planned)

- Embed: Q&A data, AI feedback strings, struggle scores
- Metadata filters: student_id, session_id, question_id
- Flow: SQL pre-filter → ChromaDB semantic search → LLM recommendation
- Store: chromadb.PersistentClient

## Reference Videos (watched, not yet acted on)

- https://youtu.be/QSW2L8dkaZk
- https://youtu.be/cm2Ze2n9lxw

## Credit

Dr. Batmaz designed this architecture — must be acknowledged in dissertation.

## Planned Actions (none started)

- [ ] Install chromadb, add to requirements.txt
- [ ] Build SQL pre-filter layer from session data
- [ ] Build ChromaDB collection, embed Q&A + feedback strings
- [ ] Wire LLM recommendation output
- [ ] Write dissertation justification
- [ ] Add RAG + ChromaDB literature review subsection
