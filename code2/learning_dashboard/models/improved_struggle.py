"""
Phase 4 — Improved struggle model (mastery-aware, difficulty-adjusted).

Combines three signal groups:
  1. Behavioral composite  (weight 0.45)
  2. Mastery gap           (weight 0.30) — BKT mastery vs recent performance
  3. Difficulty-adjusted   (weight 0.25) — failing easy questions is worse

Graceful degradation: unavailable signal groups redistribute their weight
to the behavioral composite.
"""

from __future__ import annotations

import pandas as pd

from learning_dashboard import analytics, config


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def compute_improved_struggle_scores(
    df: pd.DataFrame,
    mastery_summary: pd.DataFrame | None = None,
    irt_difficulty: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Return a struggle DataFrame compatible with the baseline schema.

    Extra diagnostic columns: ``behavioral_composite``, ``mastery_gap``,
    ``difficulty_adjusted_score``.

    Note: the weight-sum invariant (``w_beh + w_mg + w_da == 1``) is asserted
    only on the non-empty code path — empty-input early returns bypass it
    by design.
    """
    _columns = [
        "user", "struggle_score", "struggle_level", "struggle_color",
        "behavioral_composite", "mastery_gap", "difficulty_adjusted_score",
    ]

    if df.empty:
        return pd.DataFrame(columns=_columns)

    required = {"user", "question", "timestamp", "student_answer"}
    if not required.issubset(df.columns):
        return pd.DataFrame(columns=_columns)

    work = df.copy()
    if "incorrectness" not in work.columns:
        work["incorrectness"] = analytics.compute_incorrectness_column(work)

    # --- Determine effective weights with graceful degradation ---
    w_beh = config.IMPROVED_STRUGGLE_WEIGHT_BEHAVIORAL
    w_mg = config.IMPROVED_STRUGGLE_WEIGHT_MASTERY_GAP
    w_da = config.IMPROVED_STRUGGLE_WEIGHT_DIFFICULTY_ADJ

    has_mastery = mastery_summary is not None and not mastery_summary.empty
    # Require >1 distinct IRT difficulty value — with a single value, the
    # normalized difficulty is a constant 0.5 for every question, so the
    # (1 - norm_diff) weighting degenerates to a uniform halving and adds
    # no discriminative information. Redistribute its weight instead.
    has_irt = (
        irt_difficulty is not None
        and not irt_difficulty.empty
        and "irt_difficulty" in irt_difficulty.columns
        and irt_difficulty["irt_difficulty"].nunique() > 1
    )

    if not has_mastery:
        w_beh += w_mg
        w_mg = 0.0
    if not has_irt:
        w_beh += w_da
        w_da = 0.0

    # --- Per-student behavioral signals ---
    rows: list[dict] = []
    grouped = work.groupby("user")

    for user, group in grouped:
        n = len(group)

        a_raw = analytics.compute_recent_incorrectness(group)
        d_raw = analytics._compute_slope(group)

        unique_q = group["question"].nunique()
        r_hat = 1.0 - (unique_q / n) if n > 0 else 0.0

        # Exact-answer repetition rate
        total_repeat = 0
        for _q, q_group in group.groupby("question"):
            answers = q_group.sort_values("timestamp")["student_answer"].tolist()
            seen: set[str] = set()
            for ans in answers:
                cleaned = str(ans).strip()
                if cleaned in seen:
                    total_repeat += 1
                else:
                    seen.add(cleaned)
        rep_hat = total_repeat / n if n > 0 else 0.0

        rows.append({
            "user": user,
            "n": n,
            "A_raw": a_raw,
            "d_raw": d_raw,
            "r_hat": r_hat,
            "rep_hat": rep_hat,
        })

    result = pd.DataFrame(rows)

    if result.empty:
        return pd.DataFrame(columns=_columns)

    # Min-max normalize every sub-signal onto the same cohort-relative
    # [0, 1] scale so the equal-weight average is actually equal-weighted.
    # Raw rates (A_raw, r_hat, rep_hat) are kept on result for reference.
    result["d_hat"] = analytics.min_max_normalize(result["d_raw"])
    result["A_norm"] = analytics.min_max_normalize(result["A_raw"])
    result["r_norm"] = analytics.min_max_normalize(result["r_hat"])
    result["rep_norm"] = analytics.min_max_normalize(result["rep_hat"])

    # Behavioral composite: equal weight across the 4 sub-signals
    result["behavioral_composite"] = (
        (result["A_norm"] + result["r_norm"] + result["d_hat"] + result["rep_norm"]) / 4.0
    ).clip(0.0, 1.0)

    # --- Mastery gap ---
    result["mastery_gap"] = 0.0
    if has_mastery:
        result = result.merge(
            mastery_summary[["user", "mean_mastery"]],
            on="user",
            how="left",
        )
        # Coverage guard: if more than half of users have no mastery record,
        # the signal is untrustworthy — redistribute its weight to behavioral.
        coverage = result["mean_mastery"].notna().mean()
        if coverage < 0.5:
            has_mastery = False
            w_beh += w_mg
            w_mg = 0.0
            result["mastery_gap"] = 0.0
        else:
            # Impute uncovered users with the class mean rather than 0.0 —
            # "unknown" should not systematically read as "zero mastery",
            # which would silently zero their mastery_gap contribution.
            class_mean = result["mean_mastery"].mean()
            result["mean_mastery"] = result["mean_mastery"].fillna(class_mean)
            # recent_performance ≈ how correct the student is recently
            recent_perf = 1.0 - result["A_raw"]
            result["mastery_gap"] = (result["mean_mastery"] - recent_perf).clip(lower=0.0)
        result.drop(columns=["mean_mastery"], inplace=True, errors="ignore")

    # --- Difficulty-adjusted score ---
    result["difficulty_adjusted_score"] = 0.0
    if has_irt:
        result["difficulty_adjusted_score"] = _compute_difficulty_adjusted(
            work, result, irt_difficulty
        )

    # --- Weighted combination ---
    # Invariant: redistribution above must preserve sum-to-one so configured
    # weights match effective weights.
    assert abs((w_beh + w_mg + w_da) - 1.0) < 1e-9, (
        f"improved_struggle weights do not sum to 1.0: "
        f"w_beh={w_beh}, w_mg={w_mg}, w_da={w_da}"
    )
    result["struggle_score"] = (
        w_beh * result["behavioral_composite"]
        + w_mg * result["mastery_gap"]
        + w_da * result["difficulty_adjusted_score"]
    ).clip(0.0, 1.0)

    # Bayesian shrinkage toward class mean (final transform — must not be
    # followed by another normalization, which would erase the pull-toward-mean).
    s_mean = result["struggle_score"].mean()
    w_n = result["n"] / (result["n"] + config.SHRINKAGE_K)
    result["struggle_score"] = (
        w_n * result["struggle_score"] + (1.0 - w_n) * s_mean
    ).clip(0.0, 1.0)

    # Classify
    levels_colors = result["struggle_score"].apply(
        lambda s: analytics.classify_score(s, config.STRUGGLE_THRESHOLDS)
    )
    result["struggle_level"] = levels_colors.apply(lambda x: x[0])
    result["struggle_color"] = levels_colors.apply(lambda x: x[1])

    result = result.sort_values("struggle_score", ascending=False).reset_index(drop=True)

    return result[_columns]


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

def _compute_difficulty_adjusted(
    work: pd.DataFrame,
    result: pd.DataFrame,
    irt_difficulty: pd.DataFrame,
) -> pd.Series:
    """Per-student difficulty-adjusted score from recent submissions.

    For each student's last ``RECENT_SUBMISSION_COUNT`` submissions, compute
    ``incorrectness * (1 - normalized_irt_difficulty)`` and take the mean.
    Failing easy questions yields a higher score.

    Sparse-coverage handling: per-user means are shrunk toward the cohort
    mean by the coverage ratio ``n_covered / n_recent``. A student with full
    IRT coverage keeps their own mean; a student with 1-of-5 coverage leans
    heavily on the cohort mean, avoiding single-sample variance.
    """
    required = {"user", "question", "timestamp", "incorrectness"}
    if not required.issubset(work.columns):
        return pd.Series(0.0, index=result.index)

    # Normalize IRT difficulty to [0, 1] across available questions
    irt_norm = irt_difficulty[["question", "irt_difficulty"]].copy()
    irt_norm["norm_diff"] = analytics.min_max_normalize(irt_norm["irt_difficulty"])

    # Cohort-wide mean over all covered submissions — used as the shrinkage
    # target for low-coverage users.
    global_merged = work.merge(
        irt_norm[["question", "norm_diff"]], on="question", how="inner"
    )
    if global_merged.empty:
        global_mean = 0.0
    else:
        global_mean = float(
            (global_merged["incorrectness"] * (1.0 - global_merged["norm_diff"])).mean()
        )

    scores: dict[str, float] = {}
    for user, group in work.groupby("user"):
        recent = (
            group.sort_values("timestamp", ascending=False)
            .head(config.RECENT_SUBMISSION_COUNT)
        )
        if recent.empty:
            scores[user] = global_mean
            continue

        merged = recent.merge(irt_norm[["question", "norm_diff"]], on="question", how="left")
        covered = merged.dropna(subset=["norm_diff"])

        if covered.empty:
            scores[user] = global_mean
            continue

        user_mean = float(
            (covered["incorrectness"] * (1.0 - covered["norm_diff"])).mean()
        )
        coverage = len(covered) / len(recent)
        scores[user] = coverage * user_mean + (1.0 - coverage) * global_mean

    return result["user"].map(scores).fillna(global_mean).clip(0.0, 1.0)
