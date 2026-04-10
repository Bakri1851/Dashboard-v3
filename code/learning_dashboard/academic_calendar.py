# academic_calendar.py — Loughborough 2025/26 academic period converter
from datetime import date as _date, timedelta

import pandas as pd

# Ordered list of (start_date, end_date_exclusive, label) for every period in 2025/26.
ACADEMIC_PERIODS = []

def _build_periods():
    """Populate ACADEMIC_PERIODS from the boundary dates."""
    boundaries = [
        ("2025-09-29", "2025-10-06", "Sem 1 - Wk 1"),
        ("2025-10-06", "2025-10-13", "Sem 1 - Wk 2"),
        ("2025-10-13", "2025-10-20", "Sem 1 - Wk 3"),
        ("2025-10-20", "2025-10-27", "Sem 1 - Wk 4"),
        ("2025-10-27", "2025-11-03", "Sem 1 - Wk 5"),
        ("2025-11-03", "2025-11-10", "Sem 1 - Wk 6"),
        ("2025-11-10", "2025-11-17", "Sem 1 - Wk 7"),
        ("2025-11-17", "2025-11-24", "Sem 1 - Wk 8"),
        ("2025-11-24", "2025-12-01", "Sem 1 - Wk 9"),
        ("2025-12-01", "2025-12-08", "Sem 1 - Wk 10"),
        ("2025-12-08", "2025-12-15", "Sem 1 - Wk 11"),
        ("2025-12-15", "2025-12-22", "Christmas 1"),
        ("2025-12-22", "2025-12-29", "Christmas 2"),
        ("2025-12-29", "2026-01-05", "Christmas 3"),
        ("2026-01-05", "2026-01-12", "Sem 1 - Wk 12"),
        ("2026-01-12", "2026-01-19", "Sem 1 - Wk 13"),
        ("2026-01-19", "2026-01-26", "Sem 1 - Wk 14"),
        ("2026-01-26", "2026-02-02", "Inter Semester Week"),
        ("2026-02-02", "2026-02-09", "Sem 2 - Wk 1"),
        ("2026-02-09", "2026-02-16", "Sem 2 - Wk 2"),
        ("2026-02-16", "2026-02-23", "Sem 2 - Wk 3"),
        ("2026-02-23", "2026-03-02", "Sem 2 - Wk 4"),
        ("2026-03-02", "2026-03-09", "Sem 2 - Wk 5"),
        ("2026-03-09", "2026-03-16", "Sem 2 - Wk 6"),
        ("2026-03-16", "2026-03-23", "Sem 2 - Wk 7"),
        ("2026-03-23", "2026-03-30", "Easter 1"),
        ("2026-03-30", "2026-04-06", "Easter 2"),
        ("2026-04-06", "2026-04-13", "Easter 3"),
        ("2026-04-13", "2026-04-20", "Sem 2 - Wk 8"),
        ("2026-04-20", "2026-04-27", "Sem 2 - Wk 9"),
        ("2026-04-27", "2026-05-04", "Sem 2 - Wk 10"),
        ("2026-05-04", "2026-05-11", "Sem 2 - Wk 11"),
        ("2026-05-11", "2026-05-18", "Sem 2 - Wk 12"),
        ("2026-05-18", "2026-05-25", "Sem 2 - Wk 13"),
        ("2026-05-25", "2026-06-01", "Sem 2 - Wk 14"),
        ("2026-06-01", "2026-06-08", "Sem 2 - Wk 15"),
        ("2026-06-08", "2026-06-15", "Sem 2 - Wk 16"),
    ]
    for start_s, end_s, label in boundaries:
        ACADEMIC_PERIODS.append((
            _date.fromisoformat(start_s),
            _date.fromisoformat(end_s) - timedelta(days=1),  # inclusive end
            label,
        ))

_build_periods()

# All period labels in chronological order (for dropdowns).
ALL_PERIOD_LABELS = [label for _, _, label in ACADEMIC_PERIODS]


def get_period_date_range(label):
    """Return (start_date, end_date) inclusive for a period label, or None."""
    for start, end, name in ACADEMIC_PERIODS:
        if name == label:
            return start, end
    return None


def get_academic_period(date):
    """Map a date to a 2025/26 academic period label."""
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


def format_academic_period_window(start_dt, end_dt) -> str:
    """Format a date window as one academic period label or a range."""

    def _safe_period_label(value):
        if value is None:
            return None
        try:
            return get_academic_period(value)
        except (TypeError, ValueError):
            return None

    start_label = _safe_period_label(start_dt)
    end_label = _safe_period_label(end_dt)

    if start_label and end_label:
        if start_label == end_label:
            return start_label
        return f"{start_label} → {end_label}"

    if start_label:
        return start_label
    if end_label:
        return end_label
    return "Break"


def academic_period_sorter(period):
    """Return a sort tuple for correct chronological ordering of period labels."""
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


def add_academic_period_column(df, col="timestamp"):
    """Add an 'academic_period' column derived from the timestamp column."""
    if df.empty or col not in df.columns:
        df["academic_period"] = pd.Series(dtype="str")
        return df
    df["academic_period"] = df[col].apply(get_academic_period)
    return df
