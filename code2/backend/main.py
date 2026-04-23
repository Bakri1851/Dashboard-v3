"""FastAPI entry point for the code2 alternative frontend.

Launch with:
    uvicorn backend.main:app --app-dir code2 --port 8000 --reload

`--app-dir code2` puts code2/ on sys.path so both `backend.*` and
`learning_dashboard.*` resolve.
"""
from __future__ import annotations

import asyncio
import logging
import os
import tomllib
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Bootstrap OPENAI_API_KEY from .secrets/secrets.toml at the repo root.
# Lift it into the environment so analytics._get_openai_client() finds it.
# Without this, the backend runs with an empty key, every OpenAI call 401s,
# and every incorrectness score falls back to 0.5 — IRT, improved struggle,
# and measurement confidence all degrade silently.
if not os.environ.get("OPENAI_API_KEY"):
    _secrets_path = Path(__file__).resolve().parents[2] / ".secrets" / "secrets.toml"
    if _secrets_path.is_file():
        try:
            with _secrets_path.open("rb") as _f:
                _secrets = tomllib.load(_f)
            _key = _secrets.get("OPENAI_API_KEY", "")
            if _key:
                os.environ["OPENAI_API_KEY"] = _key
        except (OSError, tomllib.TOMLDecodeError):
            pass

from backend.cache import load_dataframe, load_difficulty_df, load_struggle_df
from backend.routers import analysis, cf, lab, live, meta, models_cmp, question, rag, sessions, settings, student
from learning_dashboard import analytics, lab_state
from learning_dashboard import rag as rag_module
from learning_dashboard.models import bkt as _bkt

logger = logging.getLogger("backend")
# Attach a console handler so prewarm / RAG diagnostics actually print under
# uvicorn (which only configures its own "uvicorn.*" loggers by default).
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(_h)
    logger.setLevel(logging.INFO)
    logger.propagate = False
# Attach a single handler at the learning_dashboard root so every submodule
# (rag, irt, bkt, improved_struggle, ...) logs through uvicorn's stderr with
# the same format. Without this, uvicorn silently drops all INFO logs from
# the learning_dashboard.* namespace because its own config only covers
# "uvicorn.*" loggers.
_ld_logger = logging.getLogger("learning_dashboard")
if not _ld_logger.handlers:
    _ldh = logging.StreamHandler()
    _ldh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%H:%M:%S"))
    _ld_logger.addHandler(_ldh)
    _ld_logger.setLevel(logging.INFO)
    _ld_logger.propagate = False

_openai_key_present = bool(os.environ.get("OPENAI_API_KEY"))
logger.info(
    "OPENAI_API_KEY %s; incorrectness scoring will %s.",
    "loaded" if _openai_key_present else "MISSING",
    "use OpenAI" if _openai_key_present else "fall back to 0.5 for every row",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-warm the analytics cache in the background so the first user
    request doesn't pay the 2-minute cold-start cost. The server starts
    serving immediately; the prewarm runs asynchronously."""

    def _prewarm() -> None:
        import time as _time
        try:
            t0 = _time.monotonic()
            df, err = load_dataframe()
            logger.info("prewarm: loaded %d records in %.1fs (err=%r)", len(df), _time.monotonic() - t0, err)
            # `load_dataframe` respects SCORING_PER_RUN_CAP so the df it just
            # cached has real incorrectness for only the first N uniques and
            # 0.5 for the rest — leaderboards computed on that would diverge
            # from code/'s (which has no cap). Score the remaining uncached
            # feedbacks here with the cap disabled; in-request calls still
            # use the cap, but the module-level _incorrectness_cache is now
            # fully warm, and the cached df's incorrectness column gets
            # updated in place because `df` and `_df_cache["df"][0]` are the
            # same object. Running in the background thread means this ~5–7
            # min OpenAI pass doesn't block concurrent requests.
            if not df.empty and "ai_feedback" in df.columns:
                t_score = _time.monotonic()
                try:
                    df["incorrectness"] = analytics.compute_incorrectness_column(df, max_new_scores=0)
                    logger.info("prewarm: full incorrectness scoring done in %.1fs", _time.monotonic() - t_score)
                except Exception as e:  # noqa: BLE001
                    logger.warning("prewarm: full scoring raised: %s", e)
            if "incorrectness" in df.columns and not df.empty:
                _inc = df["incorrectness"]
                logger.info(
                    "prewarm: incorrectness distribution — rows=%d "
                    "min=%.3f median=%.3f max=%.3f share_at_0.5=%.1f%% "
                    "(near 100%% at 0.5 means OpenAI scoring effectively no-op)",
                    len(_inc),
                    float(_inc.min()), float(_inc.median()), float(_inc.max()),
                    100.0 * float((_inc == 0.5).mean()),
                )
            else:
                logger.warning(
                    "prewarm: df has no 'incorrectness' column after load_dataframe — "
                    "compute_incorrectness_column was bypassed or crashed silently"
                )
            # Fit BKT parameters per skill (module) on the warmed df. The
            # fitted params live in _bkt._BKT_PARAMS_CACHE and are used by
            # compute_all_mastery when the runtime sliders are at their
            # config defaults. Calibrates each skill to its own cohort
            # rather than using literature-averaged priors globally.
            if not df.empty:
                t_bkt = _time.monotonic()
                try:
                    fitted = _bkt.fit_all_skills(df)
                    logger.info(
                        "prewarm: fit BKT params for %d skills in %.1fs",
                        len(fitted), _time.monotonic() - t_bkt,
                    )
                except Exception as e:  # noqa: BLE001
                    logger.warning("prewarm: BKT fit raised: %s", e)

            t1 = _time.monotonic()
            load_struggle_df()
            logger.info("prewarm: struggle ready in %.1fs", _time.monotonic() - t1)
            t2 = _time.monotonic()
            load_difficulty_df()
            logger.info("prewarm: difficulty ready in %.1fs", _time.monotonic() - t2)
            try:
                t3 = _time.monotonic()
                code = lab_state.read_lab_state().get("session_code")
                session_id = str(code) if code else "default"
                result = rag_module.build_rag_collection(df, session_id)
                if result is not None:
                    logger.info("prewarm: RAG collection ready (session=%s) in %.1fs", session_id, _time.monotonic() - t3)
                else:
                    logger.warning("prewarm: RAG build returned None (session=%s) after %.1fs — check earlier log lines for the failure reason", session_id, _time.monotonic() - t3)
            except Exception as e:  # noqa: BLE001
                logger.warning("prewarm: RAG build raised: %s", e)
            logger.info("prewarm: total %.1fs", _time.monotonic() - t0)
        except Exception as e:  # noqa: BLE001
            logger.exception("prewarm failed: %s", e)

    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, _prewarm)
    yield

# Resolve absolute path so the StaticFiles mount works regardless of CWD.
_DIST_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"

app = FastAPI(
    title="Dashboard v3 API",
    description="FastAPI backend for the React frontend. Coexists with the legacy stack in code/ via shared data/lab_session.json.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(live.router, prefix="/api")
app.include_router(student.router, prefix="/api")
app.include_router(question.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(models_cmp.router, prefix="/api")
app.include_router(lab.router, prefix="/api")
app.include_router(rag.router, prefix="/api")
app.include_router(meta.router, prefix="/api")
app.include_router(cf.router, prefix="/api")


@app.get("/api/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}


# Serve the built React SPA when dist/ exists (Phase 6 onward).
# During Phase 2-5 the frontend is served by Vite on :5173 instead.
if _DIST_DIR.exists():
    _MOBILE_HTML = _DIST_DIR / "mobile.html"

    # Clean URL for the mobile lab-assistant portal: /mobile → mobile.html.
    # Registered BEFORE the StaticFiles mount so it wins against the catch-all.
    if _MOBILE_HTML.exists():

        @app.get("/mobile", include_in_schema=False)
        def mobile_entry() -> FileResponse:
            return FileResponse(_MOBILE_HTML)

    app.mount("/", StaticFiles(directory=str(_DIST_DIR), html=True), name="static")
