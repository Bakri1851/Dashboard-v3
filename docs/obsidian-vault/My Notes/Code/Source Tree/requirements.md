# requirements.txt

**Path:** `code/requirements.txt`
**Folder:** [[code]]

> Pinned Python dependencies for both Streamlit apps.

## Contents

| Package | Min version | Used by | Note |
|---------|-------------|---------|------|
| `streamlit` | 1.32.0 | everything | UI runtime |
| `streamlit-autorefresh` | 1.0.1 | [[instructor_app]], [[assistant_app]] | Auto-refresh widget |
| `plotly` | 5.18.0 | [[components]], [[theme]] | All charts |
| `pandas` | 2.1.0 | [[data_loader]], [[analytics]], models/* | DataFrame core |
| `numpy` | 1.26.0 | [[analytics]], [[bkt]], [[irt]], [[improved_struggle]] | Numerics |
| `requests` | 2.31.0 | [[data_loader]] | API fetch |
| `filelock` | 3.12.0 | [[lab_state]] | Cross-process state locking |
| `openai` | 1.0.0 | [[analytics]], [[rag]] | Incorrectness scoring + cluster labelling + RAG suggestions |
| `scikit-learn` | 1.4.0 | [[analytics]] | TF-IDF, K-means, silhouette, cosine similarity |
| `chromadb` | 0.4.0 | [[rag]] | Vector store for RAG (lazy import — optional at runtime) |
| `sentence-transformers` | 2.2.0 | [[rag]] | Local embedding model (lazy import — optional at runtime) |

## Install

```bash
pip install -r code/requirements.txt
```

## Related notes

- [[OpenAI]] · [[Scikit-learn]] · [[Streamlit]] (library notes)
- [[Setup and Runbook]]
