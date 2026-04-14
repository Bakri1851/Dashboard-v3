# Reference Index

Shared reference material: glossary of project-specific terms, academic calendar converter notes, and library stubs for all dependencies (current and candidate).

---

## Core references

| Note | Summary |
|------|---------|
| [[Glossary]] | Definitions of domain-specific terms used across vault notes and the codebase |
| [[Academic Period Converter]] | How `academic_calendar.py` maps submission timestamps to semester/week labels |

---

## Library notes

| Note | Summary |
|------|---------|
| [[Streamlit]] | App framework; `@st.cache_data`, `session_state`, widget lifecycle |
| [[Plotly]] | Interactive charts; `on_select="rerun"` + `point_index` leaderboard click pattern |
| [[Pandas]] | Primary DataFrame library used across `data_loader.py` and `analytics.py` |
| [[NumPy]] | Numerical operations; used in scoring normalisation and BKT/IRT calculations |
| [[Requests]] | HTTP client for API fetch in `data_loader.py` |
| [[Streamlit Autorefresh]] | `st_autorefresh` component wiring for live-session polling |
| [[Filelock]] | File-locking mechanism for `lab_session.json` shared between both apps |
| [[OpenAI]] | `gpt-4o-mini` incorrectness scoring; batch caching pattern in `analytics.py` |
| [[Scikit-learn]] | K-means clustering for mistake clustering; cosine similarity for CF |
| [[Optuna]] | 🔲 Candidate — TPE hyperparameter optimisation for weight tuning (future work) |
| [[SHAP]] | 🔲 Candidate — Shapley feature importance values; addresses circular reasoning in tornado plots |
| [[Polars]] | 🔲 Candidate — Rust-backed DataFrame library; Pandas replacement for large sessions |
| [[MLflow]] | 🔲 Candidate — Experiment tracking for Optuna weight-optimisation trials |
| [[SentenceTransformers]] | 🔲 Candidate — Local sentence embeddings for ChromaDB RAG (vs OpenAI embeddings) |

---

Part of [[Code Index]]
