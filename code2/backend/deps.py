"""FastAPI dependency injectors — centralise DataFrame fetches behind the cache."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd
from fastapi import Depends, HTTPException, Query

from backend.cache import filter_df, load_dataframe


@dataclass
class TimeWindow:
    """Filter bounds parsed off `?from=` / `?to=` (ISO 8601)."""

    from_: Optional[str] = None
    to_: Optional[str] = None

    @property
    def active(self) -> bool:
        return bool(self.from_ or self.to_)


def get_time_window(
    from_: Optional[str] = Query(default=None, alias="from"),
    to_: Optional[str] = Query(default=None, alias="to"),
) -> TimeWindow:
    """FastAPI dependency that extracts `?from=` / `?to=` query params."""
    return TimeWindow(from_=from_, to_=to_)


def get_dataframe() -> pd.DataFrame:
    """Return the full cached DataFrame. 503 on upstream failure."""
    df, err = load_dataframe()
    if err and df.empty:
        raise HTTPException(status_code=503, detail=err)
    return df


def get_filtered_dataframe(
    df: pd.DataFrame = Depends(get_dataframe),
    window: TimeWindow = Depends(get_time_window),
) -> pd.DataFrame:
    """DataFrame sliced to [from_, to_] when either is present, otherwise full."""
    if not window.active:
        return df
    return filter_df(df, window.from_, window.to_)
