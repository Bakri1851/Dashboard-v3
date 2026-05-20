"""FastAPI backend for V2 (the code2 React + FastAPI frontend).

Imported module-path: `backend.*` when uvicorn runs with `--app-dir code2`.
Contains both the HTTP layer (main.py, cache.py, schemas.py, deps.py,
runtime_config.py, demo_data.py, routers/) AND the analytical core
(analytics.py, data_loader.py, lab_state.py, config.py, paths.py,
academic_calendar.py, rag.py, lab_classes.py, models/) — the same algorithms
V1 packages as `code/learning_dashboard/`, flattened directly into `backend/`
since the FastAPI process is itself the analytical backend.
"""
