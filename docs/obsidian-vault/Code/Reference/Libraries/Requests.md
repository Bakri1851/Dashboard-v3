---
name: Requests
description: HTTP library used to fetch raw submission data from the retrieval API
type: reference
---

# Requests

Python HTTP library for making web requests.

## Version

`requests >= 2.31.0`

## Why this library

The dashboard fetches submission data from an external retrieval API. Only simple HTTP GET calls are needed — no auth flows, WebSockets, or async. Requests is the standard Python choice for this use case.

## Where used

- `code/learning_dashboard/data_loader.py` — `fetch_raw_data()` is the only place Requests is used

## Key operations used

- `requests.get(url, timeout=config.API_TIMEOUT)` — performs a single GET request to the configured API endpoint
- `response.text` — raw response body; passed to auto-detection logic that determines whether the payload is JSON or XML
- `response.raise_for_status()` — raises an `HTTPError` on 4xx/5xx responses, surfaced as a Streamlit error message

## Caching note

`fetch_raw_data()` is wrapped with `@st.cache_data(ttl=10)`, so the HTTP request fires at most once every 10 seconds regardless of how many Streamlit reruns occur within that window.

## Related

- [[Data Loading and Session Persistence]]
- [[Configuration and Runtime Paths]]
