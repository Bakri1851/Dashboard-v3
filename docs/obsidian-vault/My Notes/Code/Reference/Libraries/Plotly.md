---
name: Plotly
description: Interactive charting library used for all dashboard visualisations
type: reference
---

# Plotly

Python graphing library that produces interactive, browser-rendered charts via a JavaScript backend.

## Version

`plotly >= 5.18.0`

## Why this library

The leaderboard charts need to be clickable — a user selects a bar or point to drill into a specific student or question. Plotly's `on_select` event (exposed through `st.plotly_chart`) is the cleanest way to achieve this inside Streamlit. Matplotlib and Altair do not support the same level of interactive selection.

## Where used

- `code/learning_dashboard/ui/components.py` — all chart-rendering functions
- `code/learning_dashboard/ui/views.py` — calls component renderers for each page
- `code/learning_dashboard/ui/theme.py` — `get_plotly_layout_defaults()` returns a shared layout dict applied to every figure

## Key classes and functions used

- `plotly.graph_objects` (`go`) — primary API for building figures
  - `go.Figure` — base figure container
  - `go.Bar` — horizontal/vertical bar charts for leaderboards
  - `go.Scatter` — line/scatter charts for trend views
  - `go.Indicator` — gauge/metric cards for student detail
- `st.plotly_chart(fig, on_select="rerun", use_container_width=True)` — renders the figure in Streamlit; `on_select="rerun"` stores the clicked point index in Streamlit widget state and triggers a rerun, which the routing logic reads to navigate to a drill-down view

## Theme integration

`theme.get_plotly_layout_defaults()` returns a dict of shared layout properties (background colour, font, grid style) matching the sci-fi neon CSS theme. Every chart passes this dict into `fig.update_layout()` to stay visually consistent.

## Related

- [[UI System]]
- [[Lab App/Flows/Pages and UI Flow]]
- [[Streamlit]]
