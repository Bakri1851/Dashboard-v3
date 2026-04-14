Part of [[Lab App]] - see also [[Question Detail]]

# Student Detail

The Student Detail page is the instructor's per-student drill-down. It is entered from the student leaderboard and is driven entirely by `st.session_state["selected_student"]` rather than a separate router entry.

Related: [[Pages and UI Flow]], [[Instructor Dashboard]], [[UI System]], [[Student Struggle Logic]], [[Question Difficulty Logic]], [[Scikit-learn]], [[OpenAI]], [[Analytics Engine]]

## Entry and exit

- `in_class_view()` opens this page when `render_student_leaderboard()` returns a student ID.
- `instructor_app.main()` prioritizes `selected_student` over `current_view`, so the drill-down replaces the normal dashboard pages.
- The back button clears `selected_student`, removes the cached `student_leaderboard` selection, and reruns the app.

## Key Algorithms

- Struggle scoring: the header and metric context use the baseline weighted behavioral struggle model from [[Student Struggle Logic]].
- Incorrectness measurement: that struggle model depends on OpenAI-derived incorrectness values from the analytics layer; see [[OpenAI]] and [[Analytics Engine]].
- Similar students: the CF panel uses collaborative filtering via cosine similarity over the normalized student feature set; see [[Scikit-learn]].
- Question difficulty columns: optional difficulty values in the question table come from the existing question-difficulty pipeline, but this page does not recompute or switch difficulty models itself.
- Descriptive views: timelines, question counts, recent submissions, and retry trend are aggregations and charts, not separate ML models.

## Main sections

- Header card: student ID, struggle score, and the current struggle label/color taken from `struggle_df`.
- Metric cards: total submissions, time active, mean incorrectness, and recent incorrectness.
- Question activity: a top attempted-questions chart plus a per-question table with attempt counts, feedback-request counts, and optional difficulty columns when `difficulty_df` is available.
- Time-based context: an hourly submission timeline and a rolling retry-intensity trend when the student has at least 3 submissions.
- Recent work: newest submissions table with timestamp, question, student answer, and AI feedback.
- Collaborative filtering: when `cf_enabled` is on, the page adds a "Most Similar Students" table based on cosine similarity over the existing behavioral features.

## Fallback and edge behavior

- If the filtered student slice is empty, the page warns and stops rendering.
- If the student is missing from `struggle_df`, the page warns instead of showing partial metrics.
- The retry trend is skipped for short histories, and the similar-student panel is wrapped in `try/except` so CF failures do not break the page.
- The page does not recalculate scores; it renders analytics that were already computed upstream.

## Code references

- `code/learning_dashboard/ui/views.py`: `student_detail_view()`
- `code/learning_dashboard/ui/components.py`: `render_back_button()`, `render_entity_header_card()`, `render_student_detail_metrics()`, `render_bar_chart()`, `render_timeline_chart()`, `render_retry_trend()`, `render_data_table()`
- `code/learning_dashboard/analytics.py`: `get_similar_students()`
- `code/learning_dashboard/data_loader.py`: `add_feedback_flag()`
