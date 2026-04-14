---
name: OpenAI
description: OpenAI API client used for incorrectness scoring and mistake-cluster labelling
type: reference
---

# OpenAI

Official Python client for the OpenAI API.

## Version

`openai >= 1.0.0`

## Why this library

Every submission carries an `ai_feedback` string produced by the upstream backend tutor. Converting that feedback into a numeric incorrectness score requires semantic understanding — rule-based string matching misses nuance (e.g., partially correct answers, hedged feedback). `gpt-4o-mini` provides sufficient quality at low cost and latency. The same client is reused for labelling mistake clusters, keeping the external dependency count low.

## Where used

- `code/learning_dashboard/analytics.py` — incorrectness scoring and cluster labelling
- `code/learning_dashboard/rag.py` — final-step generation (2–3 coaching bullets via GPT-4o-mini); reuses `_get_openai_client()` from analytics, not duplicated. See [[RAG Pipeline - Two-Layer Retrieval]].

## Key usage

```python
from openai import OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
```

The API key is read from `.streamlit/secrets.toml` via `st.secrets` — never hardcoded.

### Incorrectness scoring

- Function: `estimate_incorrectness` / `compute_incorrectness_column`
- Model: `gpt-4o-mini` (`config.OPENAI_MODEL`)
- Temperature: `0` (deterministic)
- Batching: up to `50` feedback strings per API call (`config.OPENAI_BATCH_SIZE`) to reduce round trips
- Output: float in `[0, 1]` per feedback string
- Fallback: `0.5` for empty/null feedback or API failure
- Cache: `_incorrectness_cache` (module-level dict) avoids re-scoring the same feedback text within a process lifetime

### Mistake-cluster labelling

- Function: `_label_clusters_with_openai`
- Called after K-means clustering to name each cluster with a short, human-readable label
- Single API call per question drill-down (all clusters labelled in one request)
- Fallback: generic names (`"Cluster 1"`, `"Cluster 2"`, ...) if the API call fails

## Cost considerations

Incorrectness scoring fires once per unique feedback string per process restart. The in-process cache means repeated dashboard views of the same data make no additional API calls. Cluster labelling fires once per question drill-down per process lifetime (cached in `_cluster_cache`).

## Related

- [[Analytics Engine]]
- [[Student Struggle Logic]]
- [[Configuration and Runtime Paths]]
