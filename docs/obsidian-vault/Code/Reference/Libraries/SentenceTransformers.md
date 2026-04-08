---
tags: [library, embeddings, placeholder, unused]
status: 🔲 Not yet used
---

# SentenceTransformers

> ⚠️ Not currently used. Required if ChromaDB RAG is implemented without OpenAI embeddings.

## What it is

Python library for generating dense sentence embeddings using pre-trained transformer
models (e.g. all-MiniLM-L6-v2). Open-source, runs locally, no API cost.

## Potential use in this project

Generate embeddings for the ChromaDB RAG pipeline — embed student Q&A data,
AI feedback strings, and struggle score context locally instead of calling the
OpenAI embeddings API. Reduces cost and latency for the vector store.

```python
# Sketch — not implemented
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(["Student answered incorrectly three times"])
```

## Relevant to report

Ch3/Ch4: embedding model choice for RAG pipeline.
Note trade-off: OpenAI embeddings higher quality, SentenceTransformers free and local.
