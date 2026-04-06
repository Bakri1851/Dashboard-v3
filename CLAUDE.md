# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Streamlit-based learning analytics dashboard for monitoring student struggle and question difficulty during university lab sessions. Two cooperating apps share live state through a file-locked JSON file on disk.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run instructor dashboard (port 8501)
python -m streamlit run app.py

# Run mobile lab assistant app (port 8502)
streamlit run lab_app.py --server.port 8502

# Syntax check all source files
python -m py_compile app.py lab_app.py learning_dashboard/*.py learning_dashboard/ui/*.py
```

There are no automated tests. Validation is manual smoke testing (see README.md checklist).

## Architecture

### Two-app system
- `app.py` and `lab_app.py` are thin wrappers delegating to `learning_dashboard/instructor_app.py` and `learning_dashboard/assistant_app.py`
- Both share state via `data/lab_session.json`, managed through `learning_dashboard/lab_state.py` with `filelock`

### Package layout (`learning_dashboard/`)
- `config.py` — all tunable constants (weights, thresholds, colors, API config). Start here for parameter changes.
- `data_loader.py` — API fetch, JSON/XML parsing, normalization, saved-session persistence
- `analytics.py` — scoring engine: incorrectness (OpenAI), student struggle, question difficulty, collaborative filtering, mistake clustering
- `models/` — alternative/improved models: IRT difficulty (`irt.py`), BKT mastery (`bkt.py`), improved struggle (`improved_struggle.py`), measurement confidence (`measurement.py`). Toggled via `improved_models_enabled` in Settings.
- `lab_state.py` — file-locked shared lab-session state (no Streamlit imports)
- `paths.py` — project/runtime paths and legacy-file migration
- `ui/views.py` — page-level views (in_class, student_detail, question_detail, data_analysis, settings, previous_sessions)
- `ui/components.py` — reusable Streamlit UI building blocks
- `ui/theme.py` — CSS and Plotly theme defaults

### Key data flow
1. `instructor_app.main()` initializes session state and applies deferred actions (before widgets)
2. `data_loader.load_data()` fetches from API with `@st.cache_data(ttl=10)`, parses, normalizes
3. Sidebar filters applied in order: manual time → live session start → saved session window
4. Routing sends filtered DataFrame to the appropriate view

### Deferred actions pattern
Streamlit cannot mutate `st.session_state` after widget instantiation in the same run. This repo uses `pending_*` flags (e.g., `pending_session_load_record`, `pending_return_to_live_data`) applied at the top of `main()` before sidebar widgets render.

## Important Conventions

- Thresholds are `list[tuple[float, float, str, str]]` — (low, high, label, color) for dynamic classification
- Scoring uses min-max normalization that returns 0 when min==max
- Substring matching: "correct" intentionally matches inside "incorrect" (by design)
- `_incorrectness_cache` in analytics.py avoids repeat OpenAI calls within a process
- Session code is 6-char alphanumeric excluding O/0/I/1 to avoid confusion
- Lab assistant identity persisted via URL `?aid=` query param
- OpenAI API key stored in `.streamlit/secrets.toml`
- Runtime data lives in `data/` (auto-migrated from repo root on first run)
