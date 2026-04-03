# Learning Analytics Dashboard - Developer Guide

## What this repository is
This repository contains a Streamlit dashboard used during lab sessions to track:
- student struggle (leaderboard + drill-down)
- question difficulty (leaderboard + drill-down)
- live and saved session filtering

This `README.md` is the main source of truth for understanding how the code is organized and how to work on it.

## Tech stack
- Python 3.11+
- Streamlit
- Plotly
- Pandas / NumPy
- Requests
- streamlit-autorefresh (auto-polling in lab assistant app)
- filelock (thread-safe concurrent writes to `lab_session.json`)
- openai (GPT-4o-mini incorrectness scoring via AI tutor feedback)
- scikit-learn (TF-IDF vectorisation, K-means clustering for mistake grouping, cosine similarity for collaborative filtering)

Dependencies are listed in `requirements.txt`.

## Quick start
1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Run the main instructor dashboard (port 8501):
```bash
python -m streamlit run app.py
```
3. Open the local Streamlit URL shown in terminal.

To also run the mobile lab assistant app (separate port):
```bash
streamlit run lab_app.py --server.port 8502
```
Both processes share state through `lab_session.json` on disk.

## Repository map
- `app.py`: entry point, session state initialization, sidebar controls, routing, and filter application order.
- `lab_app.py`: mobile lab assistant portal; runs on port 8502; provides join screen, waiting/unassigned view, and assigned-student view with self-claim.
- `views.py`: page-level views (`In Class`, `Data Analysis`, `Settings`, and drill-down views).
- `components.py`: reusable UI building blocks (leaderboards, cards, tables, charts, formula panel).
- `theme.py`: global CSS and Plotly theme defaults.
- `analytics.py`: scoring engine (incorrectness, struggle score, difficulty score, classification, mistake clustering).
- `data_loader.py`: API fetch/parse/clean pipeline plus saved session persistence helpers.
- `lab_state.py`: shared file-locked state management for instructor and assistant apps (session lifecycle, assistant roster, student assignments).
- `sound.py`: synthesized sci-fi sound effects via the browser Web Audio API (session start/end, navigation, selection, assistant join, high-struggle alarm, etc.). All effects respect the `sounds_enabled` session state flag.
- `config.py`: all tunable constants (weights, thresholds, colors, limits, API config).
- `saved_sessions.json`: local storage for saved sessions created when ending a lab session.
- `lab_session.json`: runtime file persisting active lab session state (assistants, assignments); auto-created on first use.
- `lab_session.lock`: filelock preventing concurrent write corruption; auto-created alongside `lab_session.json`.
- `README.md`: developer onboarding, architecture, and workflows.

## Runtime flow
1. `app.py:main()` initializes Streamlit and session state.
2. Data is loaded using `data_loader.load_data()`:
- fetch API payload (cached)
- detect JSON vs XML
- parse and normalize fields
- clean modules and timestamps
3. Pending deferred actions are applied before widgets are built:
- pending saved-session load
- pending return to live data
4. Sidebar is rendered and filters are applied in this order:
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

All scoring logic lives in `analytics.py`; all tunable constants live in `config.py`. Start in `config.py` for weight/threshold changes; only touch `analytics.py` if the algorithm itself must change.

### Incorrectness estimation

Every submission carries an `ai_feedback` string produced by the backend AI tutor. The dashboard scores that feedback using OpenAI:

- **Model**: GPT-4o-mini (`config.OPENAI_MODEL`), `temperature=0`
- **Batching**: up to 50 feedback texts per API call (`config.OPENAI_BATCH_SIZE`)
- **Output**: float in **[0, 1]** — 0 = fully correct, 1 = fully incorrect
- **Empty / null feedback** → **0.5** (neutral, no API call made)
- **In-process cache** (`_incorrectness_cache` dict in `analytics.py`): identical feedback strings are scored only once per process lifetime, avoiding redundant API calls across Streamlit reruns
- **Correct threshold**: `config.CORRECT_THRESHOLD = 0.5` — incorrectness < 0.5 is treated as "correct" in all binary counts

Key functions: `analytics.estimate_incorrectness`, `analytics.compute_incorrectness_column`

---

### Student struggle score

**Formula (S_raw):**
```
S_raw = 0.10·n̂ + 0.10·t̂ + 0.20·î + 0.10·r̂ + 0.38·A_raw + 0.05·d̂ + 0.07·rep̂
```

**Bayesian shrinkage** (reduces noise for students with few submissions):
```
w_n    = n / (n + K),   K = 5
S_final = w_n · S_raw + (1 − w_n) · S̄_class
```
Students with n >> 5 are effectively unaffected; students with n << 5 are pulled toward the class mean.

**Components:**

| Symbol | Name | Computation | Weight |
|---|---|---|---|
| `n̂` | Submission count | min-max normalized across all students | 0.10 |
| `t̂` | Time active | first-to-last submission timestamp delta (minutes); min-max normalized | 0.10 |
| `î` | Mean incorrectness | mean OpenAI incorrectness score across all of the student's submissions | 0.20 |
| `r̂` | Retry rate | `1 − (unique_questions / total_submissions)`; 0 = all unique questions, 1 = all retries | 0.10 |
| `A_raw` | Recent incorrectness | exponential time-decay weighted mean of last `N=5` submissions; `w_i = exp(−λ·Δt)`, λ = ln2 / 1800 (30-min half-life); falls back to equal weights when all timestamps are identical | 0.38 |
| `d̂` | Improvement trajectory | linear regression slope of incorrectness vs. submission order (oldest = 0); positive = getting worse; min-max normalized across all students | 0.05 |
| `rep̂` | Answer repetition rate | fraction of submissions that exactly repeat a prior answer on the same question (per-question, chronological; strip-normalized) | 0.07 |

**Struggle level thresholds:**

| Score range | Label | Color |
|---|---|---|
| [0.00, 0.20) | On Track | `#00ff88` |
| [0.20, 0.35) | Minor Issues | `#ffcc00` |
| [0.35, 0.50) | Struggling | `#ff6600` |
| [0.50, 1.00] | Needs Help | `#ff2d55` |

Key functions: `analytics.compute_student_struggle_scores`, `analytics.compute_recent_incorrectness`, `analytics.classify_score`

---

### Question difficulty score

**Formula (D):**
```
D = 0.28·c̃ + 0.12·t̃ + 0.20·ã + 0.20·f̃ + 0.20·p̃
```

**Components:**

| Symbol | Name | Computation | Weight |
|---|---|---|---|
| `c̃` | Incorrect rate | `1 − (correct_attempts / total_attempts)`; "correct" = incorrectness < 0.5 | 0.28 |
| `t̃` | Avg time per student | minutes from a student's first to last attempt on this question; 0 for single-attempt students; mean across all students; min-max normalized | 0.12 |
| `ã` | Avg attempts per student | `total_attempts / unique_students`; min-max normalized | 0.20 |
| `f̃` | Avg incorrectness | mean OpenAI incorrectness score across all attempts on this question | 0.20 |
| `p̃` | First-attempt failure rate | fraction of students whose chronologically first attempt has incorrectness ≥ 0.5 | 0.20 |

**Difficulty level thresholds:**

| Score range | Label | Color |
|---|---|---|
| [0.00, 0.35) | Easy | `#00ff88` |
| [0.35, 0.50) | Medium | `#ffcc00` |
| [0.50, 0.75) | Hard | `#ff6600` |
| [0.75, 1.00] | Very Hard | `#ff2d55` |

Key function: `analytics.compute_question_difficulty_scores`

---

### Mistake clustering

When a teacher drills into a question, incorrect student answers are automatically grouped into clusters so the teacher can see the dominant mistake types at a glance rather than raw individual answers.

**Pipeline:**
1. Filter submissions to incorrect answers (`incorrectness ≥ config.CORRECT_THRESHOLD`)
2. Deduplicate by exact answer text
3. TF-IDF vectorise unique answers (`max_features=500`, `sublinear_tf=True`)
4. Auto-select cluster count k=2..`CLUSTER_MAX_K` (default 5) using silhouette score with cosine metric; best k chosen
5. K-means cluster (final fit with best k); assign each submission to its cluster
6. Per cluster: pick up to `CLUSTER_MAX_EXAMPLES` representative answers by cosine similarity to centroid
7. Single GPT-4o-mini call labels all clusters in one request; returns short (3–6 word) conceptual mistake descriptions

**Caching:** `_cluster_cache` dict in `analytics.py`, keyed by `(question_id, wrong_answer_count)`. Cache is invalidated when new wrong answers arrive (count changes).

**Edge cases:**
- Fewer than `CLUSTER_MIN_WRONG` (default 3) wrong answers → info message, no API call
- All wrong answers identical → single "Common Wrong Answer" cluster, sklearn skipped
- Only 2 unique wrong answers → single "Mixed Wrong Answers" cluster, silhouette loop skipped
- OpenAI label call fails → fallback labels "Mistake Group 1", "Mistake Group 2", etc.

**Config constants** (all in `config.py`):

| Constant | Default | Meaning |
|---|---|---|
| `CLUSTER_MIN_WRONG` | 3 | Min incorrect submissions needed to attempt clustering |
| `CLUSTER_MAX_K` | 5 | Max clusters to evaluate via silhouette |
| `CLUSTER_MAX_EXAMPLES` | 3 | Representative answers shown per cluster |
| `CLUSTER_EXAMPLE_MAX_CHARS` | 300 | Truncate long answers in UI |

**Return format:** `list[dict]` sorted by count descending, each dict: `{label, count, percent_of_wrong, example_answers}`.

Key functions: `analytics.cluster_question_mistakes`, `analytics._label_clusters_with_openai`

---

### Min-max normalization
`analytics.min_max_normalize(series)` applies `(x − min) / (max − min)`, clamped to [0, 1].
Returns **0.0 for all entries** when `min == max` (avoids NaN when all students have identical values).

---

### Temporal smoothing (stub — not active)
Infrastructure exists in `analytics.apply_temporal_smoothing`:
```
S_t = (1 − α) · S_prev + α · S_raw,   α = 0.3
```
`config.SMOOTHING_ENABLED = False`. Not wired into any active code path.

---

### Collaborative filtering (CF) struggle detection

CF is a secondary, opt-in layer that runs **after** the parametric model. It identifies students who have not yet crossed the parametric struggle threshold but are behaviourally similar to students who have, surfacing them as proactive intervention candidates.

**How it works:**

1. Build an interaction matrix **X** from five normalised features: `n_hat`, `t_hat`, `i_hat`, `A_raw`, `d_hat`
2. Compute pairwise cosine similarity **W** using `sklearn.metrics.pairwise.cosine_similarity`
3. Label each student: `h_i = 1` if `struggle_score >= τ` (configurable threshold, default 0.6), else `h_i = 0`
4. For each student where `h_i = 0`: find k=3 nearest neighbours by similarity, compute `cf_score = weighted_avg(neighbours' h values)` using similarity as weights
5. For each student where `h_i = 1`: `cf_score = 1.0`
6. Students with `h_i = 0` and `cf_score > 0` are "elevated" — at least one of their nearest neighbours is a confirmed struggler

**Settings (Settings page only):**

| Control | Session state key | Default |
|---|---|---|
| Enable/disable toggle | `cf_enabled` | `False` |
| Threshold slider τ (0.0–1.0, step 0.05) | `cf_threshold` | `0.6` |

The threshold slider only appears when CF is enabled. No CF controls exist outside Settings.

**Dashboard visibility:**

| Location | What is shown | Condition |
|---|---|---|
| In Class View (after leaderboards) | 3 metric cards (elevated count, parametric flagged count, τ value) + table of elevated students with parametric score, CF score, and nearest neighbours | `cf_enabled = True` |
| Student drill-down (after recent submissions) | Table of 5 most similar students with similarity score, struggle score, and struggle level | `cf_enabled = True` |

When `cf_enabled = False`, no CF-related UI renders anywhere.

**Edge cases:**

| Condition | Behaviour |
|---|---|
| Fewer than 4 students | Falls back to parametric scores; shows info message |
| No students above τ | Falls back to parametric scores; shows warning |
| CF computation error | Shows `st.warning` in CF panel only; rest of dashboard unaffected |

Key functions: `analytics.compute_cf_struggle_scores`, `analytics.get_similar_students`

---

## Session behavior
There are two session concepts:

1. Live session:
- Started with `Start Lab Session` in sidebar
- Uses `session_start` to filter current data
- Ended with `End Session`
- Automatically saved to `saved_sessions.json`

2. Saved session:
- Loaded from Settings -> Saved Sessions
- Applies a fixed start/end datetime window from saved record
- Can be exited with `Back to Live Data` in sidebar

## Lab assistant system
The lab assistant system runs as two cooperating Streamlit processes sharing state through a JSON file on disk:

- **`app.py`** (port 8501): instructor dashboard — starts/ends sessions, assigns students, removes assistants.
- **`lab_app.py`** (port 8502): mobile assistant portal — join/leave sessions, view assigned student, self-claim struggling students, mark student as helped.

### Shared state
`lab_session.json` is the single source of truth. All reads and writes go through `lab_state.py`, which wraps every operation in a `filelock.FileLock` (5-second timeout) to prevent write corruption when both processes update simultaneously.

`lab_session.json` schema:
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
1. Instructor clicks **Start Lab Session** → `lab_state.start_lab_session(code)` writes a fresh state with `session_active: true`; code is stored in `st.session_state["lab_session_code"]`.
2. Instructor clicks **End Session** → `lab_state.end_lab_session()` sets `session_active: false` and clears all assignments.

### Assistant join flow
1. Assistant opens `lab_app.py`, enters name + 6-character code → `lab_state.join_session(code, name)`.
2. On success, `aid` is written to the URL query param (`?aid=...`) so the identity survives a phone browser refresh.
3. If the assistant with that name already exists in the session, the existing `aid` is returned (idempotent).

### Assignment flows
- **Instructor assigns**: sidebar dropdown selects an unassigned assistant and a struggling student → `lab_state.assign_student(student_id, assistant_id)`.
- **Assistant self-claims**: unassigned assistant sees students rated "Struggling" or "Needs Help" and clicks **Help {user}** → `lab_state.self_claim_student(student_id, assistant_id)`. Self-claim is only available when the instructor has enabled it via the `allow_self_allocation` toggle in the sidebar; when disabled, the unassigned view shows a waiting message instead of the student list.

An assistant can only hold one assignment at a time; trying to claim a second student returns an error.

### Key `lab_state.py` functions
- `read_lab_state()` — read, normalize, and re-persist state; returns full dict.
- `start_lab_session(session_code)` / `end_lab_session()` — session lifecycle.
- `join_session(code, name)` → `(ok, assistant_id, error)`.
- `assign_student(student_id, assistant_id)` / `self_claim_student(student_id, assistant_id)` → `(ok, error)`.
- `mark_student_helped(student_id)` — transitions status to `"helped"`.
- `unassign_student(student_id)` — releases the assignment and frees the assistant.
- `leave_session(assistant_id)` — assistant voluntarily leaves; releases assigned student.
- `remove_assistant(assistant_id)` — instructor removes an assistant; releases assigned student.
- `set_allow_self_allocation(flag)` — instructor toggles whether assistants can self-claim students; updates `allow_self_allocation` in shared state.

### Why deferred actions exist
Streamlit does not allow changing certain `st.session_state` keys after their widgets are instantiated in the same run.  
This repo uses deferred flags/records (for example `pending_session_load_record`) that are applied near the top of `main()` before sidebar widgets are created.

## Saved session schema
Saved sessions are stored in `saved_sessions.json`:

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

Persistence helpers live in `data_loader.py`:
- `load_saved_sessions`
- `save_session_record`
- `delete_session_record`
- `build_session_record_from_state`
- `apply_saved_session_to_state`

## Important session state keys
Key runtime state in `app.py:init_session_state()`:

| Key | Purpose |
|---|---|
| `current_view` | Active page (`In Class View`, `Data Analysis View`, `Settings`) |
| `dashboard_view` | Sidebar-selected dashboard view |
| `selected_student` | Drill-down target user ID |
| `selected_question` | Drill-down target question ID |
| `session_active` | Whether live session is running |
| `session_start` | Datetime for live-session filter start |
| `loaded_session_id` | Currently loaded saved session ID |
| `loaded_session_start` / `loaded_session_end` | Datetime window for saved-session filter |
| `pending_session_load_record` | Deferred saved-session load payload |
| `pending_return_to_live_data` | Deferred reset back to unfiltered live mode |
| `time_filter_enabled` | Manual date/time filter toggle |
| `lab_session_code` | Session code shown in sidebar code card while a live session is active |
| `pending_remove_assistant_id` | Deferred assistant removal ID; cleared before sidebar widgets render |
| `cf_enabled` | Whether collaborative filtering is active (default: `False`) |
| `cf_threshold` | CF threshold τ for labelling parametric strugglers (default: `0.6`) |
| `sounds_enabled` | Whether sci-fi sound effects are active (default: `True`) |
| `auto_refresh_enabled` | Whether automatic data polling is active (default: `True`) |
| `auto_refresh_interval` | Polling interval in seconds (default: 60; options: 5, 10, 15, 30, 60) |

## Common change recipes
### Add a new chart to existing pages
1. Add reusable chart renderer in `components.py`.
2. Call it from the target view in `views.py`.
3. Keep styling aligned with `theme.get_plotly_layout_defaults()`.

### Add new sidebar filters
1. Add state defaults in `app.py:init_session_state`.
2. Add widget in `app.py:render_sidebar`.
3. Apply filter in the existing precedence chain in `render_sidebar`.
4. Confirm interaction with live/saved session filters.

### Modify thresholds/labels/colors
1. Update constants in `config.py`.
2. Confirm `analytics.classify_score` behavior still matches intended boundaries.
3. Verify formula panel and leaderboard colors.

### Add new actions to the lab assistant portal
1. Add the new operation to `lab_state.py` using the `_lock()` context manager: read state with `_read_state_unlocked`, mutate, then write with `_write_state_unlocked`.
2. Call the new function from the relevant view in `lab_app.py` (`render_unassigned_view`, `render_assigned_view`, or a new view).
3. For instructor-side actions, add the UI and call in `_render_lab_assignment_panel` in `app.py`.
4. If new state keys are introduced, add them to `_default_state` and `_normalize_state` in `lab_state.py`.

### Extend saved session metadata
1. Update `build_session_record_from_state` in `data_loader.py`.
2. Update `apply_saved_session_to_state` in `data_loader.py`.
3. Update Settings session list rendering in `views.py`.

## Validation checklist
Run syntax checks:
```bash
python -m py_compile app.py config.py views.py theme.py components.py analytics.py data_loader.py sound.py
```

Manual smoke tests:
1. App loads data successfully.
2. Start and end live session.
3. Saved session appears in Settings.
4. Load saved session and verify data is scoped to session time window.
5. Use `Back to Live Data` and verify full live data returns.
6. Delete a saved session and confirm it is removed.
7. Toggle leaderboard legend categories and confirm no blank middle gaps appear.
8. Start a live session and verify the session code card appears in the sidebar.
9. Open `lab_app.py` on port 8502, enter the code and a name, and confirm the assistant appears in the sidebar roster.
10. Assign a struggling student to the assistant from the instructor sidebar; verify the student card appears in `lab_app.py`.
11. In `lab_app.py` (as an unassigned assistant), self-claim a struggling student; verify the assignment appears in the instructor sidebar.
12. Mark the student as helped in `lab_app.py`; verify the status updates in both apps.
13. Remove an assistant from the instructor sidebar; verify they are ejected and `lab_app.py` shows the rejoin prompt.
14. End the live session; verify `lab_app.py` shows "No Active Session".
15. In Settings, toggle sound effects off; confirm no audio fires on navigation or selection. Toggle back on and confirm sound returns.
16. During an active session, toggle the **Allow self-allocation** switch in the instructor sidebar; open `lab_app.py` as an unassigned assistant and verify the student claim list appears (enabled) or is replaced by a waiting message (disabled).
17. Click a question with ≥ 3 incorrect submissions; verify the "Mistake Clusters" section appears with AI-labelled cluster cards and expandable example answers. Click a question with fewer than 3 incorrect submissions and verify the info message appears instead.
18. In Settings, enable Collaborative Filtering; verify the threshold slider appears. Return to In Class View and verify the CF panel shows metric cards and (if applicable) an elevated students table. Click a student and verify the "Most Similar Students" table appears at the bottom of the drill-down.
19. In Settings, disable Collaborative Filtering; verify no CF-related UI appears in In Class View or student drill-downs.

## Troubleshooting notes
- If loading a saved session shows all data, check `loaded_session_start` and `loaded_session_end` are populated.
- If Streamlit raises widget-state mutation errors, verify state mutation happens in deferred phase near top of `main()`.
- If API fails, the app shows an error and stops outside Settings.
- If `saved_sessions.json` is corrupted, loader resets it and can back up a corrupt copy automatically.
- If `lab_session.json` shows stale or corrupt data, delete the file — `lab_state` recreates it with defaults on the next read.
- If a lab assistant sees "Your previous assistant session is no longer active", the session was ended or they were removed by the instructor; they need to rejoin.
- If `FileLock` times out (5-second limit), another process may be holding the lock file open; delete `lab_session.lock` when both apps are idle to reset it.

## Known implementation note
`data_loader.load_data()` is used as returning a `DataFrame` in `app.py`.  
If you rely on type hints/docstrings there, check real usage first before refactoring.
