# instructor_app.py

**Path:** `code/learning_dashboard/instructor_app.py`
**Folder:** [[learning_dashboard]]

> Entry module for the instructor dashboard. Owns session-state initialisation, sidebar rendering, filter precedence, and view routing.

## Responsibilities

- Initialise every Streamlit session-state key on first render (`init_session_state`).
- Apply the **deferred actions pattern** at the top of `main()` — pending flags (e.g., `pending_session_load_record`, `pending_return_to_live_data`) are consumed before any widget renders, because Streamlit cannot mutate `session_state` after widget instantiation in the same run.
- Render the sidebar: lab-session card (with 6-char code), auto-refresh controls, view selector, dashboard-view selector, manual time filter, module filter, today-only scope, model toggles, session save/load controls.
- Apply filters in order — manual time → live session start → saved session window — then module filter on top.
- Route the filtered DataFrame to the appropriate view in [[views]] (In Class / Question Detail / Student Detail / Comparison / Data Analysis / Previous Sessions / Settings).

## Key functions / classes

- `main()` — the single entry point called by `code/app.py`.
- `init_session_state()` — seeds all session-state keys with defaults from [[config]].
- `render_sidebar(df)` — returns the filtered DataFrame.
- `_resolve_time_filter_window()` · `_get_dataframe_window(df)` · `_resolve_display_academic_period(df)`
- `_render_lab_assignment_panel()` · `_render_lab_code_card(code)`
- `_on_view_change()` · `_on_dashboard_view_change()` — widget callbacks that play navigation sounds.
- `_coerce_datetime(value)` — defensive parsing helper.

## Dependencies

- `streamlit`, `streamlit_autorefresh`, `pandas`.
- Imports [[config]], [[data_loader]], [[analytics]], [[lab_state]], [[sound]], [[paths]], [[academic_calendar]], and everything in [[ui]].

## Related notes

- [[Instructor Dashboard]] (thematic)
- [[App Entrypoint]] · [[Deferred Actions Pattern]]
