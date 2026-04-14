# Data Pipeline

> Covers both [[Lab App]] and [[Assistant App]]

The data pipeline turns raw API payloads into a filtered DataFrame that feeds both score models and all dashboard pages. It also owns local session persistence, so the same module handles both incoming teaching data and locally stored teaching context.

Related: [[Architecture]], [[Data Loading and Session Persistence]], [[Instructor Dashboard]], [[Student Struggle Logic]], [[Question Difficulty Logic]]

## Ingest and parsing

- `fetch_raw_data()` pulls from the remote retrieval endpoint and caches the raw text for a short TTL.
- `detect_format()` distinguishes newline-delimited JSON from XML.
- `parse_json_response()` handles JSON records and can unpack embedded XML submission blocks inside the `xml` field.
- `parse_xml_response()` handles pure XML payloads.

## Normalization and cleaning

- `normalize_and_clean()` enforces expected columns, excludes configured modules, renames modules, coerces timestamps, drops invalid timestamps, and sorts chronologically.
- `add_feedback_flag()` adds a simple `has_feedback` boolean used in detail tables.
- `load_data()` hashes the raw response and reuses the previous DataFrame if the raw text is unchanged.

## Filter precedence

- Manual time filter runs first when enabled.
- If no manual time filter is active, a live session window applies through `session_start`.
- If neither of the above is active, a loaded saved-session window applies through `loaded_session_start` and `loaded_session_end`.
- After sidebar filtering, an extra today-only scope can still apply when the dashboard is in its default live-data state with no overriding filter.

## Local persistence

- Saved sessions are stored in `data/saved_sessions.json` with a versioned payload containing `sessions`.
- Live assistant coordination is stored separately in `data/lab_session.json`.
- ChromaDB RAG collection is stored in `data/rag_chroma/` (created by `paths.rag_chroma_dir()`). Built lazily on first assistant assignment; persists across restarts.
- `paths.py` migrates legacy root JSON files into `data/` on first access and keeps a fallback path if migration fails.

## RAG suggestion flow (Phase 9)

After the DataFrame is filtered and struggle scores are computed, the assistant app triggers a parallel enrichment step when a student is assigned:

```
Filtered DataFrame
       │
       ▼
rag.build_rag_collection(df, session_id)   ← embeds all Q&A + feedback
       │
       ▼
rag.generate_assistant_suggestions(student_id, ...)
  Layer 1: df[df["user"] == student_id]
  Layer 2: ChromaDB query with student_id filter
  Generation: GPT-4o-mini → 2–3 bullets
       │
       ▼
"Suggested Focus Areas" panel in assistant_app.py
```

See [[RAG Pipeline - Two-Layer Retrieval]] for detail.

## Why this matters

- Both [[Student Struggle Logic]] and [[Question Difficulty Logic]] depend on the filtered DataFrame they receive, so the same raw data can produce different scores depending on active filters.
- The assistant app currently loads live data directly and does not inherit the instructor's session scoping, which is documented in [[Known Issues]].

## Code references

- `code/learning_dashboard/data_loader.py`: `fetch_raw_data()`, `detect_format()`, `parse_json_response()`, `parse_xml_response()`, `normalize_and_clean()`, `load_data()`
- `code/learning_dashboard/data_loader.py`: `filter_by_time()`, `filter_by_session_start()`, `filter_by_datetime_window()`
- `code/learning_dashboard/paths.py`: `ensure_runtime_data_layout()`, `saved_sessions_path()`, `lab_session_path()`
- `data/saved_sessions.json`
- `data/lab_session.json`
