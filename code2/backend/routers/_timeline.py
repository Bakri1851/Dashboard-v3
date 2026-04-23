"""Shared chart-data helpers for routers."""
from __future__ import annotations

import pandas as pd


def hour_of_day_distribution(df: pd.DataFrame) -> list[int]:
    """Hour-of-day submission distribution (24 buckets: 00..23) over `df`.

    Not wall-clock-24h — this is a filtered aggregate, so it respects whatever
    filter produced `df`. Callers that also want peak_hour / peak_count can
    derive them from the returned list via argmax."""
    if df.empty or "timestamp" not in df.columns:
        return [0] * 24
    ts = pd.to_datetime(df["timestamp"], errors="coerce", utc=True).dropna()
    if ts.empty:
        return [0] * 24
    hod = ts.dt.hour
    return [int((hod == h).sum()) for h in range(24)]
