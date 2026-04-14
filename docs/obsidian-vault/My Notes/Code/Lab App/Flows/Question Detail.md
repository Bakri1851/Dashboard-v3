Part of [[Lab App]] - see also [[Student Detail]]

# Question Detail

The Question Detail page is the instructor's per-question drill-down. It is entered from the question leaderboard and is driven by `st.session_state["selected_question"]` rather than a separate page route.

Related: [[Pages and UI Flow]], [[Instructor Dashboard]], [[UI System]], [[Question Difficulty Logic]], [[Student Struggle Logic]], [[Scikit-learn]], [[OpenAI]], [[Analytics Engine]]

## Entry and exit

- `in_class_view()` opens this page when `render_question_leaderboard()` returns a question ID.
- `instructor_app.main()` prioritizes `selected_question` over the normal page routing, so the drill-down replaces the standard dashboard view.
- The back button clears `selected_question`, removes the cached `question_leaderboard` selection, and reruns the app.

## Key Algorithms

- Difficulty scoring: the header score and label use the baseline weighted difficulty model from [[Question Difficulty Logic]].
- Confidence indicator: this is a heuristic confidence signal from the measurement layer over AI-derived incorrectness, not a separate uncertainty model or classifier.
- Mistake clustering: wrong answers are vectorized with TF-IDF, grouped with K-means, and the cluster count is chosen by silhouette score; see [[Scikit-learn]].
- Representative examples: within each cluster, cosine similarity to the centroid is used to pick the examples shown in the UI; see [[Scikit-learn]].
- Cluster labels: after clustering, [[OpenAI]] generates short human-readable labels for each cluster. The LLM names the groups, but it does not decide the cluster membership.
- Descriptive views: student tables and attempt timelines are aggregations, not ML models.

## Main sections

- Header card: question ID, difficulty score, and the current difficulty label/color from `difficulty_df`.
- Metric cards: total attempts, unique students, average attempts per student, and incorrect rate.
- Confidence indicator: when `_measurement_df` contains `incorrectness_confidence`, the page shows a small summary of mean AI confidence for this question.
- Mistake clusters: if enough incorrect answers exist, the page groups wrong answers into labeled clusters with counts and example answers.
- Student coverage: a table of students who attempted the question, including attempts and feedback-request counts.
- Time-based context: an hourly attempt timeline for the selected question.

## Fallback and edge behavior

- If the filtered question slice is empty, the page warns and stops rendering.
- If the question is missing from `difficulty_df`, the page warns instead of showing partial metrics.
- Clustering is skipped when incorrectness scores are unavailable or when the number of wrong answers stays below `CLUSTER_MIN_WRONG`.
- If clustering fails or returns no usable output, the page falls back to an informational message rather than an exception.

## Code references

- `code/learning_dashboard/ui/views.py`: `question_detail_view()`
- `code/learning_dashboard/ui/components.py`: `render_back_button()`, `render_entity_header_card()`, `render_question_detail_metrics()`, `render_confidence_indicator()`, `render_mistake_clusters()`, `render_timeline_chart()`, `render_data_table()`
- `code/learning_dashboard/analytics.py`: `cluster_question_mistakes()`
- `code/learning_dashboard/data_loader.py`: `add_feedback_flag()`
