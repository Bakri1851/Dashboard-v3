# data_loader.py

**Path:** `code/learning_dashboard/data_loader.py`
**Folder:** [[learning_dashboard]]

> Fetches raw submissions from the API, parses JSON or XML, normalises to a DataFrame, and manages the saved-session JSON store.

## Responsibilities

- Fetch the raw API response (cached with `@st.cache_data(ttl=CACHE_TTL)`).
- Auto-detect whether the response is JSON or XML and parse accordingly, with fallback to the other format on error.
- Flatten embedded `<submission>` XML inside JSON records, pulling out `srep` (student answer) and `feedback/response` (AI feedback).
- Drop excluded modules, apply module renames, coerce timestamps, sort, and attach the academic-period column.
- Provide filter helpers: by module, by time range, by session start, by datetime window.
- Persist saved sessions — live-built records and retroactive records from manual time-filter values — with atomic writes, corruption backup, and dedupe by session ID.

## Key functions / classes

**Fetch + parse:**
- `fetch_raw_data()` — cached `GET`.
- `detect_format(raw)`, `parse_json_response(raw)`, `parse_xml_response(raw)`.
- `normalize_and_clean(records)` — returns the canonical DataFrame.
- `load_data()` → `(df, error_msg)` — top-level pipeline with hash-based skip when raw hasn't changed.

**Filters:**
- `filter_by_module`, `filter_by_time`, `filter_by_session_start`, `filter_by_datetime_window`
- `add_feedback_flag` — adds `has_feedback` bool column.

**Saved sessions:**
- `load_saved_sessions`, `save_session_record`, `delete_session_record`
- `build_session_record_from_state(now)` — from the currently-live session.
- `build_retroactive_session_record(...)` — from the manual time filter.
- `apply_saved_session_to_state(record, available_modules)` — restore a saved session onto Streamlit state.

## Dependencies

- `requests` for fetch, `pandas` for DataFrame, `xml.etree.ElementTree` for parsing.
- Imports [[config]] and [[paths]]; lazily imports [[academic_calendar]] to avoid a cycle.

## Related notes

- [[Data Loading and Session Persistence]] (thematic)
- [[Data Pipeline]]
