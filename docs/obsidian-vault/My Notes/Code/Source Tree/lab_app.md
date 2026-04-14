# lab_app.py

**Path:** `code/lab_app.py`
**Folder:** [[code]]

> Lab assistant mobile app entrypoint — a thin Streamlit wrapper.

## Responsibilities

- Import `main` from [[assistant_app]] and run it under Streamlit.
- Provide a separate, stable entrypoint so the assistant app can be launched on its own port (8502) alongside the instructor dashboard.

## Key functions / classes

The file just contains the re-export + `__main__` guard:

```python
from learning_dashboard.assistant_app import main

if __name__ == "__main__":
    main()
```

All four-state flow logic (no-session → join → unassigned → assigned), mobile CSS, and RAG-backed coaching suggestions live in [[assistant_app]].

## Runtime

- Port: 8502
- Command: `streamlit run code/lab_app.py --server.port 8502`

## Related notes

- [[assistant_app]] — the actual entry function
- [[Lab Assistant System]] (thematic) — full behavioural description
- [[Setup and Runbook]]
