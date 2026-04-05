# Learning Analytics Dashboard - Developer Guide

## What this repository is
This repository contains a Streamlit dashboard used during lab sessions to track:
- student struggle (leaderboard + drill-down)
- question difficulty (leaderboard + drill-down)
- live and saved session filtering
- mobile lab-assistant coordination during live sessions

This `README.md` is the main source of truth for understanding how the code is organized and how to work on it after the package reorganization.

## Tech stack
- Python 3.11+
- Streamlit
- Plotly
- Pandas / NumPy
- Requests
- `streamlit-autorefresh` for polling
- `filelock` for shared lab-session writes to `data/lab_session.json`
- OpenAI for incorrectness scoring and mistake-cluster labels
- scikit-learn for TF-IDF, K-means clustering, cosine similarity, and collaborative filtering

Dependencies are listed in `requirements.txt`.

## Quick start
1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Run the main instructor dashboard on port 8501:
```bash
python -m streamlit run app.py
```
3. Run the mobile lab assistant app on port 8502 if needed:
```bash
streamlit run lab_app.py --server.port 8502
```

The launch commands are unchanged. The root `app.py` and `lab_app.py` files are now thin compatibility wrappers around the packaged application code.

Both processes share live lab state through `data/lab_session.json`.

### Migration note
Older repo layouts stored runtime files at the repo root. On first access, the app will migrate these files into `data/` if needed:
- `saved_sessions.json` -> `data/saved_sessions.json`
- `lab_session.json` -> `data/lab_session.json`

`lab_session.lock` is not migrated; it is recreated in `data/` automatically.

## Repository map
- `app.py`: compatibility wrapper for the instructor dashboard.
- `lab_app.py`: compatibility wrapper for the assistant dashboard.
- `learning_dashboard/instructor_app.py`: instructor app entry point, sidebar, routing, and session-state setup.
- `learning_dashboard/assistant_app.py`: mobile lab assistant app implementation.
- `learning_dashboard/analytics.py`: scoring engine for incorrectness, struggle, difficulty, collaborative filtering, and mistake clustering.
- `learning_dashboard/config.py`: tunable constants only.
- `learning_dashboard/data_loader.py`: API fetch, parse, normalize, and saved-session persistence helpers.
- `learning_dashboard/lab_state.py`: file-locked shared lab-session state management.
- `learning_dashboard/paths.py`: project/runtime paths and legacy-file migration helpers.
- `learning_dashboard/sound.py`: browser-side synthesized sound effects.
- `learning_dashboard/ui/components.py`: reusable UI building blocks.
- `learning_dashboard/ui/theme.py`: CSS and Plotly theme defaults.
- `learning_dashboard/ui/views.py`: page-level views and drill-down screens.
- `data/`: runtime data directory for `saved_sessions.json`, `lab_session.json`, and `lab_session.lock`.
- `static/`: static assets.
- `.streamlit/secrets.toml`: local secrets such as `OPENAI_API_KEY`.

## Runtime flow
1. `learning_dashboard.instructor_app.main()` initializes Streamlit and session state.
2. `learning_dashboard.data_loader.load_data()` fetches cached API payloads, detects JSON vs XML, parses records, and normalizes fields.
3. Deferred actions are applied before widgets are built:
- pending saved-session load
- pending return to live data
4. The sidebar applies filters in this order:
- manual time filter
- active live-session start-time filter
- loaded saved-session start/end window filter
5. Routing sends filtered data to:
- student detail
- question detail
- in-class view
- data analysis view
- settings view
- previous sessions view

## Scoring models
All scoring logic lives in `learning_dashboard/analytics.py`. All tunable constants live in `learning_dashboard/config.py`.

Start in `learning_dashboard/config.py` for weight or threshold changes. Only edit `learning_dashboard/analytics.py` when the algorithm itself must change.

### Incorrectness estimation
Every submission carries an `ai_feedback` string produced by the backend AI tutor. The dashboard scores that feedback using OpenAI.

- Model: `gpt-4o-mini` (`config.OPENAI_MODEL`)
- Temperature: `0`
- Batch size: up to `50` feedback texts per API call (`config.OPENAI_BATCH_SIZE`)
- Output: float in `[0, 1]`
- Empty or null feedback: `0.5`
- Cache: `_incorrectness_cache` avoids repeat scoring within the same process
- Correct threshold: `config.CORRECT_THRESHOLD = 0.5`

Key functions:
- `analytics.estimate_incorrectness`
- `analytics.compute_incorrectness_column`

### Student struggle score
Raw score:

```text
S_raw = 0.10*n_hat + 0.10*t_hat + 0.20*i_bar + 0.10*r_hat + 0.38*A_raw + 0.05*d_hat + 0.07*rep_hat
```

Bayesian shrinkage:

```text
w_n = n / (n + K), K = 5
S_final = w_n*S_raw + (1 - w_n)*S_class_mean
```

Components:
- `n_hat`: normalized submission count
- `t_hat`: normalized time active
- `i_bar`: mean incorrectness
- `r_hat`: retry rate
- `A_raw`: recent incorrectness using exponential time decay across the last 5 submissions
- `d_hat`: normalized improvement trajectory slope
- `rep_hat`: answer repetition rate

Thresholds:
- `[0.00, 0.20)`: On Track
- `[0.20, 0.35)`: Minor Issues
- `[0.35, 0.50)`: Struggling
- `[0.50, 1.00]`: Needs Help

Key functions:
- `analytics.compute_student_struggle_scores`
- `analytics.compute_recent_incorrectness`
- `analytics.classify_score`

### Question difficulty score

```text
D = 0.28*c_hat + 0.12*t_hat + 0.20*a_hat + 0.20*f_hat + 0.20*p_hat
```

Components:
- `c_hat`: incorrect rate
- `t_hat`: average time per student
- `a_hat`: average attempts per student
- `f_hat`: average incorrectness
- `p_hat`: first-attempt failure rate

Thresholds:
- `[0.00, 0.35)`: Easy
- `[0.35, 0.50)`: Medium
- `[0.50, 0.75)`: Hard
- `[0.75, 1.00]`: Very Hard

Key function:
- `analytics.compute_question_difficulty_scores`

### Mistake clustering
When a teacher drills into a question, incorrect answers are grouped into clusters so the UI can show dominant mistake types instead of raw answer lists.

Pipeline:
1. Filter to incorrect answers.
2. Deduplicate exact answer text.
3. TF-IDF vectorize unique answers.
4. Auto-select `k` using silhouette score.
5. Run K-means clustering.
6. Pick representative answers by cosine similarity to centroid.
7. Label clusters with a single OpenAI request.

Important config values:
- `CLUSTER_MIN_WRONG`
- `CLUSTER_MAX_K`
- `CLUSTER_MAX_EXAMPLES`
- `CLUSTER_EXAMPLE_MAX_CHARS`

Key functions:
- `analytics.cluster_question_mistakes`
- `analytics._label_clusters_with_openai`

### Collaborative filtering
Collaborative filtering is an opt-in layer that runs after the parametric struggle model. It flags students who are similar to confirmed strugglers even if their own parametric score is below the threshold.

Key functions:
- `analytics.compute_cf_struggle_scores`
- `analytics.get_similar_students`

## Session behavior
There are two session concepts:

1. Live session:
- started with `Start Lab Session` in the sidebar
- uses `session_start` to filter current data
- ended with `End Session`
- automatically saved to `data/saved_sessions.json`

2. Saved session:
- loaded from Settings -> Saved Sessions
- applies a fixed start/end datetime window from the saved record
- can be exited with `Back to Live Data` in the sidebar

## Lab assistant system
The lab assistant system runs as two cooperating Streamlit processes sharing state through a JSON file on disk.

- `app.py` on port 8501 is the stable instructor entrypoint and delegates to `learning_dashboard/instructor_app.py`
- `lab_app.py` on port 8502 is the stable assistant entrypoint and delegates to `learning_dashboard/assistant_app.py`

### Shared state
`data/lab_session.json` is the single source of truth. All reads and writes go through `learning_dashboard/lab_state.py`, which wraps operations in `filelock.FileLock` with a 5-second timeout.

Schema:
```json
{
  "session_code": "A3X7K2",
  "session_active": true,
  "generated_at": "2026-02-07T17:00:00",
  "allow_self_allocation": true,
  "lab_assistants": {
    "alice_1234": {
      "name": "Alice",
      "joined_at": "2026-02-07T17:05:00",
      "assigned_student": "student42"
    }
  },
  "assignments": {
    "student42": {
      "assistant_id": "alice_1234",
      "status": "helping",
      "assigned_at": "2026-02-07T17:10:00"
    }
  }
}
```

`status` is either `"helping"` or `"helped"`.
`assigned_student` in the assistant record mirrors the `assignments` map; `_normalize_state` enforces consistency on every read.

### Session lifecycle
1. Instructor clicks `Start Lab Session` -> `lab_state.start_lab_session(code)` writes a fresh active state and stores the code in `st.session_state["lab_session_code"]`.
2. Instructor clicks `End Session` -> `lab_state.end_lab_session()` sets `session_active` to `False` and clears assignments.

### Assistant join flow
1. Assistant opens `lab_app.py`, enters name and the 6-character code -> `lab_state.join_session(code, name)`.
2. On success, `aid` is written to the URL query param so identity survives a phone-browser refresh.
3. If the assistant already exists in the session, the existing `aid` is returned.

### Assignment flows
- Instructor assigns: sidebar dropdown selects an unassigned assistant and a struggling student -> `lab_state.assign_student(student_id, assistant_id)`.
- Assistant self-claims: unassigned assistant clicks `Help {user}` -> `lab_state.self_claim_student(student_id, assistant_id)`.
- Self-claim is only available when the instructor enables `allow_self_allocation`.

An assistant can only hold one assignment at a time.

### Key `learning_dashboard/lab_state.py` functions
- `read_lab_state()`
- `start_lab_session(session_code)`
- `end_lab_session()`
- `join_session(code, name)`
- `assign_student(student_id, assistant_id)`
- `self_claim_student(student_id, assistant_id)`
- `mark_student_helped(student_id)`
- `unassign_student(student_id)`
- `leave_session(assistant_id)`
- `remove_assistant(assistant_id)`
- `set_allow_self_allocation(flag)`

### Why deferred actions exist
Streamlit does not allow changing certain `st.session_state` keys after their widgets are instantiated in the same run.

This repo uses deferred flags and records such as `pending_session_load_record`, applied near the top of `main()` before sidebar widgets are created.

## Saved session schema
Saved sessions are stored in `data/saved_sessions.json`:

```json
{
  "version": 1,
  "sessions": [
    {
      "id": "uuid",
      "name": "Lab Session 2026-02-07 17:00",
      "created_at": "2026-02-07T18:10:00",
      "start_time": "2026-02-07T17:00:00",
      "end_time": "2026-02-07T18:10:00",
      "duration_seconds": 4200,
      "context": {
        "dashboard_view": "In Class View",
        "secondary_module_filter": "All Modules",
        "time_filter_enabled": false,
        "time_date_range": null,
        "time_start": null,
        "time_end": null
      },
      "notes": ""
    }
  ]
}
```

Persistence helpers live in `learning_dashboard/data_loader.py`:
- `load_saved_sessions`
- `save_session_record`
- `delete_session_record`
- `build_session_record_from_state`
- `apply_saved_session_to_state`

## Important session state keys
Key runtime state in `learning_dashboard/instructor_app.py:init_session_state()`:

| Key | Purpose |
|---|---|
| `current_view` | Active page |
| `dashboard_view` | Sidebar-selected dashboard view |
| `selected_student` | Drill-down target user ID |
| `selected_question` | Drill-down target question ID |
| `session_active` | Whether a live session is running |
| `session_start` | Datetime for live-session filter start |
| `loaded_session_id` | Currently loaded saved session ID |
| `loaded_session_start` / `loaded_session_end` | Datetime window for saved-session filtering |
| `pending_session_load_record` | Deferred saved-session load payload |
| `pending_return_to_live_data` | Deferred reset back to live mode |
| `time_filter_enabled` | Manual date/time filter toggle |
| `lab_session_code` | Session code shown in the sidebar during an active live session |
| `pending_remove_assistant_id` | Deferred assistant removal ID |
| `cf_enabled` | Whether collaborative filtering is active |
| `cf_threshold` | CF threshold for labelling parametric strugglers |
| `sounds_enabled` | Whether sound effects are active |
| `auto_refresh` | Whether automatic polling is active |
| `refresh_interval` | Polling interval in seconds |

## Common change recipes
### Add a new chart to an existing page
1. Add a reusable chart renderer in `learning_dashboard/ui/components.py`.
2. Call it from the target view in `learning_dashboard/ui/views.py`.
3. Keep styling aligned with `theme.get_plotly_layout_defaults()`.

### Add a new sidebar filter
1. Add state defaults in `learning_dashboard/instructor_app.py:init_session_state`.
2. Add the widget in `learning_dashboard/instructor_app.py:render_sidebar`.
3. Apply the filter in the existing precedence chain.
4. Confirm interaction with live and saved session filters.

### Modify thresholds, labels, or colors
1. Update constants in `learning_dashboard/config.py`.
2. Confirm `analytics.classify_score` still matches intended boundaries.
3. Verify formula panel and leaderboard colors.

### Add a new lab-assistant action
1. Add the state mutation in `learning_dashboard/lab_state.py` inside the `_lock()` context.
2. Call it from `learning_dashboard/assistant_app.py` or `learning_dashboard/instructor_app.py` as appropriate.
3. If new shared-state keys are introduced, add them to `_default_state` and `_normalize_state`.

### Extend saved session metadata
1. Update `build_session_record_from_state` in `learning_dashboard/data_loader.py`.
2. Update `apply_saved_session_to_state` in `learning_dashboard/data_loader.py`.
3. Update the Settings session list in `learning_dashboard/ui/views.py`.

## Validation checklist
Run syntax checks:
```bash
python -m py_compile app.py lab_app.py learning_dashboard/*.py learning_dashboard/ui/*.py
```

Manual smoke tests:
1. App loads data successfully.
2. Start and end a live session.
3. Saved session appears in Settings.
4. Load a saved session and verify the data is scoped to the saved time window.
5. Use `Back to Live Data` and verify full live data returns.
6. Delete a saved session and confirm it is removed.
7. Start a live session and verify the session code card appears in the sidebar.
8. Open `lab_app.py` on port 8502, enter the code and a name, and confirm the assistant appears in the sidebar roster.
9. Assign a struggling student to the assistant from the instructor sidebar and verify the student card appears in `lab_app.py`.
10. In `lab_app.py`, self-claim a struggling student and verify the assignment appears in the instructor sidebar.
11. Mark the student as helped in `lab_app.py` and verify the status updates in both apps.
12. Remove an assistant from the instructor sidebar and verify they are ejected and must rejoin.
13. End the live session and verify `lab_app.py` shows `No Active Session`.
14. Toggle sound effects off in Settings and confirm no audio fires on navigation or selection, then toggle back on.
15. Toggle `Allow self-allocation` during an active session and verify the unassigned assistant view switches between claimable students and the waiting message.
16. Open a question with at least 3 incorrect submissions and verify the Mistake Clusters section appears with labelled cluster cards.
17. Enable Collaborative Filtering in Settings and verify the threshold slider and CF panel appear where expected.
18. Verify the first run migrates legacy root JSON files into `data/` without losing their contents.

## Troubleshooting notes
- If loading a saved session shows all data, check `loaded_session_start` and `loaded_session_end`.
- If Streamlit raises widget-state mutation errors, verify the mutation happens in the deferred phase near the top of `main()`.
- If the API fails, the app shows an error and stops outside Settings.
- If `data/saved_sessions.json` is corrupted, the loader resets it and can back up a corrupt copy automatically.
- If `data/lab_session.json` shows stale or corrupt data, delete it and `learning_dashboard/lab_state.py` will recreate it on the next read.
- If a lab assistant sees "Your previous assistant session is no longer active", the instructor ended the session or removed them.
- If `FileLock` times out, another process may be holding the file open; delete `data/lab_session.lock` when both apps are idle.

## Known implementation note
`learning_dashboard.data_loader.load_data()` is used in `learning_dashboard/instructor_app.py` as returning a `DataFrame`.

If you rely on type hints or docstrings there, check real usage first before refactoring.
