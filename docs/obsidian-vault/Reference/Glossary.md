# Glossary

This glossary defines the project terms that recur across the dashboard, analytics code, and session-state model. It is intentionally practical rather than theoretical, so the definitions match how the code currently behaves.

Related: [[Student Struggle Logic]], [[Question Difficulty Logic]], [[Instructor Dashboard]], [[Lab Assistant System]]

## Terms

- `Incorrectness`: continuous score in `[0, 1]` derived from `ai_feedback` text through OpenAI; lower means more correct.
- `CORRECT_THRESHOLD`: cutoff used to treat an attempt as correct vs incorrect; currently `0.5`.
- `Struggle score`: per-student weighted aggregate used for the student leaderboard.
- `Difficulty score`: per-question weighted aggregate used for the question leaderboard.
- `A_raw`: recent incorrectness term for student struggle, using the last 5 submissions with exponential time decay.
- `d_hat`: normalized slope of a student's incorrectness over time; positive means worsening performance.
- `rep_hat`: rate at which a student exactly repeats the same answer on the same question.
- `CF`: collaborative filtering layer over normalized student-behavior features; currently shown diagnostically.
- `Live session`: instructor-started time window that begins at `session_start` and coordinates assistants through a shared code.
- `Saved session`: persisted record with a fixed `start_time` and `end_time`, reloaded from `data/saved_sessions.json`.
- `Dashboard filter state`: general UI filters such as time filter, today-only scope, and secondary module filter.
- `Live session state`: session-specific runtime keys such as `session_active`, `session_start`, and `lab_session_code`.
- `Saved session state`: keys such as `loaded_session_id`, `loaded_session_start`, and `loaded_session_end`.
- `Self-allocation`: assistant ability to claim a student without instructor assignment when enabled.
- `Session code`: 6-character code that assistants use to join the live lab session.
- `Assignment status`: either `helping` or `helped` for a student/assistant pairing in shared state.

## Code references

- `learning_dashboard/config.py`
- `learning_dashboard/analytics.py`
- `learning_dashboard/instructor_app.py`
- `learning_dashboard/lab_state.py`
- `data/saved_sessions.json`
- `data/lab_session.json`
