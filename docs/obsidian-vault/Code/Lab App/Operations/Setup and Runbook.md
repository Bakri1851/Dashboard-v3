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
