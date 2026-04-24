# Report Sync

This is the central tracking note for keeping the thesis aligned with the actual Dashboard v3 implementation. Each chapter is assessed for accuracy against the current codebase.

Related: [[Thesis Overview]], [[Rewrite Queue]], [[Evidence Bank]], [[Figures and Tables]]

## Sync status key

- **Accurate** — report matches implementation
- **Outdated** — report describes V1 or earlier state; needs rewrite
- **Partial** — some content accurate, some gaps or mismatches
- **Empty** — section has no content yet
- **Future-facing** — written as proposal/plan rather than final system description

---

## Ch1 Introduction — Status: Partial

**What the report says:** Identifies the problem (shy students, prioritisation gap, passive assistants), proposes a real-time analytics dashboard, defines 7 objectives, lists 5 risks with mitigations, and outlines an agile project approach. Written in future tense throughout ("we will", "the system will").

**What the project does:** The dashboard is built and operational. Most objectives are addressed by the V2 codebase.

**Mismatches:**
- Future tense throughout — reads as a proposal, not a description of a built system
- Risk table mitigations are generic ("seek constant feedback", "explore smartwatch solutions") rather than describing what was actually done
- Objective 7 ("evaluate approach") has no evaluation chapter written yet

**Sections needing rewrite:** Review future-tense phrasing across all subsections. Update risk mitigations to reflect actual decisions made.

**Evidence needed:** None specific — this is framing content.

See [[Ch1 – Introduction]] for full chapter analysis.

---

## Ch2 Background and Requirements — Status: Partial

**What the report says:** Strong literature review covering learning analytics, dashboards (SAM, EMODA, Edsight), real-time analytics, struggle modelling (Dong, Or, Estey, Piech, BKT, LLMs), difficulty modelling (Dannath, IRT/Baucks, Pankiewicz), collaborative filtering. Defines FR1-FR7, NFR1-NFR6, MoSCoW prioritisation. Research gaps subsection is a `[FILL IN]` placeholder (commented-out draft exists below it).

**What the project does:** FR1-FR5 are fully implemented. FR6 (smart devices) is not implemented. FR7 (assistant ranking) is partially implemented (leaderboard concept exists in assistant system but no ranking by student satisfaction).

**Mismatches:**
- `[FILL IN]` placeholder at research gaps (line 119) — a commented-out draft exists immediately below but needs review and uncommenting
- Requirements have no implementation status mapping — reader cannot tell which are done
- FR6 (smart devices) is listed as "Should Have" but is completely unimplemented
- Literature review is solid and mostly version-independent

**Sections needing rewrite:** Fill research gaps. Add implementation status to requirements. Clarify FR6 status honestly.

**Evidence needed:** Requirements traceability matrix showing FR/NFR to code mapping.

See [[Ch2 – Background and Requirements]] for full chapter analysis.

---

## Ch3 Design and Modelling — Status: Partial

**What the report says:** 3-layer architecture (data generation, ingestion/processing, decision/action). Data endpoint description. Student struggle model with 5 components (n, t, e, f, A_raw) as a convex combination with temporal smoothing. Question difficulty with 4 components (c, t, a, f). CF alternative with cosine similarity and k-NN. Figma mockups of dashboard. Visual encoding tables (threshold colours).

**What the project does:** Architecture matches conceptually. Struggle model has 7 components (adds r_hat retry rate, d_hat trajectory, rep_hat repetition). Difficulty has 5 components (adds p_tilde first-attempt failure). CF is fully implemented as a toggleable secondary feature, not just an alternative. Dashboard is real, not a mockup.

**Mismatches:**
- Struggle formula: thesis has 5 components, code has 7 — missing `r_hat`, `d_hat`, `rep_hat`
- Difficulty formula: thesis has 4 components, code has 5 — missing `p_tilde`
- Thesis uses temporal smoothing (exponential) — code has a stub for this (`SMOOTHING_ENABLED = False`) but does not actively use it
- CF is described as "alternative" that "is still going to be implemented" — it IS implemented and enabled by default
- 3 Figma mockups (Figs 8-10) are explicitly labeled "conceptual design rather than a fully implemented system" — the actual dashboard exists and looks different
- Architecture mentions event-driven pipeline "currently under exploration" — still interval-based in V2
- IRT, BKT, improved struggle model, mistake clustering — none mentioned in design chapter
- No mention of saved sessions, data analysis views, sound effects, academic calendar, settings page

**Sections needing rewrite:**
- Update struggle formula to 7 components with actual weights (0.10, 0.10, 0.20, 0.10, 0.38, 0.05, 0.07)
- Update difficulty formula to 5 components with actual weights (0.28, 0.12, 0.20, 0.20, 0.20)
- Add Bayesian shrinkage to struggle model description
- Update CF section — it is implemented, describe how it works as secondary feature
- Replace Figma mockups with actual dashboard screenshots
- Add sections for IRT, BKT, improved struggle model
- Add mistake clustering design
- Remove or update temporal smoothing claims (stub exists but not active)

**Evidence needed:** Screenshots of actual dashboard. Side-by-side: thesis formula vs implemented formula.

See [[Ch3 – Design and Modelling]] for full chapter analysis.

---

## Ch4 Implementation — Status: Outdated (CRITICAL)

**What the report says:** Explicitly describes "Version 1" — a prototype with basic data pipeline, simple threshold-based indicators, Streamlit+Plotly stack, interval-based refresh. States: "Most advanced features, such as model-driven prioritisation, assistant allocation and smart device notifications, are to be implemented in the later iteration." Lists current V1 as proof of concept.

**What the project does:** V2 (Dashboard v3) is a full system with:
- OpenAI gpt-4o-mini incorrectness scoring (batch, cached)
- 7-signal student struggle with Bayesian shrinkage
- 5-signal question difficulty
- Collaborative filtering (cosine similarity, k-NN, elevation detection)
- Mistake clustering (TF-IDF + K-means + OpenAI labeling)
- IRT difficulty (Rasch 1PL via MLE)
- BKT mastery tracking (HMM with 4 parameters)
- Improved struggle model (3-component: behavioral + mastery gap + difficulty-adjusted)
- Measurement confidence scoring
- Complete lab assistant system (join, assign, self-claim, mark-helped, file-locked JSON state)
- Saved sessions (CRUD, retroactive save, academic period filtering)
- 6 data analysis charts
- 6 instructor views + 4 assistant views
- Sound effects, auto-refresh, academic calendar integration
- Settings page with model toggles

**Mismatches:** Nearly everything. The chapter describes a different, earlier version of the system.
- "Struggle based on only a single metric as a proof of concept" → V2 has 7-signal model
- "AI Based classifications not implemented" → OpenAI scoring is fully working
- "Question difficulty not implemented" → 5-signal model fully implemented
- "No task allocation to lab assistants" → Full assignment system exists
- "More advanced modelling is not yet integrated" → IRT, BKT, improved struggle all exist
- Technology stack table says "Version 1 has simple indicators" → V2 is far beyond this

**Sections needing rewrite:** The entire chapter needs rewriting to describe V2. This is the single highest-impact rewrite task.

**Evidence needed:** Code architecture diagram, feature screenshots, data flow diagram for V2.

See [[Ch4 – Implementation]] for full chapter analysis.

---

## Ch5 Results and Evaluation — Status: Empty (CRITICAL)

**What the report says:** 5 subsection headers only: Evaluation Design, Functional Testing, Non-Functional Testing, Results, Discussion. No content.

**What the project does:** No automated tests exist. No evaluation scripts. No benchmark data. Manual smoke test checklist exists in vault [[Setup and Runbook]].

**Phase 5 complete (2026-04-10):** The Model Comparison view (`comparison_view()` in `ui/views.py`) is now implemented. It provides:
- Agreement % between baseline and improved models (student struggle + question difficulty)
- Scatter plots (baseline x vs improved y) with diagonal reference line
- Comparison tables sorted by biggest disagreement (delta column colour-coded)
- Sub-model toggles and BKT parameter sliders in Settings

**This view is the primary evaluation evidence for Ch5.** Run it with real session data and capture:
- Agreement % between baseline struggle and improved struggle (categorical level match)
- Agreement % between baseline difficulty and IRT difficulty
- Scatter plots showing systematic bias (above/below diagonal)
- Students/questions with largest delta — analyse why models disagree
- **Spearman ρ** (rank correlation) between baseline and improved orderings — computed on the full common-student set, exposed as `spearman_rho` on `/api/models/compare` (implementation: `code2/backend/routers/models_cmp.py:_spearman`). Report with one of three interpretive bands: strong (>0.7), moderate (0.3–0.7), weak (<0.3).
- **Top-10 overlap** — fraction of the most-at-risk cohort both models agree on. Complements Spearman ρ when only the flagged tail matters operationally.

**Reporting guidance for Ch5:** present categorical agreement (raw %) AND rank concordance (Spearman ρ + top-10 overlap) together. Categorical agreement can be low when two models disagree on level boundaries even though they produce near-identical orderings, and Spearman ρ catches that. Cite the Spearman 1904 paper when introducing ρ (add the bibkey to `Literature/index.md` if missing). Kendall τ is NOT currently implemented — frame that as a future-work item rather than a reporting gap.

**What could go here:**
- Functional testing against FR1-FR7
- Performance testing (refresh latency, API response times)
- Model comparison: baseline vs IRT difficulty, baseline vs improved struggle ← **now supported by comparison_view()**
- CF elevation rate analysis
- Mistake clustering quality assessment
- Usability observations
- Edge case handling (empty data, single student, no AI feedback)

**Evidence needed:** Run comparison view during a live lab session; screenshot all four panels (two tabs × scatter + table).

See [[Ch5 – Results and Evaluation]] for full chapter analysis.

---

## Ch6 Conclusion — Status: Empty (CRITICAL)

**What the report says:** 2 subsection headers only: Summary, Future Work. No content.

**Future work candidates from unimplemented features:**
- Smart device integration (FR6)
- Event-driven architecture (still interval-based)
- BKT mastery visualization in assistant app (Phase 6, still deferred); BKT parameters now exposed via sliders in Settings
- Measurement confidence display (computed but never rendered)
- Temporal smoothing (stub only, not active)
- Automated evaluation framework
- Predictive alerts / forward-looking risk prediction
- Export/reporting (CSV, PDF)
- User studies / classroom evaluation

See [[Ch6 – Conclusion]] for full chapter analysis.

---

## Appendices — Status: Mostly Empty

| Appendix | Title | Status |
|----------|-------|--------|
| A | Code Snippets | Empty (header only) |
| B | UI Screenshots | Empty (header only) |
| C | Detailed Test Results | Empty (header only) |
| D | Themes and References | Complete — maps 36 citations to research themes |
| E | Formulae | Empty (header only) |
| F | Formulae Derivation | Empty (header only) |

**Priority:** Appendix B (screenshots) and C (test results) are most critical as they support Ch4 and Ch5.

---

## Progress Report — Status: Should be excluded or reframed

The Progress Report (`main sections/Progress Report.tex`) is currently commented out in `main.tex`. It uses January 2026 milestone framing, describes V1 limitations, and includes a Gantt chart. This is appropriate for a milestone submission but should not appear in the final dissertation. Confirm it remains excluded.

---

## Recent additions — Meeting 3 (2026-04-08)

| Feature | Code Status | Report Status | Priority | Notes |
|---|---|---|---|---|
| Model evaluation | ✅ Model implemented | ❌ Not yet written | 🔴 High | Ch5 placeholder added. Dr. Batmaz flagged Meeting 3. |
| Weight optimisation | ⚠️ Manual trial and error | ❌ Not in report | 🔴 High | Add as limitation + future work. Optuna/ML training possible once labeled data exists. |
| RAG / ChromaDB | ✅ Implemented (Phase 9) | ❌ Not yet written | 🔴 High | `rag.py` built. Dr. Batmaz's hybrid design. **Scope split:** code done · Ch4 description + Ch2 lit-review subsection **in scope** for this submission · empirical evaluation **deferred** to Ch6 §6.3 Future Work. See [[RAG Pipeline - Two-Layer Retrieval]]. |
| Data labelling (weight optimisation) | ⚠️ Manual weights in config.py | ❌ Not in report | 🟡 Planned | ~500 submissions needed to fit `STRUGGLE_WEIGHT_*` / `DIFFICULTY_WEIGHT_*` against ground truth. Add as limitation + future work. |

---

## Cross-cutting issues

1. **V1/V2 confusion** — The thesis was written at the V1 stage. All implementation-facing content needs updating to V2.
2. **Future tense** — Many sections use "will be", "we will" — these should become past/present tense for a final dissertation.
3. **Proposal framing** — Sections read like a project proposal rather than a completed project report.
4. **Missing features in thesis** — IRT, BKT, improved struggle, mistake clustering, saved sessions, data analysis views, sound effects, academic calendar, settings — none appear in the thesis at all.

---

## Alternative React (Vite) frontend — `code2/` shadow workspace

Added during the final sprint as an **additive** second frontend — `code/` remains untouched and is the defence-day fallback. Relevant to two places in the thesis:

| Chapter | Treatment | Status |
|---|---|---|
| Ch4 Implementation | Brief §4.x paragraph: "Alternative presentation layer (React + FastAPI) built in `code2/` while keeping `code/` as a byte-identical Streamlit fallback. Only two analytics files were changed in `code2/`: `analytics.py:25` (OpenAI key guard) and `data_loader.py:16` (cached/uncached split). The backend is FastAPI with 8 routers (`live`, `student`, `question`, `analysis`, `lab` ×11 actions, `sessions`, `settings`, `models_cmp`, `rag`), the frontend is Vite + React + TypeScript with 7 swappable themes extracted from the design mockup. All processes share `data/lab_session.json` via the same `FileLock` lab_state primitive, so the alternative frontend coordinates with the Streamlit apps automatically." | ❌ Not yet written |
| Ch6 §6.3 Future Work | Frame the Vite/FastAPI stack as the production-path migration story: it proves the analytics layer is framework-agnostic, opens the door to mobile / multi-user deployments, and gives a recognisable npm+uvicorn toolchain without requiring the defence demo to leave `code/`. | ❌ Not yet written |

**Scope guard.** This is infrastructure, not a new algorithmic contribution — no new literature citations expected. Evaluation section (Ch5) doesn't change: both frontends read the same analytics, so any results from `code/` apply unchanged.
5. **Formula divergence** — Struggle (5 vs 7 components) and difficulty (4 vs 5 components) formulas differ between thesis and code.

---

## 2026-04-24 refresh — post-Phase-11 polish audit

Code has continued past Phase 11 (defence-ready) with a polish burst that is **not yet reflected in the thesis**. Recent commits surfaced by this refresh: `54d45b7` filter fixing, `17173a8` hover tooltips, `8c4c13c` maths fix, `092f20f` bug fixers, `72ce45c` assistant themes, `5ea4d21` animated UI, `462de20` code2 cleanup. With 26 working days to 2026-05-20 submission, these need a thesis home in the Ch4 rewrite.

### Post-Phase-11 surface area (new in V2, absent in thesis)

| Feature | Code location | Thesis home | Status |
|---|---|---|---|
| Animated UI layer | `code2/frontend/src/animation/` (motion.ts, AnimatedCard, ViewTransition) | Ch4 §4.x Lab Instructor System — presentation layer | ❌ Not yet written |
| SessionProgression view | `code2/frontend/src/views/SessionProgression.tsx` | Ch4 §4.x Lab Instructor System — new 9th view | ❌ Not yet written, not in CHECKLIST |
| Hover-tooltip layer | Tooltip affordances across charts + stat cards | Ch4 §4.x Interaction design | ❌ Not yet written |
| Per-window analytics cache | `code2/backend/cache.py` keyed by `(from_, to_, module)`; TTL 10 s raw / 300 s analytics | Ch4 §4.x Data pipeline + Ch5 NFR1 performance evidence | ❌ Not yet written |
| Maths fix (weight tuning) | Commit `8c4c13c`; current `config.py` values are authoritative | Ch3 §3.3.1 / §3.3.2 — treat current values as final | ❌ Thesis weights out of date |
| 7 themes × 5 accents | `code2/frontend/src/theme/tokens.ts` (paper / newsprint / solar / scifi / blueprint / matrix / cyberpunk × indigo/teal/terracotta/forest/crimson) | Ch4 §4.x Interaction design — accessibility / presentation choice | ❌ Not yet written |
| Assistant-app theme parity | Commit `72ce45c` — lab assistant view now has themed appearance matching instructor app | Ch4 §4.x Lab Assistant System — presentation | ❌ Not yet written |

### Code-but-not-thesis divergences (stable, known, still need decisions)

| # | Divergence | Current state | Decision needed |
|---|---|---|---|
| 16 | `apply_temporal_smoothing()` exists in `analytics.py` with `SMOOTHING_ENABLED=True` but is never invoked in the compute pipeline | Dead code under a "true" flag | Ch3 should either (a) describe it as active once wired or (b) drop smoothing from Ch3 and note the stub in Ch6 future work |
| 17 | `models/measurement.py` `compute_incorrectness_with_confidence()` fully implemented but no UI surface displays `incorrectness_confidence` | Computed, discarded | Ch3 §3.4.1 + Ch6 future work entry ("wire confidence badge") |
| 18 | `models/bkt.py` has full MLE parameter-fitting logic (`fit_bkt_parameters`, `BKT_FIT_MIN_OBSERVATIONS=50`, `BKT_FIT_MAX_ITER=200`) but it is never invoked live — defaults from `config.py` are used | Fit code present, not called | Ch3 §3.4.3 should note the two modes; Ch6 future work entry ("enable BKT MLE in live runs") |
| 19 | `/api/models/compare` now surfaces `agreement` breakdown (upgraded / downgraded / unchanged), `spearman_rho`, `top10_overlap` — enough raw material for Ch5 | Endpoint live; ComparisonView consumes it | Reconcile Evidence Bank (reconciled below), Ch5 §5.4 unblocked |
| 20 | `MEMORY.md` auto-memory claims "flat layout with 10 Python files" | Stale (now package layout with `models/`, `ui/`, `rag.py`) | Out of scope — refresh in a later memory-management session |

### Status roll-up after this refresh

| Chapter | Previous status | Current status | Change |
|---|---|---|---|
| Ch1 Introduction | Partial | Partial | No change |
| Ch2 Background | Partial | Partial | No change; lit-review backlog still queued |
| Ch3 Design | Partial | Partial | **Weights must update to maths-fix values**; Figs 8–10 still marked Replace |
| Ch4 Implementation | Outdated | **Outdated + widened** | Post-Phase-11 features add 7 new subsections worth of content |
| Ch5 Evaluation | Empty | **Empty but unblocked** | Model Comparison / Spearman ρ / top-10 overlap all now sourced from `/api/models/compare` |
| Ch6 Conclusion | Empty | Empty | 3 new future-work entries (#16, #17, #18 above) |
| Appendix B screenshots | None captured | None captured | All views now stable; ready to photograph — screenshot campaign is a single sit-down task |
| Appendix E formulae | Empty | Empty | New rows needed for 7-signal struggle + 5-signal difficulty tables (maths-fix values) |
| Appendix F derivations | Empty | Empty | No change |

### Top 5 thesis-writing tasks in priority order (for next session)

1. **Ch3 weight and formula update** — struggle 7 signals with current config weights, difficulty 5 signals with current weights, Bayesian shrinkage description, CF reframed as implemented, Figs 8–10 replaced. Unblocks Ch4 rewrite.
2. **Ch4 full rewrite** — 26 Phase-6 placeholder subsections + 7 post-Phase-11 additions. Largest single writing task.
3. **Ch5 write from scratch** — Evaluation Design / Functional / NFR / Results / Discussion. `/api/models/compare` gives the results material; smoke-test walkthroughs give functional evidence.
4. **Appendix B screenshot campaign** — 11+ views in one sit-down session with a live dashboard.
5. **Ch6 conclusion** — Summary + Contributions + Future Work (includes #16, #17, #18 from divergences table).
