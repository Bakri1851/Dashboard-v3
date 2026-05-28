# struggle.py — 7-signal baseline student struggle score with Bayesian shrinkage.
#
# Carved out of the old analytics.py during the 2026-05-20 split. Holds:
#   - `compute_student_struggle_scores` (the headline function)
#   - `compute_recent_incorrectness` (A_raw with exponential time decay
#     and confidence-weighted decay)
#   - `_compute_slope` (improvement-trajectory linear regression)
#
# Depends on `incorrectness` for the per-row scoring and confidence
# weighting; depends on `analytics` for the shared `min_max_normalise`
# and `classify_score` helpers.
#
# Phase 5: `compute_student_struggle_scores` accepts optional `weights` and
# `shrinkage_k` overrides; cache.py passes the v2-trained values on every
# request (the deployed default — there is no runtime v1/v2 toggle).
# `_load_v2_weights` reads the trained JSON, falling back to the v1 constants
# only if the file is missing.
import json
import logging
import math
from typing import Optional

import numpy as np
import pandas as pd

from . import config
from .analytics import classify_score, min_max_normalise
from .incorrectness import (
    _CONFIDENCE_FLOOR,
    _confidence_weighted_mean,
    compute_feedback_confidence,
    compute_incorrectness_column,
)

logger = logging.getLogger(__name__)


def _load_v2_weights() -> Optional[dict[str, float]]:
    """Read data/eval/optimised_struggle_weights_v2.json. Returns the 7-element
    weight dict on success, None if missing/malformed/wrong-model-class.

    Cached lookup at call time (cheap — file is small + JSON parse is fast).
    `cache.load_struggle_df` passes the result through to
    `compute_student_struggle_scores` on every request — the trained v2 weights
    are the deployed default.
    """
    path = config.STRUGGLE_WEIGHTS_V2_PATH
    if not path.exists():
        logger.info("v2 struggle weights file not found at %s; falling back to v1", path)
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("v2 struggle weights load failed (%s): %s", type(exc).__name__, exc)
        return None
    if payload.get("model_class") != "LogisticRegression":
        # Defensive: the loader assumes linear LR coefficients; refuse if file
        # was produced by a different model class (e.g. gradient boosting).
        logger.warning(
            "v2 struggle weights model_class=%r != LogisticRegression; refusing to use",
            payload.get("model_class"),
        )
        return None
    weights = payload.get("weights")
    if not isinstance(weights, dict):
        return None
    expected_keys = {"n_hat", "t_hat", "i_norm", "r_norm", "A_norm", "d_hat", "rep_norm"}
    if not expected_keys.issubset(weights.keys()):
        logger.warning(
            "v2 struggle weights missing keys: have %s, need %s",
            set(weights.keys()), expected_keys,
        )
        return None
    return {k: float(v) for k, v in weights.items() if k in expected_keys}


# -----------------------------------------------------------------
# Recent Incorrectness (A_raw)
# -----------------------------------------------------------------

def compute_recent_incorrectness(student_submissions: pd.DataFrame) -> float:
    """
    Last N submissions (most recent first), weighted by exponential time decay
    AND (when present) per-row measurement confidence.

    w_i = exp(-lambda * delta_t_i) · confidence_i

    Weights are normalised to sum to 1.0. If the `incorrectness_confidence`
    column is absent, confidence weights default to 1.0 (unchanged behaviour
    for callers that haven't wired confidence yet). If all composite weights
    collapse to 0 (all empty feedback), falls back to the unweighted mean so
    we never return NaN.
    """
    # Drop NaT/NaN timestamps before sorting — the exp-decay calculation below
    # does arithmetic on timestamps, so a NaT silently propagates as NaN into
    # the weights. Upstream data_loader already drops these, but this function
    # is also called on user-supplied / saved-session slices that may bypass it.
    recent = (
        student_submissions.dropna(subset=["timestamp"])
        .sort_values("timestamp", ascending=False)
        .head(config.RECENT_SUBMISSION_COUNT)
    )
    scores = recent["incorrectness"].tolist()
    n_actual = len(scores)

    if n_actual == 0:
        return 0.0

    timestamps = recent["timestamp"].tolist()
    t_now = timestamps[0]  # most recent after descending sort
    lam = math.log(2) / config.DECAY_HALFLIFE_SECONDS

    time_weights = [
        math.exp(-lam * max(0.0, (t_now - ts).total_seconds()))
        for ts in timestamps
    ]

    if "incorrectness_confidence" in recent.columns:
        conf_weights = [
            max(_CONFIDENCE_FLOOR, float(c))
            for c in recent["incorrectness_confidence"].fillna(0.0).tolist()
        ]
    else:
        conf_weights = [1.0] * n_actual

    raw_weights = [t * c for t, c in zip(time_weights, conf_weights)]
    weight_sum = sum(raw_weights)

    # All-empty-feedback (or all-zero-confidence) cohort: fall back to the
    # time-decayed unweighted mean rather than returning 0 / NaN. With the
    # confidence floor above, this branch is only reachable when time_weights
    # themselves collapse (single-timestamp data), but kept defensively.
    if weight_sum <= 0.0:
        if all(w == time_weights[0] for w in time_weights):
            return sum(scores) / n_actual
        t_sum = sum(time_weights)
        return sum((t / t_sum) * s for t, s in zip(time_weights, scores))

    # Equal-weight fallback if all composite weights tied (e.g. bulk import
    # with uniform confidence). Exponentials are always positive.
    if all(w == raw_weights[0] for w in raw_weights):
        return sum(scores) / n_actual

    weights = [w / weight_sum for w in raw_weights]
    return sum(w * s for w, s in zip(weights, scores))


# -----------------------------------------------------------------
# Improvement Trajectory Helper
# -----------------------------------------------------------------

def _compute_slope(student_submissions: pd.DataFrame) -> float:
    """
    Linear regression slope of incorrectness vs. submission order (oldest=0).
    Positive slope = getting worse; negative = improving.
    Returns 0.0 if fewer than 2 submissions.
    """
    sorted_subs = (
        student_submissions.dropna(subset=["timestamp"])
        .sort_values("timestamp", ascending=True)
    )
    scores = sorted_subs["incorrectness"].tolist()
    n = len(scores)
    if n < 2:
        return 0.0
    slope = np.polyfit(range(n), scores, 1)[0]
    return float(slope)


# -----------------------------------------------------------------
# Student Struggle Score (7 signals, Bayesian shrinkage)
# -----------------------------------------------------------------

def compute_student_struggle_scores(
    df: pd.DataFrame,
    weights: Optional[dict[str, float]] = None,
    shrinkage_k: Optional[int] = None,
) -> pd.DataFrame:
    """
    Compute struggle scores for all students in the DataFrame.
    Returns a DataFrame with one row per student.

    Parameters
    ----------
    df : DataFrame of submissions to score.
    weights : optional dict with keys ``{n_hat, t_hat, i_norm, r_norm,
        A_norm, d_hat, rep_norm}`` — when provided, overrides the v1
        hand-set weights in ``config.STRUGGLE_WEIGHT_*``. The trained v2
        weights from ``_load_v2_weights()`` are passed through by
        ``cache.load_struggle_df`` on every request (the deployed default).
        Note: v2 weights may be NEGATIVE (LR coefficients normalised to
        L1=1), so the resulting struggle_score is clipped to [0, 1] AFTER
        the weighted sum.
    shrinkage_k : optional override for ``config.SHRINKAGE_K`` — passed
        through by cache.py from the runtime config (seeded from the
        Optuna-tuned v2 value). Defaults to ``config.SHRINKAGE_K``.
    """
    if df.empty:
        return pd.DataFrame(columns=[
            "user", "submission_count", "time_active_min", "n_hat", "t_hat",
            "i_hat", "r_hat", "rep_hat", "A_raw", "d_hat", "struggle_score",
            "struggle_level", "struggle_color", "mean_incorrectness_pct",
            "recent_incorrectness",
        ])

    work = df.copy()
    if "incorrectness" not in work.columns:
        work["incorrectness"] = compute_incorrectness_column(work)
    # Attach per-row measurement confidence. compute_recent_incorrectness and
    # the i_hat aggregation below read from this column — low-confidence rows
    # (empty/short feedback, mid-range LLM scores) contribute less weight.
    if "incorrectness_confidence" not in work.columns:
        work["incorrectness_confidence"] = compute_feedback_confidence(
            work["ai_feedback"] if "ai_feedback" in work.columns else pd.Series("", index=work.index),
            work["incorrectness"],
        )

    rows = []
    grouped = work.groupby("user")

    for user, group in grouped:
        n = len(group)

        # Time active (minutes from first to last submission)
        if n > 1:
            t = (group["timestamp"].max() - group["timestamp"].min()).total_seconds() / 60.0
        else:
            t = 0.0

        # Mean incorrectness: continuous gradient, no binary threshold.
        # Confidence-weighted — low-confidence rows (empty/short feedback,
        # mid-range LLM scores) contribute less. Falls back to simple mean
        # when all rows are low-confidence so i_hat never collapses to 0.
        i_hat = _confidence_weighted_mean(
            group["incorrectness"],
            group["incorrectness_confidence"],
            fallback=group["incorrectness"],
        )

        # Retry rate: fraction of submissions that are repeats of an already-attempted question
        unique_q = group["question"].nunique()
        r_hat = 1.0 - (unique_q / n) if n > 0 else 0.0

        # Recent incorrectness (A_raw)
        a_raw = compute_recent_incorrectness(group)

        # Improvement trajectory: linear slope of incorrectness over submission order
        d_raw = _compute_slope(group)

        # Answer repetition rate: fraction of submissions that exactly repeat
        # a previously submitted answer on the same question (exact match after strip).
        total_repeat_submissions = 0
        for _q, q_group in group.groupby("question"):
            answers = q_group.sort_values("timestamp")["student_answer"].tolist()
            seen: set[str] = set()
            for ans in answers:
                cleaned = str(ans).strip()
                if cleaned in seen:
                    total_repeat_submissions += 1
                else:
                    seen.add(cleaned)
        rep_hat = total_repeat_submissions / n if n > 0 else 0.0

        # Dominant module — kept as diagnostic metadata. NOT used for
        # normalisation: grouping students by dominant-module collapses
        # minority-module students into degenerate single-member groups
        # where every min-max signal snaps to 0.5, producing a struggle
        # score of exactly 0.5 → "Needs Help" for everyone in a small
        # module. If you need per-module rankings, use the sidebar module
        # filter instead — that scopes the whole computation to one module
        # cleanly. Within-module normalisation is only meaningful at the
        # question level (compute_question_difficulty_scores below), where
        # each item has a canonical module.
        if "module" in group.columns:
            mode = group["module"].mode()
            dominant_module = str(mode.iloc[0]) if not mode.empty else ""
        else:
            dominant_module = ""

        rows.append({
            "user": user,
            "module": dominant_module,
            "submission_count": n,
            "time_active_min": round(t, 2),
            "n_raw": n,
            "t_raw": t,
            "i_hat": i_hat,
            "r_hat": r_hat,
            "A_raw": a_raw,
            "d_raw": d_raw,
            "rep_hat": rep_hat,
        })

    result = pd.DataFrame(rows)

    # Min-max normalise every composite input so the configured weights match
    # the effective weights. Raw [0, 1] rates (i_hat, r_hat, A_raw, rep_hat)
    # are retained for display; the _norm columns feed the weighted sum.
    result["n_hat"] = min_max_normalise(result["n_raw"])
    result["t_hat"] = min_max_normalise(result["t_raw"])
    result["d_hat"] = min_max_normalise(result["d_raw"])  # positive = getting worse
    result["i_norm"] = min_max_normalise(result["i_hat"])
    result["r_norm"] = min_max_normalise(result["r_hat"])
    result["A_norm"] = min_max_normalise(result["A_raw"])
    result["rep_norm"] = min_max_normalise(result["rep_hat"])

    # Compute S_raw. Use v2 weights if provided, else fall back to v1 hand-set.
    # v2 weights may be NEGATIVE (LR coefficients L1-normalised); the .clip(0,1)
    # below handles out-of-range weighted sums.
    if weights is None:
        w_n_struct = config.STRUGGLE_WEIGHT_N
        w_t = config.STRUGGLE_WEIGHT_T
        w_i = config.STRUGGLE_WEIGHT_I
        w_r = config.STRUGGLE_WEIGHT_R
        w_a = config.STRUGGLE_WEIGHT_A
        w_d = config.STRUGGLE_WEIGHT_D
        w_rep = config.STRUGGLE_WEIGHT_REP
    else:
        w_n_struct = weights.get("n_hat", config.STRUGGLE_WEIGHT_N)
        w_t = weights.get("t_hat", config.STRUGGLE_WEIGHT_T)
        w_i = weights.get("i_norm", config.STRUGGLE_WEIGHT_I)
        w_r = weights.get("r_norm", config.STRUGGLE_WEIGHT_R)
        w_a = weights.get("A_norm", config.STRUGGLE_WEIGHT_A)
        w_d = weights.get("d_hat", config.STRUGGLE_WEIGHT_D)
        w_rep = weights.get("rep_norm", config.STRUGGLE_WEIGHT_REP)

    result["struggle_score"] = (
        w_n_struct * result["n_hat"]
        + w_t * result["t_hat"]
        + w_i * result["i_norm"]
        + w_r * result["r_norm"]
        + w_a * result["A_norm"]
        + w_d * result["d_hat"]
        + w_rep * result["rep_norm"]
    ).clip(0.0, 1.0)

    # Bayesian shrinkage: pull low-n scores toward the class mean to reduce noise.
    # w_n = n / (n + K) → students with few submissions are shrunk more strongly.
    # K comes from runtime_config (passed via cache.py) when hyperparams v2 is on;
    # otherwise falls back to the config default.
    effective_k = shrinkage_k if shrinkage_k is not None else config.SHRINKAGE_K
    s_class_mean = result["struggle_score"].mean()
    w_n = result["n_raw"] / (result["n_raw"] + effective_k)
    result["struggle_score"] = (
        w_n * result["struggle_score"] + (1 - w_n) * s_class_mean
    ).clip(0.0, 1.0)

    # Classify
    levels_colors = result["struggle_score"].apply(
        lambda s: classify_score(s, config.STRUGGLE_THRESHOLDS)
    )
    result["struggle_level"] = levels_colors.apply(lambda x: x[0])
    result["struggle_color"] = levels_colors.apply(lambda x: x[1])

    # Convenience columns
    result["mean_incorrectness_pct"] = (result["i_hat"] * 100).round(1)
    result["recent_incorrectness"] = result["A_raw"].round(3)

    # Sort descending by score
    result = result.sort_values("struggle_score", ascending=False).reset_index(drop=True)

    return result
