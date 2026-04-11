---
type: community
cohesion: 0.27
members: 12
---

# Runtime Paths & File Layout

**Cohesion:** 0.27 - loosely connected
**Members:** 12 nodes

## Members
- [[Create the runtime data directory and migrate legacy root files once.]] - rationale - code\learning_dashboard\paths.py
- [[Lock path paired with the effective lab-session file location.]] - rationale - code\learning_dashboard\paths.py
- [[Preferred saved-sessions path, with legacy fallback if migration fails.]] - rationale - code\learning_dashboard\paths.py
- [[Preferred shared lab-session path, with legacy fallback if migration fails.]] - rationale - code\learning_dashboard\paths.py
- [[Runtime path helpers for app data and backward-compatible migration.]] - rationale - code\learning_dashboard\paths.py
- [[_copy_if_missing()]] - code - code\learning_dashboard\paths.py
- [[_ensure_data_dir()]] - code - code\learning_dashboard\paths.py
- [[ensure_runtime_data_layout()]] - code - code\learning_dashboard\paths.py
- [[lab_session_lock_path()]] - code - code\learning_dashboard\paths.py
- [[lab_session_path()]] - code - code\learning_dashboard\paths.py
- [[paths.py]] - code - code\learning_dashboard\paths.py
- [[saved_sessions_path()]] - code - code\learning_dashboard\paths.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Runtime_Paths_&_File_Layout
SORT file.name ASC
```
