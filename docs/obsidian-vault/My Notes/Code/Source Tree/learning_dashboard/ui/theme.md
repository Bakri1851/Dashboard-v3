# theme.py

**Path:** `code/learning_dashboard/ui/theme.py`
**Folder:** [[ui]]

> All visual styling — sci-fi neon desktop CSS for the instructor dashboard, mobile CSS for the lab assistant app, and Plotly layout defaults.

## Responsibilities

- Generate the full main CSS block (`get_main_css`) for the instructor dashboard: gradient backgrounds (cyan / magenta glow), Orbitron headings, Share Tech Mono body, custom sidebar, buttons, inputs, metric cards, expanders.
- Generate mobile-optimised CSS (`get_mobile_css`) for the assistant portal at `375px+`.
- Expose a `get_plotly_layout_defaults()` dict that every chart in [[components]] merges into its `update_layout()`.
- Inject a Google Fonts `<link>` via `get_google_fonts_import()`.
- Resolve the accent colour by converting hex (e.g., `COLORS["cyan"]`) into `rgb(...)` for CSS rgba usage.

## Key functions / classes

- `get_google_fonts_import()` → `<link>` tag string.
- `get_main_css()` → full desktop CSS block.
- `get_mobile_css()` → mobile CSS for the assistant app.
- `get_plotly_layout_defaults()` → dict (font, paper/plot bg, grid colours, legend, axes).
- `_hex_to_rgb(hex_color)` — internal helper.

## Dependencies

- Reads [[config]] for the colour palette and font names.
- Consumed by [[instructor_app]] (once, at page top) and [[assistant_app]] (mobile CSS).

## Related notes

- [[UI System]] (thematic)
- [[Streamlit]] · [[Plotly]] (library notes)
