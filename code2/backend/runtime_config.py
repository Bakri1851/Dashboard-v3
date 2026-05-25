"""Process-local mutable settings — powers the live Settings view.

Thread-safe singleton holding every user-changeable flag: `cf_enabled`,
`struggle_model`, `difficulty_model`, BKT parameters, auto-refresh interval,
sounds etc. Any POST to `/api/settings` updates this singleton; analytics
caches are flushed so the next data request picks up the new values.

Phase 5 added four `*_version` flags ("v1" | "v2") that gate whether the
dashboard uses hand-set v1 weights or empirically-optimised v2 weights from
`data/eval/optimised_*_weights_v2.json`. When `hyperparams_version` flips
to "v2" the relevant scalar sliders (cf_threshold, BKT priors, mastery
threshold, shrinkage_k) get repopulated from
`data/eval/optimised_hyperparams_v2.json`; flipping back to "v1" resets
them to `config.py` defaults.
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field, replace
from threading import Lock
from typing import Any

from backend import config

logger = logging.getLogger(__name__)


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
    # Phase 5: V2 toggles. All default "v1" so the dashboard behaves identically
    # to before this phase unless the user explicitly opts in via Settings.
    struggle_weights_version: str = "v1"           # "v1" | "v2"
    difficulty_weights_version: str = "v1"         # "v1" | "v2"
    improved_struggle_weights_version: str = "v1"  # "v1" | "v2"
    hyperparams_version: str = "v1"                # "v1" | "v2"
    # Promoted from a hardcoded constant so the hyperparams v2 toggle can
    # override it. Default stays at config.SHRINKAGE_K_DEFAULT.
    shrinkage_k: int = 5

    @classmethod
    def defaults(cls) -> "RuntimeConfig":
        return cls(
            sounds_enabled=config.SOUNDS_ENABLED_DEFAULT,
            auto_refresh=config.AUTO_REFRESH_DEFAULT,
            refresh_interval=config.AUTO_REFRESH_INTERVAL_DEFAULT,
            cf_enabled=False,
            cf_threshold=0.7,
            struggle_model="baseline",
            difficulty_model="baseline",
            bkt_p_init=config.BKT_P_INIT,
            bkt_p_learn=config.BKT_P_LEARN,
            bkt_p_guess=config.BKT_P_GUESS,
            bkt_p_slip=config.BKT_P_SLIP,
            bkt_mastery_threshold=config.BKT_MASTERY_THRESHOLD,
            struggle_weights_version="v1",
            difficulty_weights_version="v1",
            improved_struggle_weights_version="v1",
            hyperparams_version="v1",
            shrinkage_k=config.SHRINKAGE_K_DEFAULT,
        )

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


_lock = Lock()
_current: RuntimeConfig = RuntimeConfig.defaults()


def _load_optimised_hyperparams() -> dict[str, Any] | None:
    """Read data/eval/optimised_hyperparams_v2.json. Returns a flat dict of the
    scalar overrides (cf_threshold, bkt_p_init, ..., shrinkage_k, etc.) or
    None if the file is missing/malformed.

    Used by `update()` when the user POSTs `hyperparams_version=v2` — we
    repopulate the sliders with the grid-searched optimal values so they
    take effect AND so the user can see what changed in the UI. Switching
    back to "v1" restores the `config.py` defaults.
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


def _v1_hyperparam_defaults() -> dict[str, Any]:
    """The `config.py` defaults — what to restore when toggling back to v1."""
    return {
        "cf_threshold": 0.7,
        "bkt_p_init": config.BKT_P_INIT,
        "bkt_p_learn": config.BKT_P_LEARN,
        "bkt_p_guess": config.BKT_P_GUESS,
        "bkt_p_slip": config.BKT_P_SLIP,
        "bkt_mastery_threshold": config.BKT_MASTERY_THRESHOLD,
        "shrinkage_k": config.SHRINKAGE_K_DEFAULT,
    }


def get() -> RuntimeConfig:
    with _lock:
        return replace(_current)  # return a copy so callers can't mutate directly


def update(partial: dict[str, Any]) -> RuntimeConfig:
    """Merge `partial` into the live config. Unknown keys are ignored.

    Special handling for `hyperparams_version`: when it flips to "v2", load
    the grid-searched optimal hyperparams from disk and overwrite the
    scalar sliders in the SAME update. When it flips to "v1", restore the
    `config.py` defaults. Either side-effect runs BEFORE the user's
    explicit slider overrides so they always win.
    """
    global _current
    with _lock:
        current_dict = asdict(_current)
        allowed = set(current_dict.keys())

        # Detect a hyperparams_version flip and apply its side-effects first,
        # so any user-specified slider override in this same `partial`
        # (e.g. {"hyperparams_version": "v2", "cf_threshold": 0.65}) wins.
        new_hp_version = partial.get("hyperparams_version")
        old_hp_version = current_dict.get("hyperparams_version")
        if new_hp_version in ("v1", "v2") and new_hp_version != old_hp_version:
            if new_hp_version == "v2":
                overrides = _load_optimised_hyperparams()
                if overrides:
                    current_dict.update(overrides)
                else:
                    logger.warning(
                        "hyperparams_version=v2 requested but optimised JSON "
                        "missing/malformed/deferred; sliders unchanged"
                    )
            else:  # v1
                current_dict.update(_v1_hyperparam_defaults())

        # Apply the user-specified updates last (they win over the auto-load).
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
