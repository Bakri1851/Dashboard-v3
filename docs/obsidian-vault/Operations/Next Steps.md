# Next Steps

The next round of work should tighten behavioral consistency before adding new features. Most of the highest-value improvements come from aligning analytics scope, cache correctness, and UI semantics with what the project already implies conceptually.

Related: [[Known Issues]], [[Instructor Dashboard]], [[Lab Assistant System]], [[Analytics Engine]]

## Priority backlog

1. Scope assistant analytics to the same filtered session window used by the instructor dashboard so assignment decisions and assistant views agree.
2. Decide the contract for collaborative filtering: keep it diagnostic, or let it elevate students into operational flags and assignment eligibility.
3. Replace the instructor analytics cache fingerprint with a stronger signature, ideally tied to the underlying filtered data content rather than row count and time bounds only.
4. Replace the mistake-cluster cache key with an answer-content signature so question-detail clustering invalidates when wrong-answer text changes.
5. Wire `play_session_start()` and `play_session_end()` into actual session transitions and keep `play_selection()` for navigation/selection only.
6. Add lightweight regression checks around session scoping, saved-session restore behavior, and assistant assignment flows before changing the scoring model.

## Documentation follow-up

- Keep [[Student Struggle Logic]] and [[Question Difficulty Logic]] in sync with any scoring changes.
- Update [[Dashboard Pages and UI Flow]] whenever the navigation model or assistant flow changes.
- Revisit [[Setup and Runbook]] if runtime files, commands, or secrets move.

## Code references

- `learning_dashboard/assistant_app.py`
- `learning_dashboard/instructor_app.py`
- `learning_dashboard/analytics.py`
- `learning_dashboard/sound.py`
