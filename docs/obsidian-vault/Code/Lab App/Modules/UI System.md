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

## Views (instructor)

| View | Function | Route key |
|---|---|---|
| In Class | `in_class_view(df, struggle_df, difficulty_df)` | `"In Class View"` |
| Data Analysis | `data_analysis_view(df)` | `"Data Analysis View"` |
| Model Comparison | `comparison_view(df)` | `"Model Comparison"` |
| Student Detail | `student_detail_view(...)` | `selected_student != None` |
| Question Detail | `question_detail_view(...)` | `selected_question != None` |
| Settings | `settings_view(df)` | `"Settings"` |
| Previous Sessions | `previous_sessions_view(df)` | `"Previous Sessions"` |

## Model Comparison View (Phase 5)

`comparison_view(df)` in `views.py` — gated by `improved_models_enabled` session state.

**Guard clause:** shows `st.info(...)` and returns early if improved models are disabled.

**Settings sub-panel (implemented):** when `improved_models_enabled` is on, Settings exposes three sub-model toggles (`irt_enabled`, `bkt_enabled`, `improved_struggle_enabled`) and four BKT parameter sliders (`bkt_p_init`, `bkt_p_learn`, `bkt_p_guess`, `bkt_p_slip`). Any change to these controls updates `_improved_models_settings_key` — a fingerprint string that `instructor_app.py` watches to trigger automatic recomputation of all improved-model outputs without a manual refresh.

**Layout:**
1. `render_info_bar(...)` header
2. `st.tabs(["Student Struggle Comparison", "Question Difficulty Comparison"])`
3. Each tab: merges baseline + improved DataFrames on entity key, then renders:
   - `render_agreement_summary(...)` — 4 metric cards (Agreement %, Upgraded, Downgraded, Unchanged)
   - Two columns: left = `render_comparison_scatter(...)`, right = `render_comparison_table(...)`

**Session state keys read:**
- `_struggle_df` — baseline struggle scores
- `_improved_struggle_df` — Phase 4 improved struggle scores
- `_difficulty_df` — baseline difficulty scores
- `_irt_difficulty_df` — Phase 2 IRT difficulty scores

**IRT column note:** `_irt_difficulty_df` has `irt_difficulty` (sigmoid [0,1]) and `irt_difficulty_level` classified by `IRT_DIFFICULTY_THRESHOLDS`. The view uses these directly without extra normalisation.

## Comparison Components (Phase 5)

Three new functions in `components.py`:

**`render_agreement_summary(baseline_levels, improved_levels, level_order, entity_label)`**
- Aligns two `pd.Series` of level labels; computes agreement %, upgraded, downgraded, unchanged counts
- Level order derived from config threshold list (passed in by caller); ordinal index determines direction
- Renders 4 `render_metric_card()` cells in `st.columns(4)`

**`render_comparison_scatter(baseline_scores, improved_scores, labels, title)`**
- Plotly scatter: baseline on x, improved on y; diagonal y=x reference line in `text_dim` dashed
- Points above the line = improved model rates higher
- Hover: entity label + both scores to 3 dp
- Uses `theme.get_plotly_layout_defaults()`; height 400

**`render_comparison_table(merged_df, entity_col, baseline_score_col, baseline_level_col, improved_score_col, improved_level_col)`**
- Caller passes an already-merged DataFrame
- Computes delta = improved − baseline; sorts by |delta| descending (biggest disagreements first)
- Pandas Styler colours delta column: green > 0, red < 0
- Rendered via `st.dataframe(styler, hide_index=True)`

## Code references

- `code/learning_dashboard/ui/views.py`
- `code/learning_dashboard/ui/components.py`
- `code/learning_dashboard/ui/theme.py`: `get_main_css()`, `get_plotly_layout_defaults()`
- `code/learning_dashboard/sound.py`
