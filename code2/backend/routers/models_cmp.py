"""GET /api/models/compare — baseline vs improved struggle, side-by-side.

The improved struggle model blends BKT mastery + IRT difficulty adjustment on
top of the baseline composite. Both are computed over the same cached df.
"""
from __future__ import annotations

import numpy as np
from fastapi import APIRouter, Depends

from backend.cache import load_improved_struggle_df, load_struggle_df
from backend.deps import TimeWindow, get_time_window
from backend.schemas import ModelCompareResponse, ModelRow

router = APIRouter(tags=["models"])


def _spearman(baseline_ids_in_order: list[str], improved_ids_in_order: list[str]) -> float | None:
    """Spearman rank correlation between two orderings of the same id set."""
    common = set(baseline_ids_in_order) & set(improved_ids_in_order)
    if len(common) < 3:
        return None
    rank_base = {x: i for i, x in enumerate(baseline_ids_in_order) if x in common}
    rank_impr = {x: i for i, x in enumerate(improved_ids_in_order) if x in common}
    a = np.array([rank_base[x] for x in common])
    b = np.array([rank_impr[x] for x in common])
    if a.std() == 0 or b.std() == 0:
        return None
    rho = float(np.corrcoef(a, b)[0, 1])
    return round(rho, 3) if np.isfinite(rho) else None


def _as_row(rec: dict) -> ModelRow:
    return ModelRow(
        id=str(rec["id"]),
        level=str(rec["level"]),
        score=float(rec["score"]),
    )


@router.get("/models/compare", response_model=ModelCompareResponse)
def models_compare(
    window: TimeWindow = Depends(get_time_window),
) -> ModelCompareResponse:
    baseline_df = load_struggle_df(window.from_, window.to_).sort_values(
        "struggle_score", ascending=False
    )

    improved_df = load_improved_struggle_df(window.from_, window.to_)
    if not improved_df.empty:
        improved_df = improved_df.sort_values("struggle_score", ascending=False)

    baseline_rows = [
        _as_row({
            "id": r["user"],
            "level": r.get("struggle_level", ""),
            "score": r.get("struggle_score", 0.0),
        })
        for _, r in baseline_df.head(10).iterrows()
    ]
    improved_rows = [
        _as_row({
            "id": r["user"],
            "level": r.get("struggle_level", ""),
            "score": r.get("struggle_score", 0.0),
        })
        for _, r in improved_df.head(10).iterrows()
    ]

    rho = _spearman(
        baseline_df["user"].astype(str).tolist(),
        improved_df["user"].astype(str).tolist() if not improved_df.empty else [],
    )

    # top-10 overlap fraction (needs-help + struggling bucket intuition)
    base_top = set(baseline_df["user"].astype(str).head(10))
    impr_top = set(improved_df["user"].astype(str).head(10)) if not improved_df.empty else set()
    overlap = round(len(base_top & impr_top) / 10, 2) if base_top and impr_top else None

    return ModelCompareResponse(
        baseline=baseline_rows,
        improved=improved_rows,
        spearman_rho=rho,
        top10_overlap=overlap,
    )
