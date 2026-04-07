# Architecture

Dashboard-v3 is split into two Streamlit entrypoints that share analytics logic but differ in responsibility: the instructor app owns filtering, routing, and orchestration, while the assistant app is a mobile client over shared lab-session state. Most behavior lives in the `learning_dashboard` package, with local JSON files used for runtime persistence and cross-process coordination.

Related: [[Project Overview]], [[Data Pipeline]], [[Instructor Dashboard]], [[Lab Assistant System]], [[UI System]]

## System shape

- `code/app.py` -> `learning_dashboard.instructor_app.main()`
- `code/lab_app.py` -> `learning_dashboard.assistant_app.main()`
- `code/learning_dashboard/data_loader.py` owns ingest, normalization, filters, and saved-session persistence.
- `code/learning_dashboard/analytics.py` owns incorrectness scoring, struggle/difficulty scoring, collaborative filtering, and mistake clustering.
- `code/learning_dashboard/lab_state.py` owns cross-process assistant/session state through a file lock and JSON file.
- `code/learning_dashboard/ui/` owns views, reusable components, CSS, and browser-side sound injection.

## State ownership

- Instructor UI state lives in `st.session_state`.
- Assistant identity is restored from the `aid` query parameter.
- Shared instructor/assistant coordination state lives in `data/lab_session.json`.
- Saved session history lives in `data/saved_sessions.json`.
- API fetch results and analytics outputs are cached in Streamlit session state plus small in-process module caches.

## Control flow

1. The instructor app initializes session defaults and theme.
2. It loads and normalizes API data through `data_loader.load_data()`.
3. Deferred saved-session or return-to-live actions are applied before widgets are rebuilt.
4. Sidebar filters scope the data, analytics are computed or reused, and routing sends the user to a dashboard page or drill-down.
5. The assistant app reads `data/lab_session.json`, restores the assistant ID from the URL, then routes to join, waiting, or assigned views.

## Key architectural boundaries

- The analytics layer is UI-independent but still reaches OpenAI and stores in-process caches.
- The UI layer depends on analytics outputs and session state, but does not own parsing or persistence.
- The assistant system is intentionally disk-backed rather than server-backed, which keeps setup simple but ties correctness to file locking and refresh cadence.

## Code references

- `code/app.py`
- `code/lab_app.py`
- `code/learning_dashboard/instructor_app.py`: `main()`, `render_sidebar()`, `init_session_state()`
- `code/learning_dashboard/assistant_app.py`: `main()`
- `code/learning_dashboard/data_loader.py`: `load_data()`
- `code/learning_dashboard/analytics.py`
- `code/learning_dashboard/lab_state.py`
