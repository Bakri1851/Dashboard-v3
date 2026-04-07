---
name: Filelock
description: File-based locking library used to safely share lab session state between the two Streamlit processes
type: reference
---

# Filelock

Python library providing cross-platform file locking via a `.lock` file on disk.

## Version

`filelock >= 3.12.0`

## Why this library

The instructor app (port 8501) and the lab assistant portal (port 8502) are two separate OS processes with no shared memory. Both read and write `data/lab_session.json`. Without locking, concurrent writes could produce corrupted JSON. `filelock` provides a simple `FileLock` context manager that serialises access using a companion `.lock` file (`data/lab_session.lock`).

## Where used

- `code/learning_dashboard/lab_state.py` — every public function that reads or writes `lab_session.json` acquires the lock first

## Key usage

```python
from filelock import FileLock

lock = FileLock(str(paths.LAB_SESSION_LOCK), timeout=5)

with lock:
    # safe to read / write lab_session.json here
```

A `timeout=5` means if the lock cannot be acquired within 5 seconds (e.g., another process is hanging), a `Timeout` exception is raised rather than blocking indefinitely.

## Write pattern

All writes use an atomic temp-file-then-rename strategy:

1. Write new JSON to a `.tmp` file alongside `lab_session.json`
2. Rename the `.tmp` file over the live file

This ensures a partial write never leaves `lab_session.json` in a truncated state.

## Troubleshooting

If both apps are idle but a `FileLock` timeout occurs, the `.lock` file may be stale. Delete `data/lab_session.lock` and restart both apps. See [[Known Issues]].

## Related

- [[Lab Assistant System]]
- [[Setup and Runbook]]
- [[Known Issues]]
