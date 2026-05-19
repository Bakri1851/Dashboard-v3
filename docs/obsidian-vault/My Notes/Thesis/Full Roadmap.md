# Full Roadmap

Combined coding + writing order for final submission. Work through this top to bottom — each item unblocks the next. For detailed specs see [[Coding Roadmap]] (coding) and [[Writing Roadmap]] (writing).

Related: [[Coding Roadmap]], [[Writing Roadmap]], [[Rewrite Queue]], [[Report Sync]], [[Evidence Bank]]

---

## Why this order

Rewrites of existing chapters (Ch3, Ch1&2, Ch4) must come before new chapters (Ch5, Ch6) so the implementation narrative is settled before evaluation is written. Ch4 is placed after Ch3 and Ch1&2 because the code is still subject to minor change — writing Ch4 last among the rewrites means it describes the final system. All appendices are grouped at the end, once chapter content is complete and stable, so screenshots and test evidence capture the truly final state.

Phases 10 and 11 are explicitly out of scope for this submission and will be documented in Ch6 §6.3 Future Work. Phase 9 (RAG + ChromaDB) is a special case — *code* is complete (`rag.py`), so its *written coverage* (Ch4 implementation description + Ch2 RAG literature review subsection) is in scope; only its *empirical evaluation* is deferred to Ch6 §6.3. Attempting large new coding phases with 41 days remaining and Ch4/Ch5/Ch6 unwritten would risk the submission. Phase 6 is stretch only.

---

## The order

### 1. Phase 7 — Surface computed-but-hidden data `Coding · Small`

Quick win. Two features are computed every run but produce no visible output — fix this before screenshots so Appendix B captures the live features.

- [x] Add confidence indicator next to incorrectness values in question drill-down (`ui/components.py`)
  - confidence dot added to question drill-down — green/amber/grey by threshold, mean confidence across question's submissions
- [x] Decide on temporal smoothing: activate `SMOOTHING_ENABLED = True` in `config.py` or remove the stub
  - temporal smoothing activated (SMOOTHING_ENABLED = True, α = 0.3); settings toggle added following cf_enabled pattern

*Unblocks: accurate screenshots in step 3.*

---

### 2. Phase 5 — Comparison UI `Coding · Large`

The biggest remaining coding task. Produces the model comparison view needed for Ch5 evaluation evidence.

- [x] `comparison_view()` in `ui/views.py`
- [x] `render_comparison_scatter()`, `render_comparison_table()`, `render_agreement_summary()` in `ui/components.py`
- [x] "Model Comparison" routing in `instructor_app.py`
- [x] Settings sub-panel: `improved_models_enabled` toggle + sub-toggles + BKT sliders

*Unblocks: Ch5 model comparison evidence, Appendix B comparison screenshots.*

---

### 3. Ch3 — Design updates `Writing · Medium`

Surgical edits — the chapter structure is solid, specific sections need updating. Where figures reference Appendix B screenshots, insert `[TODO: insert figure]` placeholders; these will be replaced at step 8.

- [x] Update struggle formula to 7 components + Bayesian shrinkage (was 5 in thesis) — *Done 2026-05-18; §3.3.1 closed.*
- [x] Update difficulty formula to 5 components (was 4 in thesis) — *Done 2026-05-19; §3.3.3 closed.*
- [ ] Mark Figs 8–10 (Figma mockups) for replacement — add `[TODO: replace with screenshot]` annotations
- [x] Update CF section — it is implemented, not "to be implemented" — *Done 2026-05-19; §3.3.4 closed.*
- [x] Add sections for IRT, BKT, improved struggle, mistake clustering — *All four done 2026-05-19. §3.3.5 (clustering), §3.4.2 (IRT), §3.4.3 (BKT), §3.4.4 (improved struggle) all closed.*
- [x] Fill §3.3.2 Temporal Smoothing stub (distinguish per-submission decay from EWMA across refresh) — *Done 2026-05-18.*

*Unblocks: Ch1&2 language fixes are easier once Ch3 narrative is settled.*

---

### 4. Ch1 & Ch2 — Language and framing `Writing · Small`

- [ ] Convert future tense in Ch1 §1.2, §1.3, §1.5 to past/present
- [ ] Update Table 1 risk mitigations with actual decisions made
- [ ] Fill Ch2 §2.1.7 research gaps (uncomment and revise draft at lines 121–130)
- [ ] Add implementation status column to FR/NFR tables; clarify FR6 is unimplemented
- [ ] **Add three new Ch2 subsections (Knowledge Tracing, Text Mining, RAG) + citation extensions to §2.1.4/§2.1.6/§2.1.7** — see "Methods lit-review backlog (2026-04-18)" in [[Rewrite Queue]].

*Unblocks: Ch4 — existing chapter framing is now consistent before the implementation chapter is rewritten.*

---

### 5. Ch4 — Implementation rewrite `Writing · Large`

Rewrite the entire chapter — it currently describes V1 only. Cover the full V2 system. Add `[TODO: insert figure]` placeholders for Appendix B screenshots; these will be filled in at step 8.

- [ ] Replace scope/introduction section — remove "proof of concept" framing
- [ ] Update technology stack table to reflect V2 dependencies (filelock, openai, scipy, streamlit-autorefresh)
- [ ] Data pipeline section — describe interval-based polling, JSON+XML parsing, normalization
- [ ] Analytics section — OpenAI incorrectness scoring, 7-signal struggle, 5-signal difficulty, CF, mistake clustering
- [ ] Models section — IRT, BKT, improved struggle, measurement confidence
- [ ] Lab assistant system — join/assign/self-claim/mark-helped flows, shared JSON state
- [ ] Saved sessions and session lifecycle — CRUD, retroactive save, academic period filtering
- [ ] Instructor views — all 6 views + settings + sound effects
- [ ] Mark figure slots for Appendix B screenshots (`[TODO: insert figure]`)
- [ ] **Insert L-BFGS-B / MLE / ROC-AUC citation footnotes in Ch4 §4.9.x and Ch5 §5.1** — see "Methods lit-review backlog (2026-04-18)" in [[Rewrite Queue]].

*Unblocks: Ch5 evaluation framing, Appendix A code snippets.*

---

### 6. Ch5 — Results & Evaluation `Writing · Large`

Write from scratch. Draft structure and prose first; Appendix C evidence slots can be filled in at step 9.

- [ ] §5.1 Evaluation Design — method, scope, what was tested and why
- [ ] §5.2 Functional Testing — FR1–FR7 mapped to smoke test evidence (Appendix C)
- [ ] §5.3 Non-Functional Testing — NFR1–NFR6 (performance, usability, reliability)
- [ ] §5.4 Results — model comparison results (baseline vs IRT, baseline vs improved struggle), what passed/failed
- [ ] §5.5 Discussion — limitations, what results mean, comparison to design intent

*Unblocks: Ch6.*

---

### 7. Ch6 — Conclusion `Writing · Medium`

Write from scratch once Ch5 is drafted.

- [ ] §6.1 Summary — restate objectives, what was built, what was achieved
- [ ] §6.2 Contributions — scoring model advances, lab assistant coordination, real-time analytics
- [ ] §6.3 Future Work — FR6 smart devices, Phase 6 mobile refinement, Phase 9 RAG feedback, Phase 10/11 in-app Help, event-driven architecture, temporal smoothing, BKT parameter tuning, larger evaluation study, export/reporting

---

### 8. Appendix B — UI Screenshots `Evidence · Small`

Take screenshots of every dashboard and mobile view now that all chapters are written and code is stable.

- [ ] All 6 instructor views (in-class, student detail, question detail, data analysis, model comparison, settings)
- [ ] Model comparison view (both student + question tabs)
- [ ] Lab assistant app (join screen, unassigned view, assigned view)
- [ ] Session start/end states
- [ ] Replace all `[TODO: insert figure]` placeholders in Ch3 and Ch4 with actual figures

*Unblocks: Appendix C (screenshots confirm system is in final state for smoke testing).*

---

### 8a. Figures backlog `Evidence · Medium`

Per-chapter figure work consolidated from [[Figures and Tables]] (which holds the full inventory and rationale). Tackle each block in the order the parent writing step needs it — Ch3 figures during Step 3, Ch4 screenshots during Step 5, etc. The Step 8 screenshot pass produces the raw assets; this section is the per-chapter insertion checklist.

**Verification basis:** every non-optional / non-conditional figure below is justified by either (a) an existing `\includegraphics` placeholder in the `.tex` source, or (b) an existing subsection header whose subject is intrinsically visual (a UI view, a model-output panel, a workflow state). Nothing speculative.

**Ch1 — Introduction (Step 4)**

- [ ] Tbl 1 (Risks) — update mitigations to actual V2 decisions (Bayesian shrinkage, modular `models/`, graceful degradation, FR6 scoped out)

**Ch2 — Requirements Specification (Step 4)**

- [ ] Tbl 3 (MoSCoW) — review FR6 status (currently "Should Have", unimplemented)
- Figures 1–5 (literature dashboards): no action, keep as-is

**Ch3 — Design (Step 3)**

- [ ] Fig 6 (architecture diagram) — update to show `models/` package, RAG, lab assistant
- [ ] Fig 8 — replace Figma mockup 1 with V2 In Class view screenshot (`design-and-architecture.tex:339`)
- [ ] Fig 9 — replace Figma mockup 2 with V2 lab-assistant allocation screenshot (`design-and-architecture.tex:347`)
- [ ] Fig 10 — replace Figma mockup 3 with V2 assistant leaderboard screenshot (`design-and-architecture.tex:356`)
- [ ] NEW Tbl — Struggle formula 7-signal table (signal × symbol × weight × `config.py` key)
- [ ] NEW Tbl — Difficulty formula 5-signal table (signal × symbol × weight × `config.py` key)
- [ ] NEW Tbl — Improved-struggle weight redistribution matrix (4 collapse cases, rows sum to 1.00)
- [ ] NEW Tbl — BKT parameter defaults vs fitted values
- [ ] Tbl 4 (Tech stack) — add OpenAI, filelock, scikit-learn, scipy, streamlit-autorefresh, chromadb, sentence-transformers
- [ ] Tbl 5 (CF comparison) — change wording to "implemented" not "proposed"
- [ ] Tbl 6 (Struggle thresholds) — update labels (None/Low/Medium/High → On Track / Minor Issues / Struggling / Needs Help) and values [0.00–0.20 / 0.20–0.35 / 0.35–0.50 / 0.50–1.00]
- [ ] (optional) Graceful-degradation trace screenshot — improved-struggle with mastery data sparse; place in §3.4.4 or Ch5 §5.5

**Ch4 — Implementation (Step 5)** — each maps 1:1 to an existing subsection header in `implementation.tex`

- [ ] Screenshot: In Class view → §4.4.1
- [ ] Screenshot: Student Detail view → §4.4.2
- [ ] Screenshot: Question Detail view (with mistake clusters labelled) → §4.4.3
- [ ] Screenshot: Data Analysis view → §4.4.4
- [ ] Screenshot: Model Comparison view (student + question tabs) → §4.4.5
- [ ] Screenshot: Settings view (model toggles + CF config + BKT sliders) → §4.4.6
- [ ] Screenshot: Previous Sessions view → §4.4.7
- [ ] Screenshot: Lab assistant — Session Join → §4.5.1
- [ ] Screenshot: Lab assistant — Waiting / Unassigned → §4.5.2
- [ ] Screenshot: Lab assistant — Assigned (with student card + RAG suggestions) → §4.5.3
- [ ] (optional) Tooltip-in-action screenshot — one chart with on-hover explanation visible

**Ch5 — Results & Evaluation (Step 6)**

- [ ] Model Comparison panel screenshot — Rank Concordance (Spearman ρ) + Top-10 Overlap + Agreement split + scatter plot. Capture from `/api/models/compare` → ComparisonView → §5.4.2
- [ ] NEW Tbl — Requirements traceability (FR1–FR7 / NFR1–NFR6 mapped to implementation status + evidence location) → §5.2 / §5.3
- [ ] NEW Tbl — Model comparison results (baseline vs IRT, baseline vs improved struggle: ρ, top-k overlap, agreement %) → §5.4
- [ ] (optional) Performance / refresh-latency chart → §5.3
- [ ] (optional) Test results summary — pass/fail by FR + NFR; could be a table instead of a chart

**Ch6 — Conclusion (Step 7)**

- No new figures expected. If Ch6 §6.3 names the React/FastAPI alternative as future work, the V3 architecture diagram from the conditional block below could be reused.

**Appendix B — UI Screenshots (Step 8)**

- This appendix is the host for the screenshots above. Decide policy: each figure appears in Appendix B as the full gallery AND once in-chapter, OR each appears only once. Apply consistently across all 10+ screenshots.

**Removed if Progress Report stays excluded (already commented out in `main.tex:62`)**

- Fig 11 (Gantt chart) — remove
- Tbl 8 (Gantt summary) — remove

**Cross-cutting**

- [ ] After all chapter screenshots are inserted, run a renumbering pass — figure count goes from 11 → ~20, so `\ref{fig:...}` calls and the List of Figures need a clean compile check.
- [ ] Update [[Figures and Tables]] after each batch so it stays the source of truth.

**Table colouring backlog (extra polish, not blocking)**

Add `\usepackage[table]{xcolor}` to `main.tex` once; then colour the following tables traffic-light style. Palette: `tlGreen #10A15D · tlAmber #FFCC00 · tlOrange #FF6600 · tlRed #FF2D55` (matches dashboard UI hex codes from [config.py:39-42](code/learning_dashboard/config.py#L39-L42) and [config.py:54-57](code/learning_dashboard/config.py#L54-L57)). For non-traffic-light tables, define ad-hoc named colours alongside.

- [ ] Tbl 6 (Ch3 §3.6.4 Struggle visual encoding) — colour Colour row with `tlGreen/tlAmber/tlOrange/tlRed`
- [ ] Tbl 7 (Ch3 §3.6.4 Difficulty visual encoding) — same palette mapped Easy → Very Hard
- [ ] Tbl 1 (Ch1 §1.4 Risks) — severity column: `tlRed` high · `tlAmber` medium · `tlGreen` accepted
- [ ] Tbl 3 (Ch2 §2.3.3 MoSCoW) — priority column: `tlGreen` Must · light blue (`#BBDEFB`) Should · light grey (`#E0E0E0`) Could · light red (`#FFCDD2`) Won't
- [ ] NEW Tbl Requirements Traceability (Ch5 §5.2) — status column: `tlGreen` implemented + tested · `tlAmber` implemented partial evidence · `tlRed` not implemented (FR6)
- [ ] (optional) NEW Tbl Model comparison results (Ch5 §5.4) — agreement % column: `tlGreen` ≥0.8 · `tlAmber` 0.5–0.8 · `tlRed` <0.5

Skip: Tbl 2 (Grade Scoring — literature reproduction), Tbl 4 (Tech Stack — no ordinal), Tbl 5 (CF Comparison — qualitative), Tbl 9 (Themes — reference only), and the new formula tables (Struggle 7-signal / Difficulty 5-signal / Weight redistribution / BKT params) where colour would obscure the numbers.

**Deferred extras — visual polish on tables**

Pulled out as a separate pass so it doesn't block chapter writing. Needs `\usepackage[table]{xcolor}` in `main.tex` and a 4-colour traffic-light palette (`tlGreen #10A15D`, `tlAmber #FFCC00`, `tlOrange #FF6600`, `tlRed #FF2D55`) matching `config.py` UI hexes.

- [ ] Ch3 §3.6.4 Visual Encoding tables (struggle + difficulty) — colour the threshold cells / column headers using the traffic-light palette. Most natural fit since the tables are literally about colour encoding.
- [ ] Ch1 Tbl 1 (Risks) — colour the severity column (red / amber / green).
- [ ] Ch2 Tbl 3 (MoSCoW) — colour the priority column (Must / Should / Could / Won't); needs two extra named colours outside the traffic-light set (`#BBDEFB` light blue for Should, `#E0E0E0` grey for Could).
- [ ] Ch5 NEW Requirements Traceability table — colour the status column once the table is drafted.
- [ ] Ch5 NEW Model comparison results table — conditional formatting on the agreement % column if the numbers split usefully.

*Skip on purpose: Tech Stack, CF comparison, Tech-themes appendix table, the new formula tables — colour would be noise on neutral / numerical content.*

**Conditional — only if Ch4 or Ch6 explicitly names the React/FastAPI `code2/` frontend**

- [ ] V3 architecture diagram (3 frontends + 1 shared core + 1 shared state file)
- [ ] V3 theme gallery (7 themes: paper / newsprint / solar / scifi / blueprint / matrix / cyberpunk)
- [ ] V3 In Class / Student detail / Question detail / Lab coordination screenshots
- [ ] SessionProgression timeline screenshot (`code2/` 9th view, no V2 equivalent)
- [ ] Swagger UI screenshot — `/docs` endpoint listing
- [ ] Theme × accent matrix (7 themes × 5 accents in one grid)
- [ ] NEW Tbl — API endpoint map (≥22 routes × HTTP method × `learning_dashboard.*` delegate × cache TTL)
- [ ] NEW Tbl — Theme × accent combinations (35 valid pairs with accessibility class)

*Unblocks: Step 9 (Appendix C) can begin once the screenshot batch is captured, since the smoke test runs on the same final UI state.*

---

### 9. Appendix C — Test Results `Evidence · Medium`

Run the full smoke test checklist from [[Setup and Runbook]] and document outcomes. This is the primary evidence base for Ch5.

- [ ] Run every test in the smoke test checklist; record pass/fail
- [ ] Note any observations or edge-case behaviour
- [ ] Capture model comparison results for baseline vs IRT difficulty and baseline vs improved struggle
- [ ] Fill any evidence slots left in Ch5 §5.2 and §5.4

*Unblocks: Appendices E&F and Appendix A (evidence pass confirms formulae and code snippets are final).*

---

### 10. Appendices E & F — Formulae `Writing · Small–Medium`

Collect all model formulas and derivation notes in one place.

- [ ] Appendix E: struggle formula (7 components + weights), difficulty formula (5 components + weights), IRT likelihood, BKT update rule, improved struggle weights, CF cosine similarity
- [ ] Appendix F: derivation notes for non-obvious formulas (BKT update, IRT MLE gradient, Bayesian shrinkage in struggle)

---

### 11. Appendix A — Code Snippets `Writing · Small`

Add key code excerpts to support Ch4.

- [ ] Incorrectness scoring batch call
- [ ] Struggle score function signature
- [ ] Lab state read/write pattern
- [ ] Deferred actions example

---

### 12. Polish pass `Writing · Small`

Final consistency check before submission.

- [ ] Terminology: "incorrectness", "struggle score", level labels ("On Track / Minor Issues / Struggling / Needs Help")
- [ ] Update bibliography for IRT/BKT/improved struggle sources if new citations added
- [ ] Review figure and table numbering after all additions
- [ ] LaTeX compile check — `main.tex` with no errors or warnings

---

### 13. FR6 — Smart device notifications `Coding · Large` (stretch)

Only attempt if time allows after step 8. Otherwise document as future work in Ch6 §6.3.

- [ ] Evaluate feasibility of web push notifications for the assistant app
- [ ] If viable: implement push alert when a new high-struggle student appears
- [ ] Document the decision in Ch6 regardless of outcome

---

### 14. Phase 6 — Mobile app refinement (stretch) `Coding · Medium`

Only attempt after Ch6 is written. Ch5 assistant flow testing can use the current app. BKT badges and session timer are thesis-strengthening but not thesis-critical.

- [ ] BKT mastery badge + progress bar on assigned-student card (`render_assigned_view()`)
- [ ] Per-question mastery labels on the top-3 question list
- [ ] Session elapsed timer in `_render_session_status_strip()`
- [ ] Helped-vs-struggling summary header in `render_unassigned_view()`

---

## Out of scope — document as future work

These phases will not be implemented before the May 20 deadline. Each should be documented in Ch6 §6.3 Future Work. Do not attempt coding on these items.

### Phase 9 — RAG suggested feedback ✅ Implemented (2026-04-14)

Architecture designed by Dr. Batmaz (Meeting 3) — **must be credited in dissertation**.

Implemented as an isolated `rag.py` module:
- `chromadb.PersistentClient` at `data/rag_chroma/`, collection `session_{session_id}`
- `all-MiniLM-L6-v2` embeddings via `sentence-transformers` (local, no API cost)
- Two-layer retrieval: pandas pre-filter by `student_id` + ChromaDB `where=` metadata filter
- GPT-4o-mini generates 2–3 coaching bullets surfaced in the assistant assigned-student card
- Graceful no-op if deps missing; cached per student per session

Ch4 and Ch5 sections needed. See [[RAG Pipeline - Two-Layer Retrieval]] and [[Suggested Focus Areas Panel]].

### Labelled data collection + supervised weight optimisation `Research · Ambitious`

The seven struggle weights (`α=0.10, β=0.10, γ=0.20, δ=0.10, η=0.38, ζ=0.05, θ=0.07`), the five difficulty weights (`0.28, 0.12, 0.20, 0.20, 0.20`), and the three improved-struggle bucket weights (`0.45, 0.30, 0.25`) are set by trial and error. With labelled ground truth available — instructor annotations of "this student is struggling / not struggling" captured during real sessions, or post-hoc retrospective labelling of recorded sessions — the same weights could be fitted by supervised ML (logistic regression, gradient boosting, or Bayesian hyperparameter search such as Optuna), giving the model a proper empirical foundation.

Pre-requisites that put this out of scope for the current submission:

- Ethics-approval extension to collect or share labelled session data
- Recruitment of instructor labellers (or a defensible auto-labelling proxy)
- Train/test split infrastructure (currently no automated test suite exists)
- A held-out evaluation protocol (Cohen's κ for inter-rater agreement, ROC-AUC for the fitted classifier)

Identified as the most significant methodological limitation in [[Future Work Inventory]] (#3, Ch6 Candidate #1) and called out by Dr Batmaz in Meeting 3 as the natural follow-on once labelled data exists. Discussed honestly in Ch5 §5.5 Limitations and proposed for Ch6 §6.3 Future Work.

### Phase 10 — In-app Help system (instructor dashboard)

Help section under Settings covering Quick Tour, Help Centre, Model Guide, contextual tooltips, and reliability indicators. Not feasible to implement before deadline given the writing workload.

*Document in Ch6 §6.3 Future Work.*

### Phase 11 — In-app Help system (assistant app)

Lightweight mobile Help panel for lab assistants covering join guide, student card explainer, action button guide, and RAG suggestion explainer.

*Document in Ch6 §6.3 Future Work.*

---

## At a glance

| Step | Item | Type | Effort | Status |
| --- | --- | --- | --- | --- |
| 1 | Phase 7 — Surface hidden data | Coding | Small | Done |
| 2 | Phase 5 — Comparison UI | Coding | Large | **Done** |
| 3 | Ch3 — Design updates | Writing | Medium | **In progress (2026-05-18)** |
| 4 | Ch1 & Ch2 — Language cleanup | Writing | Small | Not started |
| 5 | Ch4 — Implementation rewrite | Writing | Large | Not started |
| 6 | Ch5 — Results & Evaluation | Writing | Large | Not started |
| 7 | Ch6 — Conclusion | Writing | Medium | Not started |
| 8 | Appendix B — Screenshots | Evidence | Small | Not started |
| 8a | Figures backlog (per-chapter insertion) | Evidence | Medium | Not started |
| 9 | Appendix C — Test Results | Evidence | Medium | Not started |
| 10 | Appendices E & F — Formulae | Writing | Small–Medium | Not started |
| 11 | Appendix A — Code Snippets | Writing | Small | Not started |
| 12 | Polish pass | Writing | Small | Not started |
| 13 | FR6 — Smart devices (stretch) | Coding | Large | Not started |
| 14 | Phase 6 — Mobile app refinement | Coding | Medium | Stretch |
| — | Phase 9 — RAG suggested feedback | Coding | Large | **Done** (2026-04-14) |
| — | Phase 10 — In-app Help (instructor) | Coding | Large | Out of scope / Future work |
| — | Phase 11 — In-app Help (assistant) | Coding | Medium | Out of scope / Future work |
| — | Labelled data + supervised weight optimisation | Research | Ambitious | Out of scope / Future work |

---

## Alternative React (Vite) frontend — `code2/` shadow workspace

Additive track kicked off after the core Streamlit app was feature-complete. **`code/` stays pristine** throughout; everything happens in the `code2/` shadow copy. The thesis contribution (analytics, IRT, BKT, improved struggle, CF, RAG) is unchanged — only the presentation layer differs.

| Phase | Description | Status |
|---|---|---|
| 0 | Bootstrap — `cp -r code code2`, create `code2/CHECKLIST.md` resumable log | **Done** (2026-04-19) |
| 1 | FastAPI backend skeleton — `code2/backend/` + two 4-line `learning_dashboard/` refactors (`analytics.py:25` OpenAI-key guard, `data_loader.py:16` cached/uncached split) | **Done** (2026-04-19) |
| 2 | Vite + React + TypeScript scaffold — 7 themes (paper / newsprint / solar / scifi / blueprint / matrix / cyberpunk) extracted verbatim from `Alternative Dashboard _standalone_.html`, runtime theme + accent swap with `localStorage` persistence | **Done** (2026-04-19) |
| 3 | Port 7 non-lab views — InClassView, StudentDetail, QuestionDetail (+ new "Top Strugglers on this Question" table), DataAnalysisView, SettingsView, PreviousSessionsView, ComparisonView. Cold-start analytics mitigation via 5-min cache + `lifespan` prewarm. | **Done** (2026-04-19) |
| 4 | Lab state parity — 11 `/api/lab/*` endpoints, LabAssistantView with dispatch queue. Verified curl cycle: join → assign → mark helped → remove, state mutates through the same `FileLock`-protected `lab_session.json` that the Streamlit apps use. | **Done** (2026-04-19) |
| 5 | Sessions + settings + RAG — `/api/sessions` (read-only), `/api/settings` (read-only config snapshot), `/api/rag/{student,question}/{id}` (`async` + `to_thread` so the first-time Chroma build doesn't block the event loop). RagPanel integrated into detail views. | **Done** (2026-04-19) |
| 6 | Build + polish — ErrorBoundary, loading skeletons, `npm run build` → `dist/` (≈260 KB / 74 KB gzipped), `StaticFiles` mount at `/`, `/docs` Swagger UI, custom editorial favicon | **Done** (2026-04-19) |
| 7 | Documentation sync — this block, Evidence Bank, Report Sync, Figures and Tables, Weekly Plan, Setup and Runbook, recap toolkit panels | **In progress** |
| 8 | Defence rehearsal — 5-process smoke test, thesis screenshots, demo script | Not started |

Plan file (full context, resumable across context loss): `C:\Users\Bakri\.claude\plans\c-users-bakri-downloads-alternative-das-majestic-garden.md`.
Execution log with decision history: `code2/CHECKLIST.md`.

---

## Useful links

- [[Coding Roadmap]] — full coding phase status and sub-tasks
- [[Writing Roadmap]] — chapter-by-chapter status and writing notes
- [[Rewrite Queue]] — granular edit checklist for each thesis section
- [[Report Sync]] — where the thesis diverges from the current code
- [[Evidence Bank]] — what evaluation evidence exists or still needs to be collected
- [[Setup and Runbook]] — smoke test checklist for Appendix C
