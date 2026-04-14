Part of [[Lab App]] - see also [[Assistant App/Flows/UI Flow]]

# Live Assistant Assignment

The live assistant assignment flow lives inside the instructor sidebar rather than a standalone page. It appears only during an active lab session and is the main coordination surface between the dashboard and the assistant mobile app.

Related: [[Instructor Dashboard]], [[Lab Assistant System]], [[Pages and UI Flow]], [[Saved Session History]]

## When the panel is shown

- `render_sidebar()` calls `_render_lab_assignment_panel()` only while `session_active` is true.
- The panel reads shared state from `_lab_state_cache` or `lab_state.read_lab_state()`.
- If the session is inactive, pending assistant-removal confirmation is cleared and the panel is hidden.

## Instructor controls

- View joined assistants and their current assignment status.
- Toggle `allow_self_allocation` so assistants can either self-claim students or wait for manual assignment.
- Release an assigned student, which unassigns the student but keeps the assistant in the session.
- Remove an assistant, with a confirmation step that also releases any current student assignment.

## Assignment rules

- Manual assignment is only shown when there is at least one unassigned assistant and a non-empty `struggle_df`.
- Eligible students are limited to those currently labeled `Struggling` or `Needs Help` and not already assigned.
- The instructor selects a student and an unassigned assistant, then `assign_student()` writes the change to shared session state.
- Assigned entries show `helping` or `helped` status from the shared assignments map.

## Shared-state implications

- The panel is backed by `data/lab_session.json`, so instructor and assistant views converge through the shared file rather than direct in-memory state.
- Self-allocation and instructor assignment both operate on the same assignment map, so conflicts fall back to lab-state validation.
- The flow is live-session only; saved-session browsing does not replay or restore assistant coordination state.

## Code references

- `code/learning_dashboard/instructor_app.py`: `_render_lab_assignment_panel()`, `render_sidebar()`
- `code/learning_dashboard/lab_state.py`: `read_lab_state()`, `set_allow_self_allocation()`, `assign_student()`, `unassign_student()`, `remove_assistant()`
- `data/lab_session.json`
