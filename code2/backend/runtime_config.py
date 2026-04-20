"""Process-local mutable settings — powers the live Settings view.

Mirrors Streamlit's `st.session_state` flags for things like `cf_enabled`,
`improved_models_enabled`, BKT parameters, auto-refresh, sounds etc. Any POST
to `/api/settings` updates this singleton; analytics caches are flushed so
the next data request picks up the new values.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from threading import Lock
from typing import Any

from learning_dashboard import config


@dataclass
class RuntimeConfig:
    # Runtime-mutable settings, defaults pulled from `config.py`.
    sounds_enabled: bool = True
    auto_refresh: bool = True
    refresh_interval: int = 300
    smoothing_enabled: bool = True
    cf_enabled: bool = False
    cf_threshold: float = 0.7
    struggle_model: str = "baseline"      # "baseline" | "improved"
    difficulty_model: str = "baseline"    # "baseline" | "irt"
    bkt_p_init: float = 0.3
    bkt_p_learn: float = 0.1
    bkt_p_guess: float = 0.2
    bkt_p_slip: float = 0.1
    bkt_mastery_threshold: float = 0.95

    @classmethod
    def defaults(cls) -> "RuntimeConfig":
        return cls(
            sounds_enabled=config.SOUNDS_ENABLED_DEFAULT,
            auto_refresh=config.AUTO_REFRESH_DEFAULT,
            refresh_interval=config.AUTO_REFRESH_INTERVAL_DEFAULT,
            smoothing_enabled=config.SMOOTHING_ENABLED,
            cf_enabled=False,
            cf_threshold=0.7,
            struggle_model="baseline",
            difficulty_model="baseline",
            bkt_p_init=config.BKT_P_INIT,
            bkt_p_learn=config.BKT_P_LEARN,
            bkt_p_guess=config.BKT_P_GUESS,
            bkt_p_slip=config.BKT_P_SLIP,
            bkt_mastery_threshold=config.BKT_MASTERY_THRESHOLD,
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
