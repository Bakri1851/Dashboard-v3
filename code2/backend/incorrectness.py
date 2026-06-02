# incorrectness.py — OpenAI batched incorrectness scoring + persistent cache + feedback confidence.

import json
import logging
import re
import threading
import time
from typing import Optional

import numpy as np
import pandas as pd

from . import config, paths
from .analytics import _get_openai_client

logger = logging.getLogger(__name__)


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
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z0-9]*\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    candidates = [cleaned]
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

    uncached_all = [t for t in unique_feedbacks if t and t not in _incorrectness_cache]
    n_empty = sum(1 for t in unique_feedbacks if not t)

    if not score_new:
        result = feedbacks.map(lambda t: _incorrectness_cache.get(t, 0.5))
        logger.info(
            "compute_incorrectness_column: score_new=False lookup-only — "
            "total_rows=%d unique_feedbacks=%d already_cached=%d "
            "deferred=%d empty_feedbacks=%d",
            len(df), len(unique_feedbacks), already_cached,
            len(uncached_all), n_empty,
        )
        return result

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
