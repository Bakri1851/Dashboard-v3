# Lab Assistant System

The lab assistant system is a lightweight second app that coordinates human helpers during live teaching. Its design is intentionally simple: two Streamlit processes share a single JSON state file on disk, protected by a file lock.

Related: [[Architecture]], [[Instructor Dashboard]], [[Assistant App/Flows/UI Flow]], [[Setup and Runbook]], [[Known Issues]]

## Core model

- One active shared session code.
- Many assistants may join the same session.
- Each assistant can hold at most one assigned student at a time.
- Assignments are tracked centrally in `data/lab_session.json`.
- Self-allocation can be enabled or disabled by the instructor.

## Shared state schema

- Session fields: `session_code`, `session_active`, `generated_at`, `allow_self_allocation`.
- Assistant map: `lab_assistants[assistant_id] = {name, joined_at, assigned_student}`.
- Assignment map: `assignments[student_id] = {assistant_id, status, assigned_at, helped_at?}`.
- Status values are `helping` and `helped`.

## Main flows

- Join: assistant enters name and code, `join_session()` returns or reuses an assistant ID.
- Restore: assistant ID is stored in the `aid` query parameter so refreshes keep identity.
- Assign: instructor assigns a student, or assistant self-claims if allowed.
- Update: assistant marks a student as helped or releases the student.
- Exit: instructor ends the session or removes an assistant; assistant can also leave voluntarily.

## Safety and consistency

- Every read and write goes through a `FileLock`.
- `_normalize_state()` repairs partial or inconsistent state on every read.
- Helper functions enforce the one-assistant/one-student rule.

## Phase 9: RAG suggestions in assigned view

When an assistant is assigned a student, `render_assigned_view()` now also calls `rag.generate_assistant_suggestions()` to surface 2–3 coaching bullets beneath the student card. The RAG block is the UI chokepoint — `lab_state.py` remains Streamlit-free and is not touched. Session change clears `rag._suggestion_cache` and `st.session_state["cached_suggestions"]`. See [[Suggested Focus Areas Panel]] and [[rag.py — RAG Engine and ChromaDB Interface]].

## Code references

- `code/learning_dashboard/lab_state.py`: `_default_state()`, `_normalize_state()`, `read_lab_state()`
- `code/learning_dashboard/lab_state.py`: `join_session()`, `assign_student()`, `self_claim_student()`
- `code/learning_dashboard/lab_state.py`: `mark_student_helped()`, `unassign_student()`, `leave_session()`, `remove_assistant()`
- `code/learning_dashboard/assistant_app.py`: `render_join_screen()`, `render_unassigned_view()`, `render_assigned_view()`
- `code/learning_dashboard/rag.py`: `generate_assistant_suggestions()`, `clear_suggestion_cache()`
- `data/lab_session.json`
