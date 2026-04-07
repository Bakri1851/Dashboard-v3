# Data Loading and Session Persistence

`data_loader.py` is the gateway between raw submission data, filtered dashboard data, and locally persisted session history. It is one of the most important modules because both dashboards rely on its output shape and because saved sessions are restored through it.

Related: [[Data Pipeline]], [[Instructor Dashboard]], [[Setup and Runbook]], [[Known Issues]]

## Loading responsibilities

- Fetch raw API data with short-lived caching.
- Detect JSON vs XML and parse whichever format is present.
- Normalize records into a single DataFrame schema.
- Reuse the existing DataFrame when the raw-response hash is unchanged.

## Saved-session responsibilities

- `load_saved_sessions()` reads, validates, de-duplicates, and sorts saved sessions.
- `save_session_record()` upserts one session record by ID.
- `delete_session_record()` removes a saved session from local storage.
- `build_session_record_from_state()` snapshots the instructor's current session and filter context.
- `apply_saved_session_to_state()` restores a saved session into `st.session_state`.

## Failure handling

- API failures return an empty DataFrame plus an error message.
- Corrupt saved-session JSON is backed up and reset.
- Missing or invalid saved-session time windows trigger warnings and fall back to broader data visibility.

## Filters exposed here

- Module filter.
- Manual date/time window filter.
- Live session start filter.
- Saved session start/end window filter.

## Code references

- `code/learning_dashboard/data_loader.py`: `load_data()`
- `code/learning_dashboard/data_loader.py`: `load_saved_sessions()`, `save_session_record()`, `delete_session_record()`
- `code/learning_dashboard/data_loader.py`: `build_session_record_from_state()`, `apply_saved_session_to_state()`
- `code/learning_dashboard/data_loader.py`: `filter_by_module()`, `filter_by_time()`, `filter_by_session_start()`, `filter_by_datetime_window()`
- `data/saved_sessions.json`
