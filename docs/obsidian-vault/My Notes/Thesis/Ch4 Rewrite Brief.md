# Ch4 Implementation — Rewrite Brief

Single-file "what to write" brief for [Full Roadmap](Full%20Roadmap.md) Step 5. Target file: [`Report/main-sections/implementation.tex`](../../../../Report/main-sections/implementation.tex). Companion plan: `C:\Users\Bakri\.claude\plans\lets-continue-on-step-starry-lamport.md`.

This brief is **structured guidance, not prose**. The user authors the chapter directly into LaTeX; this file says what each subsection should contain, which constants to name, which figures to slot, which `\cite{}` keys to drop. No file:line code anchors here — those land in Step 11 (Appendix A).

Cross-references:
- Voice and tone reference: [previous-works/F221611.pdf](../../../../previous-works/F221611.pdf) §5 (own prior submission, mark 72) + [`Report/main-sections/design-and-architecture.tex`](../../../../Report/main-sections/design-and-architecture.tex) (Ch3, just rewritten — sets the formal register for this thesis).
- Source of truth for constants: [`code/learning_dashboard/config.py`](../../../../code/learning_dashboard/config.py).
- Marker feedback on prior submission: [previous-works/feedback for F221611.pdf](../../../../previous-works/feedback%20for%20F221611.pdf). The lessons are folded into Parts A, B, and G of this brief.

---

## Part A — Chapter structure

Keep the existing skeleton in `implementation.tex` (it's close to right); fix the contradictory intro, replace the technology table, and add three new subsections. Final outline:

```
4. Implementation
  4.1  Implementation Overview
  4.2  Technology Stack
  4.3  System Structure
       4.3.1  V1 — Instructor Process (Streamlit)
       4.3.2  V1 — Assistant Process (Streamlit, mobile)
       4.3.3  V2 — React + FastAPI                           [NEW]
       4.3.4  Shared Runtime State (lab_session.json + filelock)
       4.3.5  Deferred-Actions Pattern                       [NEW]
  4.4  Data Pipeline
       4.4.1  Endpoint Retrieval and Parsing
       4.4.2  Data Normalisation and Structuring
       4.4.3  Caching Strategy                               [NEW]
  4.5  Session Management
       4.5.1  Live Session Lifecycle
       4.5.2  Saved Session History and Restoration
  4.6  Analytics Implementation
       4.6.1  Incorrectness Scoring (OpenAI, batched, cached)
       4.6.2  Baseline Student Struggle Model (7 signals)
       4.6.3  Baseline Question Difficulty Model (5 signals)
       4.6.4  Collaborative Filtering
       4.6.5  Mistake Clustering
  4.7  Advanced Model Implementation
       4.7.1  Measurement Confidence
       4.7.2  Item Response Theory (IRT) Difficulty
       4.7.3  Bayesian Knowledge Tracing (BKT) Mastery
       4.7.4  Improved Struggle Model
  4.8  RAG Suggested Feedback
       4.8.1  Hybrid Two-Layer Architecture
       4.8.2  Embedding Model (all-MiniLM-L6-v2)
       4.8.3  Generation and Prompting (gpt-4o-mini, JSON)
       4.8.4  Suggestion Caching
       4.8.5  Graceful Degradation and Privacy
  4.9  Instructor System Views
       4.9.0  (preamble — comparison table)
       4.9.1  In-Class View
       4.9.2  Student Detail View
       4.9.3  Question Detail View
       4.9.4  Data Analysis View
       4.9.5  Model Comparison View
       4.9.6  Settings View                       (sound-effects sub-paragraph folded in here)
       4.9.7  Previous Sessions View
  4.10 Lab Assistant System
       4.10.1 Session Join Flow
       4.10.2 Waiting and Assignment States
       4.10.3 Live Assistant Allocation and Mark-Helped
  4.11 Problems Encountered and Solutions
```

### V1 → V2 handling

The system has two deployed versions: **V1** (Streamlit, `code/`) and **V2** (React + FastAPI, `code2/`). Both are production-quality; V1 is not a prototype. V2 evolved from V1 to address specific limitations encountered after V1 reached feature parity (see §4.3.3 for the motivation). The shared analytical core (analytics, models, RAG, data pipeline) is described **once** in §4.4–§4.8; both versions consume the same Python modules so the description is identical. The two versions diverge only in:

- **§4.3** — System Structure splits §4.3.1 / §4.3.2 (V1) from §4.3.3 (V2).
- **§4.9.0** — preamble paragraph + `tab:views-comparison` table mapping each instructor view across V1 and V2 on three columns: parity status, presentation differences, performance notes.
- **§4.8.1** — one paragraph noting RAG calls are wrapped in `async` + `asyncio.to_thread` in V2's FastAPI router so the first-time ChromaDB build does not block the event loop.

### Comparison framing (response to Marker-2 feedback)

The prior submission lost marks for "no comparison study". Inside Ch4, the comparison angle lands on the internal **V1 → V2 evolution** narrative. §4.3.3 opens with a one-paragraph **"Why V2?"** framing: V2 was built after V1 reached feature-completion to address presentation-layer limitations (Streamlit's single-thread event loop, weak theming, no native async, no SPA navigation) while keeping the analytical core unchanged. Comparison dimensions in the writing: motivating limitations of V1, architectural choices in V2, feature parity (and where V2 went beyond V1), runtime cost, accessibility (V2's seven-theme system). The `tab:views-comparison` table in §4.9.0 turns this into an evaluative artefact at the view level.

**Important — V1 is not a prototype.** Avoid any language that implies V1 was scaffolding or proof-of-concept. V1 is a deployed, full-featured system; both V1 and V2 are demonstrable and both consume the same `learning_dashboard/` core. V2 is an evolution, not a replacement. CLAUDE.md notes V1 remains the canonical defence-demo fallback; the thesis treats them as siblings, not as a draft and a final.

External-platform comparison (other learning-analytics dashboards) is Ch2 territory and is flagged for Step 4, not Ch4.

---

## Part B — Per-subsection blocks

Each block uses the same template. **Maths recap** is required in every §4.6.x and §4.7.x subsection; everywhere else it is optional. Length targets are paragraph counts, not word counts.

---

### §4.1  Implementation Overview *(replaces lines 11–18; introduces V1 / V2 framing cleanly, kills the old "Version 1 / proof of concept" prototype framing)*

**Cover:**
- The deployed system has **two versions**, both production-quality: **V1** (`code/`) is the Streamlit implementation — instructor app on port 8501, mobile lab-assistant app on 8502. **V2** (`code2/`) is the evolved implementation — a single FastAPI process on port 8000 serving both the `/api` routes and a built React SPA from `dist/`, with a Vite dev server on 5173 for frontend development.
- V2 is **not a rewrite**; it is an evolution of V1's presentation layer that retains V1's full functionality and adds new affordances (seven runtime themes, accent picker, SessionProgression replay view, asynchronous request handling). The motivation for V2 is given in §4.3.3.
- Both versions share a single analytical core (`learning_dashboard/`) and a single file-locked runtime state (`data/lab_session.json`), coordinated through `filelock`. A session started in V1 is visible in V2 within ~5 s, and vice versa.
- The chapter is organised top-down: technology choices and system structure (§4.2–§4.3), how data enters and is held (§4.4–§4.5), how it is scored and modelled (§4.6–§4.7), the feedback layer that consumes those scores (§4.8), the user-facing views (§4.9–§4.10), and the problems hit during implementation (§4.11). Because the analytical core is shared, §4.4–§4.8 describe V1 and V2 simultaneously; only §4.3 and §4.9 split the two versions explicitly.

**Voice/length:** 2 short paragraphs, ~6 sentences total. Present tense, declarative. Lead with "two versions"; emphasise that both are deployed and that V1 is not deprecated. Do not use "prototype", "proof of concept", or "alternative" — V2 is the second version, not an alternative to V1.

---

### §4.2  Technology Stack *(replaces lines 20–47)*

**Cover:** Drop in a replacement `tabularx` table. The current table is from the old V1-prototype draft; the replacement covers every dependency in [`code/requirements.txt`](../../../../code/requirements.txt) (V1) and the extras in [`code2/requirements.txt`](../../../../code2/requirements.txt) (V2). One short framing sentence above the table, no prose below; the rationale per row lives in the "Role" column. The "Version" column uses **V1**, **V2**, or **Both**.

**Drop-in LaTeX (table only — the surrounding prose is the user's call):**

```latex
\begin{table}[H]
\centering
\caption{Technologies and libraries used in V1 (Streamlit) and V2 (React + FastAPI)}
\label{tab:techstack-v2}
\begin{tabularx}{\textwidth}{lXl}
\toprule
\textbf{Component} & \textbf{Role} & \textbf{Version} \\
\midrule
Python 3.11 & Implementation language for the analytical core and both backends & Both \\
Streamlit ($\geq$1.32) & Instructor and assistant dashboard UI; session-state model & V1 \\
streamlit-autorefresh ($\geq$1.0.1) & Browser-side polling for live updates & V1 \\
Plotly ($\geq$5.18) & Interactive charts and leaderboards & V1 \\
FastAPI ($\geq$0.115) & HTTP API exposing the analytical core to the React frontend & V2 \\
Uvicorn ($\geq$0.30) & ASGI server (with reload) for FastAPI & V2 \\
React 18 + Vite + TypeScript & Single-page application; seven runtime themes & V2 \\
pandas ($\geq$2.1), NumPy ($\geq$1.26) & In-memory data frame and vectorised scoring & Both \\
SciPy ($\geq$1.11) & L-BFGS-B optimiser for the IRT (Rasch) and BKT MLE fits & Both \\
scikit-learn ($\geq$1.4) & TF-IDF + KMeans for mistake clustering; \texttt{roc\_auc\_score} for BKT predictive AUC & Both \\
OpenAI Python SDK ($\geq$1.0) & Batched incorrectness scoring (gpt-4o-mini) and RAG generation & Both \\
sentence-transformers ($\geq$2.2), ChromaDB ($\geq$0.4) & Local MiniLM-L6-v2 embeddings + persistent vector store for RAG & Both \\
filelock ($\geq$3.12) & Cross-process write lock for the shared lab-session JSON & Both \\
requests ($\geq$2.31) & HTTP client against the lab data endpoint & Both \\
cachetools ($\geq$5.3) & TTL cache for the FastAPI analytical layer & V2 \\
\bottomrule
\end{tabularx}
\end{table}
```

**Voice/length:** 1–2 framing sentences above the table. Mention that exact versions are pinned in the two `requirements.txt` files (one per version); the table lists minima.

---

### §4.3  System Structure *(rewrite lines 51–54 + extend with the three new subsubsections)*

Open the section with one short paragraph introducing V1's two processes (instructor and assistant Streamlit apps), V2's single process (FastAPI serving API + SPA), and the one shared file (`lab_session.json`) that ties them together. Optionally drop a small TikZ diagram here — see Part C Family 2 Figure `fig:arch-v2`.

#### §4.3.1  V1 — Instructor Process (Streamlit)

**Cover:**
- The entry point is [`code/app.py`](../../../../code/app.py), a thin wrapper around `learning_dashboard.instructor_app.main()`. Port 8501 by default.
- The process is single-threaded; concurrent users open separate browser tabs but share a server-side `st.session_state` keyed by Streamlit's session id.
- The sidebar drives filtering (time window, module, academic week, saved-session window) and live-session control (start/end, code display, assistant roster).
- View routing is `selected_view`-driven in session state; the main pane renders one of the seven views from §4.9.

**Voice/length:** 1 paragraph, ~4–5 sentences. First-person plural acceptable for design choices ("we run the V1 instructor app as…").

#### §4.3.2  V1 — Assistant Process (Streamlit, mobile)

**Cover:**
- Entry point [`code/lab_app.py`](../../../../code/lab_app.py), port 8502 by default; intended for phone-sized viewports.
- Assistant identity is persisted via the URL `?aid=<uuid>` query parameter so a reload preserves the assigned student.
- The page auto-refreshes every 5 s via `streamlit-autorefresh`; this is independent of the instructor app's refresh cycle.
- Each render reads the shared lab-session state (see §4.3.4); the assistant either sees the join screen, the unassigned/waiting queue, or the assigned-student card with RAG focus suggestions.

**Voice/length:** 1 paragraph. Reference figs `fig:asst-join`, `fig:asst-unassigned`, `fig:asst-assigned` here so the reader knows the screenshots arrive in §4.10.

#### §4.3.3  V2 — React + FastAPI *(NEW — this is the "evolution" narrative and the Marker-2 comparison study)*

**Cover:**
- Open with the **"Why V2?"** paragraph (response to Marker-2 feedback). Frame it as evolution of the presentation layer once V1 reached feature parity. Concrete motivating limitations of V1 to enumerate:
  - **Single-threaded request handling.** Streamlit reruns the entire script on every interaction; long-running operations (RAG build, BKT fit) block the UI thread, forcing the cold-start guards described in §4.4.3 and §4.6.1.
  - **Theming.** Streamlit's theme system is limited to a single colour scheme set in `.streamlit/config.toml`; the sci-fi neon look in V1 required CSS injection through `st.markdown(..., unsafe_allow_html=True)` rather than a first-class theming primitive.
  - **No native async.** Streamlit has no asynchronous request model; awaiting an OpenAI or ChromaDB call inside a view function is not natural.
  - **SPA navigation.** Multi-page navigation in Streamlit is route-based with a full page reload; V1's view switching uses session-state routing as a workaround.
- V2 addresses these by moving the presentation layer to React and the backend to FastAPI while keeping `learning_dashboard/` unchanged. The same Python analytics now runs behind both UIs — V2 is therefore evidence that the analytical core is genuinely decoupled from the UI.
- **One process, two browser entries.** Entry point [`code2/backend/main.py`](../../../../code2/backend/main.py); a single FastAPI process on port 8000 serves both `/api/*` and **two** built SPA bundles from `frontend/dist/`:
  - `index.html` — the **instructor** SPA, the V2 counterpart to V1's `code/app.py` (V1 port 8501). Carries seven instructor views plus the V2-only `SessionProgression` view (eight total on the instructor side).
  - `mobile.html` — the **lab-assistant** SPA, the V2 counterpart to V1's `code/lab_app.py` (V1 port 8502). A simplified bundle focused on the `LabAssistantView` join → claim → mark-helped flow.
- **Why this is a single subsection and not two (mirroring V1's §4.3.1 + §4.3.2).** V2 consolidates the two flows into one server with two SPA bundles, so the right unit of description is the consolidated process. The view-level descriptions for both flows still live where they did for V1: instructor views in §4.9, lab-assistant flow in §4.10 — both apply to V2 as well as V1 (see the parity table at §4.9.0 / `tab:views-comparison`).
- Twelve routers under `code2/backend/routers/` adapt the analytical core to HTTP: `live`, `student`, `question`, `analysis`, `sessions`, `settings`, `models_cmp`, `lab`, `rag`, `meta`, `cf`, `classes`. The `/api/lab/*` routes are what `mobile.html` consumes; the rest serve `index.html`.
- The frontend is Vite + React + TypeScript, with nine view components total (eight instructor + one assistant). The instructor side gains the V2-only `SessionProgression` view — a time-bucket replay of struggle evolution across 20 buckets, demonstrating an interaction pattern not feasible under Streamlit's rerun model.
- Seven themes (paper, newsprint, solar, scifi, blueprint, matrix, cyberpunk) are swappable at runtime via React Context + CSS custom properties; accent colour is picked separately and persisted to `localStorage`. The theme system applies to both SPA bundles. This is a V2-only affordance.
- A FastAPI `lifespan` handler runs at startup: loads the data frame, scores incorrectness asynchronously, fits BKT + IRT, builds the RAG collection. Without this prewarm, the first user request would block on cold scoring — the same cold-start cost V1 fights with its caching tower in §4.4.3, addressed differently in V2.
- V2 reuses the same analytical code V1 ships as the [`code/learning_dashboard/`](../../../../code/learning_dashboard/) package, but **flattened directly into `code2/backend/`** rather than packaged as a separately-named subfolder — the FastAPI process *is* the analytical backend, so the second package name adds no information. The eight core modules (`analytics.py`, `data_loader.py`, `lab_state.py`, `config.py`, `paths.py`, `academic_calendar.py`, `rag.py`, `lab_classes.py`) and the `models/` subpackage sit alongside `main.py` and the routers; the algorithms, signatures, constants, and weights are byte-identical to V1. The only differences are import paths (V1 uses `from learning_dashboard.X`, V2 uses relative imports inside the package) and a four-line refactor to the OpenAI-key guard that lets V2's FastAPI startup probe verify dependencies without the application secrets present.

**Citations:** Optional software footnote on FastAPI / React / Vite. No formal bibkeys required.

**Figure slot:** `[TODO: insert figure: V2 in-class view]` — a screenshot of the V2 In-Class view in one of the dark themes (recommend `scifi` so the visual continuity with V1 is obvious). Caption: *Screenshot of V2 (React + FastAPI) showing the In-Class view in the* scifi *theme; the analytical layer is identical to V1.* `\label{fig:v2-inclass}`.

**Voice/length:** 3–4 paragraphs (~14 sentences total). First-person plural for the "Why V2?" framing ("we found that…", "we therefore evolved…"); declarative third-person for the technical description. Make the **one-process / two-SPA** model explicit early — it is the architectural payoff that justifies V2 not splitting like V1. Avoid the word "alternative" — V2 is the second version, not an alternative.

#### §4.3.4  Shared Runtime State (`lab_session.json` + filelock)

**Maths recap:** None — this is a coordination subsection.

**Cover:**
- All three apps (two Streamlit + one FastAPI) read and write a single file: `data/lab_session.json`.
- Coordination is via [`filelock.FileLock`](../../../../code/learning_dashboard/lab_state.py): every read and write takes the lock with a 5 s timeout; writes use the atomic "write to `.tmp`, then `os.replace`" pattern so partial writes are never visible to readers.
- The state holds: live-session metadata (code, start time, module, class id), the joined-assistants roster keyed by assistant uuid, and the assignment map (assistant uuid → student id).
- The session code is six characters (`LAB_CODE_LENGTH = 6`), uppercase alphanumeric, excluding `O`/`0`/`I`/`1` to remove visual ambiguity.
- A change made by any process is visible to the others within one refresh cycle (≤5 s for the assistant app, on next polling tick for the instructor).

**Figure slot:** `[TODO: insert figure: lab_state filelock pattern]` — code-snippet image of the read/write helpers. Caption: *File-locked read/write pattern for the shared lab-session state.* `\label{fig:code-lablock}`.

**Voice/length:** 1 paragraph + 1 figure.

#### §4.3.5  Deferred-Actions Pattern *(NEW)*

**Cover:**
- Streamlit forbids mutating `st.session_state` after a widget has been instantiated in the same run — doing so raises `StreamlitAPIException`.
- The repo's pattern is **deferred actions**: callbacks and post-widget click handlers set a `pending_*` flag (e.g. `pending_session_load_record`, `pending_return_to_live_data`, `pending_remove_assistant_id`) on session state; the **next** rerun reads those flags at the top of `main()`, *before* any widget is constructed, applies the mutation, and clears the flag.
- This sidesteps Streamlit's reactive contract without holding extra threads or queues. It also makes state transitions atomic — one rerun, one applied change.

**Figure slot:** `[TODO: insert figure: deferred-actions pattern]` — code-snippet image showing one `pending_*` flag set inside a callback and applied at the top of `main()`. Caption: *The deferred-actions pattern used to mutate session state without violating Streamlit's widget-instantiation rule.* `\label{fig:code-deferred}`.

**Voice/length:** 1 paragraph + 1 figure. This is a small but distinctive bit of the codebase — call it out as an explicit pattern rather than burying it in §4.3.1.

---

### §4.4  Data Pipeline *(rewrite lines 56–69)*

Open the section with one paragraph summarising the pipeline: poll the lab endpoint over HTTP → detect JSON-vs-XML payload → parse → flatten the per-submission embedded XML into one row → normalise columns → cache for 10 s → hand to the scoring layer. Reference `fig:pipeline-flow` here.

#### §4.4.1  Endpoint Retrieval and Parsing

**Cover:**
- The endpoint is `API_URL` in [`config.py`](../../../../code/learning_dashboard/config.py) — Loughborough's existing PHP retrieval endpoint at `http://sccb2.sci-project.lboro.ac.uk/retrievalEndpoint.php`.
- Request goes through `requests.get()` with a 30 s timeout (`API_TIMEOUT`).
- The endpoint returns newline-delimited JSON; each record has an `xml` string field carrying the submission body in XML. The pipeline detects the format and chooses the parser accordingly — single-payload XML is still supported as a fallback for legacy endpoint behaviour.
- Per JSON record, the embedded XML is parsed with the standard library `xml.etree.ElementTree` to extract the question text, student answer, AI feedback, time taken, and attempt count.

**Voice/length:** 1 paragraph, ~5 sentences.

#### §4.4.2  Data Normalisation and Structuring

**Cover:**
- All records collapse into a single pandas `DataFrame` with one row per submission and columns: `user`, `question`, `answer`, `ai_feedback`, `timestamp`, `time_taken`, `attempt`, `module`.
- Excluded module list (`EXCLUDED_MODULES`) drops test/admin modules (`24COB231`, `24WSC701`) before scoring.
- One historical module rename is applied (`MODULE_RENAME_MAP`: `25COA504 → 25COP504`) so a module that was relabelled mid-year is not split into two cohorts.
- A boolean `has_feedback` column flags rows the OpenAI scorer should attempt; rows with empty `ai_feedback` fall back to incorrectness 0.5 (the neutral value used when scoring is unavailable, see §4.6.1).

**Voice/length:** 1 paragraph.

#### §4.4.3  Caching Strategy *(NEW)*

**Cover:**
- Three caches operate at different granularities:
  - `@st.cache_data(ttl=CACHE_TTL)` (10 s) on `fetch_raw_data()` — keeps successive sidebar reruns from re-hitting the endpoint within the same refresh cycle.
  - In-process `_incorrectness_cache` keyed by feedback text — short-circuits the OpenAI call for any feedback string the process has already scored.
  - Disk-persisted incorrectness cache at `data/incorrectness_cache.json` — survives process restarts; a cold start short-circuits scoring when ≥95% of pending pairs are already on disk, so reboot cost stays near zero.
- The auto-refresh widget runs on a separate cadence (`AUTO_REFRESH_INTERVAL_DEFAULT = 300 s`, options: 5, 10, 15, 30, 60, 120, 300 s). The 10 s `CACHE_TTL` deduplicates *within* a refresh cycle; the chosen auto-refresh interval controls *how often* a fresh cycle happens.

**Figure slot:** Optional — `[TODO: insert figure: cache hierarchy]` if the user wants a small table summarising name × scope × TTL × eviction trigger. Caption suggestion: *Caches in the analytics pipeline.* `\label{tab:cache-hierarchy}`. Defer to user judgement.

**Voice/length:** 1 paragraph + optional table.

---

### §4.5  Session Management *(rewrite lines 71–75)*

Open with one sentence on what "session" means in this system: a bounded window of submissions used for in-class focus, recorded for retrospective review.

#### §4.5.1  Live Session Lifecycle

**Cover:**
- Sequence: instructor clicks **Start Session** → a 6-character code is generated → assistants enter the code (and a name) on the assistant app and appear in the roster within ≤5 s → the instructor either auto-assigns by struggle rank or drags students onto assistant cards → assistants mark "helped" when done → instructor clicks **End Session**, optionally entering a session name to save.
- The session code uses an alphanumeric alphabet with `O`/`0`/`I`/`1` excluded — six characters give roughly 30 bits of randomness, more than sufficient for the in-room threat model.
- During a live session the instructor sidebar shows the code, elapsed time, joined-assistants count, and a one-click end button.

**Figure slot:** `[TODO: insert figure: session live sidebar]` — caption: *Instructor sidebar during a live session, showing the join code, elapsed time, and roster of joined assistants.* `\label{fig:session-live}`.

**Voice/length:** 1 paragraph + 1 figure.

#### §4.5.2  Saved Session History and Restoration

**Cover:**
- Each ended session is appended to `data/saved_sessions.json` with: uuid, display name, module/class id, start and end timestamps, context dict (assistant roster, assignment map at end).
- CRUD: list (`load_saved_sessions`), append (`save_session_record`), delete (`delete_session_record`), and "restore filter window" (`apply_saved_session_to_state`) which reapplies a saved session's time window to the sidebar filters so the instructor can re-view it after the fact.
- All writes use the same atomic tmp-then-replace pattern as the live state.
- The Previous Sessions view (§4.9.7) is the UI surface; this subsection only describes the storage shape.

**Voice/length:** 1 paragraph.

---

### §4.6  Analytics Implementation *(rewrite lines 77–87 — this is the analytical-content-heavy section; every subsection needs a maths recap)*

Open the section with one short paragraph naming the four scoring pipelines (incorrectness, struggle, difficulty, collaborative filtering) plus the unsupervised one (mistake clustering), and signposting that all five run on each cache refresh.

#### §4.6.1  Incorrectness Scoring (OpenAI, batched, cached)

**Maths recap:** Each submission $i$ receives a scalar incorrectness $x_i \in [0,1]$ where $x_i = 0$ means "fully correct" and $x_i = 1$ means "fully incorrect"; intermediate values capture partial credit. The mapping from `ai_feedback` text to $x_i$ is delegated to gpt-4o-mini (`OPENAI_MODEL`). Empty feedback returns the neutral fallback $x_i = 0.5$.

**Cover:**
- Calls go through `_call_openai_batch()`; up to `OPENAI_BATCH_SIZE = 20` (question, answer, feedback) triples per request — smaller batches parse more reliably than the API's nominal max.
- Cold-start guard: `SCORING_PER_RUN_CAP = 500` caps the new pairs scored per Streamlit rerun; the rest fall back to 0.5 and are scored on subsequent runs. This keeps the UI responsive when the cache is empty.
- Two-layer cache: an in-process dict keyed by feedback text, plus a disk-persisted JSON at `data/incorrectness_cache.json`. See §4.4.3 for the cache hierarchy.
- On API failure the cache is bypassed and the row falls back to 0.5 — bad responses are *not* persisted, so the next rerun retries.

**Constants:** `OPENAI_MODEL = "gpt-4o-mini"`, `OPENAI_BATCH_SIZE = 20`, `SCORING_PER_RUN_CAP = 500`, `CORRECT_THRESHOLD = 0.5`.

**Citations:** None required for the OpenAI call itself (software cite optional in a footnote).

**Figure slot:** `[TODO: insert figure: openai batch call]` — code-snippet image of the batched call. Caption: *Batched OpenAI call for incorrectness scoring.* `\label{fig:code-openai}`.

**Voice/length:** 2 paragraphs + 1 figure.

#### §4.6.2  Baseline Student Struggle Model (7 signals)

**Maths recap:** Each student $s$ scores
$$S(s) = \alpha N_s + \beta T_s + \gamma I_s + \delta R_s + \eta A_s + \zeta D_s + \theta\, \mathrm{REP}_s$$
where each signal is min-max normalised across the cohort, and a Bayesian shrinkage step (see below) pulls students with few submissions toward the cohort mean. Full derivation in Ch3 §3.3.1 and Appendix E.

**Cover:**
- Seven signals, all weights stored in `config.py`:
  - $N$ — submission count (`STRUGGLE_WEIGHT_N = 0.10`)
  - $T$ — time active (`STRUGGLE_WEIGHT_T = 0.10`)
  - $I$ — mean incorrectness (`STRUGGLE_WEIGHT_I = 0.20`)
  - $R$ — retry rate (`STRUGGLE_WEIGHT_R = 0.10`)
  - $A$ — recent incorrectness, exponential time decay, 30-min half-life (`STRUGGLE_WEIGHT_A = 0.38`, `DECAY_HALFLIFE_SECONDS = 1800`)
  - $D$ — improvement slope (`STRUGGLE_WEIGHT_D = 0.05`)
  - $\mathrm{REP}$ — answer repetition rate (`STRUGGLE_WEIGHT_REP = 0.07`)
  - Weights sum to 1.00; an import-time assertion in `config.py` enforces this.
- Bayesian shrinkage with prior strength `SHRINKAGE_K = 5`: a student with $n \gg K$ submissions is unaffected; a student with $n \ll K$ is pulled toward the cohort mean. This stops a single noisy submission from putting a low-volume student at the top of the leaderboard.
- The whole pipeline runs as one vectorised pass over the data frame — no per-student loops.
- Thresholds for level labels live in `STRUGGLE_THRESHOLDS`: `On Track` (0.00–0.20), `Minor Issues` (0.20–0.35), `Struggling` (0.35–0.50), `Needs Help` (0.50–1.00).

**Drop-in LaTeX table (paste under `\subsubsection{Baseline Student Struggle Model}`):**

```latex
\begin{table}[H]
\centering
\caption{Components of the baseline student struggle score with default weights}
\label{tab:struggle-7sig}
\begin{tabularx}{\textwidth}{llXl}
\toprule
\textbf{Symbol} & \textbf{config.py key} & \textbf{Meaning} & \textbf{Weight} \\
\midrule
$N$            & \texttt{STRUGGLE\_WEIGHT\_N}   & Submission count (min-max normalised)                & 0.10 \\
$T$            & \texttt{STRUGGLE\_WEIGHT\_T}   & Time active in the session (min-max normalised)      & 0.10 \\
$I$            & \texttt{STRUGGLE\_WEIGHT\_I}   & Mean incorrectness across submissions                & 0.20 \\
$R$            & \texttt{STRUGGLE\_WEIGHT\_R}   & Retry rate (repeat attempts on the same question)    & 0.10 \\
$A$            & \texttt{STRUGGLE\_WEIGHT\_A}   & Recent incorrectness, exponential time decay (30-min half-life) & 0.38 \\
$D$            & \texttt{STRUGGLE\_WEIGHT\_D}   & Improvement-slope coefficient (min-max normalised)   & 0.05 \\
$\mathrm{REP}$ & \texttt{STRUGGLE\_WEIGHT\_REP} & Answer repetition rate (exact-match repeats / total) & 0.07 \\
\bottomrule
\end{tabularx}
\end{table}
```

**Voice/length:** Maths recap + 2 paragraphs + 1 table. The first paragraph after the recap explains what's new about the implementation versus the textbook formula (vectorised pass, Bayesian shrinkage, exponential decay replacing fixed RECENT_WEIGHTS); the second names the threshold bands.

#### §4.6.3  Baseline Question Difficulty Model (5 signals)

**Maths recap:** Each question $q$ scores
$$D(q) = w_C\, C_q + w_T\, T_q + w_A\, A_q + w_F\, F_q + w_P\, P_q$$
with all components min-max normalised across the question set. Derivation in Ch3 §3.3.3 and Appendix E.

**Cover:**
- Five signals (all weights in `config.py`):
  - $C$ — incorrect rate (`DIFFICULTY_WEIGHT_C = 0.28`)
  - $T$ — average time per student (`DIFFICULTY_WEIGHT_T = 0.12`)
  - $A$ — average attempts per student (`DIFFICULTY_WEIGHT_A = 0.20`)
  - $F$ — average incorrectness score (`DIFFICULTY_WEIGHT_F = 0.20`)
  - $P$ — first-attempt failure rate (`DIFFICULTY_WEIGHT_P = 0.20`)
- Weights sum to 1.00 (asserted at import time).
- Thresholds: `Easy` (0.00–0.35), `Medium` (0.35–0.50), `Hard` (0.50–0.75), `Very Hard` (0.75–1.00).

**Drop-in LaTeX table:**

```latex
\begin{table}[H]
\centering
\caption{Components of the baseline question difficulty score with default weights}
\label{tab:difficulty-5sig}
\begin{tabularx}{\textwidth}{llXl}
\toprule
\textbf{Symbol} & \textbf{config.py key} & \textbf{Meaning} & \textbf{Weight} \\
\midrule
$C$ & \texttt{DIFFICULTY\_WEIGHT\_C} & Incorrect-attempt rate (raw ratio)               & 0.28 \\
$T$ & \texttt{DIFFICULTY\_WEIGHT\_T} & Mean time per student (min-max normalised)       & 0.12 \\
$A$ & \texttt{DIFFICULTY\_WEIGHT\_A} & Mean attempts per student (min-max normalised)   & 0.20 \\
$F$ & \texttt{DIFFICULTY\_WEIGHT\_F} & Mean incorrectness score                          & 0.20 \\
$P$ & \texttt{DIFFICULTY\_WEIGHT\_P} & First-attempt failure rate                        & 0.20 \\
\bottomrule
\end{tabularx}
\end{table}
```

**Voice/length:** Maths recap + 1 paragraph + 1 table.

#### §4.6.4  Collaborative Filtering

**Maths recap:** For each pair of students $(s, t)$, similarity is cosine over a five-element behavioural feature vector
$$\mathrm{sim}(s, t) = \frac{\mathbf{v}_s \cdot \mathbf{v}_t}{\lVert \mathbf{v}_s \rVert\, \lVert \mathbf{v}_t \rVert}.$$
A struggling student $s^*$ (flagged by the parametric model) "infects" any peer $t$ with $\mathrm{sim}(s^*, t) \geq \tau$ and $t$ not already flagged — surfacing students whose *behaviour* looks like a struggler's even when their *score* does not yet cross the threshold.

**Cover:**
- Five-element feature vector: normalised submission count, time active, mean incorrectness, retry rate, recent incorrectness.
- $k = 3$ nearest neighbours considered per student; threshold $\tau \geq 0.6$ to count as "similar".
- Output is a list of (similar student, source student, similarity score) tuples shown in the In-Class view's CF diagnostic panel.
- The view-level toggle is `cf_enabled` in session state; threshold is exposed as a slider in §4.9.6 Settings.

**Voice/length:** Maths recap + 1 paragraph.

#### §4.6.5  Mistake Clustering

**Maths recap:** None — this is unsupervised pattern surfacing, not a scoring model. (Optional: TF-IDF vectorisation produces sparse vectors $\mathbf{x}_i \in \mathbb{R}^{|V|}$ over the vocabulary of incorrect answers; KMeans minimises within-cluster squared $\ell_2$; the silhouette score selects $k$.)

**Cover:**
- For each question with at least `CLUSTER_MIN_WRONG = 3` incorrect submissions, the wrong-answer texts are TF-IDF-vectorised and clustered with KMeans.
- $k$ is selected by silhouette score, capped at `CLUSTER_MAX_K = 5`.
- The cluster with the highest centroid-to-wrong-answer cosine similarity is labelled "most common mistake"; up to `CLUSTER_MAX_EXAMPLES = 3` representative answers are shown per cluster, truncated to `CLUSTER_EXAMPLE_MAX_CHARS = 300` for the UI.
- Results surface in the Question Detail view (§4.9.3) as labelled clusters next to the question text.

**Voice/length:** 1 paragraph (no separate maths recap unless the user wants one).

---

### §4.7  Advanced Model Implementation *(rewrite lines 101–109)*

Open with one paragraph: these are the three improved models referenced from the Settings view's "Improved" toggle group (`improved_models_enabled`). They share an implementation pattern — MLE fit on the live data frame, sane defaults applied when the fit declines (too few observations), graceful fallback so the UI is never blocked on a fit.

#### §4.7.1  Measurement Confidence

**Maths recap:** For an incorrectness score $x \in [0,1]$ with feedback text of length $\ell$ characters, confidence is
$$c = \mathrm{ramp}_{\ell, 0, L}\;\cdot\;(0.5 + 0.5\,|2x - 1|)\;\cdot\;c_{\text{base}}$$
where $\mathrm{ramp}_{\ell, 0, L}$ rises linearly from 0 to 1 over $[0, L]$ characters (`MEASUREMENT_CONFIDENCE_MIN_LENGTH = 20`), $|2x-1|$ is extremity (1 at the ends, 0 at $x = 0.5$), and $c_{\text{base}} = 0.7$ (`MEASUREMENT_CONFIDENCE_BASE`).

**Cover:**
- Confidence is a meta-signal — *how confident are we in the scorer's verdict?* — surfaced as a coloured dot next to the incorrectness value in the Question Detail view.
- Short or empty feedback collapses confidence toward 0; long, extreme-valued feedback approaches the base ceiling.
- Empty `ai_feedback` returns confidence 0.0, not the neutral 0.5 — the score is fallback, not measurement.
- Aggregated mean confidence is shown per question (the dot's colour and intensity), so the instructor can see *which questions the scorer is unsure about*.

**Voice/length:** Maths recap + 1 paragraph.

#### §4.7.2  Item Response Theory (IRT) Difficulty

**Maths recap:** A 1-parameter logistic (Rasch) model:
$$P(\text{student } s \text{ correct on question } q) = \sigma(\theta_s - \beta_q)$$
with $\theta_s$ student ability, $\beta_q$ question difficulty, and $\sigma$ the logistic sigmoid. Joint MLE over all $\theta_s$ and $\beta_q$ simultaneously.

**Cover:**
- Implementation in [`models/irt.py`](../../../../code/learning_dashboard/models/irt.py); the fit calls `scipy.optimize.minimize` with `method="L-BFGS-B"`\footnote{\cite{byrdLBFGSB1995}}.
- Response matrix: one row per student, one column per question, value 1 if best-attempt incorrectness < 0.5, else 0; NaN if no attempt.
- Filtering: questions with fewer than `IRT_MIN_ATTEMPTS_PER_QUESTION = 2` responding students are dropped; students with fewer than `IRT_MIN_ATTEMPTS_PER_STUDENT = 2` answered questions are dropped. Filter is applied iteratively until both minima are satisfied.
- Optimiser max iterations `IRT_MAX_ITER = 100`; convergence is reported back to the UI.
- Output: logit-scale $\beta_q$, mapped to $[0,1]$ via sigmoid for the leaderboard. Threshold bands match the baseline (`IRT_DIFFICULTY_THRESHOLDS`).

**Citations:** `\cite{byrdLBFGSB1995}` for L-BFGS-B (verify bibkey; add if missing in Step 12). Rasch citation if the user wants the original 1960 work cited.

**Voice/length:** Maths recap + 2 paragraphs.

#### §4.7.3  Bayesian Knowledge Tracing (BKT) Mastery

**Maths recap:** Two-state HMM per (student, question). State: `learned` or `not learned`. Four parameters per fit:
- $P(L_0)$ prior probability of knowing the skill (`BKT_P_INIT = 0.3`)
- $P(T)$ probability of learning per opportunity (`BKT_P_LEARN = 0.1`)
- $P(G)$ probability of guessing correctly while not learned (`BKT_P_GUESS = 0.2`)
- $P(S)$ probability of slipping while learned (`BKT_P_SLIP = 0.1`)

Posterior after observation $c_t \in \{0,1\}$:
$$P(L_t \mid c_t) = \frac{P(L_t)\cdot P(c_t \mid L_t)}{P(c_t)},\qquad P(L_{t+1}) = P(L_t \mid c_t) + (1 - P(L_t \mid c_t))\, P(T).$$

**Cover:**
- Implementation in [`models/bkt.py`](../../../../code/learning_dashboard/models/bkt.py).
- Two functions matter: `compute_student_mastery` (inference — replay one student's chronologically-ordered submissions to produce final mastery per question) and `fit_bkt_parameters` (training — MLE via the forward algorithm + L-BFGS-B with bounds $[0,1]\times[0,1]\times[0,0.5]\times[0,0.5]$, enforcing the identifiability constraint $P(G) + P(S) < 1$).
- Fit refuses if fewer than `BKT_FIT_MIN_OBSERVATIONS = 50` attempts are available, or if every attempt is graded the same way (single-class data carries no information about learning dynamics — the function returns a diagnostic message listing the incorrectness distribution and likely cause).
- Predictive AUC is reported alongside the fitted parameters: `scikit-learn`'s `roc_auc_score` on next-attempt correctness\footnote{\cite{fawcettIntroductionROCAnalysis2006} or equivalent}. Used in Ch5 §5.4 to compare baseline-vs-BKT discrimination.
- Mastery threshold `BKT_MASTERY_THRESHOLD = 0.95`; students with mean $P(L) \geq 0.95$ across their attempted questions are flagged "mastered" on the student-detail page.

**Drop-in LaTeX table:**

```latex
\begin{table}[H]
\centering
\caption{Default Bayesian Knowledge Tracing parameters and their permitted ranges}
\label{tab:bkt-defaults}
\begin{tabularx}{\textwidth}{lXll}
\toprule
\textbf{Symbol} & \textbf{Meaning} & \textbf{Default} & \textbf{Fit bounds} \\
\midrule
$P(L_0)$ & Prior probability of knowing the skill                    & 0.30 & [0.0, 1.0] \\
$P(T)$   & Probability of learning per opportunity                    & 0.10 & [0.0, 1.0] \\
$P(G)$   & Probability of guessing correctly while not learned        & 0.20 & [0.0, 0.5] \\
$P(S)$   & Probability of slipping (wrong) while learned              & 0.10 & [0.0, 0.5] \\
\bottomrule
\end{tabularx}
\end{table}
```

**Citations:** `\cite{corbettKnowledgeTracingModeling1995}` for BKT (already in Ch3). `\cite{byrdLBFGSB1995}` for L-BFGS-B (re-used from §4.7.2). ROC-AUC citation to be confirmed in Step 12.

**Voice/length:** Maths recap + 2 paragraphs + 1 table.

#### §4.7.4  Improved Struggle Model

**Maths recap:**
$$S_{\text{improved}}(s) = w_B\, B_s + w_M\, M_s + w_D\, A_s$$
with $B_s$ the behavioural composite (§4.6.2 with the parametric weights), $M_s$ a mastery-gap term derived from BKT (§4.7.3), $A_s$ a difficulty-adjusted exposure term derived from IRT (§4.7.2), and weights $(w_B, w_M, w_D) = (0.45, 0.30, 0.25)$.

**Cover:**
- Implementation in [`models/improved_struggle.py`](../../../../code/learning_dashboard/models/improved_struggle.py).
- The behavioural component reuses the 7-signal baseline (§4.6.2). The mastery-gap term is `1 - mean(P(L))` across the student's attempted questions. The difficulty-adjustment term reweights submissions by the IRT difficulty of the questions they targeted, so attempts on hard items contribute more.
- **Graceful weight redistribution** is the distinctive piece: if BKT mastery is unavailable for a student (fewer than the minimum BKT observations) the mastery-gap weight redistributes proportionally to the other two components, and similarly for missing IRT difficulty. So the improved score is always defined — it just collapses cleanly to a lower-information variant when the upstream models cannot speak.
- The toggle `improved_models_enabled` in the Settings view (§4.9.6) switches the In-Class leaderboard between the baseline (§4.6.2) and this improved score.
- Final post-shrinkage step is identical to the baseline.

**Optional drop-in table** — weight-redistribution cases (rows must sum to 1.00):

| Available data | $w_B$ behavioural | $w_M$ mastery gap | $w_D$ difficulty adj |
|---|---|---|---|
| All three | 0.45 | 0.30 | 0.25 |
| BKT unavailable | 0.64 | — | 0.36 |
| IRT unavailable | 0.60 | 0.40 | — |
| Both unavailable | 1.00 | — | — |

If the user includes this, mention in prose that the redistribution is proportional (ratios preserved between the remaining components).

**Voice/length:** Maths recap + 2 paragraphs + (optional) table.

---

### §4.8  RAG Suggested Feedback *(rewrite lines 89–99)*

Open the section with one paragraph: what RAG does in this system (turn a struggling student's recent submission history into 2–3 actionable focus suggestions for the assistant), why retrieval beats raw prompting (keeps the model anchored to the student's own work), and how it appears in the assistant UI (a panel inside the assigned-student card). Add no inline attribution of supervisor input — credit belongs in Acknowledgments.

#### §4.8.1  Hybrid Two-Layer Architecture

**Maths recap:** Optional — Layer 2 retrieval is a top-$k$ nearest neighbour search in a 384-dimensional embedding space (`all-MiniLM-L6-v2`) using cosine similarity through ChromaDB's HNSW index.

**Cover:**
- **Layer 1**: pandas pre-filter by `student_id` — narrows the search to the requesting student's own submission history, so retrieved evidence is always personally relevant.
- **Layer 2**: ChromaDB semantic search over the embeddings of those submissions, with a `where` clause filtering on metadata.
- Output of the two layers is a small list of (submission text, feedback, score) triples, which is then handed to the generator (§4.8.3).
- In V2 (`code2/backend/routers/rag.py`) the call is wrapped in `async` + `asyncio.to_thread` so the first-time ChromaDB build does not block the event loop. V1 does not need this — under Streamlit the build happens during the cached scoring pass.

**Citations:** `\cite{lewisRetrievalAugmentedGenerationKnowledgeIntensive2020}` (already in `references.bib`, cited in Ch3).

**Voice/length:** 1 paragraph + (optional) maths recap.

#### §4.8.2  Embedding Model (all-MiniLM-L6-v2)

**Cover:**
- Embeddings are produced by `sentence-transformers` running `all-MiniLM-L6-v2` locally — no API call, no cost per query.
- 384-dimensional output, ≈80 MB model size, distilled from BERT-base. Empirically sufficient for the short submission texts (typically <100 words).
- ChromaDB collection naming: `session_{session_id}` — one collection per saved session so embeddings do not leak across sessions.
- Persistence path: `data/rag_chroma/` (Chroma's `PersistentClient`).
- `RAG_MIN_SUBMISSIONS = 2` — the panel does not attempt RAG for a student with fewer than two submissions (signal-to-noise too low).

**Citations:** Software cite for sentence-transformers and ChromaDB is optional. The MiniLM citation `\cite{reimersSentenceBERTSentenceEmbeddings2019}` would be the formal reference if the user wants it (verify it is in `references.bib`).

**Voice/length:** 1 paragraph.

#### §4.8.3  Generation and Prompting (gpt-4o-mini, JSON)

**Cover:**
- The generator is gpt-4o-mini (same model as incorrectness scoring — keeps the dependency surface narrow).
- The prompt is a system message + user message; the user message contains the retrieved evidence (submission text and feedback for the top-$k$ relevant past submissions) and asks for a JSON object with a `bullets` field containing 2–3 short coaching points.
- Output is constrained to JSON via OpenAI's response-format parameter; the parser is therefore deterministic and never has to regex-tear unstructured text.
- Each bullet is 1–2 sentences, addressed to the lab assistant (not the student), and frames a specific thing to look at — *"check the loop bounds on submission 3; the off-by-one pattern in submission 7 may recur"*.

**Figure slot:** `[TODO: insert figure: rag generation prompt]` — code-snippet image of the system + user prompt template. Caption: *RAG generation prompt — system and user messages used to produce assistant focus suggestions.* `\label{fig:code-ragprompt}`.

**Voice/length:** 1 paragraph + 1 figure.

#### §4.8.4  Suggestion Caching

**Cover:**
- Suggestions are cached per (student id, session id) — once generated, a re-render of the assistant card reuses the cached bullets without a new OpenAI call.
- Cache invalidates when the student's submission count crosses a new threshold (a new submission means new evidence is worth resurfacing).

**Voice/length:** 1 short paragraph.

#### §4.8.5  Graceful Degradation and Privacy

**Cover:**
- If `chromadb` or `sentence-transformers` is missing from the runtime, the RAG panel is replaced by an empty placeholder — the rest of the assistant UI is unaffected. The toggle `RAG_ENABLED_DEFAULT = True` is honoured but the dependency check has the final word.
- If the OpenAI call fails, the cached bullets remain on screen; no error banner.
- All retrieval is local: the only data sent over the network is the small set of bullets-and-evidence in the generation prompt itself. Student identifiers in the prompt are the same opaque user ids that appear in the leaderboard — there is no `name → id` resolution server-side.

**Voice/length:** 1 paragraph.

---

### §4.9  Instructor System Views *(rewrite lines 111–125)*

#### §4.9.0  Preamble (NEW) — V1 vs V2 parity table

One short paragraph: the instructor functionality is implemented twice — once in V1 (`code/learning_dashboard/ui/views.py`, Streamlit) and once in V2 (`code2/frontend/src/views/`, React). Both consume the same `learning_dashboard.*` analytics through different transport layers (direct Python import for V1; HTTP via FastAPI for V2). The parity is intentional and the table below is the comparison-study artefact promised by §4.3.3 — for each view, what is the parity status, where does V2 go beyond V1, and what does each version cost at runtime.

**Drop-in LaTeX table:**

```latex
\begin{table}[H]
\centering
\caption{Instructor views in V1 (Streamlit) and V2 (React + FastAPI), with view-level parity status}
\label{tab:views-comparison}
\begin{tabularx}{\textwidth}{lXll}
\toprule
\textbf{View} & \textbf{Function (purpose)} & \textbf{V1} & \textbf{V2} \\
\midrule
In Class         & Live struggle + difficulty leaderboards, CF panel & Yes & Yes \\
Student Detail   & Per-student signal breakdown, timeline            & Yes & Yes \\
Question Detail  & Mistake clusters, top strugglers                  & Yes & Yes (+ extra "Top strugglers on this question" table) \\
Data Analysis    & Cohort-level summaries across academic weeks      & Yes & Yes \\
Model Comparison & Baseline vs IRT, baseline vs improved struggle    & Yes & Yes \\
Settings         & Model toggles, CF threshold, BKT sliders          & Yes & Yes (+ theme picker, accent picker) \\
Previous Sessions& List + delete saved sessions                       & Yes & Yes \\
Session Progression & Time-bucket replay over 20 buckets              & No  & Yes \\
\bottomrule
\end{tabularx}
\end{table}
```

#### §4.9.1  In-Class View

**Cover:**
- Two leaderboards side by side: top strugglers (descending struggle score) and top difficult questions (descending difficulty score), each with up to `LEADERBOARD_MAX_ITEMS = 15` rows.
- Bar colours follow the threshold bands (green / yellow / orange / red).
- The CF diagnostic panel sits below the leaderboards: lists peers similar to currently-flagged strugglers who are themselves not yet flagged.
- Clicking a bar drills into the corresponding Student Detail or Question Detail view via `st.plotly_chart(on_select="rerun")` + a `point_index` lookup.

**Figure slot:** `[TODO: insert figure: In-Class view]` — caption: *Screenshot of the In-Class view, showing the struggle and difficulty leaderboards and the collaborative-filtering diagnostic panel.* `\label{fig:ui-inclass}`.

**Voice/length:** 1 paragraph + 1 figure.

#### §4.9.2  Student Detail View

**Cover:**
- Per-signal breakdown of the student's struggle score (one bar per of the 7 signals).
- Submission timeline ordered by timestamp, with incorrectness encoded as bar colour.
- Top `STUDENT_DETAIL_TOP_QUESTIONS = 10` hardest questions for this student.
- If improved models are enabled, the panel adds mastery and difficulty-adjusted exposure components.

**Figure slot:** `[TODO: insert figure: Student Detail view]` — caption: *Screenshot of the Student Detail view, with per-signal breakdown and submission timeline.* `\label{fig:ui-studentdetail}`.

**Voice/length:** 1 paragraph + 1 figure.

#### §4.9.3  Question Detail View

**Cover:**
- Question text, difficulty score, and aggregated incorrectness with a confidence dot (§4.7.1).
- Top `QUESTION_DETAIL_TOP_STUDENTS = 15` students who struggled on this question.
- Mistake clusters: each cluster's centroid label, member count, and up to `CLUSTER_MAX_EXAMPLES = 3` representative answers truncated to `CLUSTER_EXAMPLE_MAX_CHARS = 300` chars.

**Figure slot:** `[TODO: insert figure: Question Detail view]` — caption: *Screenshot of the Question Detail view, with labelled mistake clusters.* `\label{fig:ui-questiondetail}`.

**Voice/length:** 1 paragraph + 1 figure.

#### §4.9.4  Data Analysis View

**Cover:**
- Cohort-level summaries across academic weeks (the `academic_calendar` module maps calendar dates to Loughborough 2025/26 week labels).
- Top `DATA_ANALYSIS_TOP_QUESTIONS = 10` questions and `DATA_ANALYSIS_TOP_USERS = 20` users over the selected window.
- Distribution histograms (struggle, difficulty, incorrectness) with `HISTOGRAM_BINS = 20`.

**Figure slot:** `[TODO: insert figure: Data Analysis view]` — caption: *Screenshot of the Data Analysis view across an academic week.* `\label{fig:ui-dataanalysis}`.

**Voice/length:** 1 paragraph + 1 figure.

#### §4.9.5  Model Comparison View

**Cover:**
- Two tabs: Students and Questions.
- Students tab: scatter of baseline struggle vs improved struggle, colour-coded by level-agreement (same level / one band / two bands / three bands apart). Headline metrics: Spearman $\rho$, top-10 overlap, level-agreement breakdown.
- Questions tab: same but baseline difficulty vs IRT difficulty.
- Tables list the largest mover (the student or question whose level changed the most under the improved model).
- This view feeds Ch5 §5.4 evidence directly — the figures captured here become the model-comparison panel in Ch5.

**Figure slot:** `[TODO: insert figure: Model Comparison view]` — caption: *Screenshot of the Model Comparison view (student + question tabs).* `\label{fig:ui-comparison}`.

**Voice/length:** 1 paragraph + 1 figure.

#### §4.9.6  Settings View

**Cover:**
- Toggles: Sound Effects (`SOUNDS_ENABLED_DEFAULT`), Auto-Refresh (`AUTO_REFRESH_DEFAULT`), CF (`cf_enabled`), Temporal Smoothing (`SMOOTHING_ENABLED`), Improved Models (`improved_models_enabled`), RAG (`RAG_ENABLED_DEFAULT`).
- Sliders: Refresh Interval (from `AUTO_REFRESH_OPTIONS`), CF similarity threshold $\tau$, BKT parameters $P(L_0)$, $P(T)$, $P(G)$, $P(S)$.
- Selectboxes: Struggle Model (Baseline / Improved), Difficulty Model (Baseline / IRT).
- All values are persisted to session state; the BKT sliders re-run the per-student mastery on change.

**Sound effects sub-paragraph** *(folded in from the old standalone §4.11 — 3–4 sentences, no figure):*
- The Settings view's `Sound Effects` toggle controls a small audio layer implemented in [`code/learning_dashboard/sound.py`](../../../../code/learning_dashboard/sound.py): six short cues (session start, session end, selection, navigation, refresh, assistant join, assignment received, high struggle) authored as Web Audio API `OscillatorNode` + `GainNode` chains.
- Each cue is injected into the page through `st.components.v1.html()` inside a zero-height iframe — Streamlit cannot natively play audio, so this is the lightest workable shim.
- This is a small UX detail rather than a load-bearing feature, but it materially changes the demo experience and is worth a short paragraph alongside the rest of the Settings toggles.

**Figure slot:** `[TODO: insert figure: Settings view]` — caption: *Screenshot of the Settings view showing model toggles, CF threshold, and BKT sliders.* `\label{fig:ui-settings}`.

**Voice/length:** 1 paragraph (Settings toggles) + 1 short sub-paragraph (Sound effects, ~3–4 sentences) + 1 figure.

#### §4.9.7  Previous Sessions View

**Cover:**
- Lists saved sessions newest-first with name, module, start/end times, duration, and a delete button per row.
- Clicking a row applies the session's time window to the sidebar filters (deferred-action pattern, §4.3.5) and routes to the In-Class view so the instructor can re-view the cohort at that moment.

**Figure slot:** `[TODO: insert figure: Previous Sessions view]` — caption: *Screenshot of the Previous Sessions view.* `\label{fig:ui-previoussessions}`.

**Voice/length:** 1 paragraph + 1 figure.

---

### §4.10  Lab Assistant System *(rewrite lines 127–133)*

Open with one paragraph: the assistant app is a separate Streamlit process (`code/lab_app.py`, port 8502) designed for phone viewports. It reads the same `lab_session.json` as the instructor app and surfaces three states depending on the assistant's assignment.

#### §4.10.1  Session Join Flow

**Cover:**
- Assistant lands on the join screen: enter the 6-character code from the instructor + a display name.
- A new UUID is generated and persisted into the URL as `?aid=<uuid>` so the browser tab survives a refresh.
- The shared state is updated atomically: assistant uuid → display name appended to the roster; instructor sees the new assistant within ≤5 s.

**Figure slot:** `[TODO: insert figure: assistant join]` — caption: *Screenshot of the lab assistant join screen on mobile.* `\label{fig:asst-join}`.

**Voice/length:** 1 paragraph + 1 figure.

#### §4.10.2  Waiting and Assignment States

**Cover:**
- Unassigned state: assistant sees the queue of currently-flagged strugglers; a "Claim" button per row lets the assistant self-assign (sets the assignment map atomically via the write-lock).
- The instructor can also drag-and-assign from the instructor dashboard; the assistant sees the assignment on the next 5-s refresh.

**Figure slot:** `[TODO: insert figure: assistant unassigned]` — caption: *Screenshot of the lab assistant unassigned state with the queue of strugglers.* `\label{fig:asst-unassigned}`.

**Voice/length:** 1 paragraph + 1 figure.

#### §4.10.3  Live Assistant Allocation and Mark-Helped

**Cover:**
- Assigned state: the assistant card shows the student's id, current struggle score, the 7-signal breakdown, the recent submission timeline, and the RAG focus suggestions panel (§4.8).
- Two action buttons: "Mark helped" (clears the assignment and returns the assistant to the queue) and "Unassign" (returns the student to the queue without marking helped).
- The state mutation is the same write-lock pattern as everywhere else.

**Figure slot:** `[TODO: insert figure: assistant assigned card]` — caption: *Screenshot of the lab assistant assigned-student card with RAG focus suggestions.* `\label{fig:asst-assigned}`.

**Voice/length:** 1 paragraph + 1 figure.

---

### §4.11  Problems Encountered and Solutions *(rewrite line 137)*

Use the table format from [previous-works/F221611.pdf §5.6](../../../../previous-works/F221611.pdf). Three columns: Problem | Description | Resolution. Caption: *Implementation problems encountered and their resolutions.* `\label{tab:problems}`.

**Drop-in candidates** (pick 4–6 — these are the ones with the clearest narrative arc):

| Problem | Description | Resolution |
|---|---|---|
| Endpoint format drift | The lab endpoint occasionally returned single-payload XML instead of newline-delimited JSON, breaking the parser. | Added a format-detection step and dual parser; both branches normalise into the same DataFrame schema. |
| OpenAI cold-start cost | First Streamlit rerun on a new session would block for tens of seconds while every submission was scored. | Two-layer cache (in-process + disk-persisted JSON) + `SCORING_PER_RUN_CAP = 500` so first rerun stays responsive; remaining pairs score in subsequent runs. |
| Streamlit's widget-instantiation rule | Mutating session state after a widget has been instantiated raises `StreamlitAPIException`, breaking obvious-looking callbacks. | Deferred-actions pattern (§4.3.5): callbacks set `pending_*` flags; the next rerun applies them before any widget is built. |
| Cross-process write conflicts | V1 (two Streamlit processes) and V2 (one FastAPI process) can all write the same `lab_session.json`; naïve writes corrupt the file. | `filelock.FileLock` with a 5 s timeout on every read and write; atomic `os.replace` from a `.tmp` file so partial writes never appear. |
| V2 startup latency | First request to V2 would block on cold scoring + cold RAG build under the FastAPI event loop. | `lifespan` handler runs scoring, BKT/IRT fits, and ChromaDB build in the background at startup; V2 loads against a warm cache. V1 addresses the same cold-start problem with the layered caches in §4.4.3. |
| BKT identifiability on single-class data | When every observed attempt is graded the same way, the BKT log-likelihood surface degenerates and the fit returns useless parameters. | The fit refuses (and reports a diagnostic listing the incorrectness distribution + likely cause) when fewer than two classes are present. |

**Voice/length:** 1 framing sentence + 1 table.

---

## Part C — Figure inventory

Family counts: **11 UI screenshots, 2 architecture/flow diagrams, 4 code-snippet images, 6 typeset tables** (+ 2 optional). Every entry below already has its `\label{}` defined inline above; this section is the consolidated index for the renumbering pass at Step 8.

### Family 1 — UI screenshots

| § | Slot | `\label{}` |
|---|---|---|
| 4.3.3 | V2 In-Class view (scifi theme) | `fig:v2-inclass` |
| 4.5.1 | Instructor sidebar during live session (V1) | `fig:session-live` |
| 4.9.1 | In-Class view | `fig:ui-inclass` |
| 4.9.2 | Student Detail view | `fig:ui-studentdetail` |
| 4.9.3 | Question Detail view (with clusters) | `fig:ui-questiondetail` |
| 4.9.4 | Data Analysis view | `fig:ui-dataanalysis` |
| 4.9.5 | Model Comparison view (both tabs) | `fig:ui-comparison` |
| 4.9.6 | Settings view | `fig:ui-settings` |
| 4.9.7 | Previous Sessions view | `fig:ui-previoussessions` |
| 4.10.1 | Assistant join screen | `fig:asst-join` |
| 4.10.2 | Assistant unassigned/queue | `fig:asst-unassigned` |
| 4.10.3 | Assistant assigned card (with RAG) | `fig:asst-assigned` |

### Family 2 — Architecture / data-flow diagrams

| § | Slot | `\label{}` |
|---|---|---|
| 4.3 (preamble) | System architecture — 3 frontends + shared core + shared state file | `fig:arch-v2` |
| 4.4 (preamble) | Data pipeline flow — endpoint → parse → normalise → cache → scoring | `fig:pipeline-flow` |

Recommendation: draw both as TikZ. Ch3 Fig 6 is design-level (logical layers); Ch4 needs an implementation-level architecture diagram that shows **process boundaries and version split** — V1 instructor (Streamlit, 8501), V1 assistant (Streamlit, 8502), V2 FastAPI (8000) serving the V2 React SPA, browser and mobile clients, OpenAI, ChromaDB — and the shared `lab_session.json` file in the middle. Label the V1 and V2 boxes clearly so the diagram itself communicates the evolution framing.

### Family 3 — Code-snippet images

| § | Slot | `\label{}` |
|---|---|---|
| 4.3.4 | `lab_state` filelock pattern | `fig:code-lablock` |
| 4.3.5 | Deferred-actions pattern | `fig:code-deferred` |
| 4.6.1 | OpenAI batch call | `fig:code-openai` |
| 4.8.3 | RAG generation prompt | `fig:code-ragprompt` |

**Critical:** screenshots from the editor, not LaTeX `lstlisting`. The user's prior chapter (F221611.pdf §5) uses dark-themed code-image figures throughout — this is the established convention. Take these **after** the de-AI cleanup pass (Part F) so the code in the figure looks like the user's own.

### Family 4 — Typeset tables

| § | Slot | `\label{}` |
|---|---|---|
| 4.2 | Technology stack | `tab:techstack-v2` |
| 4.6.2 | 7-signal struggle | `tab:struggle-7sig` |
| 4.6.3 | 5-signal difficulty | `tab:difficulty-5sig` |
| 4.8.3 | BKT defaults | `tab:bkt-defaults` |
| 4.9.0 | Views comparison (Streamlit vs React) | `tab:views-comparison` |
| 4.12 | Problems and resolutions | `tab:problems` |

Optional (only if helpful):
- `tab:cache-hierarchy` (§4.4.3 cache layers)
- `tab:improved-redistribution` (§4.7.4 weight redistribution cases)

---

## Part D — Citation hooks

The brief lists what `\cite{}` calls Ch4 expects; the user inserts them inline as they write. Bibkeys not yet in `references.bib` are flagged for **Step 12 (Polish pass)**, not added now.

| Hook | Used in | Suggested bibkey | Status |
|---|---|---|---|
| L-BFGS-B optimiser | §4.7.2, §4.7.3 | `byrdLBFGSB1995` (Byrd, Lu, Nocedal, Zhu 1995) | verify in references.bib; add at Step 12 if absent |
| Knowledge Tracing (Corbett & Anderson 1995) | §4.7.3 | `corbettKnowledgeTracingModeling1995` | already cited in Ch3 |
| RAG (Lewis et al. 2020) | §4.8.1 | `lewisRetrievalAugmentedGenerationKnowledgeIntensive2020` | already cited in Ch3 |
| Sentence-BERT (Reimers & Gurevych 2019) | §4.8.2 (optional) | `reimersSentenceBERTSentenceEmbeddings2019` | verify; optional |
| ROC-AUC (Fawcett 2006 or equivalent) | §4.7.3 — cross-ref with Ch5 §5.1 | `fawcettIntroductionROCAnalysis2006` | defer to Step 6/12 |
| Rasch model (Rasch 1960) | §4.7.2 (optional) | `raschProbabilisticModels1960` | verify; optional but expected by markers |
| Streamlit / FastAPI / React | §4.3 | software cite — footnote URL is fine | optional, no formal cite |
| ChromaDB / sentence-transformers / OpenAI | §4.8 | software cite — footnote URL | optional |

**Per the writing-workflow memory, this brief does not embed citations into prose** — the user inserts them while writing. The Polish pass (Step 12) handles missing bibkeys.

---

## Part E — Voice and tone reminder

Two reference points. The actual register sits between them.

1. **[`Report/main-sections/design-and-architecture.tex`](../../../../Report/main-sections/design-and-architecture.tex) (Ch3)** — formal register. Present tense, third-person passive or first-person plural for design choices ("we propose", "we adopt"). British spelling (`colour`, `modelling`, `normalised`). Inline `\cite{}`, displayed equations numbered when later referenced.
2. **[`previous-works/F221611.pdf`](../../../../previous-works/F221611.pdf) §5** — own prior implementation chapter; sets the *tone* for implementation prose specifically. First-person singular acceptable for build decisions ("I used", "I decided"), short declarative sentences, bullet lists for per-component breakdowns, code snippets and screenshots interleaved with 2–4-sentence explanatory paragraphs.

**For this Ch4**, write in the Ch3 register by default but allow first-person plural ("we") for design choices where it reads naturally. Avoid first-person singular ("I") — this is a co-supervised dissertation; "we" is the right pronoun. The two references combine into: **declarative, present-tense, technical, British-spelled, with `\cite{}` inline and the occasional "we" for design framing.**

**Forbidden patterns:**
- **No supervisor attribution inline.** Dr Batmaz's contribution to the RAG architecture is acknowledged in the Acknowledgments section, not in §4.8.
- **No future tense.** The chapter describes a deployed system. "will be implemented", "is planned", "we intend to" — all banned.
- **No "proof of concept" / "prototype" / "version 1".** The implementation IS the deliverable.

---

## Part F — Code de-AI pre-pass

The user flagged a concern: "I may need to clean up code so it doesn't look too AI-generated." This is a real concern for the code snippets captured in §4.6.1, §4.3.4, §4.3.5, and §4.8.3 (and again at Step 11 for Appendix A).

**Symptoms to watch for** in [`code/learning_dashboard/`](../../../../code/learning_dashboard/):

- Multi-paragraph docstrings on private helpers (one-line comments are more in line with the user's own prior work)
- Redundant inline annotations: `# Note: this is necessary because …` on lines whose purpose is obvious
- Defensive over-validation: `if value is None or value == "" or len(str(value)) == 0:` where one check would do
- Type hints on every local variable, not just function signatures
- Helpers that are called from exactly one place and could be inlined
- Excessively long variable names (`processed_dataframe_with_normalised_columns` where `df` works in context)
- Perfectly-spaced blank lines between every micro-section
- `from __future__ import annotations` where it isn't strictly needed (mostly harmless, but flag)

**Recommended order** (do this **before Step 11**, not now — Ch4 prose only names constants and does not embed code, so cleanup does not block writing):

1. Run the [simplify skill](../../../../) once on each of: `analytics.py`, `data_loader.py`, `models/irt.py`, `models/bkt.py`, `models/improved_struggle.py`, `models/measurement.py`, `rag.py`. Review the diff each time before accepting.
2. Manually re-read `lab_state.py`, `instructor_app.py`, `lab_app.py` — these are the files that contain the most "narrative" code (callbacks, state transitions) and benefit most from a human pass.
3. Re-take any code-snippet screenshots (§4.6.1, §4.3.4, §4.3.5, §4.8.3) **after** the cleanup is done.
4. Defer Appendix A code listing capture (Step 11) until the cleanup is complete.

The cleanup is **the user's call** on timing — flagged here so it does not get forgotten, but not on the Step 5 critical path.

---

## Part G — Lessons from F221611 marker feedback (mark 72)

Both markers' criticisms of the prior submission are folded into the brief at specific points; this section is a single place to verify the lessons were honoured before submitting.

### Marker 1 — "very much focused on coding and does not contain any math modeling part"

**Implication for Ch4:** every analytics and model subsection re-states its formula in compact form before describing the implementation. This is encoded as the **Maths recap** line in the Part B template. It is **required** for every §4.6.x and §4.7.x subsection — non-negotiable.

The full derivations stay in Ch3 (§3.3, §3.4) and Appendix E; Ch4 reaches back to them by equation reference rather than re-deriving. This way:
- Ch4 does not bloat into a maths chapter
- The reader who skipped Ch3 still sees, on every model subsection, the equation the implementation realises
- The chapter as a whole reads as *maths materialised in code*, which is what the marker wanted

### Marker 2 — "add aims & objective and original contributions subsections in Chapter 1, and present more about any similar existing application platform … plus comparison study"

Three threads, split by where they belong:

| Thread | Where it lives | Status in this brief |
|---|---|---|
| Aims & objective subsection in Ch1 | Step 4 (Ch1 cleanup) — out of scope for Ch4 | Cross-referenced as a note for Step 4 |
| Original contributions subsection in Ch1 | Step 4 (Ch1 cleanup) — out of scope for Ch4 | Cross-referenced as a note for Step 4 |
| Similar-existing-platforms survey | Step 4 (Ch2 lit review extension) — out of scope for Ch4 | Cross-referenced as a note for Step 4 |
| **Comparison study** | **Inside Ch4** via the V1 → V2 evolution narrative (§4.3.3 "Why V2?" + §4.9.0 `tab:views-comparison`) | **Addressed** |

### What this changes in the overall shape

The prior submission's implementation chapter read: per-component subsection → bullets → screenshot. No analytical lens. Ch4 here does three things in each subsection:

1. **States the maths** (one line, equation reference back to Ch3) — Marker 1
2. **Describes the implementation** — the normal implementation-chapter content
3. **Comments on observed behaviour or trade-off** — the analytical lens

The view subsections (§4.9.x, §4.10.x) skip step 1 since they are interface concerns; the analytics and model subsections (§4.6.x, §4.7.x) carry all three.

---

## Part H — Drop-in LaTeX skeleton

A single paste-ready block. Open [`Report/main-sections/implementation.tex`](../../../../Report/main-sections/implementation.tex), select everything from line 1 to end-of-file, delete, paste the block below. Then `pdflatex Report/main.tex` twice to regenerate the ToC.

**Style notes:**
- Tables use plain `tabular` with `|p{X\textwidth}|` columns and `\hline` — matching the convention already used in Ch3 (`design-and-architecture.tex`). The same data appears in Part B above using `tabularx` + `booktabs` for visual readability; if you prefer that style, add `\usepackage{tabularx}` and `\usepackage{booktabs}` to [`Report/main.tex`](../../../../Report/main.tex) preamble and swap the table bodies. The Part H versions below compile against the **current** preamble unchanged.
- All figure slots are commented out so `pdflatex` does not error on missing PNGs. Uncomment each one during Step 8 once the screenshot lands in `Report/figures/`.
- Each empty subsection carries one `% TODO: write per Ch4 Rewrite Brief §X.Y` line as a backlink to the Part B block that owns it.
- The stale V1-prototype prose from the previous draft is preserved at the bottom of the file inside a `\begin{comment}...\end{comment}` block (the `comment` package is already loaded in `main.tex`). Delete that block once you confirm nothing in it is worth salvaging.

```latex
% =============================================================
% Chapter 4 — Implementation
% Drop-in skeleton from Ch4 Rewrite Brief Part H (2026-05-20).
% V1 = Streamlit stack (code/);  V2 = React + FastAPI stack (code2/).
% Body prose is left as TODOs — author each subsection against the
% corresponding block in Ch4 Rewrite Brief Part B.
% =============================================================

\section{Implementation}

% TODO: write per Ch4 Rewrite Brief §4.1 — Implementation Overview
% Lead with "two versions, both production-quality": V1 (code/, Streamlit) and
% V2 (code2/, React + FastAPI). Both share the analytical core and the
% file-locked lab_session.json. V2 is an evolution of V1, not an alternative
% — both are deployed. Do not use "prototype" / "proof of concept" anywhere.

\subsection{Implementation Overview}

% TODO: write per Ch4 Rewrite Brief §4.1

\subsection{Technology Stack}

% TODO: 1--2 framing sentences above the table — see Ch4 Rewrite Brief §4.2

\begin{table}[H]
    \centering
    \begin{tabular}{|p{0.22\textwidth}|p{0.58\textwidth}|p{0.12\textwidth}|}
    \hline
    \textbf{Component} & \textbf{Role} & \textbf{Version} \\
    \hline
    \hline
    Python 3.11 & Implementation language for the analytical core and both backends & Both \\
    \hline
    Streamlit ($\geq$1.32) & Instructor and assistant dashboard UI; session-state model & V1 \\
    \hline
    streamlit-autorefresh ($\geq$1.0.1) & Browser-side polling for live updates & V1 \\
    \hline
    Plotly ($\geq$5.18) & Interactive charts and leaderboards & V1 \\
    \hline
    FastAPI ($\geq$0.115) & HTTP API exposing the analytical core to the React frontend & V2 \\
    \hline
    Uvicorn ($\geq$0.30) & ASGI server (with reload) for FastAPI & V2 \\
    \hline
    React 18 + Vite + TypeScript & Single-page application; seven runtime themes & V2 \\
    \hline
    pandas ($\geq$2.1), NumPy ($\geq$1.26) & In-memory data frame and vectorised scoring & Both \\
    \hline
    SciPy ($\geq$1.11) & L-BFGS-B optimiser for IRT (Rasch) and BKT MLE fits & Both \\
    \hline
    scikit-learn ($\geq$1.4) & TF-IDF + KMeans for mistake clustering; \texttt{roc\_auc\_score} for BKT predictive AUC & Both \\
    \hline
    OpenAI Python SDK ($\geq$1.0) & Batched incorrectness scoring (gpt-4o-mini) and RAG generation & Both \\
    \hline
    sentence-transformers ($\geq$2.2), ChromaDB ($\geq$0.4) & Local MiniLM-L6-v2 embeddings + persistent vector store for RAG & Both \\
    \hline
    filelock ($\geq$3.12) & Cross-process write lock for the shared lab-session JSON & Both \\
    \hline
    requests ($\geq$2.31) & HTTP client against the lab data endpoint & Both \\
    \hline
    cachetools ($\geq$5.3) & TTL cache for the FastAPI analytical layer & V2 \\
    \hline
    \end{tabular}
    \caption{Technologies and libraries used in V1 (Streamlit) and V2 (React + FastAPI)}
    \label{tab:techstack-v2}
\end{table}

\subsection{System Structure}

% TODO: 1 opening paragraph — see Ch4 Rewrite Brief §4.3 preamble
% Reference fig:arch-v2 in the prose.

% TODO: insert figure — architecture diagram (TikZ recommended) — see Ch4 Rewrite Brief Part C Family 2
% \begin{figure}[H]
%     \centering
%     \includegraphics[width=0.9\textwidth]{figures/arch-v2.pdf}
%     \caption{Architecture of the deployed system: V1 (instructor and assistant Streamlit apps) and V2 (React + FastAPI single process) share a single analytical core and a file-locked lab-session state.}
%     \label{fig:arch-v2}
% \end{figure}

\subsubsection{V1 --- Instructor Process (Streamlit)}

% TODO: write per Ch4 Rewrite Brief §4.3.1

\subsubsection{V1 --- Assistant Process (Streamlit, mobile)}

% TODO: write per Ch4 Rewrite Brief §4.3.2

\subsubsection{V2 --- React + FastAPI}

% TODO: write per Ch4 Rewrite Brief §4.3.3 — open with the "Why V2?" paragraph naming concrete V1 limitations (single-threaded reruns, weak theming, no native async, no SPA navigation)

% TODO: insert figure — V2 In-Class view screenshot — see Ch4 Rewrite Brief Part C Family 1
% \begin{figure}[H]
%     \centering
%     \includegraphics[width=0.9\textwidth]{figures/v2-inclass.png}
%     \caption{Screenshot of V2 (React + FastAPI) showing the In-Class view in the \emph{scifi} theme; the analytical layer is identical to V1.}
%     \label{fig:v2-inclass}
% \end{figure}

\subsubsection{Shared Runtime State}

% TODO: write per Ch4 Rewrite Brief §4.3.4

% TODO: insert figure — filelock pattern code-snippet image — see Ch4 Rewrite Brief Part C Family 3
% \begin{figure}[H]
%     \centering
%     \includegraphics[width=0.85\textwidth]{figures/code-lablock.png}
%     \caption{File-locked read/write pattern for the shared lab-session state.}
%     \label{fig:code-lablock}
% \end{figure}

\subsubsection{Deferred-Actions Pattern}

% TODO: write per Ch4 Rewrite Brief §4.3.5

% TODO: insert figure — deferred-actions pattern code-snippet image — see Ch4 Rewrite Brief Part C Family 3
% \begin{figure}[H]
%     \centering
%     \includegraphics[width=0.85\textwidth]{figures/code-deferred.png}
%     \caption{The deferred-actions pattern used to mutate session state without violating Streamlit's widget-instantiation rule.}
%     \label{fig:code-deferred}
% \end{figure}

\subsection{Data Pipeline}

% TODO: 1 opening paragraph summarising the pipeline — see Ch4 Rewrite Brief §4.4 preamble
% Reference fig:pipeline-flow in the prose.

% TODO: insert figure — data-pipeline flow (TikZ recommended) — see Ch4 Rewrite Brief Part C Family 2
% \begin{figure}[H]
%     \centering
%     \includegraphics[width=0.9\textwidth]{figures/pipeline-flow.pdf}
%     \caption{Data pipeline from the lab-session endpoint to the scoring layer.}
%     \label{fig:pipeline-flow}
% \end{figure}

\subsubsection{Endpoint Retrieval and Parsing}

% TODO: write per Ch4 Rewrite Brief §4.4.1

\subsubsection{Data Normalisation and Structuring}

% TODO: write per Ch4 Rewrite Brief §4.4.2

\subsubsection{Caching Strategy}

% TODO: write per Ch4 Rewrite Brief §4.4.3

\subsection{Session Management}

% TODO: 1 opening sentence — see Ch4 Rewrite Brief §4.5 preamble

\subsubsection{Live Session Lifecycle}

% TODO: write per Ch4 Rewrite Brief §4.5.1

% TODO: insert figure — instructor sidebar during live session — see Ch4 Rewrite Brief Part C Family 1
% \begin{figure}[H]
%     \centering
%     \includegraphics[width=0.5\textwidth]{figures/session-live.png}
%     \caption{Instructor sidebar during a live session, showing the join code, elapsed time, and roster of joined assistants.}
%     \label{fig:session-live}
% \end{figure}

\subsubsection{Saved Session History and Restoration}

% TODO: write per Ch4 Rewrite Brief §4.5.2

\subsection{Analytics Implementation}

% TODO: 1 opening paragraph — see Ch4 Rewrite Brief §4.6 preamble

\subsubsection{Incorrectness Scoring}

% TODO: write per Ch4 Rewrite Brief §4.6.1 — REQUIRED Maths recap line (Marker-1 check)

% TODO: insert figure — batched OpenAI call code-snippet — see Ch4 Rewrite Brief Part C Family 3
% \begin{figure}[H]
%     \centering
%     \includegraphics[width=0.85\textwidth]{figures/code-openai.png}
%     \caption{Batched OpenAI call for incorrectness scoring.}
%     \label{fig:code-openai}
% \end{figure}

\subsubsection{Baseline Student Struggle Model}

% TODO: write per Ch4 Rewrite Brief §4.6.2 — REQUIRED Maths recap line (Marker-1 check)

\begin{table}[H]
    \centering
    \begin{tabular}{|p{0.10\textwidth}|p{0.28\textwidth}|p{0.45\textwidth}|p{0.07\textwidth}|}
    \hline
    \textbf{Symbol} & \textbf{config.py key} & \textbf{Meaning} & \textbf{Weight} \\
    \hline
    \hline
    $N$            & \texttt{STRUGGLE\_WEIGHT\_N}   & Submission count (min-max normalised)                & 0.10 \\
    \hline
    $T$            & \texttt{STRUGGLE\_WEIGHT\_T}   & Time active in the session (min-max normalised)      & 0.10 \\
    \hline
    $I$            & \texttt{STRUGGLE\_WEIGHT\_I}   & Mean incorrectness across submissions                & 0.20 \\
    \hline
    $R$            & \texttt{STRUGGLE\_WEIGHT\_R}   & Retry rate (repeat attempts on the same question)    & 0.10 \\
    \hline
    $A$            & \texttt{STRUGGLE\_WEIGHT\_A}   & Recent incorrectness, exponential time decay (30-min half-life) & 0.38 \\
    \hline
    $D$            & \texttt{STRUGGLE\_WEIGHT\_D}   & Improvement-slope coefficient (min-max normalised)   & 0.05 \\
    \hline
    $\mathrm{REP}$ & \texttt{STRUGGLE\_WEIGHT\_REP} & Answer repetition rate (exact-match repeats / total) & 0.07 \\
    \hline
    \end{tabular}
    \caption{Components of the baseline student struggle score with default weights}
    \label{tab:struggle-7sig}
\end{table}

\subsubsection{Baseline Question Difficulty Model}

% TODO: write per Ch4 Rewrite Brief §4.6.3 — REQUIRED Maths recap line (Marker-1 check)

\begin{table}[H]
    \centering
    \begin{tabular}{|p{0.10\textwidth}|p{0.30\textwidth}|p{0.43\textwidth}|p{0.07\textwidth}|}
    \hline
    \textbf{Symbol} & \textbf{config.py key} & \textbf{Meaning} & \textbf{Weight} \\
    \hline
    \hline
    $C$ & \texttt{DIFFICULTY\_WEIGHT\_C} & Incorrect-attempt rate (raw ratio)               & 0.28 \\
    \hline
    $T$ & \texttt{DIFFICULTY\_WEIGHT\_T} & Mean time per student (min-max normalised)       & 0.12 \\
    \hline
    $A$ & \texttt{DIFFICULTY\_WEIGHT\_A} & Mean attempts per student (min-max normalised)   & 0.20 \\
    \hline
    $F$ & \texttt{DIFFICULTY\_WEIGHT\_F} & Mean incorrectness score                          & 0.20 \\
    \hline
    $P$ & \texttt{DIFFICULTY\_WEIGHT\_P} & First-attempt failure rate                        & 0.20 \\
    \hline
    \end{tabular}
    \caption{Components of the baseline question difficulty score with default weights}
    \label{tab:difficulty-5sig}
\end{table}

\subsubsection{Collaborative Filtering}

% TODO: write per Ch4 Rewrite Brief §4.6.4 — REQUIRED Maths recap line (Marker-1 check)

\subsubsection{Mistake Clustering}

% TODO: write per Ch4 Rewrite Brief §4.6.5

\subsection{Advanced Model Implementation}

% TODO: 1 opening paragraph — see Ch4 Rewrite Brief §4.7 preamble

\subsubsection{Measurement Confidence}

% TODO: write per Ch4 Rewrite Brief §4.7.1 — REQUIRED Maths recap line (Marker-1 check)

\subsubsection{Item Response Theory (IRT) Difficulty}

% TODO: write per Ch4 Rewrite Brief §4.7.2 — REQUIRED Maths recap line + \cite{byrdLBFGSB1995} (verify bibkey, add at Step 12 if missing)

\subsubsection{Bayesian Knowledge Tracing (BKT) Mastery}

% TODO: write per Ch4 Rewrite Brief §4.7.3 — REQUIRED Maths recap line + \cite{corbettKnowledgeTracingModeling1995} (already cited in Ch3)

\begin{table}[H]
    \centering
    \begin{tabular}{|p{0.12\textwidth}|p{0.55\textwidth}|p{0.10\textwidth}|p{0.13\textwidth}|}
    \hline
    \textbf{Symbol} & \textbf{Meaning} & \textbf{Default} & \textbf{Fit bounds} \\
    \hline
    \hline
    $P(L_0)$ & Prior probability of knowing the skill                    & 0.30 & [0.0, 1.0] \\
    \hline
    $P(T)$   & Probability of learning per opportunity                    & 0.10 & [0.0, 1.0] \\
    \hline
    $P(G)$   & Probability of guessing correctly while not learned        & 0.20 & [0.0, 0.5] \\
    \hline
    $P(S)$   & Probability of slipping (wrong) while learned              & 0.10 & [0.0, 0.5] \\
    \hline
    \end{tabular}
    \caption{Default Bayesian Knowledge Tracing parameters and their permitted ranges}
    \label{tab:bkt-defaults}
\end{table}

\subsubsection{Improved Struggle Model}

% TODO: write per Ch4 Rewrite Brief §4.7.4 — REQUIRED Maths recap line (Marker-1 check)

\subsection{RAG Suggested Feedback}

% TODO: 1 opening paragraph — see Ch4 Rewrite Brief §4.8 preamble (no inline supervisor attribution)

\subsubsection{Hybrid Two-Layer Architecture}

% TODO: write per Ch4 Rewrite Brief §4.8.1 — include \cite{lewisRetrievalAugmentedGenerationKnowledgeIntensive2020}

\subsubsection{Embedding Model (all-MiniLM-L6-v2)}

% TODO: write per Ch4 Rewrite Brief §4.8.2

\subsubsection{Generation and Prompting}

% TODO: write per Ch4 Rewrite Brief §4.8.3

% TODO: insert figure — RAG generation prompt code-snippet — see Ch4 Rewrite Brief Part C Family 3
% \begin{figure}[H]
%     \centering
%     \includegraphics[width=0.85\textwidth]{figures/code-ragprompt.png}
%     \caption{RAG generation prompt --- system and user messages used to produce assistant focus suggestions.}
%     \label{fig:code-ragprompt}
% \end{figure}

\subsubsection{Suggestion Caching}

% TODO: write per Ch4 Rewrite Brief §4.8.4

\subsubsection{Graceful Degradation and Privacy}

% TODO: write per Ch4 Rewrite Brief §4.8.5

\subsection{Instructor System Views}

% TODO: 1 opening paragraph framing the V1-vs-V2 view parity — see Ch4 Rewrite Brief §4.9.0
% This is the Marker-2 comparison-study artefact.

\begin{table}[H]
    \centering
    \begin{tabular}{|p{0.18\textwidth}|p{0.40\textwidth}|p{0.10\textwidth}|p{0.20\textwidth}|}
    \hline
    \textbf{View} & \textbf{Function (purpose)} & \textbf{V1} & \textbf{V2} \\
    \hline
    \hline
    In Class            & Live struggle and difficulty leaderboards, CF panel & Yes & Yes \\
    \hline
    Student Detail      & Per-student signal breakdown, timeline              & Yes & Yes \\
    \hline
    Question Detail     & Mistake clusters, top strugglers                    & Yes & Yes (+ extra ``Top strugglers'' table) \\
    \hline
    Data Analysis       & Cohort-level summaries across academic weeks        & Yes & Yes \\
    \hline
    Model Comparison    & Baseline vs IRT, baseline vs improved struggle      & Yes & Yes \\
    \hline
    Settings            & Model toggles, CF threshold, BKT sliders            & Yes & Yes (+ theme + accent picker) \\
    \hline
    Previous Sessions   & List and delete saved sessions                      & Yes & Yes \\
    \hline
    Session Progression & Time-bucket replay over 20 buckets                  & No  & Yes \\
    \hline
    \end{tabular}
    \caption{Instructor views in V1 (Streamlit) and V2 (React + FastAPI), with view-level parity status}
    \label{tab:views-comparison}
\end{table}

\subsubsection{In-Class View}

% TODO: write per Ch4 Rewrite Brief §4.9.1

% TODO: insert figure — In-Class view screenshot — see Ch4 Rewrite Brief Part C Family 1
% \begin{figure}[H]
%     \centering
%     \includegraphics[width=0.9\textwidth]{figures/ui-inclass.png}
%     \caption{Screenshot of the In-Class view, showing the struggle and difficulty leaderboards and the collaborative-filtering diagnostic panel.}
%     \label{fig:ui-inclass}
% \end{figure}

\subsubsection{Student Detail View}

% TODO: write per Ch4 Rewrite Brief §4.9.2

% TODO: insert figure — Student Detail view screenshot — see Ch4 Rewrite Brief Part C Family 1
% \begin{figure}[H]
%     \centering
%     \includegraphics[width=0.9\textwidth]{figures/ui-studentdetail.png}
%     \caption{Screenshot of the Student Detail view, with per-signal breakdown and submission timeline.}
%     \label{fig:ui-studentdetail}
% \end{figure}

\subsubsection{Question Detail View}

% TODO: write per Ch4 Rewrite Brief §4.9.3

% TODO: insert figure — Question Detail view screenshot — see Ch4 Rewrite Brief Part C Family 1
% \begin{figure}[H]
%     \centering
%     \includegraphics[width=0.9\textwidth]{figures/ui-questiondetail.png}
%     \caption{Screenshot of the Question Detail view, with labelled mistake clusters.}
%     \label{fig:ui-questiondetail}
% \end{figure}

\subsubsection{Data Analysis View}

% TODO: write per Ch4 Rewrite Brief §4.9.4

% TODO: insert figure — Data Analysis view screenshot — see Ch4 Rewrite Brief Part C Family 1
% \begin{figure}[H]
%     \centering
%     \includegraphics[width=0.9\textwidth]{figures/ui-dataanalysis.png}
%     \caption{Screenshot of the Data Analysis view across an academic week.}
%     \label{fig:ui-dataanalysis}
% \end{figure}

\subsubsection{Model Comparison View}

% TODO: write per Ch4 Rewrite Brief §4.9.5

% TODO: insert figure — Model Comparison view screenshot — see Ch4 Rewrite Brief Part C Family 1
% \begin{figure}[H]
%     \centering
%     \includegraphics[width=0.9\textwidth]{figures/ui-comparison.png}
%     \caption{Screenshot of the Model Comparison view (student and question tabs).}
%     \label{fig:ui-comparison}
% \end{figure}

\subsubsection{Settings View}

% TODO: write per Ch4 Rewrite Brief §4.9.6

% TODO: insert figure — Settings view screenshot — see Ch4 Rewrite Brief Part C Family 1
% \begin{figure}[H]
%     \centering
%     \includegraphics[width=0.9\textwidth]{figures/ui-settings.png}
%     \caption{Screenshot of the Settings view showing model toggles, CF threshold, and BKT sliders.}
%     \label{fig:ui-settings}
% \end{figure}

\subsubsection{Previous Sessions View}

% TODO: write per Ch4 Rewrite Brief §4.9.7

% TODO: insert figure — Previous Sessions view screenshot — see Ch4 Rewrite Brief Part C Family 1
% \begin{figure}[H]
%     \centering
%     \includegraphics[width=0.9\textwidth]{figures/ui-previoussessions.png}
%     \caption{Screenshot of the Previous Sessions view.}
%     \label{fig:ui-previoussessions}
% \end{figure}

\subsection{Lab Assistant System}

% TODO: 1 opening paragraph — see Ch4 Rewrite Brief §4.10 preamble

\subsubsection{Session Join Flow}

% TODO: write per Ch4 Rewrite Brief §4.10.1

% TODO: insert figure — assistant join screen screenshot — see Ch4 Rewrite Brief Part C Family 1
% \begin{figure}[H]
%     \centering
%     \includegraphics[width=0.5\textwidth]{figures/asst-join.png}
%     \caption{Screenshot of the lab assistant join screen on mobile.}
%     \label{fig:asst-join}
% \end{figure}

\subsubsection{Waiting and Assignment States}

% TODO: write per Ch4 Rewrite Brief §4.10.2

% TODO: insert figure — assistant unassigned/queue screenshot — see Ch4 Rewrite Brief Part C Family 1
% \begin{figure}[H]
%     \centering
%     \includegraphics[width=0.5\textwidth]{figures/asst-unassigned.png}
%     \caption{Screenshot of the lab assistant unassigned state with the queue of strugglers.}
%     \label{fig:asst-unassigned}
% \end{figure}

\subsubsection{Live Assistant Allocation and Mark-Helped}

% TODO: write per Ch4 Rewrite Brief §4.10.3

% TODO: insert figure — assistant assigned card screenshot — see Ch4 Rewrite Brief Part C Family 1
% \begin{figure}[H]
%     \centering
%     \includegraphics[width=0.5\textwidth]{figures/asst-assigned.png}
%     \caption{Screenshot of the lab assistant assigned-student card with RAG focus suggestions.}
%     \label{fig:asst-assigned}
% \end{figure}

\subsection{Problems Encountered and Solutions}

% TODO: 1 framing sentence above the table — see Ch4 Rewrite Brief §4.11
% Note: sound-effects discussion now lives inside §4.9.6 Settings View (the toggle is there); old standalone §4.11 Sound Effects subsection removed during 2026-05-20 layout refinement.

\begin{table}[H]
    \centering
    \begin{tabular}{|p{0.20\textwidth}|p{0.36\textwidth}|p{0.36\textwidth}|}
    \hline
    \textbf{Problem} & \textbf{Description} & \textbf{Resolution} \\
    \hline
    \hline
    Endpoint format drift & The lab endpoint occasionally returned single-payload XML instead of newline-delimited JSON, breaking the parser. & Added a format-detection step and a dual parser; both branches normalise into the same DataFrame schema. \\
    \hline
    OpenAI cold-start cost & First Streamlit rerun on a new session would block for tens of seconds while every submission was scored. & Two-layer cache (in-process and disk-persisted JSON) and \texttt{SCORING\_PER\_RUN\_CAP = 500} so the first rerun stays responsive; remaining pairs score in subsequent runs. \\
    \hline
    Streamlit's widget-instantiation rule & Mutating session state after a widget has been instantiated raises \texttt{StreamlitAPIException}, breaking obvious-looking callbacks. & Deferred-actions pattern (§4.3.5): callbacks set \texttt{pending\_*} flags; the next rerun applies them before any widget is built. \\
    \hline
    Cross-process write conflicts & V1 (two Streamlit processes) and V2 (one FastAPI process) can all write the same \texttt{lab\_session.json}; na\"{\i}ve writes corrupt the file. & \texttt{filelock.FileLock} with a 5\,s timeout on every read and write; atomic \texttt{os.replace} from a \texttt{.tmp} file so partial writes never appear. \\
    \hline
    V2 startup latency & First request to V2 would block on cold scoring and cold RAG build under the FastAPI event loop. & \texttt{lifespan} handler runs scoring, BKT/IRT fits, and ChromaDB build in the background at startup; V2 loads against a warm cache. V1 addresses the same cold-start problem with the layered caches in §4.4.3. \\
    \hline
    BKT identifiability on single-class data & When every observed attempt is graded the same way, the BKT log-likelihood surface degenerates and the fit returns useless parameters. & The fit refuses (and reports a diagnostic listing the incorrectness distribution and the likely cause) when fewer than two classes are present. \\
    \hline
    \end{tabular}
    \caption{Implementation problems encountered and their resolutions}
    \label{tab:problems}
\end{table}

% =============================================================
% Preserved from the previous V1-prototype draft.  Wrapped in
% \begin{comment} so it does not render.  Reference only — delete
% this whole block once you confirm nothing inside is worth
% salvaging into the new §4.1 / §4.4 prose.
% =============================================================

\begin{comment}
This chapter describes the implemented version of the real-time lab support system.
Earlier work focused on validating the endpoint, testing the data pipeline, and establishing a working dashboard with basic dashboard prototype.
The current implementation Version 2 (v2) builds on this foundation, allowing for a live instructor dashboard, a lab assistant application that works with the instructor dashboard, session history as well as both baseline and more advanced models.

The implementation is interval-based rather than event-based.
However, it provides a full end-to-end workflow, from endpoint ingestion, parsing, normalisation to live scoring, student prioritisation and assistant coordination.
The system represents a functional tool to support instructors and assistants during labs allowing for improved learning outcomes, with the potential for further refinement and expansion in future iterations.

The implementation represents Version 1 of the dashboard. Version 1 was implemented to ensure end-to-end functionality worked as planned and to experiment with data visualisation rather than to deploy the whole system proposed.

Version 1 focused on establishing a working data pipeline capable of processing live interaction data during labs, aggregating student activity at the lab level, and presenting indicators in near real time. This provides the foundation for the proposed system. By working on Version 1, I have familiarised myself with the relevant technology and the data pipeline.

The implemented system addresses the core objectives of the project by supporting live monitoring of student progress, prioritisation of students who are struggling, identifications of difficult questions so that lab teachers can go through those questions as a class, and allocation of lab assistants during sessions.

The implementation is made up of a number of components essential to the system's functionality. First

Version 1 implements an interval-based data pipeline designed to support near real-time monitoring during lab sessions. The pipeline proceeds as follows:
\begin{enumerate}
    \item \textbf{Data Retrieval: }At fixed intervals the Python application re-requests the full dataset from the existing PHP endpoint. This refresh is implemented within the Python code. The refresh helps ensure that metrics are up to date.
    \item \textbf{Data Parsing: }The retrieved response, formatted as JSON with embedded XML strings, is parsed within Python. Relevant fields such as question, student and timestamps are extracted
    \item \textbf{Data Structuring: }Parsed records are transformed into an immediate representation suitable for analysis
    \item \textbf{Metric Computation: }A naive metric approach was used, where thresholds are used for the attempt amount of a question. This was done to demonstrate the concept
    \item \textbf{Dashboard Update: }The dashboard is refreshed using the newly computed values, providing an updated view of lab activity each time the Python refresh executes
\end{enumerate}
More advanced modelling described in the Design Chapter is not yet integrated and is reserved for the proposed system.

\subsection{User Interface and Interaction Design}
\subsubsection{Auto Refresh and State Persistence}
\subsubsection{Sound Effects and Visual Theme}

\subsection{Dashboard and UI}
The Version 1 dashboard provides a live visual overview of student activity. It is implemented as a Streamlit application that integrates data retrieval, metric computation and visualisation in a Python workflow.

The primary aim of the dashboard is to support fast awareness for instructors and lab assistants. Visualisations focus on simple, predictable indicators, some of which are not relevant but are a proof of concept and testing of the data. The indicators are presented through interactive Plotly charts, providing an intuitive user interface.

Basic interactivity is supported through Streamlit controls, enabling users to switch between different views. The dashboard refreshes automatically, following each refresh cycle, ensuring up-to-date information is displayed.

At this stage, the dashboard serves as a functional prototype for testing and validating the feasibility of live monitoring during labs. Most advanced features, such as model-driven prioritisation, assistant allocation and smart device notifications, are to be implemented in the later iteration.
\end{comment}
```

---

## Closing checklist (for the user)

Before considering Ch4 done:

- [ ] Every subsection in Part A has been written
- [ ] Every §4.6.x and §4.7.x subsection has a Maths recap line (Marker-1 check)
- [ ] §4.3.3 contains the "Why V2?" paragraph naming concrete V1 limitations (Marker-2 check)
- [ ] `tab:views-comparison` is present in §4.9.0 with V1 / V2 columns (Marker-2 check)
- [ ] V1 is never called "prototype", "proof of concept", or "alternative" anywhere in the chapter
- [ ] All 11 UI screenshot slots in Part C Family 1 are marked `[TODO: insert figure: …]` in the LaTeX — actual PNGs land at Step 8
- [ ] All 4 code-snippet slots in Part C Family 3 are marked `[TODO: insert figure: …]` — actual PNGs land **after** the de-AI cleanup pass (Part F)
- [ ] All 6 typeset tables in Part C Family 4 are pasted in (using the LaTeX given in Part B)
- [ ] `pdflatex` compiles `main.tex` with no errors; outstanding warnings are `\cite{}` (Step 12) and `\ref{}` to unfilled figures (Step 8)
- [ ] No mention of "Version 1", "prototype", "proof of concept" anywhere in the chapter
- [ ] No future tense ("will be", "is planned")
- [ ] No inline supervisor attribution
- [ ] Marked off in [Full Roadmap](Full%20Roadmap.md) Step 5; status updated in [Report Sync](Report%20Sync.md)
