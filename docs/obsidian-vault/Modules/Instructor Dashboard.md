# Instructor Dashboard

The instructor dashboard is the orchestration center of the project. It owns session-state initialization, filter precedence, live-session controls, assistant management, analytics caching, and the routing between dashboard pages and drill-down screens.

Related: [[Architecture]], [[Dashboard Pages and UI Flow]], [[Data Loading and Session Persistence]], [[Lab Assistant System]], [[Known Issues]]

## Main responsibilities

- Initialize all expected `st.session_state` keys.
- Render the sidebar for session controls, filters, settings access, and history access.
- Start and end live sessions, including saved-session persistence and lab-state updates.
- Cache filtered analytics outputs and route to the correct page.
- Manage instructor-side assistant assignment, release, and removal actions.

## State categories

- Navigation: `current_view`, `dashboard_view`, `selected_student`, `selected_question`.
- Live session: `session_active`, `session_start`, `session_name_draft`, `lab_session_code`.
- Saved session: `loaded_session_id`, `loaded_session_start`, `loaded_session_end`, `pending_session_load_record`.
- Filters: `time_filter_enabled`, `time_date_range`, `time_start`, `time_end`, `secondary_module_filter`, `today_filter_only`.
- Diagnostics and caching: `_df`, `_struggle_df`, `_difficulty_df`, `_analytics_key`, `_lab_state_cache`.
- UX toggles: `cf_enabled`, `cf_threshold`, `sounds_enabled`, `auto_refresh`, `refresh_interval`.

## Flow highlights

- Deferred state changes are applied before widgets are rebuilt to avoid Streamlit widget mutation errors.
- Analytics are computed on the filtered instructor DataFrame, then reused until the cache fingerprint changes.
- When a live session starts, the dashboard writes a fresh shared lab-session file and shows a 6-character code.
- When a live session ends, the dashboard attempts to persist a saved-session record before clearing live state.

## Lab-assistant management inside the dashboard

- The sidebar lists current assistants and assignments.
- Instructors can toggle self-allocation.
- Unassigned assistants can be paired with students already classified as `Struggling` or `Needs Help`.
- Assistants can be released or removed from the instructor view.

## Code references

- `learning_dashboard/instructor_app.py`: `init_session_state()`
- `learning_dashboard/instructor_app.py`: `_render_lab_assignment_panel()`
- `learning_dashboard/instructor_app.py`: `render_sidebar()`
- `learning_dashboard/instructor_app.py`: `main()`
- `learning_dashboard/data_loader.py`: `build_session_record_from_state()`
- `learning_dashboard/lab_state.py`: `start_lab_session()`, `end_lab_session()`, `assign_student()`, `remove_assistant()`
