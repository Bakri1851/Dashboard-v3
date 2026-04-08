# Known Issues — Assistant App

Confirmed implementation gap for the assistant app. See also [[Lab App/Operations/Known Issues]] for instructor-side issues.

Related: [[Lab Assistant System]], [[Assistant App/Flows/UI Flow]]

## Confirmed issues

- Assistant data scope mismatch: the assistant app computes `struggle_df` from whatever `data_loader.load_data()` returns, without applying the instructor's active live-session window or loaded saved-session window. This means assistants can be shown students outside the instructor's current teaching scope. See [[Lab Assistant System]] and [[Data Pipeline]].

## Why this matters

- Assistants may be directed to help students who are outside the instructor's current teaching context.
- It blurs the boundary between live teaching scope and global live data, reducing the practical accuracy of assistant-side struggle scores.

## Code references

- `code/learning_dashboard/assistant_app.py`: `_load_student_data()`
