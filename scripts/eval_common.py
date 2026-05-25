"""Phase 2 + shared utilities for the v2 weights/hyperparams evaluation pipeline.

Provides utilities used by every downstream script (eval_label, optimise_v2_weights,
optimise_hyperparams, eval_main). When run as ``__main__``, samples stratified
``(student, t)`` snapshots across the healthy sessions and writes them — plus
per-question difficulty aggregates — to ``data/eval_snapshots.json``.

Run from repo root::

    python scripts/eval_common.py
    python scripts/eval_common.py --target-n 2000 --cutoffs 12 --per-band 3 --seed 42
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "code2"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from backend import cache, config, difficulty, paths, struggle  # noqa: E402
from backend.models import bkt, improved_struggle, irt  # noqa: E402


STRUGGLE_FEATURE_COLS = ["n_hat", "t_hat", "i_norm", "r_norm", "A_norm", "d_hat", "rep_norm"]
DIFFICULTY_FEATURE_COLS = ["c_norm", "t_tilde", "a_tilde", "f_norm", "p_norm"]
STRUGGLE_BANDS = ["On Track", "Minor Issues", "Struggling", "Needs Help"]
DEFAULT_HORIZON_MINUTES = 15
DEFAULT_DUP_THRESHOLD = 3
DEFAULT_INCORRECT_THRESHOLD = 0.5


# ---------- shared library functions ----------

def load_cached_df() -> pd.DataFrame:
    """Read cached DataFrame from data/eval/submissions.{parquet,pkl}."""
    stem = paths.DATA_DIR / "eval" / "submissions"
    for suffix in (".parquet", ".pkl"):
        path = stem.with_suffix(suffix)
        if path.exists():
            return pd.read_parquet(path) if suffix == ".parquet" else pd.read_pickle(path)
    raise FileNotFoundError(
        f"No cached submissions at {stem}.{{parquet,pkl}}. Run scripts/eval_fetch.py first."
    )


def load_sessions() -> list[dict]:
    blob = json.loads(paths.saved_sessions_path().read_text(encoding="utf-8"))
    return blob.get("sessions", [])


def healthy_sessions(
    df: pd.DataFrame,
    sessions: list[dict],
    min_students: int = 10,
    min_rows: int = 100,
) -> list[dict]:
    healthy = []
    for sess in sessions:
        sliced = session_window(df, sess)
        if (
            len(sliced) >= min_rows
            and "user" in sliced.columns
            and sliced["user"].nunique() >= min_students
        ):
            healthy.append(sess)
    return healthy


def session_window(df: pd.DataFrame, session: dict) -> pd.DataFrame:
    start = session.get("start_time") or session.get("start") or ""
    end = session.get("end_time") or session.get("end") or ""
    return cache.filter_df(df, start, end)


def _to_utc(ts: pd.Timestamp) -> pd.Timestamp:
    return ts.tz_convert("UTC") if ts.tzinfo else ts.tz_localize("UTC")


def sorted_window(window_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DatetimeIndex]:
    """Return (window + _ts column, DatetimeIndex on _ts) sorted ascending."""
    ts = pd.to_datetime(window_df["timestamp"], errors="coerce", utc=True)
    working = (
        window_df.assign(_ts=ts)
        .dropna(subset=["_ts"])
        .sort_values("_ts", kind="stable")
        .reset_index(drop=True)
    )
    return working, pd.DatetimeIndex(working["_ts"])


def cutoffs_for_session(session: dict, n_buckets: int = 12) -> list[pd.Timestamp]:
    start = _to_utc(pd.Timestamp(session["start_time"]))
    end = _to_utc(pd.Timestamp(session["end_time"]))
    duration_s = (end - start).total_seconds()
    bucket_s = max(duration_s / n_buckets, 60.0)
    return [start + pd.Timedelta(seconds=bucket_s * i) for i in range(1, n_buckets + 1)]


def slice_at_t(working: pd.DataFrame, ts_index: pd.DatetimeIndex, t: pd.Timestamp) -> pd.DataFrame:
    end_idx = int(ts_index.searchsorted(t, side="right"))
    if end_idx == 0:
        return working.iloc[0:0].drop(columns=["_ts"])
    return working.iloc[:end_idx].drop(columns=["_ts"])


def compute_struggle_at_t(
    working: pd.DataFrame, ts_index: pd.DatetimeIndex, t: pd.Timestamp
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Returns (scores_df, slice_df). Both empty on failure."""
    slice_df = slice_at_t(working, ts_index, t)
    if slice_df.empty:
        return pd.DataFrame(), slice_df
    try:
        return struggle.compute_student_struggle_scores(slice_df), slice_df
    except Exception:
        return pd.DataFrame(), slice_df


def compute_difficulty_full(window_df: pd.DataFrame) -> pd.DataFrame:
    if window_df.empty:
        return pd.DataFrame()
    try:
        return difficulty.compute_question_difficulty_scores(window_df)
    except Exception:
        return pd.DataFrame()


def horizon_window(
    window_df: pd.DataFrame, t: pd.Timestamp, delta_minutes: int = DEFAULT_HORIZON_MINUTES
) -> pd.DataFrame:
    ts = pd.to_datetime(window_df["timestamp"], errors="coerce", utc=True)
    horizon_end = t + pd.Timedelta(minutes=delta_minutes)
    return window_df[(ts > t) & (ts <= horizon_end)]


def cohort_horizon_labels(
    window_df: pd.DataFrame,
    sliced_at_t: pd.DataFrame,
    t: pd.Timestamp,
    delta_minutes: int = DEFAULT_HORIZON_MINUTES,
    dup_threshold: int = DEFAULT_DUP_THRESHOLD,
    incorrect_threshold: float = DEFAULT_INCORRECT_THRESHOLD,
) -> dict[str, dict]:
    """Compute Family B horizon-shifted labels for every user in sliced_at_t."""
    horizon = horizon_window(window_df, t, delta_minutes)
    per_user: dict[str, dict] = {}

    for user in sliced_at_t["user"].unique():
        per_user[str(user)] = {
            "future_n_submissions": 0,
            "future_mean_incorrectness": 0.0,
            "future_max_gap_s": 0.0,
            "past_median_gap_s": 0.0,
            "future_dup_count": 0,
            "L_top20_obs": 0,
            "L_needs_help_obs": 0,
            "L_struggling_plus_obs": 0,
        }

    # Past median gap per user, as a personal-baseline reference
    past = sliced_at_t.assign(
        _ts=pd.to_datetime(sliced_at_t["timestamp"], errors="coerce", utc=True)
    ).dropna(subset=["_ts"])
    for user, u_group in past.groupby("user"):
        u_ts = u_group["_ts"].sort_values()
        if len(u_ts) >= 2:
            gaps = u_ts.diff().dropna().dt.total_seconds()
            if len(gaps):
                per_user[str(user)]["past_median_gap_s"] = float(gaps.median())

    # Per-user horizon metrics
    if not horizon.empty:
        h_ts = pd.to_datetime(horizon["timestamp"], errors="coerce", utc=True)
        horizon = horizon.assign(_ts=h_ts).dropna(subset=["_ts"])
        for user, h_group in horizon.groupby("user"):
            key = str(user)
            if key not in per_user:
                continue
            per_user[key]["future_n_submissions"] = len(h_group)
            per_user[key]["future_mean_incorrectness"] = float(
                h_group["incorrectness"].fillna(0.5).mean()
            )
            sorted_ts = h_group["_ts"].sort_values()
            if len(sorted_ts) >= 2:
                per_user[key]["future_max_gap_s"] = float(
                    sorted_ts.diff().max().total_seconds()
                )
            wrong = h_group[h_group["incorrectness"].fillna(0) >= incorrect_threshold]
            dup = 0
            for _q, q_group in wrong.groupby("question"):
                seen: set[str] = set()
                for ans in q_group["student_answer"].dropna().astype(str).str.strip().tolist():
                    if not ans:
                        continue
                    if ans in seen:
                        dup += 1
                    else:
                        seen.add(ans)
            per_user[key]["future_dup_count"] = dup

    # L_top20_obs over students with non-zero horizon activity
    rated = [
        (u, d["future_mean_incorrectness"])
        for u, d in per_user.items()
        if d["future_n_submissions"] > 0
    ]
    if rated:
        rated.sort(key=lambda x: -x[1])
        n_top = max(1, len(rated) // 5)
        top_users = {u for u, _ in rated[:n_top]}
        for u in top_users:
            per_user[u]["L_top20_obs"] = 1

    # L_needs_help_obs (retry spiral OR abandonment) + L_struggling_plus_obs
    for d in per_user.values():
        retry_spiral = d["future_dup_count"] >= dup_threshold
        abandonment = (
            d["past_median_gap_s"] > 0
            and d["future_max_gap_s"] > 3 * d["past_median_gap_s"]
        )
        d["L_needs_help_obs"] = int(retry_spiral or abandonment)
        d["L_struggling_plus_obs"] = int(d["L_top20_obs"] or d["L_needs_help_obs"])

    return per_user


def compute_improved_components_at_t(slice_df: pd.DataFrame) -> dict[str, dict]:
    """Per-student improved-struggle component scores at time t.

    Fits BKT + IRT on the slice, then calls
    ``improved_struggle.compute_improved_struggle_scores`` to extract the
    three component columns (behavioural_composite, mastery_gap,
    difficulty_adjusted_score) for each user.

    Returns dict keyed by user → {behavioural_composite, mastery_gap,
    difficulty_adjusted_score, improved_struggle_score}. Empty dict on
    any failure (sparse slice, BKT/IRT non-convergence).
    """
    if slice_df.empty:
        return {}

    # BKT: per-skill MLE fit using config defaults. fit_all_skills is the
    # heavy operation but we can call compute_all_mastery directly with the
    # default priors and let it use whatever per-skill fitted params are
    # cached. For per-cutoff training we use the defaults (priors live in
    # config), matching how the dashboard runs when hyperparams_version=v1.
    mastery_summary = None
    try:
        mastery_df = bkt.compute_all_mastery(
            slice_df,
            p_init=config.BKT_P_INIT,
            p_learn=config.BKT_P_LEARN,
            p_guess=config.BKT_P_GUESS,
            p_slip=config.BKT_P_SLIP,
            per_skill_params=None,
        )
        if not mastery_df.empty:
            mastery_summary = bkt.compute_student_mastery_summary(mastery_df)
    except Exception:
        mastery_summary = None

    # IRT 2PL fit
    irt_difficulty = None
    irt_ability = None
    try:
        irt_model = irt.compute_irt_model(slice_df)
        irt_difficulty = irt_model.get("difficulty_df")
        irt_ability = irt_model.get("ability_df")
        if irt_difficulty is not None and irt_difficulty.empty:
            irt_difficulty = None
        if irt_ability is not None and irt_ability.empty:
            irt_ability = None
    except Exception:
        irt_difficulty = None
        irt_ability = None

    # Call improved_struggle to extract the three component columns
    try:
        improved_df = improved_struggle.compute_improved_struggle_scores(
            slice_df,
            mastery_summary=mastery_summary,
            irt_difficulty=irt_difficulty,
            irt_ability=irt_ability,
        )
    except Exception:
        return {}

    if improved_df.empty:
        return {}

    return {
        str(row["user"]): {
            "behavioural_composite": round(float(row["behavioural_composite"]), 4),
            "mastery_gap": round(float(row["mastery_gap"]), 4),
            "difficulty_adjusted_score": round(float(row["difficulty_adjusted_score"]), 4),
            "improved_struggle_score": round(float(row["struggle_score"]), 4),
        }
        for _, row in improved_df.iterrows()
    }


def recent_submissions_trail(
    window_df: pd.DataFrame, user: str, t: pd.Timestamp, n: int = 10
) -> list[dict]:
    """Last n submissions for the user up to t, most recent first."""
    ts = pd.to_datetime(window_df["timestamp"], errors="coerce", utc=True)
    mask = (window_df["user"] == user) & (ts <= t) & ts.notna()
    sub = window_df[mask].assign(_ts=ts[mask])
    sub = sub.sort_values("_ts", ascending=False).head(n)
    return [
        {
            "timestamp": row["_ts"].isoformat(),
            "question": str(row.get("question", "")),
            "answer_excerpt": str(row.get("student_answer", ""))[:200],
            "feedback_excerpt": str(row.get("ai_feedback", ""))[:300],
            "incorrectness": round(float(row.get("incorrectness", 0.5) or 0.5), 3),
        }
        for _, row in sub.iterrows()
    ]


# ---------- Phase 2 main: sampler ----------

def _build_snapshot(
    session: dict,
    user: str,
    t: pd.Timestamp,
    cutoffs: list[pd.Timestamp],
    score_row: pd.Series,
    slice_df: pd.DataFrame,
    window_df: pd.DataFrame,
    horizon: dict,
    horizon_minutes: int,
    improved_components: dict | None = None,
) -> dict:
    minutes_in = max(0, int((t - cutoffs[0]).total_seconds() / 60))
    h = horizon.get(user, {})
    improved = (improved_components or {}).get(user, {})
    return {
        "snapshot_id": f"{session.get('id', '')}__{user}__{t.isoformat()}",
        "session_id": str(session.get("id", "")),
        "session_name": str(session.get("name", "")),
        "user": user,
        "t": t.isoformat(),
        "t_minutes_into_session": minutes_in,
        "context": {
            "n_submissions_so_far": int(score_row["submission_count"]),
            "n_unique_questions_so_far": int(
                slice_df[slice_df["user"] == user]["question"].nunique()
            ),
            "mean_incorrectness_so_far": round(float(score_row["i_hat"]), 3),
            "time_active_min": round(float(score_row["time_active_min"]), 2),
            "recent_incorrectness_ewma": round(float(score_row["A_raw"]), 3),
            "recent_trail": recent_submissions_trail(window_df, user, t, n=10),
        },
        "v1_features": {col: round(float(score_row[col]), 4) for col in STRUGGLE_FEATURE_COLS},
        "v1_struggle_score": round(float(score_row["struggle_score"]), 4),
        "v1_struggle_level": str(score_row["struggle_level"]),
        "horizon_labels": {
            "delta_minutes": horizon_minutes,
            **{
                k: (round(v, 3) if isinstance(v, float) else int(v))
                for k, v in h.items()
            },
        },
        "improved_components": improved,
    }


def sample_struggle_snapshots(
    df: pd.DataFrame,
    sessions: list[dict],
    n_cutoffs: int = 12,
    per_band_per_bucket: int = 3,
    seed: int = 42,
    horizon_minutes: int = DEFAULT_HORIZON_MINUTES,
) -> list[dict]:
    rng = np.random.default_rng(seed)
    snapshots: list[dict] = []

    for s_idx, session in enumerate(sessions, 1):
        window = session_window(df, session)
        if window.empty:
            continue
        working, ts_index = sorted_window(window)
        cutoffs = cutoffs_for_session(session, n_cutoffs)
        n_before = len(snapshots)

        for t in cutoffs:
            scores, slice_df = compute_struggle_at_t(working, ts_index, t)
            if scores.empty:
                continue
            horizon = cohort_horizon_labels(window, slice_df, t, horizon_minutes)
            # Improved-struggle component scores per user (B_s, M_s, D_s) — needed
            # by Phase 4c training. Fits BKT + IRT on the slice; ~3–15 s per cutoff
            # depending on slice size. Empty dict on failure → snapshots still
            # written but with empty improved_components (train_improved filters).
            improved = compute_improved_components_at_t(slice_df)
            for band in STRUGGLE_BANDS:
                band_rows = scores[scores["struggle_level"] == band]
                if band_rows.empty:
                    continue
                k = min(per_band_per_bucket, len(band_rows))
                chosen = rng.choice(len(band_rows), size=k, replace=False)
                for idx in chosen:
                    row = band_rows.iloc[int(idx)]
                    snapshots.append(
                        _build_snapshot(
                            session, str(row["user"]), t, cutoffs,
                            row, slice_df, window, horizon, horizon_minutes,
                            improved_components=improved,
                        )
                    )

        name = str(session.get("name", ""))[:35]
        print(
            f"  [{s_idx:>2}/{len(sessions)}] {name:<35}  "
            f"+{len(snapshots) - n_before:>4} snapshots  (total: {len(snapshots)})"
        )
    return snapshots


def difficulty_question_aggregates(df: pd.DataFrame, sessions: list[dict]) -> list[dict]:
    """One entry per unique question across all healthy sessions, with end-of-session aggregates."""
    frames = [session_window(df, s) for s in sessions]
    frames = [f for f in frames if not f.empty]
    if not frames:
        return []
    pooled = pd.concat(frames, ignore_index=True)
    diff_df = compute_difficulty_full(pooled)
    if diff_df.empty:
        return []
    return [
        {
            "question": str(row["question"]),
            "module": str(row.get("module", "")),
            "total_attempts": int(row["total_attempts"]),
            "unique_students": int(row["unique_students"]),
            "avg_attempts": round(float(row["avg_attempts"]), 2),
            "incorrect_rate_pct": round(float(row["incorrect_rate_pct"]), 2),
            "v1_features": {col: round(float(row[col]), 4) for col in DIFFICULTY_FEATURE_COLS},
            "v1_difficulty_score": round(float(row["difficulty_score"]), 4),
            "v1_difficulty_level": str(row["difficulty_level"]),
        }
        for _, row in diff_df.iterrows()
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-n", type=int, default=2000)
    parser.add_argument("--cutoffs", type=int, default=12)
    parser.add_argument("--per-band", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--horizon-min", type=int, default=DEFAULT_HORIZON_MINUTES)
    parser.add_argument("--out", type=Path, default=paths.DATA_DIR / "eval" / "snapshots.json")
    args = parser.parse_args()

    (paths.DATA_DIR / "eval").mkdir(parents=True, exist_ok=True)
    print(f"Loading cached DataFrame from {paths.DATA_DIR}\\eval\\submissions.* ...")
    df = load_cached_df()
    print(f"  {len(df):,} rows x {len(df.columns)} cols")

    all_sessions = load_sessions()
    healthy = healthy_sessions(df, all_sessions)
    print(f"Sessions: {len(healthy)}/{len(all_sessions)} healthy")
    print()

    print(
        f"Sampling struggle snapshots "
        f"(<= {args.per_band} per (session x cutoff x band), {args.cutoffs} cutoffs/session)..."
    )
    snapshots = sample_struggle_snapshots(
        df, healthy, args.cutoffs, args.per_band, args.seed, args.horizon_min
    )

    if len(snapshots) > int(args.target_n * 1.5):
        rng = np.random.default_rng(args.seed)
        keep = sorted(rng.choice(len(snapshots), size=args.target_n, replace=False))
        snapshots = [snapshots[int(i)] for i in keep]
        print(f"  Trimmed to {len(snapshots)} (target was {args.target_n})")

    print()
    print(f"Computing per-question difficulty aggregates across {len(healthy)} sessions...")
    questions = difficulty_question_aggregates(df, healthy)
    print(f"  {len(questions)} unique questions")

    payload = {
        "version": 1,
        "config": {
            "target_n": args.target_n,
            "cutoffs": args.cutoffs,
            "per_band": args.per_band,
            "seed": args.seed,
            "horizon_minutes": args.horizon_min,
            "healthy_session_ids": [s.get("id") for s in healthy],
        },
        "struggle_snapshots": snapshots,
        "difficulty_questions": questions,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print()
    print(f"Wrote {len(snapshots)} struggle snapshots + {len(questions)} difficulty entries to {args.out}")

    # Sanity prints
    band_counts = Counter(s["v1_struggle_level"] for s in snapshots)
    print()
    print("Struggle band distribution:")
    for band in STRUGGLE_BANDS:
        print(f"  {band:<14} {band_counts.get(band, 0):>5}")

    print()
    print("Family B (horizon-shifted) positive rates:")
    for label_key in ("L_top20_obs", "L_needs_help_obs", "L_struggling_plus_obs"):
        pos = sum(s["horizon_labels"].get(label_key, 0) for s in snapshots)
        rate = pos / len(snapshots) if snapshots else 0
        print(f"  {label_key:<22} {pos:>5}  ({rate:.1%})")

    if questions:
        print()
        print("Difficulty level distribution (full-session aggregate):")
        diff_counts = Counter(q["v1_difficulty_level"] for q in questions)
        for level in ("Easy", "Medium", "Hard", "Very Hard"):
            print(f"  {level:<14} {diff_counts.get(level, 0):>5}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
