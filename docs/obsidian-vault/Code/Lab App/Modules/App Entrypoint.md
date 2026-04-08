Part of [[Lab App]] · see also [[Assistant App/Modules/App Entrypoint]]

# Lab App — App Entrypoint

The instructor app entrypoint is intentionally thin, while the real implementation lives under `learning_dashboard/`. This gives a stable launch command for Streamlit while letting the internal package evolve without changing how the app is started.

Related: [[Project Overview]], [[Architecture]], [[Instructor Dashboard]]

## Entry strategy

- `code/app.py` imports `learning_dashboard.instructor_app.main` and calls it.
- This keeps external launch commands simple while centralizing behavior inside the `instructor_app` module.

## Package layout

- `code/learning_dashboard/config.py`: tunable constants only.
- `code/learning_dashboard/data_loader.py`: ingest, cleanup, filters, saved sessions.
- `code/learning_dashboard/analytics.py`: scoring and clustering.
- `code/learning_dashboard/lab_state.py`: shared session coordination.
- `code/learning_dashboard/ui/`: views, reusable components, CSS, and sound helpers.

## Why the split matters

- Code lives under `code/`, report under `Report/` — clear separation by artifact type.
- Testing and refactoring are easier because the real logic is imported from named modules.
- Documentation can describe responsibilities by subsystem rather than by ad hoc script.

## Code references

- `code/app.py`
- `code/learning_dashboard/__init__.py`
- `code/learning_dashboard/instructor_app.py`
