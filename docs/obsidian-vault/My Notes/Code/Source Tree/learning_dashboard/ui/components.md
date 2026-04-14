# components.py

**Path:** `code/learning_dashboard/ui/components.py`
**Folder:** [[ui]]

> Reusable Streamlit and Plotly building blocks used across all instructor views.

## Responsibilities

- Render the branded header, info strip, and neon metric cards.
- Render the four struggle-level summary cards and the student/question detail metric rows.
- Render the Plotly leaderboards (struggle, difficulty) with `on_select="rerun"` for click-to-drill-down.
- Render Plotly score distributions, bar charts, timelines, retry trends, data tables, and the Data Analysis view's specialised charts (module usage, top questions, user activity, activity timeline, academic period, students by module).
- Render the model-comparison panels (agreement summary, scatter, side-by-side table).
- Render the mistake-cluster card grid, the AI confidence indicator, the navigation loader, the back button, and the formula info expander.

## Key functions / classes

**Header / cards:** `render_header`, `render_info_bar`, `render_metric_card`, `render_summary_cards`, `render_entity_header_card`, `render_confidence_indicator`.

**Leaderboards + distributions:** `render_student_leaderboard`, `render_question_leaderboard`, `render_score_distributions`, `_apply_leaderboard_layout`.

**Detail metrics:** `render_student_detail_metrics`, `render_question_detail_metrics`.

**Charts:** `render_bar_chart`, `render_timeline_chart`, `render_retry_trend`, `render_data_table`, `render_module_usage_chart`, `render_top_questions_chart`, `render_user_activity_chart`, `render_activity_timeline_chart`, `render_academic_period_chart`, `render_students_by_module_chart`.

**Clusters + comparison + nav:** `render_mistake_clusters`, `render_agreement_summary`, `render_comparison_scatter`, `render_comparison_table`, `render_back_button`, `render_nav_loader`, `render_formula_info`, `_hex_to_rgb`.

## Dependencies

- `streamlit`, `plotly.graph_objects`, `plotly.express`, `pandas`, `numpy`.
- Uses [[config]] for thresholds/colours and [[theme]] for Plotly layout defaults.

## Related notes

- [[UI System]] (thematic)
- [[views]] — the consumers of every component
