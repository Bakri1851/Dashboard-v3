Part of [[Lab App]] - see also [[Setup and Runbook]]

# Saved Session History

Saved-session history covers how the instructor stores, reloads, deletes, and exits historic lab windows. The visible UI lives in the sidebar and the `Previous Sessions` page, while the actual session records are built and restored in `data_loader.py`.

Related: [[Pages and UI Flow]], [[Instructor Dashboard]], [[Data Loading and Session Persistence]], [[Live Assistant Assignment]]

## Entry points

- A live session can be saved when it ends, using the current session timing and filter context.
- The sidebar also exposes `Save Current Session`, which opens a small retroactive-save form for the current time-filter window.
- `Open Previous Sessions` switches `current_view` to the history page, where saved records can be browsed, filtered, loaded, and deleted.
- When a saved session is loaded, the sidebar offers `Back to Live Data` to clear the loaded-session state and return to normal live filtering.

## Record types

- `build_session_record_from_state()` captures an actual live session using `session_start`, the end time, duration, and the instructor's current dashboard/module/time-filter context.
- `build_retroactive_session_record()` creates a manual record from the selected date/time window and marks it as a retroactive save in `notes`.
- Both record types are persisted as JSON objects with an `id`, `name`, `start_time`, `end_time`, `duration_seconds`, `context`, and `notes`.

## Previous Sessions page behavior

- `previous_sessions_view()` loads saved records newest-first and lets the instructor filter them by academic period.
- Each session card shows the stored time window, duration, dashboard view, module filter, and whether the time filter was enabled when the record was created.
- `Load` defers restoration by storing the record in `pending_session_load_record`; the actual state mutation is applied in `main()` before widgets rebuild.
- `Delete` uses a confirmation step and clears the loaded-session markers if the deleted record is the one currently being viewed.

## Restoration and filtering rules

- `apply_saved_session_to_state()` restores `dashboard_view`, module filter, time-filter settings, loaded-session ID, and the saved datetime window into `st.session_state`.
- Loading a saved session forces `session_active` off, clears student/question drill-down selections, and routes the UI back to `In Class View`.
- While a saved session is loaded, the instructor data is filtered by the stored start/end window rather than by the normal live-session start logic.
- Returning to live data clears the loaded-session window, resets filters to the default live state, and restores the dashboard to `In Class View`.

## Storage and failure handling

- Saved history is stored in `data/saved_sessions.json`.
- `load_saved_sessions()` de-duplicates by session ID and sorts by `end_time` descending.
- If a saved module filter no longer exists or a saved time window is invalid, restoration falls back to safer defaults and records a warning in `session_load_warning`.

## Code references

- `code/learning_dashboard/ui/views.py`: `previous_sessions_view()`
- `code/learning_dashboard/instructor_app.py`: `render_sidebar()`, `main()`
- `code/learning_dashboard/data_loader.py`: `load_saved_sessions()`, `save_session_record()`, `delete_session_record()`, `build_session_record_from_state()`, `build_retroactive_session_record()`, `apply_saved_session_to_state()`
- `data/saved_sessions.json`
