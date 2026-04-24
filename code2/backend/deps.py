"""FastAPI dependency injectors — centralise DataFrame fetches behind the cache."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd
from fastapi import Depends, HTTPException, Query

from backend.cache import filter_df, load_dataframe
from learning_dashboard import data_loader


@dataclass
class TimeWindow:
    """Filter bounds parsed off `?from=` / `?to=` / `?module=` query params."""

    from_: Optional[str] = None
    to_: Optional[str] = None
    module: Optional[str] = None

    @property
    def active(self) -> bool:
        return bool(self.from_ or self.to_ or self.module)


def get_time_window(
    from_: Optional[str] = Query(default=None, alias="from"),
    to_: Optional[str] = Query(default=None, alias="to"),
    module: Optional[str] = Query(default=None, alias="module"),
) -> TimeWindow:
    """FastAPI dependency that extracts `?from=` / `?to=` / `?module=` query params."""
    mod = module.strip() if isinstance(module, str) else None
    if not mod or mod == "All Modules":
        mod = None
    return TimeWindow(from_=from_, to_=to_, module=mod)


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
    """DataFrame sliced to [from_, to_] and optionally scoped to a single module."""
    if not window.active:
        return df
    out = filter_df(df, window.from_, window.to_) if (window.from_ or window.to_) else df
    if window.module:
        out = data_loader.filter_by_module(out, window.module)
    return out
