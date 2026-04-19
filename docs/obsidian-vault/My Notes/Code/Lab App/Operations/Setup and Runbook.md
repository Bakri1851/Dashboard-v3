# Setup and Runbook

This project is simple to run locally, but it depends on one external API and one local secret for the OpenAI-backed analytics features. The instructor and assistant apps are separate Streamlit processes that share JSON files under `data/`.

Related: [[Project Overview]], [[Configuration and Runtime Paths]], [[Lab Assistant System]], [[Known Issues]]

## Prerequisites

- Python `3.11+`
- Packages from `code/requirements.txt`
- Network access to the configured retrieval API
- `OPENAI_API_KEY` in `.streamlit/secrets.toml` for incorrectness scoring and mistake-cluster labels

## Install

```bash
pip install -r code/requirements.txt
```

## Run

Run all commands from the repo root (`Dashboard v3/`).

Instructor dashboard on port `8501`:

```bash
python -m streamlit run code/app.py
```

Lab assistant portal on port `8502`:

```bash
streamlit run code/lab_app.py --server.port 8502
```

## Runtime files

- `data/saved_sessions.json`: saved session history
- `data/lab_session.json`: active shared assistant state
- `data/lab_session.lock`: file lock for shared assistant state
- Legacy root JSON files may still exist, but runtime prefers `data/`

## Quick smoke test

1. Launch the instructor app and confirm the dashboard loads data.
2. Start a lab session and confirm a session code appears.
3. Launch the assistant app, join with the code, and confirm the assistant appears in the instructor sidebar.
4. Assign a struggling student from the instructor view or self-claim from the assistant view.
5. Mark the student as helped and confirm the status syncs across both apps.
6. End the session and confirm a saved-session record is created.

---

## Alternative frontend (`code2/`) — React + FastAPI

A second frontend lives under `code2/`. It is **additive** — `code/` stays untouched and is the defence-day fallback. The React UI matches the design mockup at `C:\Users\Bakri\Downloads\Alternative Dashboard _standalone_.html` (7 themes, editorial typography, clickable drill-downs). All four processes (two Streamlit apps in `code/`, two mirrored Streamlit apps in `code2/`, and FastAPI) share `data/lab_session.json` via the same `FileLock`, so lab-assistant state is coordinated automatically.

### Prerequisites (in addition to the ones above)

- Node.js `18+` and npm
- Extra Python packages (already in `code2/requirements.txt`): `fastapi`, `uvicorn[standard]`, `cachetools`, `python-dotenv`
- Set `OPENAI_API_KEY` as an environment variable (FastAPI path reads it from env, not `secrets.toml`) for incorrectness scoring and RAG suggestions.

### Install

```bash
pip install -r code2/requirements.txt
cd code2/frontend && npm install && cd ../..
```

### Run (5 processes)

```bash
# Fallback — original Streamlit
python -m streamlit run code/app.py                              # 8501
streamlit run code/lab_app.py --server.port 8502                 # 8502

# Cross-check Streamlit (optional — same codebase, different ports)
streamlit run code2/app.py --server.port 8503                    # 8503
streamlit run code2/lab_app.py --server.port 8504                # 8504

# Alternative frontend stack
uvicorn backend.main:app --app-dir code2 --port 8000 --reload    # 8000 (FastAPI + built React)
cd code2/frontend && npm run dev                                 # 5173 (Vite HMR dev server, proxies /api → :8000)
```

`--app-dir code2` adds `code2/` to `sys.path` so both `backend.*` and `learning_dashboard.*` resolve. Defence demo URL is `http://localhost:8000/` after `npm run build` (FastAPI's `StaticFiles` mount serves `code2/frontend/dist/`). `/docs` serves the FastAPI Swagger UI.

### Performance notes

- Cold start: the first `/api/struggle` or `/api/live` call takes ~2 minutes (fetch + parse 34k records + struggle/difficulty compute over 203 students × 119 questions). A `lifespan` hook prewarms at server start; subsequent calls hit the 5-minute analytics TTL cache at ~250 ms.
- First RAG call builds a ChromaDB collection and downloads the sentence-transformers model (several minutes). Handlers are `async` + `asyncio.to_thread` so this does not block other endpoints.

### Repo layout (code2/)

```
code2/
  CHECKLIST.md            — resumable execution log
  learning_dashboard/     — copy of code/learning_dashboard with 2 refactors
  app.py, lab_app.py      — Streamlit entries (unchanged copies)
  backend/                — FastAPI app + 8 routers (live / student / question / analysis / lab / sessions / settings / models_cmp / rag)
  frontend/               — Vite + React + TypeScript
    src/theme/            — 7 themes (paper/newsprint/solar/scifi/blueprint/matrix/cyberpunk)
    src/views/            — all 8 views ported
    mockup-extracted/     — 72 decompressed mockup assets (design reference)
    scripts/extract_mockup.py — one-shot helper that unpacks the mockup's single-file bundler
```
7. Open `Previous Sessions`, load a saved session, and confirm the data is time-windowed.
8. Return to live data and confirm the dashboard resets to default live mode.

## Troubleshooting

- If the instructor dashboard shows an API error, check the retrieval endpoint in `config.py` and network access.
- If incorrectness or mistake labels seem generic, check `OPENAI_API_KEY`.
- If assistant state gets stuck, stop both apps and inspect `data/lab_session.json` and `data/lab_session.lock`.
- If saved sessions reset unexpectedly, inspect backups created from corrupt JSON.
- If a widget-state mutation error appears, review deferred actions in `code/learning_dashboard/instructor_app.py`.

## Verification command

PowerShell-friendly syntax check:

```bash
$files = @('code/app.py','code/lab_app.py') + (Get-ChildItem code/learning_dashboard -File -Filter *.py | ForEach-Object { $_.FullName }) + (Get-ChildItem code/learning_dashboard/ui -File -Filter *.py | ForEach-Object { $_.FullName }); python -m py_compile @files
```

## Code references

- `code/requirements.txt`
- `code/app.py`
- `code/lab_app.py`
- `code/learning_dashboard/config.py`
- `code/learning_dashboard/instructor_app.py`
- `code/learning_dashboard/lab_state.py`
- `data/saved_sessions.json`
- `data/lab_session.json`
