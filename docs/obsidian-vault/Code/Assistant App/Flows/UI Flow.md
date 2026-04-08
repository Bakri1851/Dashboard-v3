Part of [[Assistant App]] · see also [[Lab App/Flows/Pages and UI Flow]]

# Assistant App — UI Flow

The assistant app routes to one of four views depending on session state and the assistant's URL identity. All state is read from `data/lab_session.json` on each refresh cycle (every 5 seconds).

Related: [[Lab Assistant System]], [[Setup and Runbook]]

## Assistant app pages

- `No Active Session`: shown when the shared session is inactive.
- `Join Session`: shown when there is an active session but no assistant ID in the query string.
- `Waiting for Assignment`: shown when the assistant is joined but unassigned.
- `Assigned View`: shown when the assistant has a current student assignment.

## Session lifecycle from assistant perspective

- Assistant navigates to the lab app URL (port 8502).
- If a session is active, the join screen prompts for name and session code.
- After joining, the assistant's ID is appended to the URL as `?aid=<id>` so page refreshes restore identity without re-joining.
- If the instructor ends the session, the assistant is shown the inactive session screen.

## URL ?aid= persistence

- Assistant identity survives phone refreshes through the `aid` query parameter.
- On each load, the app reads `aid` from the URL and restores the assistant's state from `lab_session.json`.
- If the `aid` is not found in the current session state (e.g. the session was reset), the app falls back to the join screen.

## Self-allocation flow (when enabled)

- If `allow_self_allocation` is enabled in the session, the unassigned view shows a list of available struggling students.
- The assistant can self-claim a student directly without waiting for instructor assignment.

## Mark as helped

- From the assigned view, the assistant taps "Mark as Helped".
- This calls `mark_student_helped()` which updates the shared JSON state.
- The instructor sidebar reflects the helped status in real time (next refresh cycle).

## Sound triggers

- Assistant join and assignment receipt are separate cues from the instructor sound system.

## Code references

- `code/learning_dashboard/assistant_app.py`: `render_session_ended()`, `render_join_screen()`, `render_unassigned_view()`, `render_assigned_view()`
- `code/learning_dashboard/sound.py`
