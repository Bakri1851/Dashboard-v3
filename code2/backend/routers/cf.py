"""Collaborative-filtering diagnostics.

- `GET /api/cf` — elevated students (CF surfaces them above the parametric
  baseline because their behaviour looks like a flagged student).
- `GET /api/student/{id}/similar` — top-K most similar students by cosine
  similarity on the 5 CF behavioural features.

Both endpoints respect the sidebar time-filter (the struggle cache is keyed
by window already) and the runtime `cf_enabled` / `cf_threshold` settings.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sklearn.metrics.pairwise import cosine_similarity

from backend import runtime_config
from backend.cache import _cf_cache, load_struggle_df
from backend.deps import TimeWindow, get_time_window
from backend.schemas import (
    CFDiagnostics,
    CFElevatedStudent,
    SimilarStudent,
)
from learning_dashboard import analytics

router = APIRouter(tags=["cf"])


_CF_FEATURES = analytics.CF_FEATURES  # ["n_hat", "t_hat", "i_norm", "A_norm", "d_hat"]
# Graceful fallback if struggle_df doesn't expose *_norm variants — use raw.
_CF_FEATURE_FALLBACKS = {
    "i_norm": "i_hat",
    "A_norm": "A_raw",
}


def _feature_matrix(struggle_df: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
    """Pull a (n_students × n_features) matrix out of the struggle DataFrame,
    substituting fallback columns when a preferred one is missing."""
    cols: list[str] = []
    for f in _CF_FEATURES:
        if f in struggle_df.columns:
            cols.append(f)
        elif _CF_FEATURE_FALLBACKS.get(f) in struggle_df.columns:
            cols.append(_CF_FEATURE_FALLBACKS[f])
        # else: skip silently
    if not cols:
        return np.empty((0, 0)), []
    X = struggle_df[cols].astype(float).fillna(0.0).to_numpy()
    return X, cols


@router.get("/cf", response_model=CFDiagnostics)
def get_cf(window: TimeWindow = Depends(get_time_window)) -> CFDiagnostics:
    rc = runtime_config.get()
    cache_key = (window.from_ or "", window.to_ or "", float(rc.cf_threshold))
    cached = _cf_cache.get(cache_key)
    if cached is not None:
        return cached

    struggle_df = load_struggle_df(window.from_, window.to_)
    if struggle_df.empty:
        result = CFDiagnostics(
            threshold=rc.cf_threshold,
            k=3,
            n_flagged_parametric=0,
            n_elevated_cf=0,
            fallback=True,
            reason="no data in window",
            elevated_students=[],
        )
        _cf_cache[cache_key] = result
        return result

    # Run the analytics function directly to reuse its logic.
    try:
        _cf_series, diagnostics = analytics.compute_cf_struggle_scores(
            struggle_df, threshold=rc.cf_threshold, k=3
        )
    except Exception as e:
        # Don't cache transient failures.
        return CFDiagnostics(
            threshold=rc.cf_threshold, k=3, n_flagged_parametric=0, n_elevated_cf=0,
            fallback=True, reason=f"{type(e).__name__}: {e}", elevated_students=[],
        )

    # Shape the elevated list for the UI. analytics.compute_cf_struggle_scores
    # emits rows keyed for the legacy Streamlit table ("Student" / "Parametric
    # Score" / "CF Score"); the React frontend expects snake_case, and level
    # isn't carried in the dict, so look it up from struggle_df.
    user_to_level: dict[str, str] = {}
    if "struggle_level" in struggle_df.columns:
        user_to_level = dict(
            zip(
                struggle_df["user"].astype(str),
                struggle_df["struggle_level"].astype(str),
            )
        )

    elevated_raw: list[dict] = diagnostics.get("elevated_students") or []
    elevated: list[CFElevatedStudent] = []
    for row in elevated_raw:
        try:
            uid = str(row.get("Student") or row.get("user") or row.get("id", ""))
            baseline = float(
                row.get("Parametric Score")
                if row.get("Parametric Score") is not None
                else (row.get("baseline_score") if row.get("baseline_score") is not None else row.get("struggle_score", 0.0))
            )
            cf = float(
                row.get("CF Score")
                if row.get("CF Score") is not None
                else row.get("cf_score", 0.0)
            )
            delta_val = row.get("delta")
            delta_f = float(delta_val) if delta_val is not None else (cf - baseline)
            level = str(
                row.get("struggle_level")
                or row.get("level")
                or user_to_level.get(uid, "")
            )
            elevated.append(
                CFElevatedStudent(
                    id=uid,
                    level=level,
                    baseline_score=baseline,
                    cf_score=cf,
                    delta=delta_f,
                )
            )
        except Exception:
            continue

    result = CFDiagnostics(
        threshold=float(diagnostics.get("threshold", rc.cf_threshold)),
        k=int(diagnostics.get("k", 3)),
        n_flagged_parametric=int(diagnostics.get("n_flagged_parametric", 0)),
        n_elevated_cf=int(diagnostics.get("n_elevated_cf", len(elevated))),
        fallback=bool(diagnostics.get("fallback", False)),
        reason=diagnostics.get("reason"),
        elevated_students=elevated,
    )
    _cf_cache[cache_key] = result
    return result


@router.get("/student/{student_id}/similar", response_model=list[SimilarStudent])
def get_similar(
    student_id: str,
    window: TimeWindow = Depends(get_time_window),
) -> list[SimilarStudent]:
    struggle_df = load_struggle_df(window.from_, window.to_)
    if struggle_df.empty or "user" not in struggle_df.columns:
        raise HTTPException(status_code=404, detail="no data")

    ids = struggle_df["user"].astype(str).tolist()
    if student_id not in ids:
        raise HTTPException(status_code=404, detail=f"student {student_id!r} not in current window")

    X, cols = _feature_matrix(struggle_df)
    if X.size == 0 or len(cols) < 2:
        return []

    with np.errstate(all="ignore"):
        W = cosine_similarity(X)

    i = ids.index(student_id)
    sims = W[i]
    # Build (id, similarity) pairs excluding self.
    pairs = [(ids[j], float(sims[j])) for j in range(len(ids)) if j != i]
    pairs.sort(key=lambda p: -p[1])

    out: list[SimilarStudent] = []
    lookup = struggle_df.set_index(struggle_df["user"].astype(str))
    for sid, sim in pairs[:5]:
        row = lookup.loc[sid] if sid in lookup.index else None
        if row is None:
            continue
        out.append(
            SimilarStudent(
                id=sid,
                level=str(row.get("struggle_level", "") if hasattr(row, "get") else row["struggle_level"]) if "struggle_level" in struggle_df.columns else "",
                struggle_score=float(row.get("struggle_score", 0.0) if hasattr(row, "get") else row["struggle_score"]) if "struggle_score" in struggle_df.columns else 0.0,
                similarity=round(sim, 3),
            )
        )
    return out
