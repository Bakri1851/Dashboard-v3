Part of [[Assistant App]] · see also [[Lab App/Operations/Next Steps]]

# Next Steps — Assistant App

Assistant-app-specific implementation work. For all instructor dashboard phases (Phases 1–5, 7, conceptual additions) see [[Lab App/Operations/Next Steps]].

Related: [[Lab Assistant System]], [[Assistant App/Flows/UI Flow]], [[Known Issues]]

---

## Context

The project already has a working baseline system. This includes:

- a live instructor dashboard
- a mobile lab assistant app
- live and saved session support
- assistant assignment / self-claim / helped-state flows
- a baseline student struggle model

The next phase for the assistant app is about fixing known bugs in assistant-specific flows (Phase 0d, 0e) and enriching the mobile experience (Phase 6).

---

## Phase 0: Bug fixes (assistant-side)

- [x] Complete

### 0d. Assistant data scope mismatch

- **File:** `code/learning_dashboard/assistant_app.py` ~lines 19–25
- **Problem:** `_load_student_data()` calls `data_loader.load_data()` without applying the instructor's active live-session window. Assistants can see students outside the instructor's current teaching scope.
- **Fix:** Add a `session_start` ISO timestamp field to `lab_session.json` (set in `start_lab_session()`). In the assistant app, read this from lab state and filter the DataFrame to only include submissions after `session_start` before computing struggle scores.
- **Also touches:** `code/learning_dashboard/lab_state.py` — add `session_start` to `_default_state()` and `start_lab_session()`

### 0e. Name collision on rejoin

- **File:** `code/learning_dashboard/lab_state.py` ~lines 192–195
- **Problem:** When a name matches an existing assistant case-insensitively, `join_session()` returns the old `assistant_id` with potentially stale `assigned_student` state
- **Fix:** When returning an existing assistant_id on name match, clear `assigned_student` to `None` so the rejoining assistant starts fresh

### Phase 0 verification (assistant-side)

- Start session, join as assistant, leave, rejoin with same name — verify fresh state (no inherited assignment)
- Check assistant app shows only students within instructor's session window

---

## Phase 6: Mobile app refinement

- [ ] Complete

**Goal:** Polish the lab assistant app so Appendix B mobile screenshots show the full feature set and Ch5 functional testing covers the assistant flows properly.

### Modified files

- `code/learning_dashboard/assistant_app.py` — BKT badge, mastery labels, session timer, helped counts
- `code/learning_dashboard/ui/theme.py` — mobile CSS additions if needed

### Sub-tasks

- [ ] Add BKT mastery badge + mini progress bar to the assigned-student card in `render_assigned_view()`
- [ ] Show per-question mastery level alongside the top-3 question list (`mastered` / `learning` / `not started`)
- [ ] Add session elapsed timer to `_render_session_status_strip()`
- [ ] Add helped-vs-struggling summary header to the unassigned view (`render_unassigned_view()`)
- [ ] Show "currently attempting" question if derivable from most recent submission timestamp

### Verification

- Join as assistant, get assigned a student → verify BKT mastery badge and progress bar appear on the student card
- Check per-question mastery labels appear alongside the top-3 question list
- Verify session elapsed timer increments correctly
- Check helped-vs-struggling header counts are accurate

---

## Code references

- `code/learning_dashboard/assistant_app.py`: `_load_student_data()`, `render_unassigned_view()`, `render_assigned_view()`, `_render_session_status_strip()`
- `code/learning_dashboard/lab_state.py`: `join_session()`, `_default_state()`, `start_lab_session()`
- `code/learning_dashboard/ui/theme.py`: `get_mobile_css()`
