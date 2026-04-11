---
type: community
cohesion: 0.15
members: 13
---

# Academic Calendar Module

**Cohesion:** 0.15 - loosely connected
**Members:** 13 nodes

## Members
- [[Add an 'academic_period' column derived from the timestamp column.]] - rationale - code\learning_dashboard\academic_calendar.py
- [[Format a date window as one academic period label or a range.]] - rationale - code\learning_dashboard\academic_calendar.py
- [[Map a date to a 202526 academic period label.]] - rationale - code\learning_dashboard\academic_calendar.py
- [[Populate ACADEMIC_PERIODS from the boundary dates.]] - rationale - code\learning_dashboard\academic_calendar.py
- [[Return (start_date, end_date) inclusive for a period label, or None.]] - rationale - code\learning_dashboard\academic_calendar.py
- [[Return a sort tuple for correct chronological ordering of period labels.]] - rationale - code\learning_dashboard\academic_calendar.py
- [[_build_periods()]] - code - code\learning_dashboard\academic_calendar.py
- [[academic_calendar.py]] - code - code\learning_dashboard\academic_calendar.py
- [[academic_period_sorter()]] - code - code\learning_dashboard\academic_calendar.py
- [[add_academic_period_column()]] - code - code\learning_dashboard\academic_calendar.py
- [[format_academic_period_window()]] - code - code\learning_dashboard\academic_calendar.py
- [[get_academic_period()]] - code - code\learning_dashboard\academic_calendar.py
- [[get_period_date_range()]] - code - code\learning_dashboard\academic_calendar.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Academic_Calendar_Module
SORT file.name ASC
```
