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

### How it works

The same ChromaDB collection feeds **two query paths** — one for the assistant app (`generate_assistant_suggestions`, filters by `student_id`) and one for the instructor dashboard (`generate_cluster_suggestions`, filters by `question` and is fed by the mistake-cluster analytics). Both are implemented in [[rag.py — RAG Engine and ChromaDB Interface]].

```mermaid
flowchart TD
    df["session DataFrame<br/>(question, student_answer,<br/>ai_feedback, incorrectness)"]

    subgraph index["Indexing path — build_rag_collection (once per session)"]
        chunk["Chunk text<br/>'{question} | {student_answer} | {ai_feedback}'"]
        embed["Embed<br/>all-MiniLM-L6-v2<br/>(local, no API)"]
        upsert["Upsert into collection<br/>session_{session_id}<br/>metadata: student_id, question, incorrectness"]
        store[("ChromaDB<br/>data/rag_chroma/")]
    end

    subgraph assistant["Assistant path — generate_assistant_suggestions (per student assignment)"]
        assign["Student assigned<br/>student_id"]
        l1a["Layer 1 — pandas pre-filter<br/>df[df['user'] == student_id]<br/>→ student_df"]
        l2a["Layer 2 — ChromaDB semantic search<br/>where={'student_id': student_id}<br/>→ top-k chunks, sorted by incorrectness"]
        gena["GPT-4o-mini<br/>tutoring prompt<br/>(struggle + top-3 questions + snippets)"]
        outa["2–3 coaching bullets<br/>(≤15 words each)"]
        cachea["_suggestion_cache<br/>+ session_state['cached_suggestions']"]
        panela["Assistant app UI<br/>'Suggested Focus Areas'"]
    end

    subgraph instructor["Instructor path — generate_cluster_suggestions (per question view)"]
        qsel["Question opened<br/>question_id"]
        l1i["Layer 1 — pandas pre-filter<br/>df[df['question'] == question_id]<br/>+ analytics.cluster_question_mistakes<br/>→ top-3 misconception clusters"]
        l2i["Layer 2 — ChromaDB semantic search<br/>where={'question': question_id}<br/>→ top-k chunks across all students"]
        geni["GPT-4o-mini<br/>teaching prompt<br/>(clusters + snippets)"]
        outi["2–3 teaching-feedback bullets<br/>(≤15 words each)"]
        cachei["_cluster_suggestion_cache<br/>+ session_state['cached_cluster_suggestions']"]
        paneli["Instructor question detail UI<br/>'Suggested Teaching Feedback'"]
    end

    df --> chunk --> embed --> upsert --> store

    assign --> l1a
    df --> l1a
    l1a --> l2a
    store -.feeds.-> l2a
    l2a --> gena --> outa
    outa -.cached in.-> cachea
    cachea --> panela

    qsel --> l1i
    df --> l1i
    l1i --> l2i
    store -.feeds.-> l2i
    l2i --> geni --> outi
    outi -.cached in.-> cachei
    cachei --> paneli
```

Both paths reuse `build_rag_collection` and the same `_get_openai_client()` from `analytics.py`. Caches are cleared together on session change via `clear_suggestion_cache()` / `clear_cluster_suggestion_cache()`.

See [[RAG Pipeline - Two-Layer Retrieval]] for the code-level walk-through of the assistant path, and [[Phase 9 RAG Suggested Feedback for Question Clusters]] for the instructor cluster-feedback path.

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
