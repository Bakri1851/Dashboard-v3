# assistant_app.py

**Path:** `code/learning_dashboard/assistant_app.py`
**Folder:** [[learning_dashboard]]

> Entry module for the mobile lab assistant portal. Implements a four-state flow driven by `lab_state.json` and persists assistant identity in the URL (`?aid=`).

## Responsibilities

- Own its own `@st.cache_data(ttl=10)` cycle via `_load_student_data()` — independent from the instructor app's cache.
- Render one of four screens based on `read_lab_state()`:
  1. **No active session** — `render_session_ended()`
  2. **Active session, not joined** — `render_join_screen(lab_data)`
  3. **Joined, unassigned** — `render_unassigned_view(...)` with the struggle-ranked student list (and self-claim, when allowed)
  4. **Joined and assigned** — `render_assigned_view(...)` with the student card, struggle badge, and RAG coaching suggestions
- Persist the assistant's identity across refreshes via the `?aid=` URL query parameter (`_coerce_query_value`, `_clear_assistant_query_param`).
- Fire event sounds on join, assignment received, high struggle; auto-refresh the page every 5 s.

## Key functions / classes

- `main()` — single entry point called by `code/lab_app.py`.
- `_load_student_data()` — cached fetch + analytics shortcut that returns the struggle DataFrame.
- `render_session_ended()` · `render_join_screen(lab_data)` · `render_unassigned_view(...)` · `render_assigned_view(...)`
- `_render_session_status_strip(lab_data, assistant_name)`
- Notice helpers: `_set_join_notice`, `_pop_join_notice`, `_leave_session`.
- Presentation helpers: `_heading`, `_section_label`, `_struggle_badge`.

## Dependencies

- `streamlit`, `streamlit_autorefresh`, `pandas`.
- Imports [[config]], [[data_loader]], [[analytics]], [[lab_state]], [[sound]], [[rag]], and the mobile CSS from [[theme]].

## Related notes

- [[Assistant App]] · [[Lab Assistant System]] (thematic)
- [[Assistant App Four-View Routing Flow]] (hyperedge in graphify report)
