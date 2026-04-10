Part of [[Assistant App]] · [[UI Flow]]

# Assistant App — Unassigned View (Waiting for Assignment)

Shown when the assistant has joined the session but has not yet been assigned a student. The instructor may assign them via the sidebar, or the assistant can self-claim if self-allocation is enabled.

Related: [[Lab Assistant System]], [[Join Session]], [[Assigned View]]

## What is displayed

- Heading: **"Hello, [name]"** with subtitle **"WAITING FOR ASSIGNMENT"**
- Session status strip: current session code + assistant name
- **Leave Session** button
- Section: **"Available Students"** — list of students at "Struggling" or "Needs Help" struggle level who are not already assigned to another assistant
  - Each student card shows: student ID, struggle level badge (colour-coded), and struggle score
  - Students at "Minor Issues" or "On Track" are hidden; a caption shows the hidden count
- If self-allocation is enabled: each student card has a **"Help [student]"** button
- If all struggling students are already assigned: `st.success("All struggling students are covered")`

## Self-allocation flow

If `allow_self_allocation` is true in the session state:

1. Assistant taps "Help [student]".
2. Calls `lab_state.self_claim_student(assistant_id, student_id)`.
3. `st.rerun()` — transitions to [[Assigned View]].

## Auto-transition

On every 5-second refresh cycle, if `get_assignment_for_assistant(assistant_id)` returns a non-None value (instructor has assigned a student), `st.rerun()` fires immediately to show the [[Assigned View]] without any tap required.

## Render function

`render_unassigned_view(assistant_id, lab_data, struggle_df)` in `code/learning_dashboard/assistant_app.py`

## Trigger condition

```python
student_id = get_assignment_for_assistant(assistant_id, lab_data)
if student_id is None:
    render_unassigned_view(assistant_id, lab_data, struggle_df)
    st.stop()
```
