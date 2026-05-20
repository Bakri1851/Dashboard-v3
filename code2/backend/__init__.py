"""FastAPI backend for V2 (the code2 React + FastAPI frontend).

Imported module-path: `backend.*` when uvicorn runs with `--app-dir code2`.
Contains both the HTTP layer and the analytical core:

HTTP layer:
    main.py · cache.py · schemas.py · deps.py · runtime_config.py · demo_data.py
    routers/  (12 router files exposing /api/*)

Analytical core (carved from the old monolithic `analytics.py` during the
2026-05-20 modularity split):
    incorrectness.py — OpenAI batched scoring + disk-persisted cache + feedback confidence
    struggle.py      — 7-signal baseline student struggle + Bayesian shrinkage
    difficulty.py    — 5-signal baseline question difficulty + within-module normalisation
    collab.py        — collaborative-filtering similar-students lookup
    clustering.py    — TF-IDF + KMeans mistake clustering + OpenAI cluster labelling
    analytics.py     — shared helpers: _get_openai_client, min_max_normalize,
                       min_max_normalize_grouped, classify_score, apply_temporal_smoothing
    rag.py           — retrieval-augmented feedback layer (ChromaDB + sentence-transformers)
    data_loader.py · lab_state.py · config.py · paths.py · academic_calendar.py · lab_classes.py
    models/          — irt.py · bkt.py · improved_struggle.py · measurement.py

These are the same algorithms V1 packages as `code/learning_dashboard/`,
flattened directly into `backend/` since the FastAPI process is itself the
analytical backend.
"""
