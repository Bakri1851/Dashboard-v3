"""GET /api/student/{student_id} — deep-dive panel data."""
from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException

from backend import demo_data
from backend.cache import filter_df, load_active_difficulty_df, load_active_struggle_df
from backend.deps import TimeWindow, get_dataframe, get_time_window
from backend.routers._timeline import hour_of_day_distribution
from backend.schemas import (
    ScoreComponent,
    StudentDetail,
    StudentQuestionRow,
    StudentRecentRow,
)
from learning_dashboard import analytics, config

router = APIRouter(tags=["student"])


_COMPONENT_KEYS: list[tuple[str, str, float]] = [
    ("n_hat", "n̂ submissions", config.STRUGGLE_WEIGHT_N),
    ("t_hat", "t̂ time active", config.STRUGGLE_WEIGHT_T),
    ("i_hat", "ī mean incorrect.", config.STRUGGLE_WEIGHT_I),
    ("r_hat", "r̂ retry rate", config.STRUGGLE_WEIGHT_R),
    ("A_raw", "A recent (EMA)", config.STRUGGLE_WEIGHT_A),
    ("d_hat", "d̂ trajectory", config.STRUGGLE_WEIGHT_D),
    ("rep_hat", "rep̂ repetition", config.STRUGGLE_WEIGHT_REP),
]


def _safe(val: object, default: float = 0.0) -> float:
    try:
        f = float(val)  # type: ignore[arg-type]
        return 0.0 if (f != f) else f  # NaN check
    except (TypeError, ValueError):
        return default


@router.get("/student/{student_id}", response_model=StudentDetail)
def get_student(
    student_id: str,
    df: pd.DataFrame = Depends(get_dataframe),
    window: TimeWindow = Depends(get_time_window),
) -> StudentDetail:
    if demo_data.is_active() and demo_data.has_student(student_id):
        mock = demo_data.student_detail(student_id)
        if mock is not None:
            return mock
    if df.empty or "user" not in df.columns:
        raise HTTPException(status_code=404, detail="No data loaded")

    working = filter_df(df, window.from_, window.to_) if window.active else df
    user_df = working[working["user"].astype(str) == student_id].copy()
    if user_df.empty:
        raise HTTPException(status_code=404, detail=f"Student {student_id!r} not found")

    # Pull pre-computed struggle row from the cached window-specific leaderboard
    struggle_all = load_active_struggle_df(window.from_, window.to_)
    row = struggle_all[struggle_all["user"].astype(str) == student_id]
    if row.empty:
        raise HTTPException(status_code=404, detail=f"Student {student_id!r} has no struggle score")
    r = row.iloc[0]

    # --- score components ---------------------------------------------------
    components = [
        ScoreComponent(key=k, label=lbl, value=_safe(r.get(k, 0.0)), weight=w)
        for (k, lbl, w) in _COMPONENT_KEYS
    ]

    # --- trajectory (up to last 10 incorrectness scores, chronological) ----
    if "incorrectness" not in user_df.columns:
        user_df["incorrectness"] = analytics.compute_incorrectness_column(user_df)
    ts = pd.to_datetime(user_df["timestamp"], errors="coerce", utc=True)
    user_df = user_df.assign(_ts=ts).sort_values("_ts", kind="stable")
    trajectory = user_df["incorrectness"].dropna().tail(10).astype(float).tolist()

    # --- top questions attempted ------------------------------------------
    top_q = (
        user_df.groupby("question")
        .agg(attempts=("question", "size"), last_inc=("incorrectness", "last"))
        .sort_values("attempts", ascending=False)
        .head(10)
    )
    difficulty_all = load_active_difficulty_df(window.from_, window.to_)
    difficulty_lookup = {
        str(q): str(lvl)
        for q, lvl in zip(difficulty_all.get("question", []), difficulty_all.get("difficulty_level", []))
    } if not difficulty_all.empty else {}
    top_questions = [
        StudentQuestionRow(
            question=str(r2["question"]),
            attempts=int(r2["attempts"]),
            difficulty=difficulty_lookup.get(str(r2["question"]), ""),
            last_incorrectness=_safe(r2.get("last_inc")),
        )
        for r2 in top_q.reset_index().to_dict("records")
    ]

    # --- recent submissions (newest first) --------------------------------
    recent = user_df.dropna(subset=["_ts"]).sort_values("_ts", ascending=False).head(10)
    recent_submissions = [
        StudentRecentRow(
            timestamp=row["_ts"].isoformat() if pd.notna(row["_ts"]) else "",
            question=str(row.get("question", "")),
            answer=str(row.get("student_answer", ""))[:400],
            incorrectness=_safe(row.get("incorrectness")),
        )
        for row in recent.to_dict("records")
    ]

    return StudentDetail(
        id=student_id,
        level=str(r.get("struggle_level", "")),
        score=_safe(r.get("struggle_score")),
        submissions=int(_safe(r.get("submission_count"))),
        recent=_safe(r.get("recent_incorrectness")),
        trend=-_safe(r.get("d_hat")),
        mean_incorrectness=_safe(r.get("mean_incorrectness_pct")) / 100.0,
        time_active_min=_safe(r.get("time_active_min")),
        retry_rate=_safe(r.get("r_hat")),
        components=components,
        trajectory=trajectory,
        top_questions=top_questions,
        recent_submissions=recent_submissions,
        timeline_24h=hour_of_day_distribution(user_df),
    )
