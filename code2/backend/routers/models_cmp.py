"""GET /api/models/compare — baseline vs improved struggle + difficulty, side-by-side.

The improved struggle model blends BKT mastery + IRT difficulty adjustment on
top of the baseline composite. Difficulty comparison pairs the baseline
(behavioural composite) against the IRT Rasch-fit b_i. Both are computed
over the same cached df so agreement + rank concordance are directly
comparable.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends

from backend.cache import (
    load_difficulty_df,
    load_improved_struggle_df,
    load_irt_difficulty_df,
    load_struggle_df,
)
from backend.deps import TimeWindow, get_time_window
from backend.schemas import (
    AgreementSummary,
    ModelComparisonSection,
    ModelCompareResponse,
    ModelPairRow,
    ModelRow,
)
from learning_dashboard import config

router = APIRouter(tags=["models"])


_STRUGGLE_LEVEL_ORDER: dict[str, int] = {lbl: i for i, (_, _, lbl, _) in enumerate(config.STRUGGLE_THRESHOLDS)}
_DIFFICULTY_LEVEL_ORDER: dict[str, int] = {lbl: i for i, (_, _, lbl, _) in enumerate(config.DIFFICULTY_THRESHOLDS)}


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


def _agreement(pairs: list[ModelPairRow], level_order: dict[str, int]) -> AgreementSummary | None:
    if not pairs:
        return None
    upgraded = downgraded = unchanged = 0
    for p in pairs:
        b = level_order.get(p.baseline_level, -1)
        i = level_order.get(p.improved_level, -1)
        if b < 0 or i < 0:
            continue
        if i > b:
            upgraded += 1
        elif i < b:
            downgraded += 1
        else:
            unchanged += 1
    total = upgraded + downgraded + unchanged
    if total == 0:
        return None
    return AgreementSummary(
        agreement_pct=round(100.0 * unchanged / total, 1),
        upgraded=upgraded,
        downgraded=downgraded,
        unchanged=unchanged,
        total=total,
    )


def _rows_from_df(df: pd.DataFrame, id_col: str, level_col: str, score_col: str, n: int | None = None) -> list[ModelRow]:
    if df.empty:
        return []
    sub = df.head(n) if n is not None else df
    return [
        ModelRow(
            id=str(r[id_col]),
            level=str(r.get(level_col, "")),
            score=float(r.get(score_col, 0.0)),
        )
        for _, r in sub.iterrows()
    ]


def _pair_rows(
    baseline_df: pd.DataFrame,
    improved_df: pd.DataFrame,
    id_col: str,
    baseline_level_col: str,
    baseline_score_col: str,
    improved_level_col: str,
    improved_score_col: str,
) -> list[ModelPairRow]:
    """Inner-join baseline + improved on id_col and return paired rows sorted by |delta| desc."""
    if baseline_df.empty or improved_df.empty:
        return []
    b = baseline_df[[id_col, baseline_level_col, baseline_score_col]].copy()
    b[id_col] = b[id_col].astype(str)
    b = b.rename(
        columns={baseline_level_col: "_b_level", baseline_score_col: "_b_score"}
    )
    i = improved_df[[id_col, improved_level_col, improved_score_col]].copy()
    i[id_col] = i[id_col].astype(str)
    i = i.rename(
        columns={improved_level_col: "_i_level", improved_score_col: "_i_score"}
    )
    merged = b.merge(i, on=id_col, how="inner")
    if merged.empty:
        return []
    merged["_delta"] = merged["_i_score"].astype(float) - merged["_b_score"].astype(float)
    merged = merged.reindex(merged["_delta"].abs().sort_values(ascending=False).index)
    return [
        ModelPairRow(
            id=str(r[id_col]),
            baseline_level=str(r["_b_level"] or ""),
            baseline_score=float(r["_b_score"] or 0.0),
            improved_level=str(r["_i_level"] or ""),
            improved_score=float(r["_i_score"] or 0.0),
            delta=round(float(r["_delta"]), 4),
        )
        for _, r in merged.iterrows()
    ]


def _top10_overlap(a_ids: list[str], b_ids: list[str]) -> float | None:
    if not a_ids or not b_ids:
        return None
    a_top = set(a_ids[:10])
    b_top = set(b_ids[:10])
    return round(len(a_top & b_top) / 10, 2)


def _build_difficulty_section(window: TimeWindow) -> ModelComparisonSection | None:
    baseline_df = load_difficulty_df(window.from_, window.to_)
    irt_df = load_irt_difficulty_df(window.from_, window.to_)
    if baseline_df.empty:
        return None

    baseline_sorted = baseline_df.sort_values("difficulty_score", ascending=False)
    irt_sorted = (
        irt_df.sort_values("irt_difficulty", ascending=False)
        if not irt_df.empty and "irt_difficulty" in irt_df.columns
        else pd.DataFrame()
    )

    baseline_rows = _rows_from_df(baseline_sorted, "question", "difficulty_level", "difficulty_score", n=10)
    improved_rows = (
        _rows_from_df(irt_sorted, "question", "irt_difficulty_level", "irt_difficulty", n=10)
        if not irt_sorted.empty
        else []
    )

    pairs = _pair_rows(
        baseline_sorted,
        irt_sorted,
        id_col="question",
        baseline_level_col="difficulty_level",
        baseline_score_col="difficulty_score",
        improved_level_col="irt_difficulty_level",
        improved_score_col="irt_difficulty",
    ) if not irt_sorted.empty else []

    rho = (
        _spearman(
            baseline_sorted["question"].astype(str).tolist(),
            irt_sorted["question"].astype(str).tolist(),
        )
        if not irt_sorted.empty
        else None
    )
    overlap = (
        _top10_overlap(
            baseline_sorted["question"].astype(str).tolist(),
            irt_sorted["question"].astype(str).tolist(),
        )
        if not irt_sorted.empty
        else None
    )

    return ModelComparisonSection(
        baseline=baseline_rows,
        improved=improved_rows,
        pairs=pairs,
        agreement=_agreement(pairs, _DIFFICULTY_LEVEL_ORDER),
        spearman_rho=rho,
        top10_overlap=overlap,
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

    baseline_rows = _rows_from_df(baseline_df, "user", "struggle_level", "struggle_score", n=10)
    improved_rows = (
        _rows_from_df(improved_df, "user", "struggle_level", "struggle_score", n=10)
        if not improved_df.empty
        else []
    )

    pairs = _pair_rows(
        baseline_df,
        improved_df,
        id_col="user",
        baseline_level_col="struggle_level",
        baseline_score_col="struggle_score",
        improved_level_col="struggle_level",
        improved_score_col="struggle_score",
    ) if not improved_df.empty else []

    rho = _spearman(
        baseline_df["user"].astype(str).tolist(),
        improved_df["user"].astype(str).tolist() if not improved_df.empty else [],
    )
    overlap = _top10_overlap(
        baseline_df["user"].astype(str).tolist(),
        improved_df["user"].astype(str).tolist() if not improved_df.empty else [],
    )

    difficulty_section = _build_difficulty_section(window)

    return ModelCompareResponse(
        baseline=baseline_rows,
        improved=improved_rows,
        spearman_rho=rho,
        top10_overlap=overlap,
        pairs=pairs,
        agreement=_agreement(pairs, _STRUGGLE_LEVEL_ORDER),
        difficulty=difficulty_section,
    )
