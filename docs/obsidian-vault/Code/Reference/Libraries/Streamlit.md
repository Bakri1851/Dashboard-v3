---
name: Streamlit
description: Web framework used for both the instructor dashboard and lab assistant portal
type: reference
---

# Streamlit

Python library for building interactive web apps from pure Python — no HTML, CSS, or JavaScript required.

## Version

`streamlit >= 1.32.0`

## Why this library

The entire dashboard is Python-only. Streamlit eliminates the need for a separate frontend stack while providing reactive re-rendering, a widget toolkit, and a built-in development server. It is the standard choice for Python data dashboards and has first-class Plotly support.

## Where used

- `code/app.py` — launches the instructor app via `st.` entrypoint
- `code/lab_app.py` — launches the assistant portal
- `code/learning_dashboard/instructor_app.py` — session state, sidebar widgets, routing, caching
- `code/learning_dashboard/assistant_app.py` — assistant join/waiting/assigned views, URL query params
- `code/learning_dashboard/data_loader.py` — `@st.cache_data` on API fetch; `st.secrets` for OpenAI key
- `code/learning_dashboard/analytics.py` — `st.secrets` for OpenAI key; `@st.cache_data` indirectly
- `code/learning_dashboard/ui/views.py` — all page-level rendering
- `code/learning_dashboard/ui/components.py` — all reusable UI building blocks

## Key classes and functions used

- `st.session_state` — persistent key-value store across Streamlit reruns; used for navigation state, filter state, live/saved session state, and deferred action flags
- `@st.cache_data(ttl=10)` — caches `fetch_raw_data()` for 10 seconds to avoid hammering the API on every rerun
- `st.secrets` — reads `OPENAI_API_KEY` from `.streamlit/secrets.toml` without hardcoding credentials
- `st.plotly_chart(on_select="rerun")` — makes leaderboard charts clickable; triggers a rerun with the selected point index stored in widget state
- `st.query_params` — reads and writes the `?aid=` URL parameter to persist lab assistant identity across phone browser refreshes
- `st.rerun()` — forces an immediate rerun after state mutations (e.g., after joining a session)
- `st.sidebar` — contains session controls, filters, and the live assistant roster
- `st.set_page_config()` — sets page title, icon, and wide layout in both apps
- Widget primitives: `st.selectbox`, `st.button`, `st.slider`, `st.text_input`, `st.toggle`, `st.expander`, `st.columns`, `st.metric`, `st.markdown`, `st.error`, `st.warning`, `st.success`

## Deferred actions pattern

Streamlit cannot mutate `st.session_state` keys after their widgets are instantiated in the same run. The instructor app uses `pending_*` flags (e.g., `pending_session_load_record`, `pending_return_to_live_data`) that are applied at the top of `main()` before any widgets are built. See [[Instructor Dashboard]] for full details.

## Related

- [[Instructor Dashboard]]
- [[Lab Assistant System]]
- [[UI System]]
- [[Data Loading and Session Persistence]]
- [[Analytics Engine]]
