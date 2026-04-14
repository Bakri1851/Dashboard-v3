# lab_state.py

**Path:** `code/learning_dashboard/lab_state.py`
**Folder:** [[learning_dashboard]]

> Cross-process shared state for the two apps — a JSON file guarded by `filelock` with atomic tmp-replace writes. No Streamlit imports, so the same functions are safe to call from either app.

## Responsibilities

- Maintain the lab-session document: `active`, `session_code`, `created_at`, `allow_self_allocation`, `assistants`, `assignments`, `helped_students`.
- Generate a 6-char alphanumeric `session_code` excluding `O/0/I/1`.
- Handle session lifecycle: `start_lab_session`, `end_lab_session`.
- Handle assistant identity: `join_session`, `leave_session`, `remove_assistant`.
- Handle allocation — both directions: instructor `assign_student`, assistant `self_claim_student`, plus `unassign_student` and `mark_student_helped`.
- Normalise the state schema on read so older / partial files don't crash the app.

## Key functions / classes

**Internal:** `_lock()`, `_read_state_unlocked()`, `_write_state_unlocked()`, `_default_state()`, `_normalize_state(raw_state)`, `_build_assistant_id(name, existing_ids)`.

**Session:** `read_lab_state()`, `generate_session_code()`, `start_lab_session(session_code=None)`, `end_lab_session()`.

**Assistants:** `join_session(code, name)`, `leave_session(assistant_id)`, `remove_assistant(assistant_id)`.

**Assignment:** `assign_student(student_id, assistant_id)`, `self_claim_student(student_id, assistant_id)`, `unassign_student(student_id)`, `mark_student_helped(student_id)`, `get_assignment_for_assistant(assistant_id)`, `set_allow_self_allocation(enabled)`.

## Dependencies

- `filelock.FileLock` on `lab_session.lock`, JSON via stdlib, paths from [[paths]].
- **No `streamlit` import** — deliberate.
- Called from [[instructor_app]] and [[assistant_app]].

## Related notes

- [[Lab Assistant System]] (thematic)
- [[Two-App Shared State System]] (god node in the graphify report)
