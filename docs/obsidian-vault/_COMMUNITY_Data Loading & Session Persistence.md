---
type: community
cohesion: 0.06
members: 47
---

# Data Loading & Session Persistence

**Cohesion:** 0.06 - loosely connected
**Members:** 47 nodes

## Members
- [[Absolute path to the local saved-session store.]] - rationale - code\learning_dashboard\data_loader.py
- [[Apply a saved session record onto active Streamlit state.]] - rationale - code\learning_dashboard\data_loader.py
- [[Auto-detect whether the raw response is JSON or XML.]] - rationale - code\learning_dashboard\data_loader.py
- [[Build a persisted record from the current Streamlit session state.]] - rationale - code\learning_dashboard\data_loader.py
- [[Build a session record from manual time-filter values.      Used when an instruc]] - rationale - code\learning_dashboard\data_loader.py
- [[Convert records to DataFrame and apply cleaning rules.]] - rationale - code\learning_dashboard\data_loader.py
- [[Delete one session record by ID; returns True if deleted.]] - rationale - code\learning_dashboard\data_loader.py
- [[Filter DataFrame to rows within the datetime range.]] - rationale - code\learning_dashboard\data_loader.py
- [[Filter rows to an inclusive datetime window.]] - rationale - code\learning_dashboard\data_loader.py
- [[Filter to a single module. Pass 'All Modules' or None to skip.]] - rationale - code\learning_dashboard\data_loader.py
- [[Filter to rows with timestamp = session_start.]] - rationale - code\learning_dashboard\data_loader.py
- [[GET request to the API endpoint. Cached for CACHE_TTL seconds.]] - rationale - code\learning_dashboard\data_loader.py
- [[Move corrupt session JSON aside so the app can recover safely.]] - rationale - code\learning_dashboard\data_loader.py
- [[Parse newline-delimited JSON objects with optional embedded XML.]] - rationale - code\learning_dashboard\data_loader.py
- [[Parse pure XML format PayloadsPayload...PayloadPayloads.]] - rationale - code\learning_dashboard\data_loader.py
- [[Persist a single session record to the local JSON store.]] - rationale - code\learning_dashboard\data_loader.py
- [[Return a copy of df with a boolean 'has_feedback' column.]] - rationale - code\learning_dashboard\data_loader.py
- [[Return saved session records sorted by newest end_time first.]] - rationale - code\learning_dashboard\data_loader.py
- [[Safely extract text from a child XML element.]] - rationale - code\learning_dashboard\data_loader.py
- [[Top-level fetch - detect - parse - clean. Returns (DataFrame, error_msg).]] - rationale - code\learning_dashboard\data_loader.py
- [[_backup_corrupt_saved_sessions()]] - code - code\learning_dashboard\data_loader.py
- [[_empty_saved_sessions_payload()]] - code - code\learning_dashboard\data_loader.py
- [[_parse_iso_date()]] - code - code\learning_dashboard\data_loader.py
- [[_parse_iso_datetime()]] - code - code\learning_dashboard\data_loader.py
- [[_parse_iso_time()]] - code - code\learning_dashboard\data_loader.py
- [[_read_saved_sessions_payload()]] - code - code\learning_dashboard\data_loader.py
- [[_saved_sessions_path()]] - code - code\learning_dashboard\data_loader.py
- [[_write_saved_sessions_payload()]] - code - code\learning_dashboard\data_loader.py
- [[_xml_text()]] - code - code\learning_dashboard\data_loader.py
- [[add_feedback_flag()]] - code - code\learning_dashboard\data_loader.py
- [[apply_saved_session_to_state()]] - code - code\learning_dashboard\data_loader.py
- [[build_retroactive_session_record()]] - code - code\learning_dashboard\data_loader.py
- [[build_session_record_from_state()]] - code - code\learning_dashboard\data_loader.py
- [[data_loader.py]] - code - code\learning_dashboard\data_loader.py
- [[delete_session_record()]] - code - code\learning_dashboard\data_loader.py
- [[detect_format()]] - code - code\learning_dashboard\data_loader.py
- [[fetch_raw_data()]] - code - code\learning_dashboard\data_loader.py
- [[filter_by_datetime_window()]] - code - code\learning_dashboard\data_loader.py
- [[filter_by_module()]] - code - code\learning_dashboard\data_loader.py
- [[filter_by_session_start()]] - code - code\learning_dashboard\data_loader.py
- [[filter_by_time()]] - code - code\learning_dashboard\data_loader.py
- [[load_data()]] - code - code\learning_dashboard\data_loader.py
- [[load_saved_sessions()]] - code - code\learning_dashboard\data_loader.py
- [[normalize_and_clean()]] - code - code\learning_dashboard\data_loader.py
- [[parse_json_response()]] - code - code\learning_dashboard\data_loader.py
- [[parse_xml_response()]] - code - code\learning_dashboard\data_loader.py
- [[save_session_record()]] - code - code\learning_dashboard\data_loader.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Data_Loading_&_Session_Persistence
SORT file.name ASC
```
