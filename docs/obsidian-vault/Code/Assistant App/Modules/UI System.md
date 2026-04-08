Part of [[Assistant App]] · see also [[Lab App/Modules/UI System]]

# Assistant App — UI System

The assistant app UI is phone-friendly: a collapsed sidebar, mobile-optimized CSS, and four simple views rendered by `assistant_app.py`. It shares the color palette from `config.py` but has a distinct layout from the instructor dashboard.

Related: [[Architecture]], [[Assistant App/Flows/UI Flow]], [[Lab Assistant System]]

## Mobile layout

- The assistant app loads `get_mobile_css()` from `theme.py` and collapses the sidebar for phone-friendly use.
- The layout is designed for single-column reading on small screens.

## Views rendered by the assistant app

- `render_session_ended()` — shown when the session is inactive.
- `render_join_screen()` — session code + name entry form.
- `render_unassigned_view()` — waiting state, with optional self-allocation student list.
- `render_assigned_view()` — student card with struggle score, top-3 questions, and mark-as-helped button.

## Code references

- `code/learning_dashboard/assistant_app.py`: `render_session_ended()`, `render_join_screen()`, `render_unassigned_view()`, `render_assigned_view()`
- `code/learning_dashboard/ui/theme.py`: `get_mobile_css()`
