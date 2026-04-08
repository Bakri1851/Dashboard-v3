Part of [[Lab App]] · see also [[Assistant App/Modules/UI System]]

# Lab App — UI System

The instructor UI layer is split into page layouts, reusable widgets, theme/CSS helpers, and browser-side sound effects. This keeps the app visually consistent while letting routing and analytics stay outside the rendering code.

Related: [[Architecture]], [[Lab App/Flows/Pages and UI Flow]], [[Instructor Dashboard]]

## Page composition

- `views.py` owns page-level layouts for the instructor app.
- `components.py` owns reusable cards, charts, tables, leaderboards, and formula panels.
- `theme.py` provides the sci-fi neon desktop theme plus a separate mobile CSS bundle.
- `sound.py` injects JavaScript audio snippets through Streamlit components.

## Desktop layout

- The instructor app loads `get_main_css()` and uses a wide layout.
- Both apps share the same font family and color palette from `config.py`.

## Interaction patterns

- Leaderboards use Plotly selection events to trigger drill-down navigation.
- Page transitions are managed through `st.session_state` rather than a router framework.
- Sound effects are optional and triggered on navigation, refresh, selection, and high-struggle alerts.

## Plotly defaults

- `get_plotly_layout_defaults()` in `theme.py` returns a shared layout dict applied to all charts for visual consistency.

## Code references

- `code/learning_dashboard/ui/views.py`
- `code/learning_dashboard/ui/components.py`
- `code/learning_dashboard/ui/theme.py`: `get_main_css()`, `get_plotly_layout_defaults()`
- `code/learning_dashboard/sound.py`
