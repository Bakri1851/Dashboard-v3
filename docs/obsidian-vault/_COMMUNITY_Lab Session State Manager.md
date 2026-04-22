---
type: community
cohesion: 0.28
members: 23
---

# Lab Session State Manager

**Cohesion:** 0.28 - loosely connected
**Members:** 23 nodes

## Members
- [[Shared lab-session state management for instructor and assistant apps.]] - rationale - code\learning_dashboard\lab_state.py
- [[_build_assistant_id()]] - code - code\learning_dashboard\lab_state.py
- [[_default_state()]] - code - code\learning_dashboard\lab_state.py
- [[_lock()]] - code - code\learning_dashboard\lab_state.py
- [[_normalize_state()]] - code - code\learning_dashboard\lab_state.py
- [[_now_iso()]] - code - code\learning_dashboard\lab_state.py
- [[_read_state_unlocked()]] - code - code\learning_dashboard\lab_state.py
- [[_remove_assistant_unlocked()]] - code - code\learning_dashboard\lab_state.py
- [[_write_state_unlocked()]] - code - code\learning_dashboard\lab_state.py
- [[assign_student()]] - code - code\learning_dashboard\lab_state.py
- [[end_lab_session()]] - code - code\learning_dashboard\lab_state.py
- [[generate_session_code()]] - code - code\learning_dashboard\lab_state.py
- [[get_assignment_for_assistant()]] - code - code\learning_dashboard\lab_state.py
- [[join_session()]] - code - code\learning_dashboard\lab_state.py
- [[lab_state.py]] - code - code\learning_dashboard\lab_state.py
- [[leave_session()]] - code - code\learning_dashboard\lab_state.py
- [[mark_student_helped()]] - code - code\learning_dashboard\lab_state.py
- [[read_lab_state()]] - code - code\learning_dashboard\lab_state.py
- [[remove_assistant()]] - code - code\learning_dashboard\lab_state.py
- [[self_claim_student()]] - code - code\learning_dashboard\lab_state.py
- [[set_allow_self_allocation()]] - code - code\learning_dashboard\lab_state.py
- [[start_lab_session()]] - code - code\learning_dashboard\lab_state.py
- [[unassign_student()]] - code - code\learning_dashboard\lab_state.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Lab_Session_State_Manager
SORT file.name ASC
```
