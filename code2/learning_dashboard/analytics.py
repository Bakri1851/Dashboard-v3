# analytics.py — Scoring calculations (UI-independent)
import hashlib
import json
import logging
import math
import os
import re
import threading
import time
from typing import Optional

import numpy as np
import pandas as pd
from openai import OpenAI
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity

from learning_dashboard import config, paths

logger = logging.getLogger(__name__)


def _get_openai_client() -> OpenAI:
    # Key is sourced from OPENAI_API_KEY in the environment. backend/main.py
    # lifts it out of .secrets/secrets.toml at FastAPI boot.
    key = os.environ.get("OPENAI_API_KEY", "")
    return OpenAI(api_key=key, max_retries=1, timeout=20.0)


# Incorrectness Estimation via OpenAI

# Disk-backed cache: scores persist across uvicorn restarts so a clean boot
# doesn't re-score ~3,400 unique feedbacks against OpenAI. The on-disk file
# stores the OPENAI_MODEL it was built with — if the model changes, the cache
# is discarded on load because scores are model-dependent.
_SAVE_DEBOUNCE_SECONDS = 30.0
_incorrectness_save_lock = threading.Lock()
_last_incorrectness_save_ts: float = 0.0


def _load_incorrectness_cache() -> dict[str, float]:
    path = paths.incorrectness_cache_path()
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("incorrectness cache load failed (%s): %s", type(exc).__name__, exc)
        return {}
    if not isinstance(payload, dict):
        return {}
    stored_model = payload.get("model")
    if stored_model != config.OPENAI_MODEL:
        logger.info(
            "incorrectness cache on disk was built for model=%r, current=%r — discarding",
            stored_model, config.OPENAI_MODEL,
        )
        return {}
    scores = payload.get("scores")
    if not isinstance(scores, dict):
        return {}
    out: dict[str, float] = {}
    for k, v in scores.items():
        if isinstance(k, str) and isinstance(v, (int, float)):
            out[k] = float(v)
    logger.info("incorrectness cache: loaded %d entries from disk (model=%s)", len(out), stored_model)
    return out


def _save_incorrectness_cache(*, force: bool = False) -> None:
    """Persist the in-memory cache to disk with debounce.

    The prewarm adds ~170 batches of 20 scores back-to-back; without the
    debounce, each batch would trigger a JSON dump of the full dict (~3,400
    entries), which is wasted I/O. Call with ``force=True`` at the end of a
    scoring pass to guarantee the final state reaches disk.
    """
    global _last_incorrectness_save_ts
    with _incorrectness_save_lock:
        now = time.monotonic()
        if not force and (now - _last_incorrectness_save_ts) < _SAVE_DEBOUNCE_SECONDS:
            return
        _last_incorrectness_save_ts = now
        snapshot = dict(_incorrectness_cache)
    payload = {"model": config.OPENAI_MODEL, "scores": snapshot}
    path = paths.incorrectness_cache_path()
    try:
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload), encoding="utf-8")
        tmp.replace(path)
    except OSError as exc:
        logger.warning("incorrectness cache save failed: %s", exc)


_incorrectness_cache: dict[str, float] = _load_incorrectness_cache()
_cluster_cache: dict[tuple[str, int, str], list[dict] | None] = {}


_JSON_ARRAY_RE = re.compile(r"\[[^\[\]]*\]", re.DOTALL)


def _parse_scores_response(text: str, expected_len: int) -> Optional[list[float]]:
    """Extract a JSON array of floats from a model response.

    Handles markdown code fences (``` ```json ... ``` ```) and prose wrapping
    that gpt-4o-mini tends to add despite instructions to the contrary.
    Returns None when no valid float list of ``expected_len`` can be recovered.
    """
    if not text:
        return None
    cleaned = text.strip()
    # Strip markdown fences: ```json ... ``` or ``` ... ```
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z0-9]*\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    candidates = [cleaned]
    # Fallback — pull the first [...] block out of whatever prose wraps it.
    match = _JSON_ARRAY_RE.search(cleaned)
    if match and match.group(0) != cleaned:
        candidates.append(match.group(0))

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except (json.JSONDecodeError, ValueError):
            continue
        if not isinstance(parsed, list) or len(parsed) != expected_len:
            continue
        try:
            return [float(max(0.0, min(1.0, float(s)))) for s in parsed]
        except (TypeError, ValueError):
            continue
    return None


def _call_openai_batch(feedbacks: list[str]) -> Optional[list[float]]:
    """Send a batch of feedback texts to OpenAI and return incorrectness scores.

    Returns a list of floats in [0, 1] on success, or ``None`` on any failure
    (API error, empty response, unparseable response, wrong-length response).
    Callers are responsible for deciding the fallback — typically 0.5 without
    caching so a transient failure doesn't poison the cache.
    """
    numbered = "\n".join(f"{i + 1}. {text}" for i, text in enumerate(feedbacks))
    prompt = (
        "You are scoring student answers based on AI tutor feedback.\n"
        "For each numbered feedback text below, return a JSON array of floats "
        "from 0.0 (fully correct) to 1.0 (fully incorrect).\n"
        "Return ONLY the JSON array, nothing else.\n\n"
        f"Feedbacks:\n{numbered}"
    )
    try:
        client = _get_openai_client()
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            timeout=15.0,
        )
    except Exception as exc:
        logger.warning("OpenAI batch call failed (%s): %s", type(exc).__name__, exc)
        return None

    raw = (response.choices[0].message.content or "") if response.choices else ""
    scores = _parse_scores_response(raw, len(feedbacks))
    if scores is None:
        logger.warning(
            "OpenAI response did not parse to %d floats; raw=%r",
            len(feedbacks),
            raw[:200],
        )
    return scores


def estimate_incorrectness(feedback: Optional[str]) -> float:
    """Score a single feedback string via OpenAI. Returns float in [0, 1].

    On API failure, returns 0.5 without caching so the next call retries.
    """
    if not feedback or not str(feedback).strip():
        return 0.5
    key = str(feedback).strip()
    if key in _incorrectness_cache:
        return _incorrectness_cache[key]
    scores = _call_openai_batch([key])
    if scores is None:
        return 0.5
    _incorrectness_cache[key] = scores[0]
    _save_incorrectness_cache()
    return scores[0]


def compute_incorrectness_column(
    df: pd.DataFrame,
    max_new_scores: Optional[int] = None,
    *,
    score_new: bool = True,
) -> pd.Series:
    """
    Score all ai_feedback values via OpenAI, batched for efficiency.
    Successful batches are cached in-process to avoid repeat API calls.
    Failed batches leave the cache untouched so the next call retries —
    this prevents transient API errors from poisoning downstream analytics.
    Empty/null feedback → 0.5 without an API call.

    ``max_new_scores`` overrides the per-run scoring cap:
      - ``None`` (default) → fall back to ``config.SCORING_PER_RUN_CAP``.
      - ``0`` → no cap, score every uncached feedback in this call.
      - positive int → that many new scores at most.
    The background prewarm (``backend/main.py::_prewarm``) passes ``0`` so it
    fully warms ``_incorrectness_cache`` without blocking in-request calls.

    ``score_new=False`` skips all OpenAI calls — the result is built purely
    from ``_incorrectness_cache`` lookups, with uncached feedbacks mapped to
    0.5. The in-request raw-data load path uses this so it never blocks on
    OpenAI; the background prewarm is responsible for warming the cache.
    """
    feedbacks = df["ai_feedback"].astype(str).str.strip()

    if not getattr(config, "OPENAI_SCORING_ENABLED", True):
        logger.info(
            "compute_incorrectness_column: OPENAI_SCORING_ENABLED=False — "
            "returning 0.5 for all %d rows without any API call.",
            len(df),
        )
        return pd.Series(0.5, index=df.index)

    unique_feedbacks = feedbacks.unique()
    already_cached = sum(1 for t in unique_feedbacks if t in _incorrectness_cache)

    # Collect unique non-empty texts not yet cached
    uncached_all = [t for t in unique_feedbacks if t and t not in _incorrectness_cache]
    n_empty = sum(1 for t in unique_feedbacks if not t)

    if not score_new:
        # Pure cache-lookup mode — no OpenAI, no blocking. Deferred items
        # remain at 0.5 until the background prewarm fills the cache.
        result = feedbacks.map(lambda t: _incorrectness_cache.get(t, 0.5))
        logger.info(
            "compute_incorrectness_column: score_new=False lookup-only — "
            "total_rows=%d unique_feedbacks=%d already_cached=%d "
            "deferred=%d empty_feedbacks=%d",
            len(df), len(unique_feedbacks), already_cached,
            len(uncached_all), n_empty,
        )
        return result

    # Cap the number of new feedbacks scored per request so a cold cache
    # (~3k uniques on this dataset) doesn't block the first /struggle or /live
    # call for 5–10 minutes of serial OpenAI round-trips. Remaining uncached
    # feedbacks stay at 0.5 for this request and get picked up by subsequent
    # calls (the raw-data TTL evicts the window cache every CACHE_TTL seconds,
    # so the cache fills progressively across a few poll cycles).
    if max_new_scores is None:
        cap = int(getattr(config, "SCORING_PER_RUN_CAP", 0) or 0)
    else:
        cap = int(max_new_scores)
    uncached = uncached_all[:cap] if cap > 0 else uncached_all
    deferred = len(uncached_all) - len(uncached)

    logger.info(
        "compute_incorrectness_column: total_rows=%d unique_feedbacks=%d "
        "already_cached=%d non_empty_uncached=%d scoring_this_run=%d "
        "deferred=%d empty_feedbacks=%d model=%s",
        len(df), len(unique_feedbacks), already_cached, len(uncached_all),
        len(uncached), deferred, n_empty, config.OPENAI_MODEL,
    )

    batches_attempted = 0
    batches_succeeded = 0
    scores_added = 0

    # Fetch in batches — only cache successful responses.
    for i in range(0, len(uncached), config.OPENAI_BATCH_SIZE):
        batch = uncached[i : i + config.OPENAI_BATCH_SIZE]
        batches_attempted += 1
        scores = _call_openai_batch(batch)
        if scores is not None:
            _incorrectness_cache.update(zip(batch, scores))
            batches_succeeded += 1
            scores_added += len(batch)
            _save_incorrectness_cache()

    if scores_added > 0:
        _save_incorrectness_cache(force=True)

    result = feedbacks.map(lambda t: _incorrectness_cache.get(t, 0.5))
    share_at_half = float((result == 0.5).mean()) if len(result) else 0.0

    logger.info(
        "compute_incorrectness_column: batches_attempted=%d batches_succeeded=%d "
        "scores_added=%d cache_size=%d | result min=%.3f median=%.3f max=%.3f "
        "share_at_0.5=%.1f%%",
        batches_attempted, batches_succeeded, scores_added, len(_incorrectness_cache),
        float(result.min()) if len(result) else 0.0,
        float(result.median()) if len(result) else 0.0,
        float(result.max()) if len(result) else 0.0,
        100.0 * share_at_half,
    )

    return result


# Feedback Confidence (consumed by struggle pipeline and measurement.py)

_EMPTY_FEEDBACK_MARKERS = {"", "nan", "none", "null", "n/a", "na"}


def compute_feedback_confidence(
    feedbacks: pd.Series,
    scores: pd.Series,
) -> pd.Series:
    """Per-row confidence in [0, 1] for an incorrectness score.

    confidence = BASE · length_factor · (0.5 + 0.5 · extremity_factor)

    - length_factor ramps 0→1 over the first MIN_LENGTH chars of feedback.
    - extremity_factor = 2·|score − 0.5|  — mid-range LLM scores (≈0.5) are
      the least trustworthy, so confidence dips toward the middle ("confidence
      valley").
    - Empty/null/whitespace-only feedback → 0.0 (the 0.5 fallback score is a
      prior, not a measurement, so it should carry zero weight downstream).
    """
    feed_str = feedbacks.astype(str).str.strip()
    is_empty = (
        feed_str.str.lower().isin(_EMPTY_FEEDBACK_MARKERS)
        | feedbacks.isna()
        | scores.isna()
    )

    lengths = feed_str.str.len().fillna(0).astype(float)
    length_factor = np.minimum(
        1.0, lengths / config.MEASUREMENT_CONFIDENCE_MIN_LENGTH
    )
    safe_scores = scores.fillna(0.5)
    extremity_factor = 2.0 * np.abs(safe_scores - 0.5)

    confidence = (
        config.MEASUREMENT_CONFIDENCE_BASE
        * length_factor
        * (0.5 + 0.5 * extremity_factor)
    )
    confidence = pd.Series(confidence, index=feedbacks.index).clip(0.0, 1.0)
    confidence[is_empty] = 0.0
    return confidence


# Minimum weight applied to every row regardless of confidence. Without this
# floor, rows with empty / short feedback (confidence = 0) are dropped
# entirely from the aggregation. That systematically under-counts correct
# answers (which in this dataset often have shorter / empty feedback)
# and biases the resulting i_hat / A_raw upward — producing a false
# "everyone is struggling" signal in the aggregate. The floor keeps every
# row in the mean while still letting high-confidence rows count more.
_CONFIDENCE_FLOOR: float = 0.2


def _confidence_weighted_mean(
    values: pd.Series,
    weights: pd.Series,
    fallback: Optional[pd.Series] = None,
) -> float:
    """Weighted mean with a confidence floor + fallback when all weights vanish.

    Each row's effective weight is ``max(confidence, _CONFIDENCE_FLOOR)`` so
    low-confidence rows still contribute to the mean, preventing the bias
    introduced by hard-zeroing empty-feedback rows (which often correlate
    with correct answers in this dataset).
    """
    eff = weights.clip(lower=_CONFIDENCE_FLOOR)
    w_sum = float(eff.sum())
    if w_sum <= 0.0:
        pool = fallback if fallback is not None else values
        return float(pool.mean()) if len(pool) else 0.0
    return float((values * eff).sum() / w_sum)


# Min-Max Normalization

def min_max_normalize(series: pd.Series) -> pd.Series:
    """(x - min) / (max - min), clamped to [0, 1].

    Returns 0.5 if min == max — the neutral midpoint preserves the feature's
    weight contribution in composite sums when the cohort is degenerate
    (e.g. all students have A_raw=0). Rankings are unchanged either way.
    """
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series(0.5, index=series.index)
    result = (series - min_val) / (max_val - min_val)
    return result.clip(0.0, 1.0)


def min_max_normalize_grouped(
    series: pd.Series,
    groups: Optional[pd.Series],
) -> pd.Series:
    """Min-max normalise within each group label.

    Different modules have different difficulty/workload distributions — a
    CS student's time-on-task is not commensurable with a maths student's.
    Grouping by module before normalisation keeps the rankings meaningful
    when the global leaderboard mixes cohorts.

    A single-group input (or ``groups=None``) is equivalent to
    ``min_max_normalize``. Groups of size 1 or with all-equal values
    return 0.5 for each member (same semantics as the ungrouped helper).
    """
    if groups is None:
        return min_max_normalize(series)
    groups = groups.reindex(series.index)
    out = pd.Series(0.5, index=series.index, dtype=float)
    for _label, idx in groups.groupby(groups, dropna=False).groups.items():
        sub = series.loc[idx]
        out.loc[idx] = min_max_normalize(sub).values
    return out


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
# Classification Helpers
# -----------------------------------------------------------------

def classify_score(
    score: float,
    thresholds: list[tuple[float, float, str, str]],
) -> tuple[str, str]:
    """Return (label, color) for the matching threshold range."""
    for i, (low, high, label, color) in enumerate(thresholds):
        if i == len(thresholds) - 1:
            if low <= score <= high:
                return label, color
        else:
            if low <= score < high:
                return label, color
    return thresholds[-1][2], thresholds[-1][3]


# -----------------------------------------------------------------
# Student Struggle Score
# -----------------------------------------------------------------

def compute_student_struggle_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute struggle scores for all students in the DataFrame.
    Returns a DataFrame with one row per student.
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

    # Min-max normalize every composite input so the configured weights match
    # the effective weights. Raw [0, 1] rates (i_hat, r_hat, A_raw, rep_hat)
    # are retained for display; the _norm columns feed the weighted sum.
    result["n_hat"] = min_max_normalize(result["n_raw"])
    result["t_hat"] = min_max_normalize(result["t_raw"])
    result["d_hat"] = min_max_normalize(result["d_raw"])  # positive = getting worse
    result["i_norm"] = min_max_normalize(result["i_hat"])
    result["r_norm"] = min_max_normalize(result["r_hat"])
    result["A_norm"] = min_max_normalize(result["A_raw"])
    result["rep_norm"] = min_max_normalize(result["rep_hat"])

    # Compute S_raw
    result["struggle_score"] = (
        config.STRUGGLE_WEIGHT_N * result["n_hat"]
        + config.STRUGGLE_WEIGHT_T * result["t_hat"]
        + config.STRUGGLE_WEIGHT_I * result["i_norm"]
        + config.STRUGGLE_WEIGHT_R * result["r_norm"]
        + config.STRUGGLE_WEIGHT_A * result["A_norm"]
        + config.STRUGGLE_WEIGHT_D * result["d_hat"]
        + config.STRUGGLE_WEIGHT_REP * result["rep_norm"]
    ).clip(0.0, 1.0)

    # Bayesian shrinkage: pull low-n scores toward the class mean to reduce noise.
    # w_n = n / (n + K) → students with few submissions are shrunk more strongly.
    s_class_mean = result["struggle_score"].mean()
    w_n = result["n_raw"] / (result["n_raw"] + config.SHRINKAGE_K)
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


# -----------------------------------------------------------------
# Collaborative Filtering Struggle Detection
# -----------------------------------------------------------------

# All CF features must be on the same cohort-relative [0, 1] scale for
# cosine similarity to be meaningful — use the normalized columns added in M1.
CF_FEATURES = ["n_hat", "t_hat", "i_norm", "A_norm", "d_hat"]


def compute_cf_struggle_scores(
    struggle_df: pd.DataFrame,
    threshold: float = 0.7,
    k: int = 3,
) -> tuple[pd.Series, dict]:
    """
    Collaborative filtering layer: identify students behaviourally similar
    to those flagged by the parametric model.

    Returns (cf_scores Series, diagnostics dict).
    """
    diagnostics: dict = {
        "threshold": threshold,
        "k": k,
        "n_flagged_parametric": 0,
        "n_elevated_cf": 0,
        "elevated_students": [],
        "fallback": False,
    }

    try:
        n_students = len(struggle_df)
        if n_students < 4:
            diagnostics["fallback"] = True
            diagnostics["reason"] = "fewer than 4 students"
            return struggle_df["struggle_score"].copy(), diagnostics

        missing = [c for c in CF_FEATURES if c not in struggle_df.columns]
        if missing:
            diagnostics["fallback"] = True
            diagnostics["reason"] = f"missing baseline feature columns: {missing}"
            return struggle_df["struggle_score"].copy(), diagnostics

        # Interaction matrix from normalised features. Guard against NaN
        # leaking in from upstream (e.g. min_max_normalize on all-equal
        # columns in degenerate cohorts) — cosine_similarity returns NaN
        # rows when fed NaN, which would silently collapse scores to 0.
        X = np.nan_to_num(struggle_df[CF_FEATURES].values, nan=0.0)

        # Pairwise cosine similarity
        W = cosine_similarity(X)

        # Binary help-need labels from parametric scores
        h = (struggle_df["struggle_score"].values >= threshold).astype(float)
        diagnostics["n_flagged_parametric"] = int(h.sum())

        if diagnostics["n_flagged_parametric"] == 0:
            diagnostics["fallback"] = True
            diagnostics["reason"] = "no students above threshold"
            return struggle_df["struggle_score"].copy(), diagnostics

        cf_scores = np.copy(h)
        users = struggle_df["user"].values
        elevated = []

        for i in range(n_students):
            if h[i] == 1.0:
                continue

            sims = W[i].copy()
            sims[i] = -1.0  # exclude self

            neighbour_idx = np.argsort(sims)[-k:][::-1]

            weights = sims[neighbour_idx]
            positive_mask = weights > 0
            if positive_mask.any():
                w_pos = weights[positive_mask]
                h_pos = h[neighbour_idx[positive_mask]]
                cf_scores[i] = float(np.dot(w_pos, h_pos) / w_pos.sum())
            else:
                cf_scores[i] = 0.0

            if cf_scores[i] > 0:
                elevated.append({
                    "Student": users[i],
                    "Parametric Score": round(float(struggle_df.iloc[i]["struggle_score"]), 3),
                    "CF Score": round(cf_scores[i], 3),
                    "Nearest Neighbours": ", ".join(
                        users[neighbour_idx].tolist()
                    ),
                })

        diagnostics["n_elevated_cf"] = len(elevated)
        diagnostics["elevated_students"] = sorted(
            elevated, key=lambda x: x["CF Score"], reverse=True
        )

        return pd.Series(cf_scores, index=struggle_df.index), diagnostics

    except Exception as e:
        diagnostics["fallback"] = True
        diagnostics["error"] = str(e)
        return struggle_df["struggle_score"].copy(), diagnostics


def get_similar_students(
    student_id: str,
    struggle_df: pd.DataFrame,
    k: int = 5,
) -> pd.DataFrame | None:
    """
    Return the k most similar students to *student_id* based on cosine
    similarity over the CF feature set.

    Returns a DataFrame with columns: Student, Similarity, Struggle Score,
    Struggle Level — sorted by similarity descending.  Returns None on error
    or if the student is not found.
    """
    try:
        if len(struggle_df) < 2:
            return None

        idx_match = struggle_df.index[struggle_df["user"] == student_id]
        if len(idx_match) == 0:
            return None

        X = np.nan_to_num(struggle_df[CF_FEATURES].values, nan=0.0)
        W = cosine_similarity(X)

        pos = struggle_df.index.get_loc(idx_match[0])
        sims = W[pos].copy()
        sims[pos] = -1.0  # exclude self

        top_k = min(k, len(struggle_df) - 1)
        neighbour_idx = np.argsort(sims)[-top_k:][::-1]

        rows = []
        for ni in neighbour_idx:
            row = struggle_df.iloc[ni]
            rows.append({
                "Student": row["user"],
                "Similarity": round(float(sims[ni]), 3),
                "Struggle Score": round(float(row["struggle_score"]), 3),
                "Struggle Level": row["struggle_level"],
            })

        return pd.DataFrame(rows)
    except Exception:
        return None


# -----------------------------------------------------------------
# Question Difficulty Score
# -----------------------------------------------------------------

def compute_question_difficulty_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute difficulty scores for all questions in the DataFrame.
    Returns a DataFrame with one row per question.
    """
    if df.empty:
        return pd.DataFrame(columns=[
            "question", "total_attempts", "unique_students", "avg_attempts",
            "c_tilde", "t_tilde", "a_tilde", "f_tilde", "p_tilde",
            "difficulty_score", "difficulty_level", "difficulty_color",
            "incorrect_rate_pct",
        ])

    work = df.copy()
    if "incorrectness" not in work.columns:
        work["incorrectness"] = compute_incorrectness_column(work)

    rows = []
    grouped = work.groupby("question")

    for question, group in grouped:
        total_attempts = len(group)
        unique_students = group["user"].nunique()

        # c_tilde: incorrect rate
        correct_count = (group["incorrectness"] < config.CORRECT_THRESHOLD).sum()
        c_tilde = 1.0 - (correct_count / total_attempts) if total_attempts > 0 else 0.0

        # t_raw: avg time per student (all students; 1-attempt students contribute 0)
        time_values = []
        for _user, user_group in group.groupby("user"):
            if len(user_group) >= 2:
                t_student = (
                    user_group["timestamp"].max() - user_group["timestamp"].min()
                ).total_seconds() / 60.0
            else:
                t_student = 0.0
            time_values.append(t_student)
        t_raw = np.mean(time_values) if time_values else 0.0

        # a_raw: avg attempts per student
        a_raw = total_attempts / unique_students if unique_students > 0 else 0.0

        # f_tilde: average incorrectness across all attempts
        f_tilde = group["incorrectness"].mean()

        # p_tilde: first-attempt failure rate
        first_attempts = group.sort_values("timestamp").groupby("user").first().reset_index()
        failed_first = (first_attempts["incorrectness"] >= config.CORRECT_THRESHOLD).sum()
        p_tilde = failed_first / unique_students if unique_students > 0 else 0.0

        # Module attribution: questions belong to exactly one module, so
        # group["module"].iloc[0] is canonical. Used for within-module
        # normalisation — see compute_student_struggle_scores.
        if "module" in group.columns:
            question_module = str(group["module"].iloc[0]) if len(group) else ""
        else:
            question_module = ""

        rows.append({
            "question": question,
            "module": question_module,
            "total_attempts": total_attempts,
            "unique_students": unique_students,
            "avg_attempts": round(a_raw, 2),
            "c_tilde": c_tilde,
            "t_raw": t_raw,
            "a_raw": a_raw,
            "f_tilde": f_tilde,
            "p_tilde": p_tilde,
        })

    result = pd.DataFrame(rows)

    # Min-max normalize every composite input so configured weights match
    # effective weights. Raw rates (c_tilde, f_tilde, p_tilde) are retained
    # for display (incorrect_rate_pct); _norm columns feed the weighted sum.
    # Grouped by module — a "hard" CS question is not commensurable with a
    # "hard" maths question when both appear on the global leaderboard.
    modules = result["module"] if "module" in result.columns else None
    result["t_tilde"] = min_max_normalize_grouped(result["t_raw"], modules)
    result["a_tilde"] = min_max_normalize_grouped(result["a_raw"], modules)
    result["c_norm"] = min_max_normalize_grouped(result["c_tilde"], modules)
    result["f_norm"] = min_max_normalize_grouped(result["f_tilde"], modules)
    result["p_norm"] = min_max_normalize_grouped(result["p_tilde"], modules)

    # Compute D_raw
    result["difficulty_score"] = (
        config.DIFFICULTY_WEIGHT_C * result["c_norm"]
        + config.DIFFICULTY_WEIGHT_T * result["t_tilde"]
        + config.DIFFICULTY_WEIGHT_A * result["a_tilde"]
        + config.DIFFICULTY_WEIGHT_F * result["f_norm"]
        + config.DIFFICULTY_WEIGHT_P * result["p_norm"]
    ).clip(0.0, 1.0)

    # Classify
    levels_colors = result["difficulty_score"].apply(
        lambda s: classify_score(s, config.DIFFICULTY_THRESHOLDS)
    )
    result["difficulty_level"] = levels_colors.apply(lambda x: x[0])
    result["difficulty_color"] = levels_colors.apply(lambda x: x[1])

    # Convenience columns
    result["incorrect_rate_pct"] = (result["c_tilde"] * 100).round(1)

    # Sort descending by score
    result = result.sort_values("difficulty_score", ascending=False).reset_index(drop=True)

    return result


# -----------------------------------------------------------------
# Mistake Clustering
# -----------------------------------------------------------------

def _label_clusters_with_openai(clusters: list[dict], question_id: str) -> list[dict]:
    """
    Send all cluster representative answers to OpenAI in one call and fill in 'label'.
    Falls back to 'Mistake Group N' on any error.
    """
    cluster_blocks = []
    for i, c in enumerate(clusters):
        examples = "; ".join(f'"{e}"' for e in c["example_answers"])
        cluster_blocks.append(f"Cluster {i + 1}: {examples}")

    numbered = "\n".join(cluster_blocks)
    prompt = (
        f"You are analysing wrong student answers to a computing/programming question "
        f"(question ID: {question_id}).\n"
        f"Below are {len(clusters)} clusters of incorrect answers, each shown with up to 3 "
        f"representative examples.\n"
        f"For each cluster, provide a concise label (3-6 words) describing the TYPE of mistake "
        f"students are making — focus on the conceptual error, not just what they wrote.\n\n"
        f"Return ONLY a JSON array of strings, one label per cluster, in the same order.\n"
        f"Example output for 3 clusters: "
        f'["Off-by-one indexing error", "Wrong loop condition", "Incorrect variable scope"]\n\n'
        f"Clusters:\n{numbered}"
    )

    try:
        client = _get_openai_client()
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            timeout=15.0,
        )
        labels = json.loads(response.choices[0].message.content.strip())
        if isinstance(labels, list) and len(labels) == len(clusters):
            for i, lbl in enumerate(labels):
                clusters[i]["label"] = str(lbl).strip()
            return clusters
    except Exception:
        pass

    for i, c in enumerate(clusters):
        if c["label"] is None:
            c["label"] = f"Mistake Group {i + 1}"
    return clusters


def cluster_question_mistakes(
    question_df: pd.DataFrame,
    question_id: str,
) -> list[dict] | None:
    """
    Cluster incorrect student answers for a question using TF-IDF + K-means.

    Returns a list of cluster dicts sorted by count descending:
        label            (str)   — short AI-generated description of the mistake type
        count            (int)   — number of incorrect submissions in this cluster
        percent_of_wrong (float) — percentage of all wrong submissions
        example_answers  (list[str]) — up to CLUSTER_MAX_EXAMPLES representative answers

    Returns None if there are fewer than CLUSTER_MIN_WRONG incorrect submissions
    or if vectorisation fails.
    """
    wrong_df = question_df[question_df["incorrectness"] >= config.CORRECT_THRESHOLD].copy()
    wrong_df = wrong_df[wrong_df["student_answer"].notna()]
    wrong_df["student_answer"] = wrong_df["student_answer"].astype(str).str.strip()
    wrong_df = wrong_df[wrong_df["student_answer"] != ""]

    total_wrong = len(wrong_df)
    if total_wrong < config.CLUSTER_MIN_WRONG:
        return None

    # Deterministic digest — Python's built-in hash() is salted per process,
    # so caching keyed on it collides or misses unpredictably across reruns.
    _answer_payload = "\0".join(sorted(wrong_df["student_answer"].tolist()))
    _answer_hash = hashlib.sha1(_answer_payload.encode("utf-8")).hexdigest()
    cache_key = (question_id, total_wrong, _answer_hash)
    if cache_key in _cluster_cache:
        return _cluster_cache[cache_key]

    unique_answers = wrong_df["student_answer"].unique().tolist()

    # Single unique answer — no point clustering
    if len(unique_answers) == 1:
        result = [{
            "label": "Common Wrong Answer",
            "count": total_wrong,
            "percent_of_wrong": 100.0,
            "example_answers": unique_answers[:config.CLUSTER_MAX_EXAMPLES],
        }]
        _cluster_cache[cache_key] = result
        return result

    # TF-IDF on deduplicated texts
    vectorizer = TfidfVectorizer(
        max_features=500,
        sublinear_tf=True,
        strip_accents="unicode",
        analyzer="word",
        min_df=1,
    )
    try:
        X = vectorizer.fit_transform(unique_answers)
    except ValueError:
        _cluster_cache[cache_key] = None
        return None

    n_unique = len(unique_answers)
    max_k = min(config.CLUSTER_MAX_K, n_unique - 1)

    if max_k < 2:
        result = [{
            "label": "Mixed Wrong Answers",
            "count": total_wrong,
            "percent_of_wrong": 100.0,
            "example_answers": unique_answers[:config.CLUSTER_MAX_EXAMPLES],
        }]
        _cluster_cache[cache_key] = result
        return result

    # Auto-select k via silhouette score
    best_k = 2
    best_score = -1.0
    for k in range(2, max_k + 1):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X)
        if len(set(labels)) < 2:
            continue
        try:
            score = silhouette_score(X, labels, metric="cosine")
        except ValueError:
            continue
        if score > best_score:
            best_score = score
            best_k = k

    km_final = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    dedup_labels = km_final.fit_predict(X)

    # Map cluster assignment back to all (non-deduped) rows
    answer_to_cluster: dict[str, int] = dict(zip(unique_answers, dedup_labels.tolist()))
    wrong_df["_cluster"] = wrong_df["student_answer"].map(answer_to_cluster)

    clusters: list[dict] = []
    centroids = km_final.cluster_centers_

    for cluster_id in range(best_k):
        cluster_rows = wrong_df[wrong_df["_cluster"] == cluster_id]
        count = len(cluster_rows)
        if count == 0:
            continue

        dedup_indices = [i for i, lbl in enumerate(dedup_labels) if lbl == cluster_id]

        # Cosine similarity to centroid → pick most representative answers
        centroid = centroids[cluster_id]
        centroid_norm = centroid / (np.linalg.norm(centroid) + 1e-9)
        cluster_dense = X[dedup_indices].toarray()
        norms = np.linalg.norm(cluster_dense, axis=1, keepdims=True) + 1e-9
        similarities = (cluster_dense / norms).dot(centroid_norm)
        sorted_idx = np.argsort(-similarities)
        example_answers = [
            unique_answers[dedup_indices[i]]
            for i in sorted_idx[:config.CLUSTER_MAX_EXAMPLES]
        ]

        clusters.append({
            "label": None,
            "count": count,
            "percent_of_wrong": round(count / total_wrong * 100, 1),
            "example_answers": example_answers,
        })

    clusters.sort(key=lambda c: c["count"], reverse=True)
    clusters = _label_clusters_with_openai(clusters, question_id)

    _cluster_cache[cache_key] = clusters
    return clusters


# -----------------------------------------------------------------
# Temporal Smoothing (Stub — not actively used)
# -----------------------------------------------------------------

def apply_temporal_smoothing(
    s_raw: float,
    s_previous: Optional[float],
    alpha: float = config.SMOOTHING_ALPHA,
) -> float:
    """
    S_t = (1 - alpha) * S_previous + alpha * S_raw
    Returns s_raw if s_previous is None (first computation).
    """
    if s_previous is None:
        return s_raw
    return (1 - alpha) * s_previous + alpha * s_raw
