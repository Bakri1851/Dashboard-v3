# Academic Period Converter (2025/26)

This page documents the academic period converter used in the dashboard. It maps any date to a Loughborough University 2025/26 academic period label.

Related: [[Glossary]], [[Configuration and Runtime Paths]], [[Analytics Engine]]

## Period Labels

- `Sem 1 - Wk X`
- `Christmas X`
- `Inter Semester Week`
- `Sem 2 - Wk X`
- `Easter X`
- `Break`

## Implementation

The converter lives in `learning_dashboard/academic_calendar.py` and exposes:

- `get_academic_period(date)` — returns the period label for any date
- `academic_period_sorter(period)` — returns a sort tuple for chronological ordering
- `add_academic_period_column(df)` — adds an `academic_period` column to a DataFrame

The `academic_period` column is added automatically during `normalize_and_clean()` in `data_loader.py`, so all downstream views have access to it.

## Where It Appears in the Dashboard

1. **Info bar** — every page shows the current academic period next to the view name
2. **Data Analysis > Activity by Academic Week** — bar chart of submissions grouped by period

## Copy-Paste Python Converter

```python
import pandas as pd


def get_academic_period(date):
    """
    Map a date to a 2025/26 academic period label.
    """
    date_ts = pd.Timestamp(date)

    sem1_start = pd.Timestamp("2025-09-29")
    christmas_start = pd.Timestamp("2025-12-15")
    sem1_resume = pd.Timestamp("2026-01-05")
    inter_semester_week = pd.Timestamp("2026-01-26")
    sem2_start = pd.Timestamp("2026-02-02")
    easter_start = pd.Timestamp("2026-03-23")
    sem2_resume = pd.Timestamp("2026-04-13")
    sem2_end = pd.Timestamp("2026-06-15")

    if sem1_start <= date_ts < christmas_start:
        week_num = ((date_ts - sem1_start).days // 7) + 1
        return f"Sem 1 - Wk {week_num}"

    if christmas_start <= date_ts < sem1_resume:
        week_num = ((date_ts - christmas_start).days // 7) + 1
        return f"Christmas {week_num}"

    if sem1_resume <= date_ts < inter_semester_week:
        pre_christmas_weeks = 11
        additional_weeks = ((date_ts - sem1_resume).days // 7) + 1
        week_num = pre_christmas_weeks + additional_weeks
        return f"Sem 1 - Wk {week_num}"

    if inter_semester_week <= date_ts < sem2_start:
        return "Inter Semester Week"

    if sem2_start <= date_ts < easter_start:
        week_num = ((date_ts - sem2_start).days // 7) + 1
        return f"Sem 2 - Wk {week_num}"

    if easter_start <= date_ts < sem2_resume:
        week_num = ((date_ts - easter_start).days // 7) + 1
        return f"Easter {week_num}"

    if sem2_resume <= date_ts < sem2_end:
        pre_easter_weeks = 7
        additional_weeks = ((date_ts - sem2_resume).days // 7) + 1
        week_num = pre_easter_weeks + additional_weeks
        return f"Sem 2 - Wk {week_num}"

    return "Break"
```

## Sorting Function

```python
def academic_period_sorter(period):
    if "Sem 1" in period:
        week_num = int(period.split("Wk")[1].strip())
        if week_num <= 11:
            return 1, week_num
        return 3, week_num

    if "Christmas" in period:
        return 2, int(period.split(" ")[1])

    if period == "Inter Semester Week":
        return 4, 0

    if "Sem 2" in period:
        week_num = int(period.split("Wk")[1].strip())
        if week_num <= 7:
            return 5, week_num
        return 7, week_num

    if "Easter" in period:
        return 6, int(period.split(" ")[1])

    return 8, 0
```

## 2025/26 Weekly Mapping

### Semester 1

- `Sem 1 - Wk 1` starts `2025-09-29`
- `Sem 1 - Wk 2` starts `2025-10-06`
- `Sem 1 - Wk 3` starts `2025-10-13`
- `Sem 1 - Wk 4` starts `2025-10-20`
- `Sem 1 - Wk 5` starts `2025-10-27`
- `Sem 1 - Wk 6` starts `2025-11-03`
- `Sem 1 - Wk 7` starts `2025-11-10`
- `Sem 1 - Wk 8` starts `2025-11-17`
- `Sem 1 - Wk 9` starts `2025-11-24`
- `Sem 1 - Wk 10` starts `2025-12-01`
- `Sem 1 - Wk 11` starts `2025-12-08`

### Christmas

- `Christmas 1` starts `2025-12-15`
- `Christmas 2` starts `2025-12-22`
- `Christmas 3` starts `2025-12-29`

### Semester 1 Resume

- `Sem 1 - Wk 12` starts `2026-01-05`
- `Sem 1 - Wk 13` starts `2026-01-12`
- `Sem 1 - Wk 14` starts `2026-01-19`

### Inter Semester

- `Inter Semester Week` starts `2026-01-26`

### Semester 2 Before Easter

- `Sem 2 - Wk 1` starts `2026-02-02`
- `Sem 2 - Wk 2` starts `2026-02-09`
- `Sem 2 - Wk 3` starts `2026-02-16`
- `Sem 2 - Wk 4` starts `2026-02-23`
- `Sem 2 - Wk 5` starts `2026-03-02`
- `Sem 2 - Wk 6` starts `2026-03-09`
- `Sem 2 - Wk 7` starts `2026-03-16`

### Easter

- `Easter 1` starts `2026-03-23`
- `Easter 2` starts `2026-03-30`
- `Easter 3` starts `2026-04-06`

### Semester 2 Resume

- `Sem 2 - Wk 8` starts `2026-04-13`
- `Sem 2 - Wk 9` starts `2026-04-20`
- `Sem 2 - Wk 10` starts `2026-04-27`
- `Sem 2 - Wk 11` starts `2026-05-04`
- `Sem 2 - Wk 12` starts `2026-05-11`
- `Sem 2 - Wk 13` starts `2026-05-18`
- `Sem 2 - Wk 14` starts `2026-05-25`
- `Sem 2 - Wk 15` starts `2026-06-01`
- `Sem 2 - Wk 16` starts `2026-06-08`

Dates before `2025-09-29` or on/after `2026-06-15` return `Break`.

## Example Checks

- `2025-09-29 -> Sem 1 - Wk 1`
- `2025-12-15 -> Christmas 1`
- `2026-01-05 -> Sem 1 - Wk 12`
- `2026-01-26 -> Inter Semester Week`
- `2026-02-02 -> Sem 2 - Wk 1`
- `2026-03-23 -> Easter 1`
- `2026-04-13 -> Sem 2 - Wk 8`
- `2026-06-08 -> Sem 2 - Wk 16`
- `2026-06-15 -> Break`
