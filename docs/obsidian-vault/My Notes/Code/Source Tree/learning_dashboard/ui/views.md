# views.py

**Path:** `code/learning_dashboard/ui/views.py`
**Folder:** [[ui]]

> Page-level layouts for every instructor view. Each function takes the filtered DataFrame (and any precomputed score DataFrames) and composes [[components]] into a full page.

## Responsibilities

- Render the main **In Class View**: summary cards → leaderboards → distributions → retry trend.
- Render the **Student Detail View**: header card → metrics → recent submissions → top questions for that student → CF similar-students panel.
- Render the **Question Detail View**: header card → metrics → mistake clusters → top strugglers on this question.
- Render the **Data Analysis View**: filters → raw submissions table → specialised activity charts.
- Render the **Comparison View**: baseline vs improved models (struggle and difficulty) with agreement summary, scatter, side-by-side table.
- Render the **Previous Sessions View**: list of saved sessions with load / delete / retroactive-save controls.
- Render the **Settings view**: model toggles, sub-toggles (IRT/BKT/Improved Struggle/RAG), sound toggle, temporal smoothing toggle, weight sliders — with setting helpers that keep `st.session_state` in sync.

## Key functions / classes

- `in_class_view(df, struggle_df, difficulty_df)`
- `student_detail_view(df, student_id, struggle_df, difficulty_df=None)`
- `question_detail_view(df, question_id, difficulty_df)`
- `data_analysis_view(df)`
- `comparison_view(df)`
- `previous_sessions_view(df)`
- `settings_view(df)`
- `_setting_toggle(label, state_key, **kwargs)` · `_setting_slider(...)` · `_setting_selectbox(...)`
- `_format_session_timestamp(raw_value)` · `_format_duration(seconds)`

## Dependencies

- `streamlit`, `pandas`, `plotly`.
- Imports [[config]], [[analytics]], [[data_loader]] (for filter helpers + saved sessions), [[rag]] (for cluster suggestions), [[academic_calendar]], every [[components]] helper, and the four advanced models in [[models]].

## Related notes

- [[UI System]]
- [[Instructor Dashboard]] — end-to-end view descriptions
