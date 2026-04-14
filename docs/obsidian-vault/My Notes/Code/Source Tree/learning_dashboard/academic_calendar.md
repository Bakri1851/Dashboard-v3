# academic_calendar.py

**Path:** `code/learning_dashboard/academic_calendar.py`
**Folder:** [[learning_dashboard]]

> Loughborough 2025/26 academic calendar — converts dates to period labels used in the Data Analysis view and session summaries.

## Responsibilities

- Define the full 2025/26 period list (`ACADEMIC_PERIODS`) — Sem 1 Wks 1–14, Christmas 1–3, Inter-Semester Week, Sem 2 Wks 1–16, Easter 1–3.
- Map a date → the period it falls in, with a `"Break"` fallback for out-of-range dates.
- Format a date window as a single period label or a `Start → End` range.
- Provide a chronological sort key so dropdowns list periods correctly.
- Add an `academic_period` column onto a submissions DataFrame.

## Key functions / classes

- `get_academic_period(date)` → period label string.
- `get_period_date_range(label)` → `(start, end)` inclusive.
- `format_academic_period_window(start_dt, end_dt)` → single label or range string.
- `academic_period_sorter(period)` → sort tuple `(phase, week)`.
- `add_academic_period_column(df, col="timestamp")` — in-place column addition.

## Dependencies

- `pandas` for `Timestamp` comparisons.
- Called from [[data_loader]] during `normalize_and_clean()`; used in [[views]] for the Data Analysis period chart.

## Related notes

- [[Academic Period Converter]] (thematic, Reference section)
