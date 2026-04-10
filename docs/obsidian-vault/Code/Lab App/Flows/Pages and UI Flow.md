Part of [[Lab App]] · see also [[Assistant App/Flows/UI Flow]]

# Lab App — Pages and UI Flow

The instructor dashboard is driven by a small set of page states and drill-down targets rather than a large routing system. Understanding the user flow means tracking how `current_view`, `selected_student`, and `selected_question` interact with sidebar actions, chart selections, and auto-refresh.

Related: [[Instructor Dashboard]], [[UI System]], [[Setup and Runbook]], [[Student Struggle Logic]], [[Question Difficulty Logic]], [[Analytics Engine]]

## Instructor app pages

- `In Class View`: default page with summary cards, student leaderboard, question leaderboard, collaborative-filtering diagnostics, score distributions, and formula panel.
- `Student Detail`: opened by selecting a student on the leaderboard; surfaces the baseline struggle score plus collaborative-filtering context. See [[Student Detail]].
- `Question Detail`: opened by selecting a question on the leaderboard; surfaces the baseline weighted difficulty score, measurement confidence, and mistake clustering. See [[Question Detail]].
- `Data Analysis View`: secondary charts for module usage, top questions, user activity, activity timeline, and students by module.
- `Settings`: toggles sound, auto-refresh, and collaborative filtering settings.
- `Previous Sessions`: lists saved sessions and supports load/delete actions; see [[Saved Session History]].

## Main transitions

- Sidebar radio switches between `In Class View` and `Data Analysis View`.
- Leaderboard selection sets `selected_student` or `selected_question`.
- Back buttons clear the selection and return to the dashboard.
- Loading a saved session is deferred, then applied before widgets are rebuilt.
- Returning to live data clears loaded-session state and resets the dashboard to default live mode.

## Detailed note map

- [[Student Detail]]: per-student drill-down layout, baseline struggle scoring, and collaborative-filtering context.
- [[Question Detail]]: per-question drill-down layout, weighted difficulty scoring, confidence heuristics, and mistake clustering.
- [[Analytics Engine]]: central algorithm map linking incorrectness measurement, baseline scoring, CF, clustering, and improved models.
- [[Live Assistant Assignment]]: live session assistant coordination inside the sidebar.
- [[Saved Session History]]: save/load/delete flows for historic lab windows.

## Sound triggers

- Refresh: plays on auto-refresh tick changes.
- Navigation: plays when the instructor changes between dashboard pages.
- Selection: plays on student/question selection and also on session start/end transitions in current code.

## Code references

- `code/learning_dashboard/instructor_app.py`: `_on_dashboard_view_change()`, `render_sidebar()`, `main()`
- `code/learning_dashboard/ui/views.py`: `in_class_view()`, `student_detail_view()`, `question_detail_view()`, `data_analysis_view()`, `settings_view()`, `previous_sessions_view()`
- `code/learning_dashboard/sound.py`
