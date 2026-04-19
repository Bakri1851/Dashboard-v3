"""FastAPI entry point for the code2 alternative frontend.

Launch with:
    uvicorn backend.main:app --app-dir code2 --port 8000 --reload

`--app-dir code2` puts code2/ on sys.path so both `backend.*` and
`learning_dashboard.*` resolve.
"""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.cache import load_dataframe, load_difficulty_df, load_struggle_df
from backend.routers import analysis, lab, live, models_cmp, question, rag, sessions, settings, student

logger = logging.getLogger("backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-warm the analytics cache in the background so the first user
    request doesn't pay the 2-minute cold-start cost. The server starts
    serving immediately; the prewarm runs asynchronously."""

    def _prewarm() -> None:
        try:
            df, err = load_dataframe()
            logger.info("prewarm: loaded %d records (err=%r)", len(df), err)
            load_struggle_df()
            logger.info("prewarm: struggle ready")
            load_difficulty_df()
            logger.info("prewarm: difficulty ready")
        except Exception as e:  # noqa: BLE001
            logger.exception("prewarm failed: %s", e)

    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, _prewarm)
    yield

# Resolve absolute path so the StaticFiles mount works regardless of CWD.
_DIST_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"

app = FastAPI(
    title="Dashboard v3 API",
    description="Alternative-frontend backend. Streamlit apps in code/ and code2/ are unaffected.",
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


@app.get("/api/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}


# Serve the built React SPA when dist/ exists (Phase 6 onward).
# During Phase 2-5 the frontend is served by Vite on :5173 instead.
if _DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=str(_DIST_DIR), html=True), name="static")
