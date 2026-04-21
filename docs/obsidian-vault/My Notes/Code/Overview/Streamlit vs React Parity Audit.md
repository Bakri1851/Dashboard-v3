# Streamlit vs React/FastAPI — Functionality Loss Audit

**Scope:** Compare `code/` (Streamlit, canonical + defence fallback) against `code2/` (React + FastAPI) to identify any functionality lost in the port.
**Date:** 2026-04-21
**Audited against:** `code2/CHECKLIST.md` claim of ~95% parity after Phase 9.

## Summary

All 8 views are ported. Core analytics (struggle, difficulty, CF, BKT, IRT, RAG, mistake clusters, saved sessions, lab lifecycle) have full parity. Losses are concentrated in **detail-view time-domain charts** and **small UI affordances** — not in analytical capability. Several of the gaps below are **not** in `CHECKLIST.md`'s deferred list.

Tick one of these when you want it filled in.

---

## Genuine losses (not in `code2/`)

### [ ] 1. StudentDetail — three charts dropped
Streamlit (`code/learning_dashboard/ui/views.py:182–298`) renders, `code2/frontend/src/views/StudentDetail.tsx` does not:

- **Questions Attempted horizontal bar chart** — top N questions by attempt count. React replaced with a table only.
- **Submission Timeline** — hourly submission-frequency line chart with filled area (`code/learning_dashboard/ui/components.py:721–764`). No React equivalent.
- **Retry Intensity Trend** — rolling-window mean of attempt-number over submission sequence (`components.py:767–794`, window = `min(5, n)`). No React equivalent.

React adds a trajectory sparkline and a Score Components HBars breakdown — useful but **does not replace** the time-domain charts. Instructor asking "when was this student active today?" has no answer in `code2/`.

### [ ] 2. QuestionDetail — one chart dropped
- **Attempt Timeline** — hourly attempt-frequency line chart (`views.py:417–419`). Not in `code2/frontend/src/views/QuestionDetail.tsx`.

### [ ] 3. QuestionDetail — ConfidenceBadge dropped
Coloured dot + "AI confidence: High/Medium/Low (XX%)" (`components.py:126–145`). **Explicitly deferred** in `CHECKLIST.md:142`. Score-bar colour is an indirect proxy; the explicit signal is gone.

### [ ] 4. InClassView — headline breakdown collapsed 4 → 2 levels
Streamlit: **Needs Help · Struggling · Minor Issues · On Track** as four headline cards (`components.py:78–87`).
React: "Priority Now" (Needs Help + Struggling only) + four non-level stats (Total Submissions, Unique Students, Questions Answered, Mean Incorrectness) — see `InClassView.tsx:208–272`. Minor Issues and On Track counts survive only inside the struggle-distribution histogram bars, not as headline numbers.

### [ ] 5. InClassView — formula panel relocated to Settings only
Streamlit has an inline expander "Scoring Formulas & Methodology" with full weights, component labels, and thresholds for both scores (`components.py:526–586`). In `code2/`, this lives **only** in the SettingsView read-only reference block. Instructors viewing the dashboard no longer see the formula in context.

### [ ] 6. InClassView — secondary module filter has different semantics
Streamlit's per-view module selectbox **recomputes** struggle/difficulty scores *within* the filtered module (`views.py:47–70`: `_sec_struggle_df`, `_sec_analytics_key`). React's InClassView module pills (`InClassView.tsx:274–308`) filter the already-computed global rows by module — no recompute. In Streamlit, filtering to module X shows who is struggling *relative to X*; in React, it shows who is globally struggling and happens to be on X. CHECKLIST called this "deferred" but understates the difference.

### [ ] 7. ComparisonView — 4×4 confusion matrix dropped
Streamlit: level-confusion matrix (baseline × improved level counts). React: Spearman ρ + top-10 overlap + biggest-disagreements table. Explicitly deferred (`CHECKLIST.md:143`). Replacement gives rank agreement; the matrix's view of level-band flow (e.g. "how many of Baseline's 'On Track' moved to Improved's 'Struggling'?") is gone.

### [ ] 8. PreviousSessions — academic-period filter dropdown dropped
Streamlit's list view has a "Filter by Academic Period" selectbox on the saved-sessions list (`views.py:843`). Explicitly deferred (`CHECKLIST.md:132`) on the grounds that the sidebar academic-week picker covers it — but that's a different thing: the dropdown filtered the **list of saved sessions**, not the current time window.

### [ ] 9. Sidebar — refresh affordance dropped
Streamlit sidebar has "Refresh Now" + "Last refresh: HH:MM:SS" (`app.py:500–504`). React relegates both to SettingsView. For a live classroom demo, the top-level refresh affordance is gone.

### [ ] 10. `play_high_struggle` sound trigger — function likely missing, trigger definitely missing
Streamlit trigger: `instructor_app.py:882–885` compares `_prev_high_struggle_count` to current and fires `sound.play_high_struggle()` when Needs-Help count increases.
Grep of `code2/frontend/src` for `play_high_struggle|highStruggle|high_struggle` → **zero matches**. `CHECKLIST.md:141` claims all 8 sounds were ported; this one is not visible. The audible alarm when a new student crosses into "Needs Help" is not firing in `code2/`.

### [ ] 11. Leaderboard — legend toggle
Streamlit's Plotly leaderboards (`components.py:285–460`) support clicking the colour-level legend to hide/show bars for that struggle or difficulty band. React's custom `Leaderboard` component has no clickable legend.

---

## UX reorganised but functionally equivalent (not losses)

- **Instructor lab-assignment UI** — moved from a sidebar expander (`instructor_app.py:213–347`) to the LabAssistantView "Dispatch Queue". Same capability set (assign, release, remove, self-alloc toggle).
- **Mistake clusters** — Streamlit uses an expander ("Example answers"); React shows up to 3 examples inline in each cluster card. Same information, no expander.
- **Lab-assignment inline controls** — sidebar selectboxes "Struggling student → Assistant → Assign" replaced by per-row "Dispatch →" buttons.

---

## Net gains in `code2/` (for context)

- 7 themes + 5 accent-colour swatches with live swap (Streamlit has one sci-fi neon theme).
- Time-window analytics caching (`backend/cache.py`, keyed by `(from, to)`) vs Streamlit's 10s raw-fetch cache only.
- `/docs` Swagger UI for the full API surface.
- RAG cold-start on `asyncio.to_thread` so it doesn't block the event loop.
- Settings live-editable and process-durable (`backend/runtime_config.py`); Streamlit settings reset on rerun.

---

## Ghost-settings fix (2026-04-21)

Separate from the 11 parity gaps above, an audit of `runtime_config` found that six Settings controls wrote to the backend but no code ever read them — they were UI-only ghosts. Fixed in one pass:

- **`auto_refresh` + `refresh_interval`** — now drive every instructor-facing poll via new `useAutoRefreshInterval.ts`. Off → polling stops; interval dropdown retimes every poll. `/lab/state` stays hardcoded at 3s (peer coordination).
- **`struggle_model` (baseline/improved)** — new `cache.load_active_struggle_df` dispatches. Improved path now actually runs BKT + IRT. Baseline ancillary columns (`submission_count`, `d_hat`, …) are merged onto improved so router schemas stay stable.
- **`difficulty_model` (baseline/irt)** — new `cache.load_active_difficulty_df` dispatches, renames IRT columns to the baseline schema.
- **BKT parameters (`p_init`, `p_learn`, `p_guess`, `p_slip`, `bkt_mastery_threshold`)** — `cache.load_improved_struggle_df` rewritten to compute mastery with runtime values. Sliders now move the leaderboard.
- **`smoothing_enabled`** — removed entirely from the Settings UI, `runtime_config`, `schemas`, and `types/api.ts`. The backend `apply_temporal_smoothing` is still a stub (noted in `analytics.py:858`); wiring the toggle would have required reworking the score-composition flow. Follow-up if temporal smoothing is ever properly implemented.

Sidebar "Refresh Now" button (item 9 above) deliberately **not** added — auto-refresh honouring the user's setting covers the use case. Can be added later if demo UX demands it.

Still outstanding from the 11 parity gaps: items 1–8 and 10–11 (chart additions, confusion matrix, academic-period filter, `play_high_struggle` trigger, legend toggle).

---

## Fix-pointer reference

When you pick items to fill in, these are the files to touch:

| # | Fix location | Reference in `code/` |
|---|---|---|
| 1 | `code2/frontend/src/views/StudentDetail.tsx` — add two charts; `recent_submissions[]` already has the timestamps | `code/learning_dashboard/ui/components.py:721–794` |
| 2 | `code2/frontend/src/views/QuestionDetail.tsx` — add timeline using `recent_attempts[]` | `code/learning_dashboard/ui/views.py:417–419` |
| 3 | `code2/frontend/src/views/QuestionDetail.tsx` — add ConfidenceBadge; backend needs to expose a confidence field | `code/learning_dashboard/ui/components.py:126–145` |
| 4 | `code2/frontend/src/views/InClassView.tsx:208–272` — counts already in `struggleBuckets`, trivial add-back | `code/learning_dashboard/ui/components.py:78–87` |
| 5 | `code2/frontend/src/views/InClassView.tsx` — inline formula expander at bottom of page | `code/learning_dashboard/ui/components.py:526–586` |
| 6 | `code2/backend/routers/live.py` (or new endpoint) — filter DF before struggle/difficulty compute, not after | `code/learning_dashboard/ui/views.py:47–70` |
| 7 | `code2/frontend/src/views/ComparisonView.tsx` — `/api/models/compare` already returns the counts | (Streamlit uses pandas crosstab) |
| 8 | `code2/frontend/src/views/PreviousSessions.tsx` — dropdown over distinct `academic_period` values in the session list | `code/learning_dashboard/ui/views.py:843` |
| 9 | `code2/frontend/src/components/layout/Sidebar.tsx` — add refetch button + timestamp | `code/app.py:500–504` |
| 10 | `code2/frontend/src/sound.ts` + wherever `/api/live` is consumed — diff Needs-Help count between polls | `code/learning_dashboard/instructor_app.py:882–885` |
| 11 | `code2/frontend/src/components/charts/Leaderboard.tsx` — level-filter pills or clickable header chips | `code/learning_dashboard/ui/components.py:285–460` |

## How to verify independently

Run both stacks side by side and walk the views:
```bash
python -m streamlit run code/app.py                  # Streamlit instructor on :8501
uvicorn backend.main:app --app-dir code2 --port 8000  # React+FastAPI on :8000
```
The timeline-chart gaps in StudentDetail and QuestionDetail are visible on first load.
