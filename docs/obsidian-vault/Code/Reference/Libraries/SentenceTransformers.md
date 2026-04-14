---
tags: [library, embeddings, rag, phase9]
status: ✅ Active
date: 2026-04-14
---

# SentenceTransformers

Python library for generating dense sentence embeddings using pre-trained transformer models. Open-source, runs locally, no API cost.

## Version

`sentence-transformers >= 2.2.0`

## Where used

- `code/learning_dashboard/rag.py` — generates document embeddings for the ChromaDB RAG pipeline. Imported lazily so the rest of the app keeps working if this library is not installed.

## Model used

`all-MiniLM-L6-v2` — configured in `config.RAG_EMBEDDING_MODEL`.

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(documents, show_progress_bar=False)
```

## First-run cost

~90 MB download from Hugging Face on first use. Cached at `~/.cache/torch/sentence_transformers/` — subsequent runs are instant.

## Trade-off vs OpenAI embeddings

OpenAI embeddings generally have higher quality but incur API cost per token. `all-MiniLM-L6-v2` is free, local, and sufficient for matching Q&A feedback strings within a single lab session. Worth noting in Ch3/Ch4 implementation justification.

## Related

- [[rag.py — RAG Engine and ChromaDB Interface]]
- [[ChromaDB]]
- [[RAG Pipeline - Two-Layer Retrieval]]
