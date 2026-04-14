---
name: Streamlit Autorefresh
description: Streamlit extension that adds client-side periodic page refresh for the lab assistant portal
type: reference
---

# Streamlit Autorefresh

Third-party Streamlit component that injects a client-side timer to trigger a full page rerun at a configurable interval.

## Version

`streamlit-autorefresh >= 1.0.1`

## Why this library

Streamlit has no native push or WebSocket mechanism for real-time updates. The lab assistant portal needs to pick up changes to `data/lab_session.json` (e.g., a new assignment from the instructor) without the assistant manually refreshing the browser. `streamlit-autorefresh` adds a lightweight polling loop that triggers a Streamlit rerun every few seconds, which re-reads the shared JSON file.

## Where used

- `code/learning_dashboard/assistant_app.py` — called once at the top of `main()` to set up the polling loop

## Key usage

```python
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=5000)  # rerun every 5 000 ms
```

The refresh interval is not currently configurable from the Settings page — it is hardcoded in the assistant app. The instructor dashboard uses a separate configurable auto-refresh toggle (also backed by this component) controlled via `refresh_interval` in `st.session_state`.

## Trade-off

Polling every 5 seconds means there is up to a 5-second lag between the instructor assigning a student and the assistant seeing it. This is acceptable for lab sessions but would not suit real-time notification use cases.

## Related

- [[Lab Assistant System]]
- [[Instructor Dashboard]]
- [[Streamlit]]
