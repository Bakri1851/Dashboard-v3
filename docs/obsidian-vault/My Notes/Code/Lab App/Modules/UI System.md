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

## Metric Card Tooltips

`render_metric_card(label, value, color, tooltip="")` accepts an optional `tooltip` parameter. When provided, a `data-tooltip` HTML attribute is emitted on the card `<div>`. The matching CSS in `get_main_css()` (`theme.py`) uses a `::after` pseudo-element to show a styled tooltip on hover — dark card background, cyan border glow, mono font, 210 px wide, fades in over 0.18 s.

`_SUMMARY_TOOLTIPS` (module-level dict in `components.py`) holds the four struggle-level summary tooltips.

### All metric cards and their tooltips

| View | Label | Tooltip |
| --- | --- | --- |
| In Class | Needs Help | Struggle score > 0.50. Highest combined incorrectness, retry rate, and recent difficulty. Immediate attention recommended. |
| In Class | Struggling | Struggle score 0.35–0.50. Consistent difficulty signals. Consider checking in soon. |
| In Class | Minor Issues | Struggle score 0.20–0.35. Some difficulty present. Monitor over upcoming submissions. |
| In Class | On Track | Struggle score < 0.20. Performing well with low incorrectness and positive trends. |
| In Class (CF) | CF Elevated | Students whose struggle level was raised by Collaborative Filtering above the parametric model prediction. CF compares incorrectness patterns to similar peers. |
| In Class (CF) | Parametric Flagged | Students flagged by the baseline parametric model (incorrectness, retry rate, time, trajectory) without CF adjustment. |
| In Class (CF) | Threshold (τ) | Minimum cosine similarity for two students to be considered similar peers in CF. Lower = broader peer groups; higher = stricter matching. |
| Student Detail | Total Submissions | Total answer submissions by this student across all questions in the current session window. |
| Student Detail | Time Active (min) | Minutes between this student's first and last submission in the session window. |
| Student Detail | Mean Incorrectness (%) | Average AI-scored incorrectness across all submissions. 0 = fully correct, 100 = fully incorrect. |
| Student Detail | Recent Incorrectness | Time-decayed incorrectness weighting recent submissions more heavily (30-min half-life). |
| Question Detail | Total Attempts | Total number of times this question was attempted by any student in the current session. |
| Question Detail | Unique Students | Distinct students who submitted at least one answer to this question. |
| Question Detail | Avg Attempts/Student | Mean submission attempts per student. High values indicate repeated retries due to difficulty. |
| Question Detail | Incorrect Rate (%) | Percentage of attempts scored as incorrect (incorrectness ≥ 0.50 by AI model). |
| Comparison | Agreement (students/questions) | Percentage where both models assigned the same level. Higher = improved model broadly confirms the baseline. |
| Comparison | Upgraded | Count rated at a higher severity by the improved model — may have been underestimated by the baseline. |
| Comparison | Downgraded | Count rated at a lower severity by the improved model — may have been overestimated by the baseline. |
| Comparison | Unchanged | Count where both models agree on the same level — forms the agreement cohort. |

## Code references

- `code/learning_dashboard/ui/views.py`
- `code/learning_dashboard/ui/components.py`
- `code/learning_dashboard/ui/theme.py`: `get_main_css()`, `get_plotly_layout_defaults()`
- `code/learning_dashboard/sound.py`
