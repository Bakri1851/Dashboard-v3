"""GET /api/question/{question_id} — deep-dive panel data."""
from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException

from backend.cache import filter_df, load_difficulty_df, load_struggle_df
from backend.deps import TimeWindow, get_dataframe, get_time_window
from backend.routers._timeline import hour_of_day_distribution
from backend.schemas import (
    MistakeCluster,
    QuestionDetail,
    QuestionRecentAttempt,
    QuestionStudentRow,
)
from learning_dashboard import analytics, config

router = APIRouter(tags=["question"])


def _safe(val: object, default: float = 0.0) -> float:
    try:
        f = float(val)  # type: ignore[arg-type]
        return 0.0 if (f != f) else f
    except (TypeError, ValueError):
        return default


@router.get("/question/{question_id}", response_model=QuestionDetail)
def get_question(
    question_id: str,
    df: pd.DataFrame = Depends(get_dataframe),
    window: TimeWindow = Depends(get_time_window),
) -> QuestionDetail:
    if df.empty or "question" not in df.columns:
        raise HTTPException(status_code=404, detail="No data loaded")

    working = filter_df(df, window.from_, window.to_) if window.active else df
    q_df = working[working["question"].astype(str) == question_id].copy()
    if q_df.empty:
        raise HTTPException(status_code=404, detail=f"Question {question_id!r} not found")

    difficulty_all = load_difficulty_df(window.from_, window.to_)
    row_sel = difficulty_all[difficulty_all["question"].astype(str) == question_id]
    if row_sel.empty:
        raise HTTPException(status_code=404, detail=f"No difficulty score for {question_id!r}")
    r = row_sel.iloc[0]

    # --- ensure incorrectness column for cluster + rate calcs -------------
    if "incorrectness" not in q_df.columns:
        q_df["incorrectness"] = analytics.compute_incorrectness_column(q_df)

    wrong_mask = q_df["incorrectness"] > config.CORRECT_THRESHOLD
    incorrect_rate = float(wrong_mask.mean()) if len(q_df) else 0.0

    # First-attempt failure rate: group by user, take first attempt, count wrong.
    ts = pd.to_datetime(q_df["timestamp"], errors="coerce", utc=True)
    q_df = q_df.assign(_ts=ts).sort_values("_ts", kind="stable")
    first_attempts = q_df.groupby("user").first()
    if not first_attempts.empty:
        first_fail_rate = float((first_attempts["incorrectness"] > config.CORRECT_THRESHOLD).mean())
    else:
        first_fail_rate = 0.0

    # --- clusters ---------------------------------------------------------
    try:
        clusters = analytics.cluster_question_mistakes(q_df, question_id) or []
    except Exception:
        clusters = []
    mistake_clusters = [
        MistakeCluster(
            label=str(c.get("label", "(unlabelled)")),
            count=int(c.get("count", 0)),
            percent_of_wrong=float(c.get("percent_of_wrong", 0.0)) / 100.0
            if float(c.get("percent_of_wrong", 0.0)) > 1.0
            else float(c.get("percent_of_wrong", 0.0)),
            example_answers=[str(a)[:400] for a in (c.get("example_answers") or [])][:3],
        )
        for c in clusters
    ]

    # --- top strugglers on this question (per-student summary) -----------
    top_strugglers: list[QuestionStudentRow] = []
    if "user" in q_df.columns:
        per_user = (
            q_df.groupby("user").agg(
                attempts=("user", "size"),
                mean_inc=("incorrectness", "mean"),
            )
        )
        # Join struggle-level + global-score from the cached window-specific leaderboard.
        struggle_all = load_struggle_df(window.from_, window.to_)
        level_lookup: dict[str, str] = {}
        score_lookup: dict[str, float] = {}
        if not struggle_all.empty:
            uid_idx = struggle_all["user"].astype(str)
            level_lookup = dict(zip(uid_idx, struggle_all.get("struggle_level", pd.Series(dtype=str)).astype(str)))
            score_lookup = dict(zip(uid_idx, struggle_all.get("struggle_score", pd.Series(dtype=float)).astype(float)))

        per_user = per_user.sort_values(
            ["mean_inc", "attempts"], ascending=[False, False]
        ).head(15)
        for r2 in per_user.reset_index().to_dict("records"):
            uid = str(r2["user"])
            top_strugglers.append(
                QuestionStudentRow(
                    id=uid,
                    attempts=int(r2["attempts"]),
                    mean_incorrectness=_safe(r2.get("mean_inc")),
                    struggle_level=level_lookup.get(uid, ""),
                    struggle_score=score_lookup.get(uid, 0.0),
                )
            )

    # --- recent attempts --------------------------------------------------
    recent = q_df.dropna(subset=["_ts"]).sort_values("_ts", ascending=False).head(10)
    recent_attempts = [
        QuestionRecentAttempt(
            timestamp=row["_ts"].isoformat() if pd.notna(row["_ts"]) else "",
            user=str(row.get("user", "")),
            answer=str(row.get("student_answer", ""))[:400],
            incorrectness=_safe(row.get("incorrectness")),
        )
        for row in recent.to_dict("records")
    ]

    return QuestionDetail(
        id=question_id,
        level=str(r.get("difficulty_level", "")),
        score=_safe(r.get("difficulty_score")),
        module=str(q_df["module"].iloc[0]) if "module" in q_df.columns and not q_df.empty else "",
        students=int(_safe(r.get("unique_students"))),
        avg_attempts=_safe(r.get("avg_attempts")),
        incorrect_rate=incorrect_rate,
        first_fail_rate=first_fail_rate,
        mistake_clusters=mistake_clusters,
        recent_attempts=recent_attempts,
        top_strugglers=top_strugglers,
        timeline_24h=hour_of_day_distribution(q_df),
    )
