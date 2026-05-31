"""Process-local mutable settings — powers the live Settings view.

Thread-safe singleton holding every user-changeable flag: `cf_enabled`,
`struggle_model`, `difficulty_model`, BKT parameters, auto-refresh interval,
sounds etc. Any POST to `/api/settings` updates this singleton; analytics
caches are flushed so the next data request picks up the new values.

The scoring path uses the empirically-trained v2 weights and Optuna-tuned
hyperparameters unconditionally — these are the deployed system. The scalar
sliders are seeded at boot from `data/eval/optimised_hyperparams_v2.json`
(cf_threshold is adopted from the Optuna-tuned value; shrinkage_k is held at its
`config.py` default, the Optuna tuning of K being within noise) and remain
user-adjustable; the trained composite weights are loaded directly by
`cache.py` from `data/eval/optimised_*_weights_v2.json`. The hand-set v1
weights survive only as `config.py` constants for the offline evaluation
comparison; they are no longer a runtime-selectable option.
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field, replace
from threading import Lock
from typing import Any

from backend import config

logger = logging.getLogger(__name__)


def _load_optimised_hyperparams() -> dict[str, Any] | None:
    """Read data/eval/optimised_hyperparams_v2.json. Returns a flat dict of the
    scalar overrides (cf_threshold, bkt_p_init, ..., shrinkage_k, etc.) or
    None if the file is missing/malformed.

    Called by `defaults()` at process boot. `defaults()` adopts `cf_threshold`
    (and the BKT priors, held at their config defaults) from these v2 values but
    retains `shrinkage_k` at the `config.py` default — the Optuna tuning of K was
    within noise. The sliders remain user-adjustable after boot.
    """
    path = config.OPTIMISED_HYPERPARAMS_V2_PATH
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("optimised hyperparams v2 load failed: %s", exc)
        return None
    if payload.get("status") == "DEFERRED":
        # Stub file — no real grid-search results yet. Don't override.
        return None
    overrides = payload.get("best_values") or payload.get("optimal") or payload.get("values")
    if not isinstance(overrides, dict):
        return None
    # Coerce to a flat dict of known keys, ignoring unknowns.
    allowed = {"cf_threshold", "bkt_p_init", "bkt_p_learn", "bkt_p_guess",
               "bkt_p_slip", "bkt_mastery_threshold", "shrinkage_k"}
    return {k: v for k, v in overrides.items() if k in allowed}


@dataclass
class RuntimeConfig:
    # Runtime-mutable settings, defaults pulled from `config.py`.
    sounds_enabled: bool = True
    auto_refresh: bool = True
    refresh_interval: int = 60
    cf_enabled: bool = False
    cf_threshold: float = 0.7
    struggle_model: str = "baseline"      # "baseline" | "improved"
    difficulty_model: str = "baseline"    # "baseline" | "irt"
    bkt_p_init: float = 0.3
    bkt_p_learn: float = 0.1
    bkt_p_guess: float = 0.2
    bkt_p_slip: float = 0.1
    bkt_mastery_threshold: float = 0.95
    # Shrinkage K — promoted from a hardcoded constant so it can be seeded
    # from the Optuna-tuned v2 value at boot. Stays user-adjustable.
    shrinkage_k: int = 5

    @classmethod
    def defaults(cls) -> "RuntimeConfig":
        # Seed the scalar sliders from the Optuna-tuned v2 hyperparameters on
        # disk so a fresh boot matches the deployed (trained) configuration.
        # Falls back to config.py defaults if the v2 JSON is missing.
        scalars = {
            "cf_threshold": 0.7,
            "bkt_p_init": config.BKT_P_INIT,
            "bkt_p_learn": config.BKT_P_LEARN,
            "bkt_p_guess": config.BKT_P_GUESS,
            "bkt_p_slip": config.BKT_P_SLIP,
            "bkt_mastery_threshold": config.BKT_MASTERY_THRESHOLD,
            "shrinkage_k": config.SHRINKAGE_K_DEFAULT,
        }
        v2_overrides = _load_optimised_hyperparams()
        if v2_overrides:
            # K is retained at its hand-set default: the Optuna tuning of K was
            # within per-fold noise (see Ch5) and the design relies on shrinkage,
            # so only cf_threshold (and the BKT priors) seed from the v2 study.
            v2_overrides.pop("shrinkage_k", None)
            scalars.update(v2_overrides)
        return cls(
            sounds_enabled=config.SOUNDS_ENABLED_DEFAULT,
            auto_refresh=config.AUTO_REFRESH_DEFAULT,
            refresh_interval=config.AUTO_REFRESH_INTERVAL_DEFAULT,
            cf_enabled=False,
            struggle_model="baseline",
            difficulty_model="baseline",
            **scalars,
        )

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


_lock = Lock()
_current: RuntimeConfig = RuntimeConfig.defaults()


def get() -> RuntimeConfig:
    with _lock:
        return replace(_current)  # return a copy so callers can't mutate directly


def update(partial: dict[str, Any]) -> RuntimeConfig:
    """Merge `partial` into the live config. Unknown keys are ignored."""
    global _current
    with _lock:
        current_dict = asdict(_current)
        allowed = set(current_dict.keys())
        for k, v in partial.items():
            if k in allowed:
                current_dict[k] = v
        _current = RuntimeConfig(**current_dict)
        return replace(_current)


def reset() -> RuntimeConfig:
    global _current
    with _lock:
        _current = RuntimeConfig.defaults()
        return replace(_current)
