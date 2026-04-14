Part of [[Assistant App]] · [[UI Flow]]

# Assistant App — Assigned View

Shown when the assistant has an active student assignment. This is the primary working screen for a lab assistant during a session.

Related: [[Lab Assistant System]], [[Unassigned View]]

## What is displayed

- Heading: **"Hello, [name]"** (no subtitle)
- Session status strip: session code + assistant name
- **Leave Session** button
- **Student card** — bordered with the student's struggle level colour:
  - Student ID
  - Struggle score (3 decimal places, coloured by level)
  - Struggle level badge (e.g. "Needs Help", "Struggling")
- **"Suggested Focus Areas"** panel (Phase 9 RAG) — appears between the student card and the top-3 questions divider:
  - On first render: spinner → calls `rag.generate_assistant_suggestions(student_id, df, struggle_row, session_id)` → 2–3 bullet points grounded in the student's own submission history
  - Cached in `st.session_state["cached_suggestions"]` — auto-refresh cycles return instantly from cache
  - Shows `"Not enough data yet"` if student has < 2 submissions
  - Silent (no block shown) if `chromadb`/`sentence-transformers` not installed or LLM fails
  - See [[Suggested Focus Areas Panel]] and [[RAG Pipeline - Two-Layer Retrieval]]
- Divider
- **"Top Struggling Questions"** section — up to 3 questions this student has the highest mean incorrectness on:
  - Question text (truncated to 50 characters)
  - Average incorrectness % for this student on that question
- Divider
- Action buttons:
  - **"Mark as Helped"** — calls `lab_state.mark_student_helped(student_id)`; shows `st.success("Marked as helped.")` and updates the instructor sidebar on the next refresh
  - **"Release Student"** — calls `lab_state.unassign_student(student_id)`; transitions back to [[Unassigned View]]

## Sound

On the first render after a None → assigned transition, `sound.play_assignment_received()` fires (a brief sci-fi audio cue injected via `st.components.v1.html()`).

## Data sources

- Student struggle score and level: row from `struggle_df` filtered by `student_id`
- Top questions: computed by filtering `df` to this student's submissions, grouping by question, taking mean incorrectness, top 3 by that metric

## Render function

`render_assigned_view(assistant_id, student_id, lab_data, df, struggle_df)` in `code/learning_dashboard/assistant_app.py`

## Trigger condition

This view is the final routing branch — reached when `get_assignment_for_assistant(assistant_id)` returns a non-None `student_id` and the session is active.
