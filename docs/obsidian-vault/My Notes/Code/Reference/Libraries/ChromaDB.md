---
tags: [library, chromadb, rag, vector-db, phase9]
status: ✅ Active
date: 2026-04-14
---

# ChromaDB

Vector database used for the Phase 9 RAG pipeline. Stores and retrieves embedded Q&A + feedback documents by semantic similarity.

---

## Usage in this project

- **Module:** `code/learning_dashboard/rag.py`
- **Storage path:** `data/rag_chroma/` (created by `paths.rag_chroma_dir()`)
- **Collection per session:** `session_{session_id}`
- **Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers`

---

## Key API

### PersistentClient

```python
import chromadb
client = chromadb.PersistentClient(path="data/rag_chroma/")
```

Persists collections across process restarts — an assistant reconnecting mid-session reuses prebuilt embeddings.

### get_or_create_collection / delete_collection

```python
collection = client.get_or_create_collection(name="session_abc123")
client.delete_collection(name="session_abc123")  # clear on session change
```

### upsert

```python
collection.upsert(
    ids=["id1", "id2"],
    embeddings=[[0.1, ...], [0.2, ...]],
    documents=["doc1", "doc2"],
    metadatas=[{"student_id": "u1", "question": "Q1", "incorrectness": 0.8}, ...],
)
```

### query with metadata filter

```python
results = collection.query(
    query_texts=["what should I check with this student?"],
    n_results=5,
    where={"student_id": "u123"},   # enforces student privacy (NFR5)
)
# returns: {"documents": [[...]], "metadatas": [[...]], "distances": [[...]]}
```

---

## Privacy note

The `where={"student_id": student_id}` filter in every query ensures only the assigned student's data is retrieved — no cross-student leakage. This satisfies NFR5 in the requirements.

---

## First-run cost

The embedding model (`all-MiniLM-L6-v2`) is downloaded on first use (~90 MB) from Hugging Face. Subsequent runs use the local `~/.cache/torch/sentence_transformers/` cache.

---

## Related notes

- [[rag.py — RAG Engine and ChromaDB Interface]]
- [[RAG Pipeline - Two-Layer Retrieval]]
- [[RAG Architecture]]
