# Learning Analytics Dashboard - Developer Guide

## What this repository is
This repository contains a Streamlit dashboard used during lab sessions to track:
- student struggle (leaderboard + drill-down)
- question difficulty (leaderboard + drill-down)
- live and saved session filtering

This `README.md` is the main source of truth for understanding how the code is organized and how to work on it.

## Tech stack
- Python 3.11+
- Streamlit
- Plotly
- Pandas / NumPy
- Requests

Dependencies are listed in `requirements.txt`.

## Quick start
1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Run the app:
```bash
python -m streamlit run app.py
```
3. Open the local Streamlit URL shown in terminal.

## Repository map
- `app.py`: entry point, session state initialization, sidebar controls, routing, and filter application order.
- `views.py`: page-level views (`In Class`, `Data Analysis`, `Settings`, and drill-down views).
- `components.py`: reusable UI building blocks (leaderboards, cards, tables, charts, formula panel).
- `theme.py`: global CSS and Plotly theme defaults.
- `analytics.py`: scoring engine (incorrectness, struggle score, difficulty score, classification).
- `data_loader.py`: API fetch/parse/clean pipeline plus saved session persistence helpers.
- `config.py`: all tunable constants (weights, thresholds, colors, limits, API config).
- `saved_sessions.json`: local storage for saved sessions created when ending a lab session.
- `README.md`: developer onboarding, architecture, and workflows.

## Runtime flow
1. `app.py:main()` initializes Streamlit and session state.
2. Data is loaded using `data_loader.load_data()`:
- fetch API payload (cached)
- detect JSON vs XML
- parse and normalize fields
- clean modules and timestamps
3. Pending deferred actions are applied before widgets are built:
- pending saved-session load
- pending return to live data
4. Sidebar is rendered and filters are applied in this order:
- manual time filter
- active live-session start-time filter
- loaded saved-session start/end window filter
5. Routing sends filtered data to:
- student detail
- question detail
- in-class view
- data analysis view
- settings view

## Scoring model locations
- Incorrectness estimation: `analytics.py:estimate_incorrectness`
- Student struggle score: `analytics.py:compute_student_struggle_scores`
- Question difficulty score: `analytics.py:compute_question_difficulty_scores`
- Level classification helper: `analytics.py:classify_score`
- Weights and thresholds: `config.py`

If you need to change model behavior, start in `config.py`, then update `analytics.py` only if logic must change.

## Session behavior
There are two session concepts:

1. Live session:
- Started with `Start Lab Session` in sidebar
- Uses `session_start` to filter current data
- Ended with `End Session`
- Automatically saved to `saved_sessions.json`

2. Saved session:
- Loaded from Settings -> Saved Sessions
- Applies a fixed start/end datetime window from saved record
- Can be exited with `Back to Live Data` in sidebar

### Why deferred actions exist
Streamlit does not allow changing certain `st.session_state` keys after their widgets are instantiated in the same run.  
This repo uses deferred flags/records (for example `pending_session_load_record`) that are applied near the top of `main()` before sidebar widgets are created.

## Saved session schema
Saved sessions are stored in `saved_sessions.json`:

```json
{
  "version": 1,
  "sessions": [
    {
      "id": "uuid",
      "name": "Lab Session 2026-02-07 17:00",
      "created_at": "2026-02-07T18:10:00",
      "start_time": "2026-02-07T17:00:00",
      "end_time": "2026-02-07T18:10:00",
      "duration_seconds": 4200,
      "context": {
        "dashboard_view": "In Class View",
        "secondary_module_filter": "All Modules",
        "time_filter_enabled": false,
        "time_date_range": null,
        "time_start": null,
        "time_end": null
      },
      "notes": ""
    }
  ]
}
```

Persistence helpers live in `data_loader.py`:
- `load_saved_sessions`
- `save_session_record`
- `delete_session_record`
- `build_session_record_from_state`
- `apply_saved_session_to_state`

## Important session state keys
Key runtime state in `app.py:init_session_state()`:

| Key | Purpose |
|---|---|
| `current_view` | Active page (`In Class View`, `Data Analysis View`, `Settings`) |
| `dashboard_view` | Sidebar-selected dashboard view |
| `selected_student` | Drill-down target user ID |
| `selected_question` | Drill-down target question ID |
| `session_active` | Whether live session is running |
| `session_start` | Datetime for live-session filter start |
| `loaded_session_id` | Currently loaded saved session ID |
| `loaded_session_start` / `loaded_session_end` | Datetime window for saved-session filter |
| `pending_session_load_record` | Deferred saved-session load payload |
| `pending_return_to_live_data` | Deferred reset back to unfiltered live mode |
| `time_filter_enabled` | Manual date/time filter toggle |

## Common change recipes
### Add a new chart to existing pages
1. Add reusable chart renderer in `components.py`.
2. Call it from the target view in `views.py`.
3. Keep styling aligned with `theme.get_plotly_layout_defaults()`.

### Add new sidebar filters
1. Add state defaults in `app.py:init_session_state`.
2. Add widget in `app.py:render_sidebar`.
3. Apply filter in the existing precedence chain in `render_sidebar`.
4. Confirm interaction with live/saved session filters.

### Modify thresholds/labels/colors
1. Update constants in `config.py`.
2. Confirm `analytics.classify_score` behavior still matches intended boundaries.
3. Verify formula panel and leaderboard colors.

### Extend saved session metadata
1. Update `build_session_record_from_state` in `data_loader.py`.
2. Update `apply_saved_session_to_state` in `data_loader.py`.
3. Update Settings session list rendering in `views.py`.

## Validation checklist
Run syntax checks:
```bash
python -m py_compile app.py config.py views.py theme.py components.py analytics.py data_loader.py
```

Manual smoke tests:
1. App loads data successfully.
2. Start and end live session.
3. Saved session appears in Settings.
4. Load saved session and verify data is scoped to session time window.
5. Use `Back to Live Data` and verify full live data returns.
6. Delete a saved session and confirm it is removed.
7. Toggle leaderboard legend categories and confirm no blank middle gaps appear.

## Troubleshooting notes
- If loading a saved session shows all data, check `loaded_session_start` and `loaded_session_end` are populated.
- If Streamlit raises widget-state mutation errors, verify state mutation happens in deferred phase near top of `main()`.
- If API fails, the app shows an error and stops outside Settings.
- If `saved_sessions.json` is corrupted, loader resets it and can back up a corrupt copy automatically.

## Known implementation note
`data_loader.load_data()` is used as returning a `DataFrame` in `app.py`.  
If you rely on type hints/docstrings there, check real usage first before refactoring.
