# UI System

The UI layer is split into page layouts, reusable widgets, theme/CSS helpers, and browser-side sound effects. This keeps the app visually consistent while letting routing and analytics stay outside the rendering code.

Related: [[Architecture]], [[Dashboard Pages and UI Flow]], [[Instructor Dashboard]], [[Lab Assistant System]]

## Page composition

- `views.py` owns page-level layouts for the instructor app.
- `components.py` owns reusable cards, charts, tables, leaderboards, and formula panels.
- `theme.py` provides the sci-fi neon desktop theme plus a separate mobile CSS bundle.
- `sound.py` injects JavaScript audio snippets through Streamlit components.

## Desktop vs mobile split

- The instructor app loads `get_main_css()` and uses a wide layout.
- The assistant app loads `get_mobile_css()` and collapses the sidebar for phone-friendly use.
- Both apps share the same font family and color palette from `config.py`.

## Interaction patterns

- Leaderboards use Plotly selection events to trigger drill-down navigation.
- Page transitions are managed through `st.session_state` rather than a router framework.
- Sound effects are optional and triggered on navigation, refresh, selection, assistant join, assignment receipt, and high-struggle alerts.

## Code references

- `learning_dashboard/ui/views.py`
- `learning_dashboard/ui/components.py`
- `learning_dashboard/ui/theme.py`: `get_main_css()`, `get_mobile_css()`, `get_plotly_layout_defaults()`
- `learning_dashboard/sound.py`
