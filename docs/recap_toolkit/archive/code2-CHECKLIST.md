# code2 — Alternative Frontend Execution Checklist

**If you're reading this cold (context loss / new session):**
1. Read the plan first: `C:\Users\Bakri\.claude\plans\c-users-bakri-downloads-alternative-das-majestic-garden.md`.
2. Read the design reference: `C:\Users\Bakri\Downloads\Alternative Dashboard _standalone_.html`.
3. Read the project `CLAUDE.md` for conventions.
4. Resume at the lowest unchecked box below. Keep this file updated after every completed task.

## Decisions locked in
- **Strategy:** shadow-copy `code/` → `code2/`, never edit `code/`.
- **Frontend stack:** Vite + React + TypeScript (not the single-file bundle).
- **Design goal:** match `Alternative Dashboard _standalone_.html` visually — OKLch palette, Courier Prime, neon dark theme.
- **Backend:** FastAPI, launched with `uvicorn backend.main:app --app-dir code2 --port 8000`.
- **Shared state:** `data/lab_session.json` (file-locked).
- **Ports:** fallback `code/` on 8501/8502, Vite dev 5173, FastAPI 8000.

## Phase 0 — Bootstrap
- [x] `cp -r code code2` (PowerShell: `Copy-Item -Recurse code code2`) — 2026-04-19
- [x] `code2/CHECKLIST.md` created from plan §15 — 2026-04-19
- [~] Legacy app entries at ports 8503/8504 — dropped 2026-04-21; `code2/` no longer ships a legacy UI (see Phase 10). `code/` on 8501 is the canonical legacy fallback.
- [~] Legacy mobile-app entry at port 8504 — dropped 2026-04-21; see Phase 10.
- [~] Cross-copy state sharing verified — superseded by the 3-process model (`code/` × 2 + `code2/` FastAPI × 1) sharing `data/lab_session.json`.

## Phase 1 — Backend skeleton
- [x] Append `fastapi`, `uvicorn[standard]`, `cachetools`, `python-dotenv` to `code2/requirements.txt`; `pip install` — 2026-04-19
- [x] Create `code2/backend/{__init__.py,main.py,cache.py,deps.py,schemas.py}` and `code2/backend/routers/__init__.py` — 2026-04-19
- [x] Apply refactor 7.1 to `code2/learning_dashboard/analytics.py:25` (OpenAI key guard) — 2026-04-19
- [x] Apply refactor 7.2 to `code2/learning_dashboard/data_loader.py:16` (split cached/uncached) — 2026-04-19
- [x] Implement `code2/backend/routers/live.py` with `GET /api/live` — 2026-04-19
- [x] `uvicorn backend.main:app --app-dir code2 --port 8000` starts without errors — 2026-04-19
- [x] `curl localhost:8000/api/live` returns real JSON with non-zero record count (34450 records, 203 students, 119 questions, 4 modules) — 2026-04-19
- [x] Fallback verified: `git status code/` clean + `py_compile code/` passes — 2026-04-19

## Phase 2 — Vite scaffold + design tokens
- [x] `npm create vite@latest frontend -- --template react-ts` — 2026-04-19
- [x] `npm install` + `npm install d3 @types/d3 zustand` — 2026-04-19
- [x] `vite.config.ts` proxy: `/api` → `http://localhost:8000` — 2026-04-19
- [x] Extracted **7 themes** (paper/newsprint/solar/scifi/blueprint/matrix/cyberpunk) from mockup → `src/theme/tokens.ts` + `src/theme/global.css` with per-theme OKLch vars, web fonts (IBM Plex Sans/Serif/Mono, Playfair Display, Fraunces, Space Grotesk, Inconsolata, VT323, Rajdhani, Courier Prime), scanline/grid/paper-grain overlays — 2026-04-19
- [x] `ThemeContext.tsx` with `html.theme-*` class swap + `--accent` hue rotation (5 swatches: indigo/teal/terracotta/forest/crimson) + localStorage persistence — 2026-04-19
- [x] `src/api/{client.ts, hooks.ts}` + `src/state/viewStore.ts` (zustand) + `src/types/api.ts` — 2026-04-19
- [x] Empty shell: `App.tsx` + `Sidebar.tsx` + `TopBar.tsx` + `ErrorBoundary.tsx` — 2026-04-19
- [x] `npx tsc --noEmit` exit 0; `npm run build` → dist/ (201 KB JS, 6 KB CSS gzipped to 63.74 + 1.60 KB) — 2026-04-19
- [ ] `npm run dev` live visual check at :5173 (user to verify palette/fonts match mockup side-by-side)

## Phase 3 — Port views (in order)
For each view: extract from mockup → port to .tsx → implement backing endpoint(s) → wire `useApiData` → screenshot-diff vs mockup.

- [x] InClassView.tsx (+ `GET /api/struggle`, `GET /api/difficulty`, Leaderboard/Stat/Pill/ScoreBar/SectionLabel/Histogram/TimelineChart) — 2026-04-19
- [x] StudentDetail.tsx (+ `GET /api/student/{id}` — components, trajectory sparkline, top questions, recent submissions) — 2026-04-19
- [x] QuestionDetail.tsx (+ `GET /api/question/{id}` — mistake clusters, recent attempts, top strugglers with click-to-drill) — 2026-04-19
- [x] DataAnalysisView.tsx (+ `GET /api/analysis` — module breakdown, 24h timeline, peak hour, avg session length) — 2026-04-19
- [x] SettingsView.tsx (+ `GET /api/settings` — theme/accent picker + read-only backend config snapshot) — 2026-04-19
- [x] PreviousSessions.tsx (+ `GET /api/sessions` — list of saved sessions; save stayed in the legacy stack at this point) — 2026-04-19
- [x] LabAssistantView.tsx (see Phase 4 below) — 2026-04-19
- [x] ComparisonView.tsx (+ `GET /api/models/compare` — baseline vs improved with Spearman ρ + top-10 overlap) — 2026-04-19

### Phase 3 perf fix — 2026-04-19
- [x] Cold-start was 2m09s (fetch + parse 34k records + full struggle/difficulty compute over 203 students × 119 questions)
- [x] Extended analytics cache TTL 10s → 300s (raw df stays at 10s); second+ call = 0.25s
- [x] Added FastAPI `lifespan` prewarm so subsequent server starts hit the 2-min compute at boot, not at the user's first click
- [x] InClassView shows a visible error banner ("Backend unreachable") + loading indicator so empty state is no longer silent

## Phase 4 — Lab state parity
- [x] `code2/backend/routers/lab.py` — 11 endpoints (state, start, end, join, leave, assign, self-claim, mark-helped, unassign, remove-assistant, allow-self-alloc) — 2026-04-19
- [x] `LabAssistantView.tsx` — live roster, dispatch queue (strugglers not yet assigned), session-start prompt, end/self-alloc/remove/release controls, assignments table with Mark Helped + Release, polls `/lab/state` every 3s — 2026-04-19
- [x] End-to-end cycle verified via curl: join (code DLXY6V, name "React Test") → assign fppo2 → mark helped → remove assistant. Assignment state mutates correctly through the `FileLock`-protected `data/lab_session.json`. — 2026-04-19
- [ ] Manual 4-way shared-state check (user to run): join in React → all legacy `code/` apps (`code/app.py:8501`, `code/lab_app.py:8502`) see it in ≤5s
- [ ] Reverse: remove in `code/` on 8501 → React sees them leave within ≤5s
- [ ] Assign via React → `code/lab_app.py` on 8502 (mobile lab assistant app) sees the assignment

## Phase 5 — Sessions + settings + RAG
- [x] `code2/backend/routers/sessions.py` — `GET /api/sessions` wraps `data_loader.load_saved_sessions` (read-only; saving stayed in the legacy stack because `build_session_record_from_state` pulled from the legacy session-state store) — 2026-04-19
- [x] `code2/backend/routers/settings.py` — `GET /api/settings` surfaces current `config.*` weights / thresholds / BKT params (read-only by design — live edits would invalidate the 5-min analytics cache on every request; tune in `config.py` and restart) — 2026-04-19
- [x] `code2/backend/routers/rag.py` — `/api/rag/student/{id}` and `/api/rag/question/{id}` wrap `rag.generate_{assistant,cluster}_suggestions`, both `async` with `asyncio.to_thread` so the first-time ChromaDB build (~5 min: downloads sentence-transformers model, embeds 34k records) doesn't starve the FastAPI event loop — 2026-04-19
- [x] `RagPanel.tsx` used from StudentDetail (section 6) and QuestionDetail (section 3) — renders `accentSoft` card with bullets + cold-start notice — 2026-04-19
- [x] PreviousSessions view functional against `/api/sessions` — 2026-04-19
- [x] Settings view renders theme picker + read-only backend config snapshot — 2026-04-19

## Phase 6 — Build + polish
- [x] `ErrorBoundary.tsx` wraps all views (`src/components/layout/ErrorBoundary.tsx`) — Phase 2
- [x] Loading skeletons on every `useApiData` (per-view "loading…" + error banner) — Phase 3
- [x] `cd code2/frontend && npm run build` → `dist/` populated (256 KB JS / 74 KB gzipped)
- [x] FastAPI's conditional `StaticFiles` mount picks up `dist/` — visit `localhost:8000/` shows the built app — Phase 1
- [x] FastAPI `/docs` accessible (Swagger UI) for defence (automatic with FastAPI; all endpoints grouped by tag)
- [x] Favicon added — paper-cream/indigo/terracotta editorial mark (`code2/frontend/public/favicon.svg`) — 2026-04-19
- [x] Theme swatches change `--accent` via React context (no page reload) — Phase 2

## Phase 7 — Documentation sync
- [x] `docs/obsidian-vault/My Notes/Code/Lab App/Operations/Setup and Runbook.md` — appended "Alternative frontend (`code2/`) — React + FastAPI" section with prereqs, install, 5-process run commands, performance notes, repo layout — 2026-04-19
- [x] `docs/obsidian-vault/My Notes/Thesis/Evidence Bank.md` — appended "Alternative React (Vite) frontend" implementation-evidence table + screenshot-capture plan — 2026-04-19
- [x] `docs/obsidian-vault/My Notes/Thesis/Report Sync.md` — appended Ch4 Implementation + Ch6 §6.3 Future Work notes for the alt frontend, with scope guard (no new citations) — 2026-04-19
- [x] `docs/obsidian-vault/My Notes/Thesis/Figures and Tables.md` — appended "V3 architecture diagram" + 7-theme gallery + per-view screenshot list + 2 new tables — 2026-04-19
- [x] `docs/obsidian-vault/My Notes/Thesis/Full Roadmap.md` — inserted 8-phase block pointing at the plan file + checklist — 2026-04-19
- [x] `docs/obsidian-vault/My Notes/Thesis/Weekly Plan.md` — reflected compressed one-session delivery of phases 0–6 — 2026-04-19
- [x] `docs/recap_toolkit/dashboard_v3_toolkit.html` — Overview (new `code2/` card), Operations (full alt-frontend Run section), Plan (new "Alternative React (Vite) frontend track" section) — 2026-04-19
- [x] Graphify regenerated — jumped from 340 / 489 / 21 to **1742 nodes / 4628 edges / 61 communities** (captures all of `code2/`) — 2026-04-19

## Phase 9 — Functional parity with the legacy stack (gap fill)

**Priority 0 — user-reported bugs — 2026-04-19**
- [x] `Sidebar.tsx` drives session card from `/api/lab/state`; hidden when `session_active === false`
- [x] Sidebar Start / End session buttons (POST `/api/lab/start` / `/api/lab/end`)

**Priority 1A — sidebar time filter — 2026-04-19**
- [x] `src/state/filterStore.ts` (zustand) — 8 presets + custom date/time + academic-week
- [x] Sidebar panel: All Time / Live Session / Today / Past Hour / Past 24H / Current Week / Last Week / Custom + Custom form
- [x] Backend `filter_df(df, from_, to_)` helper in `cache.py`; `TimeWindow` FastAPI dep in `deps.py`
- [x] `/api/live`, `/api/struggle`, `/api/difficulty`, `/api/student/{id}`, `/api/question/{id}`, `/api/analysis`, `/api/models/compare`, `/api/cf`, `/api/student/{id}/similar` all accept `?from` / `?to`
- [x] `backend/cache.py` TTLCache maxsize 8, keyed by `(from_, to_)`
- [x] Academic-week picker pulls from `/api/meta/academic-periods` (37 periods from `learning_dashboard.academic_calendar`)
- [x] "Live Session" preset auto-filters `session_start → now`
- [x] `useApiData` extended to accept a `query` string; `useFilterQuery()` helper ties filter+lab+periods into a single query
- [x] **Smoke test**: no filter → 34,475 records; narrow 6-hour window → 7 records

**Priority 1B — settings persistence — 2026-04-19**
- [x] `backend/runtime_config.py` singleton — sounds, auto_refresh, refresh_interval, smoothing, cf_enabled, cf_threshold, struggle/difficulty_model, BKT p_* (with thread-safe update/reset)
- [x] `POST /api/settings` + `POST /api/settings/reset` (both invalidate analytics caches)
- [x] `src/api/useSettings.ts` hook (no separate zustand — useApiData + refetch)
- [x] `SettingsView.tsx` live toggles / sliders / dropdowns (matches the legacy control inventory)
- [x] **Smoke test**: POST `{sounds_enabled: false, struggle_model: "improved"}` → GET reflects change → /reset → GET reflects defaults

**Priority 1C — Data Analysis 6-chart selector — 2026-04-19**
- [x] `/api/analysis` now returns all 6 shapes in one payload: module_breakdown / top_questions / user_activity / timeline_24h / activity_by_week / (module_breakdown again for students-per-module reuse)
- [x] `DataAnalysisView.tsx` pill selector + 5 new variants (Top Questions table, User Activity table, Students-per-Module HBars, Activity-by-Week Heatmap reusing new `Heatmap.tsx`)
- [x] `components/charts/Heatmap.tsx` — generic row × col heatmap with OKLch accent intensity
- [x] Academic-calendar integration: backend iterates timestamps through `academic_calendar.get_academic_period`

**Priority 1D — Previous Sessions CRUD — 2026-04-19**
- [x] `POST /api/sessions/save` — retroactive save from the frontend's current filter window
- [x] `DELETE /api/sessions/{id}` — wraps `data_loader.delete_session_record`
- [x] `PreviousSessions.tsx` — Save dialog (name + from + to), Load (applies as filter + switches to InClass), Delete (with confirm)
- [~] Academic-period filter on the list — deferred (sidebar filter already supports it via academic-week picker, so list doesn't duplicate)

**Priority 1E — CF panels — 2026-04-19**
- [x] `GET /api/cf` — wraps `analytics.compute_cf_struggle_scores(struggle_df, threshold, k)`; returns elevated students + diagnostics
- [x] `GET /api/student/{id}/similar` — top-5 cosine-sim neighbours on CF_FEATURES (`n_hat`, `t_hat`, `i_norm|i_hat`, `A_norm|A_raw`, `d_hat` with graceful fallback)
- [x] InClassView CF panel (gated on `settings.runtime.cf_enabled`) — 3 metric cards + elevated-students table with click-to-drill
- [x] StudentDetail "Similar Students" grid — 5 cards with cosine-sim badges, click-to-drill

**Priority 2 — polish — 2026-04-19**
- [x] `src/sound.ts` — 8 Web Audio functions mirroring the legacy sound helper (sessionStart/End, selection, navigation, refresh, assistantJoin, assignmentReceived, highStruggle); gated via `viewStore.soundsEnabled` which is mirrored from `settings.runtime.sounds_enabled`
- [~] QuestionDetail `ConfidenceBadge` — deferred (low visual-impact; measurement confidence already surfaced indirectly via the struggle-score ScoreBar colour)
- [~] ComparisonView 4×4 confusion matrix — deferred (Spearman ρ + top-10 overlap already communicate concordance; matrix is a Phase 10 polish item)
- [~] InClassView secondary module pills + formula panel — deferred (module filter is covered by the global time-filter; formula panel available in Settings read-only reference)

**Verification — 2026-04-19**
- [x] Typecheck clean (`npx tsc --noEmit` exit 0) across all edits
- [x] Vite build clean — 283 KB JS / 81 KB gzipped
- [x] Backend `py_compile` clean for all new + edited files
- [x] `git status code/` clean, `py_compile code/` clean — fallback intact
- [x] Filter round-trip: `?from=…&to=…` drops record count from 34,475 → 7 as expected
- [x] Settings round-trip: POST + GET + reset all reflect changes; analytics cache invalidated
- [x] Meta endpoints: `/api/meta/filter-presets` → 8 presets; `/api/meta/academic-periods` → 37 weeks

## Phase 8 — Defence rehearsal (run AFTER Phase 9)
- [ ] All 3 processes started (`code/` ×2 legacy, `code2/` ×1 FastAPI+SPA) — was 5 before Phase 10 cleanup
- [ ] End-to-end smoke test per plan §12
- [ ] Thesis screenshots captured (8 views, 3 states per view)
- [ ] Demo script rehearsed

## Phase 10 — Legacy UI removal from code2/ — 2026-04-21
- [x] Deleted `code2/app.py`, `code2/lab_app.py`, `code2/learning_dashboard/instructor_app.py`, `code2/learning_dashboard/assistant_app.py`, `code2/learning_dashboard/sound.py`, `code2/learning_dashboard/ui/` — the React SPA covers every view these rendered.
- [x] Stripped the legacy framework import + secrets fallback from `analytics.py` — OpenAI key now sourced only from `OPENAI_API_KEY`, which `backend/main.py` lifts out of `.secrets/secrets.toml` at boot.
- [x] Stripped the legacy cache decorator and the legacy-only `fetch_raw_data()` wrapper from `data_loader.py`; `fetch_raw_data_uncached()` stays as the single entry point (caching is handled by `backend/cache.py`).
- [x] Removed legacy-only helpers from `data_loader.py`: `load_data()` (used a session-state short-circuit), `build_session_record_from_state()`, `apply_saved_session_to_state()`, `build_retroactive_session_record()` — the FastAPI `sessions.py` router builds its record dict inline from POST args.
- [x] Replaced the one legacy warning call in `_read_saved_sessions_payload` with a `logger.warning(...)`.
- [x] Dropped the legacy-framework packages (plus `plotly`, only consumed by the deleted UI; React uses D3) from `code2/requirements.txt`.
- [x] Updated `code2/backend/routers/sessions.py` docstring to drop the stale reference to `build_session_record_from_state`.
- [x] Updated project-root `CLAUDE.md` — "Two-app system" section now describes the two stacks (`code/` legacy vs `code2/` React+FastAPI) and the shared-state contract.
- [x] Verification: `python -m py_compile` clean across `code2/backend/` + `code2/learning_dashboard/`; import check loads every backend router without error; `code/` untouched and remains the legacy reference.

## Phase 11 — Final scrub — 2026-04-23
- [x] Deleted orphaned legacy source files: `code2/app.py`, `code2/lab_app.py`, `code2/learning_dashboard/{instructor_app,assistant_app,sound}.py`, `code2/learning_dashboard/ui/` (already done in Phase 10, verified clean).
- [x] Scrubbed cosmetic legacy-framework references from all `.py` / `.ts` / `.tsx` files in `code2/` and from this checklist.
- [x] Verified the legacy-framework keyword no longer appears in any `.py` / `.ts` / `.tsx` file under `code2/`.

## Running notes (append below as you go)

_Use this section to log surprises, blockers, deviations from the plan, and decisions. Keep entries dated._

- **2026-04-19** — Phase 0 bootstrap: `cp -r code code2` completed; `diff -rq code code2` shows zero differences (verbatim copy). Checklist created from plan §15.
- **2026-04-19** — Phase 1: FastAPI scaffold built under `code2/backend/`. Two `learning_dashboard/` refactors applied (analytics.py OpenAI key guard, data_loader.py cached/uncached split). `data_loader.load_data()` used a legacy session-state in-process cache shortcut, so FastAPI path goes through a new `backend.cache.load_dataframe()` that replicates fetch→parse→normalise without any legacy-framework dependency. `/api/live` returns live JSON. `code/` integrity confirmed via `git status` (clean) and `py_compile` (passes).
- **2026-04-19** — Phase 2: Mockup decompressed via `code2/frontend/scripts/extract_mockup.py` — 72 bundle assets written to `code2/frontend/mockup-extracted/`. Key refs for Phase 3: InClassView lives in `86acc801-a38d-488b-8cff-b07aa3e5c264.js`, detail screens (StudentDetail/QuestionDetail/LabAssistant/Settings/ModelComparison/PreviousSessions) in `65392968-07cb-4c17-b0ff-f452b5adb468.js`, main CSS in `50ccb9a4-bb20-4ef0-828c-efebfe1d8a03.css`. **Surprise**: mockup has **7 themes** (not 5 as earlier assumed) and default is `paper` (light cream), not the dark neon I initially expected. All 7 ported verbatim to `src/theme/global.css`. Vite build clean.
- **2026-04-19** — Phase 3: all 7 non-lab views ported. Cold start exposed a 2-minute analytics compute over 34k records / 203 students — addressed via 5-min analytics cache (on top of existing 10s raw-data cache) and a FastAPI `lifespan` prewarm hook that fires at server boot. User saw silent-empty leaderboards during the cold window — now shows an explicit "Backend unreachable" banner + loading indicator. QuestionDetail spacing tightened into a consistent marginBottom rhythm (was cramped around the big score number); added a new "Top Strugglers on this Question" section with click-to-drill navigation into StudentDetail.
- **2026-04-19** — Phase 3 overflow fix: at default 100% zoom the page leaked horizontally. Root cause: default flex-item `min-width: auto` and `grid-template-columns: 1fr` both refuse to shrink below content width. Fixed by adding `minWidth: 0` on the `<main>` flex child and converting every content grid to `minmax(0, 1fr)` so columns compress instead of pushing the viewport wider.
- **2026-04-19** — Phase 4: `/api/lab/*` router (11 endpoints) delegates to `learning_dashboard.lab_state.*` which uses `FileLock` on `data/lab_session.json` — so FastAPI coordinates with the two `code/` apps automatically. LabAssistantView polls `/lab/state` every 3s, auto-dispatches to the first idle assistant, and supports release / mark-helped / remove / end-session / self-allocation toggle.
- **2026-04-19** — Phase 5: RAG wired but first call found to block the event loop (first-time ChromaDB build + sentence-transformers model download = minutes). Rewrote handlers as `async def` + `asyncio.to_thread(...)` so the blocking work runs on a worker and /api/live, /api/lab/state etc stay responsive. RagPanel in both detail views shows a cold-start message while the Chroma collection builds; subsequent calls (same session_id) return cached bullets instantly. Also replaced the Vite default favicon with a thematic editorial mark (paper cream + indigo + terracotta stripes).
- **2026-04-19** — Phase 6 closed out with a single new item (favicon). All other items ticked by earlier phases (ErrorBoundary in Phase 2, loading skeletons per-view in Phase 3, `dist/` served by FastAPI since Phase 1, `/docs` automatic with FastAPI, theme-swatch context-swap in Phase 2).
- **2026-04-19** — Phase 7: Vault + toolkit synced. Graphify regen needed `PYTHONIOENCODING=utf-8 PYTHONUTF8=1` on Windows because the default cp1252 codec couldn't handle the arrow glyph inside the docstrings — logged here so the next regen remembers.
- **2026-04-19** — Phase 9: full feature-gap audit vs the legacy instructor app done (was ~50% feature-complete). Shipped Priority 0 (session card from `/api/lab/state`, Start/End in sidebar), 1A (time filter with 8 presets + academic-week + backend `TimeWindow` dep + window-keyed analytics cache), 1B (runtime_config singleton + live Settings view), 1C (6-chart Data Analysis with new Heatmap), 1D (Previous Sessions save + delete + load-as-filter), 1E (CF diagnostic panel in InClassView + similar-students grid in StudentDetail), and Priority 2 sound effects (8 Web Audio functions gated on runtime sounds toggle). Deferred: ConfidenceBadge, ComparisonView confusion matrix, secondary module filter — low-impact polish for Phase 10 if defence schedule allows. Graphify jumped 1742 → 1815 nodes to cover the new backend modules.
