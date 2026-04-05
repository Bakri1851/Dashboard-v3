# App Entrypoints and Packaging

The repo keeps its root entrypoints intentionally thin, while the real implementation lives under `learning_dashboard/`. This gives stable launch commands for Streamlit while letting the internal package evolve without changing how the app is started.

Related: [[Project Overview]], [[Architecture]], [[Instructor Dashboard]], [[Lab Assistant System]]

## Entry strategy

- `app.py` imports `learning_dashboard.instructor_app.main` and calls it.
- `lab_app.py` imports `learning_dashboard.assistant_app.main` and calls it.
- This keeps external launch commands simple while centralizing behavior inside package modules.

## Package layout

- `learning_dashboard/config.py`: tunable constants only.
- `learning_dashboard/data_loader.py`: ingest, cleanup, filters, saved sessions.
- `learning_dashboard/analytics.py`: scoring and clustering.
- `learning_dashboard/lab_state.py`: shared session coordination.
- `learning_dashboard/ui/`: views, reusable components, CSS, and sound helpers.

## Why the split matters

- Packaging reduces clutter in the repo root.
- Testing and refactoring are easier because the real logic is imported from named modules.
- Documentation can describe responsibilities by subsystem rather than by ad hoc script.

## Code references

- `app.py`
- `lab_app.py`
- `learning_dashboard/__init__.py`
- `learning_dashboard/instructor_app.py`
- `learning_dashboard/assistant_app.py`
