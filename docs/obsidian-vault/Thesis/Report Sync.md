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

**What could go here:**
- Functional testing against FR1-FR7
- Performance testing (refresh latency, API response times)
- Model comparison: baseline vs IRT difficulty, baseline vs improved struggle
- CF elevation rate analysis
- Mistake clustering quality assessment
- Usability observations
- Edge case handling (empty data, single student, no AI feedback)

**Evidence needed:** All testing evidence needs to be created from scratch.

See [[Ch5 – Results and Evaluation]] for full chapter analysis.

---

## Ch6 Conclusion — Status: Empty (CRITICAL)

**What the report says:** 2 subsection headers only: Summary, Future Work. No content.

**Future work candidates from unimplemented features:**
- Smart device integration (FR6)
- Event-driven architecture (still interval-based)
- BKT mastery visualization (computed but never displayed in UI)
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
| RAG / ChromaDB | ❌ Not yet implemented | ❌ Not yet written | 🟡 Planned | Ch3 placeholder added. Dr. Batmaz's design, Meeting 3. |

---

## Cross-cutting issues

1. **V1/V2 confusion** — The thesis was written at the V1 stage. All implementation-facing content needs updating to V2.
2. **Future tense** — Many sections use "will be", "we will" — these should become past/present tense for a final dissertation.
3. **Proposal framing** — Sections read like a project proposal rather than a completed project report.
4. **Missing features in thesis** — IRT, BKT, improved struggle, mistake clustering, saved sessions, data analysis views, sound effects, academic calendar, settings — none appear in the thesis at all.
5. **Formula divergence** — Struggle (5 vs 7 components) and difficulty (4 vs 5 components) formulas differ between thesis and code.
