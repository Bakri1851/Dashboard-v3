# paths.py

**Path:** `code/learning_dashboard/paths.py`
**Folder:** [[learning_dashboard]]

> Resolves runtime file locations and migrates legacy files from the repo root into `data/` on first run.

## Responsibilities

- Expose path constants (`PACKAGE_ROOT`, `PROJECT_ROOT`, `DATA_DIR`) and the effective locations of the lab-session JSON, the lock file, the saved-sessions JSON, and the ChromaDB store.
- Migrate `saved_sessions.json` / `lab_session.json` from the legacy repo-root location into `data/` without overwriting existing runtime files.
- Provide path accessors with legacy fallback, so the app still works if migration was skipped.

## Key functions / classes

- `ensure_runtime_data_layout()` — create `data/` and copy legacy files into it if missing.
- `saved_sessions_path()` — preferred `data/saved_sessions.json` with fallback to the legacy root file.
- `lab_session_path()` — same pattern for the shared state file.
- `lab_session_lock_path()` — returns the `.lock` path matching the effective state file.
- `rag_chroma_dir()` — creates and returns `data/rag_chroma/`.

## Dependencies

- Standard library only (`pathlib`, `shutil`).
- Imported by [[data_loader]], [[lab_state]], [[rag]].

## Related notes

- [[Configuration and Runtime Paths]] (thematic)
- [[Data Loading and Session Persistence]]
