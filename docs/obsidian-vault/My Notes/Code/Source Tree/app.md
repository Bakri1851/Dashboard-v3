# app.py

**Path:** `code/app.py`
**Folder:** [[code]]

> Instructor dashboard entrypoint — a thin Streamlit wrapper.

## Responsibilities

- Import `main` from [[instructor_app]] and run it under Streamlit.
- Exist so users can run `streamlit run code/app.py` without thinking about the package layout.

## Key functions / classes

The whole file is effectively:

```python
from learning_dashboard.instructor_app import main

if __name__ == "__main__":
    main()
```

No logic of its own. All routing, state initialisation, and view rendering lives in [[instructor_app]].

## Runtime

- Port: 8501
- Command: `python -m streamlit run code/app.py`

## Related notes

- [[instructor_app]] — the actual entry function
- [[App Entrypoint]] (thematic) — wider narrative about what happens at startup
- [[Setup and Runbook]]
