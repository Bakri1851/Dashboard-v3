"""FastAPI dependency injectors — centralise DataFrame fetches behind the cache."""
from __future__ import annotations

import pandas as pd
from fastapi import HTTPException

from backend.cache import load_dataframe


def get_dataframe() -> pd.DataFrame:
    """Return the current cached DataFrame. Raises 503 if the API upstream failed."""
    df, err = load_dataframe()
    if err and df.empty:
        raise HTTPException(status_code=503, detail=err)
    return df
