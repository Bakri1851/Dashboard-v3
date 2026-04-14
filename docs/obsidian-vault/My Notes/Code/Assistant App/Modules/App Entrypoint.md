Part of [[Assistant App]] · see also [[Lab App/Modules/App Entrypoint]]

# Assistant App — App Entrypoint

The assistant app entrypoint is intentionally thin, while the real implementation lives under `learning_dashboard/`. This gives a stable launch command for Streamlit while letting the internal package evolve without changing how the app is started.

Related: [[Project Overview]], [[Architecture]], [[Lab Assistant System]]

## Entry strategy

- `code/lab_app.py` imports `learning_dashboard.assistant_app.main` and calls it.
- This keeps external launch commands simple while centralizing behavior inside the `assistant_app` module.

## Join flow

The assistant app `main()` routes to one of four views depending on session state and URL:
1. Reads `data/lab_session.json` to determine if a session is active.
2. Reads the `aid` query parameter to restore assistant identity.
3. Routes to join, waiting, or assigned views accordingly.

## Code references

- `code/lab_app.py`
- `code/learning_dashboard/__init__.py`
- `code/learning_dashboard/assistant_app.py`
