# Known Issues

Several important behaviors in Dashboard-v3 are clear once the code is traced, but they are easy to miss from the UI alone. This note captures confirmed implementation gaps so future changes can distinguish intended behavior from current behavior.

Related: [[Instructor Dashboard]], [[Lab Assistant System]], [[Analytics Engine]], [[Next Steps]]

## Confirmed issues

- Assistant data scope mismatch: the assistant app computes `struggle_df` from whatever `data_loader.load_data()` returns, without applying the instructor's active live-session window or loaded saved-session window. This means assistants can be shown students outside the instructor's current teaching scope. See [[Lab Assistant System]] and [[Data Pipeline]].
- Collaborative filtering is diagnostic-only and defaults on: `cf_enabled` starts as `True` in the instructor session state, but CF output is only rendered as a panel and similar-student table. It does not update `struggle_level`, the main leaderboard, or assistant assignment eligibility. See [[Student Struggle Logic]] and [[Instructor Dashboard]].
- Instructor analytics caching is too weak: the cache key uses only `(len(df), min(timestamp), max(timestamp))`. If the contents change while those values stay the same, stale struggle and difficulty results can be reused. See [[Instructor Dashboard]] and [[Analytics Engine]].
- Mistake-cluster caching is too coarse: `_cluster_cache` is keyed only by `(question_id, total_wrong)`. Different wrong answers with the same count can therefore reuse stale cluster output. See [[Question Difficulty Logic]] and [[Analytics Engine]].
- Session lifecycle sounds are miswired: `play_session_start()` and `play_session_end()` exist, but the instructor app currently calls `play_selection()` when session activity toggles. See [[UI System]] and [[Dashboard Pages and UI Flow]].

## Why these matter

- They affect trust in what the dashboard is showing.
- They blur the boundary between live teaching scope and global live data.
- They make some analytics outputs feel more authoritative than their current implementation supports.

## Code references

- `learning_dashboard/assistant_app.py`: `_load_student_data()`
- `learning_dashboard/instructor_app.py`: `init_session_state()`, `main()`
- `learning_dashboard/ui/views.py`: `in_class_view()`, `student_detail_view()`
- `learning_dashboard/analytics.py`: `_cluster_cache`, `cluster_question_mistakes()`
- `learning_dashboard/sound.py`: `play_session_start()`, `play_session_end()`
