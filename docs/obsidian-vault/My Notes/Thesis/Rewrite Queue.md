# Rewrite Queue

Specific, actionable rewrite tasks for the thesis, grouped by priority. Each item references an exact chapter/section and describes what to change.

Related: [[Report Sync]], [[Thesis Overview]], [[Evidence Bank]], [[Figures and Tables]]

---

## Critical — chapters that must be written

- [ ] **Write Ch5 Evaluation** — entire chapter is empty (5 subsections: Evaluation Design, Functional Testing, Non-Functional Testing, Results, Discussion). See [[Ch5 – Results and Evaluation]] for suggested content.
- [ ] **Write Ch6 Conclusion** — entire chapter is empty (Summary, Future Work). See [[Ch6 – Conclusion]] for suggested content.
- [ ] **Fill research gaps placeholder** — Ch2 §2.1.7 has `[FILL IN]` at line 119 of `requirements specification.tex`. A commented-out draft exists at lines 121-130 — review, update, and uncomment.
- [ ] **Populate Appendix B (UI Screenshots)** — empty; needs screenshots of all dashboard views to support Ch4 and Ch5.
- [ ] **Populate Appendix C (Detailed Test Results)** — empty; needs test evidence to support Ch5.
- [ ] **Populate Appendix A (Code Snippets)** — empty; needs key implementation code to support Ch4.
- [ ] **Populate Appendix E (Formulae)** — empty; collect all model formulas in one reference.
- [ ] **Populate Appendix F (Formulae Derivation)** — empty; provide derivation steps for key models.

---

## High — outdated content that misrepresents the system

- [ ] **Rewrite Ch4 Implementation for V2** — entire chapter describes V1 prototype. Must describe: OpenAI scoring, 7-signal struggle, 5-signal difficulty, CF, mistake clustering, IRT, BKT, improved struggle, lab assistant system, saved sessions, 6 views, settings. See [[Ch4 – Implementation]].
- [ ] **Remove V1 prototype framing from Ch4** — replace "at this stage", "proof of concept", "to be implemented in the later iteration", "foundation for what the dashboard will eventually become" with final-system language.
- [ ] **Update Ch3 §3.3.1 struggle formula** — thesis has 5 components (n, t, e, f, A_raw); code has 7 (adds r_hat, d_hat, rep_hat). Update formula, add Bayesian shrinkage description. See [[Ch3 – Design and Modelling]].
- [ ] **Update Ch3 §3.3.2 difficulty formula** — thesis has 4 components; code has 5 (adds p_tilde first-attempt failure). Update formula and weights.
- [ ] **Replace Figma mockups in Ch3 §3.4.2** — Figs 8, 9, 10 are Figma conceptual designs. Replace with actual dashboard screenshots. Remove "conceptual design rather than a fully implemented system" caveat.
- [ ] **Update Ch3 CF section** — change "is still going to be implemented" to describe actual implementation. CF is live, toggleable, enabled by default with k=3, threshold configurable.
- [ ] **Update Ch4 deferred features list** — line 58 says "assistant allocation and smart device notifications, are to be implemented in the later iteration." Assistant allocation IS implemented. Only smart devices remain deferred.
- [ ] **Add missing V2 features to Ch3 or Ch4** — IRT difficulty, BKT mastery, improved struggle model, mistake clustering, measurement confidence, saved sessions, data analysis views, lab assistant system, settings page, sound effects, academic calendar. None appear anywhere in the thesis.

---

## Medium — language and framing improvements

- [x] **Convert Ch1 future tense to past/present** — §1.2, §1.3, §1.5 use "we will", "the system will" throughout. Should describe completed work.
- [ ] **Update Ch1 risk mitigations** — Table 1 mitigations are generic ("seek constant feedback", "explore smartwatch solutions"). Update to describe actual decisions (Bayesian shrinkage for insufficient data, modular design for extensibility, smart devices scoped out).
- [ ] **Add implementation status to Ch2 requirements** — FR1-FR7 and NFR1-NFR6 need mapping to current implementation state. Could be inline or in Ch5 evaluation.
- [ ] **Update Ch2 FR6 status** — smart device integration is "Should Have" but completely unimplemented. Either move to "Won't Have" or discuss honestly as future work.
- [ ] **Update Ch3 threshold label names** — thesis uses None/Low/Medium/High; code uses On Track/Minor Issues/Struggling/Needs Help.
- [ ] **Address temporal smoothing** — Ch3 proposes exponential smoothing for both models. Code has `SMOOTHING_ENABLED = False` stub. Either remove from design or explain why it was deferred.
- [ ] **Remove or update "event-driven pipeline under exploration"** — Ch3 §3.1 mentions this; V2 is still interval-based. Either remove claim or discuss as future work.
- [ ] **Confirm Progress Report exclusion** — `Progress Report.tex` is commented out in `main.tex`. Verify it stays excluded from final submission.
- [ ] **Review Ch2 commented-out research gaps** — lines 121-130 have a draft that may be suitable with minor updates.

---

## Supervisor meeting items — outstanding

- [ ] **Document improvement trajectory in report** — linear regression slope is implemented in `analytics.py` but not described anywhere in the thesis. Add to Ch3 §3.3.1 or Ch4 with citation.
- [ ] **Document answer repetition rate in report** — `rep_hat` is a live signal in the 7-component struggle model but undocumented in the thesis. Add formula component and citation.
- [ ] **Document Bayesian shrinkage in report** — shrinkage is applied to all struggle signals but not described in Ch3 or Ch4. Add formal description with citation.
- [ ] **Reconcile temporal smoothing (report vs code)** — Ch3 proposes exponential smoothing; `SMOOTHING_ENABLED = False` in config. Either remove from Ch3 design or explain deferral explicitly.
- [ ] **Align retry rate / feedback requests naming** — report uses "feedback requests"; code uses `retry_rate`. Pick one term and apply consistently across Ch3, Ch4, and config comments.
- [ ] **Draft CF evaluation subsection in Ch5** — use held-out historical sessions as proxy ground truth; report RMSE, precision@k, and coverage. This was flagged as an open question by Dr Batmaz.
- [ ] **Add future work item: ML-based weight optimisation** — Ch6 future work should mention that once labelled ground truth data is available, the parametric weights (α, β, γ, δ, η) could be optimised via supervised ML rather than set manually.
- [ ] **Insert all pending citations** — new sections added (CF alternative model §3.3.3, weight justification §3.3.4, struggle modelling §2.1.4, recommender systems §2.1.5) have identified sources but no inline `\cite{}` calls yet.

---

## Low — polish and consistency

- [ ] **Terminology consistency check** — ensure thesis terms match codebase terms (e.g., "incorrectness" not "wrongness", "struggle score" not "struggle metric").
- [ ] **Update bibliography** — 36 references currently; may need additions for IRT, BKT, or new features if they get dedicated sections.
- [ ] **Review figure/table numbering** — after adding/replacing figures, ensure captions and cross-references are correct.
- [ ] **Check LaTeX compilation** — after all edits, verify `main.tex` compiles without errors.

---

## Meeting 3 Additions (2026-04-08)

- [ ] **Ch5 — Model Evaluation** — mathematical model comparison, parametric vs alternative. Dr. Batmaz priority. #meeting3
- [ ] **Ch5 — Limitation** — state explicitly that α β γ δ η were set by trial and error due to absence of labeled ground truth. #meeting3
- [ ] **Ch5 — Future Work** — ML-based weight optimisation (Optuna, logistic regression, gradient boosting) once labeled data available. #future-work
- [ ] **Ch3 — RAG Design** — hybrid SQL + ChromaDB architecture, justification (citations to be inserted once literature review is done). Placeholder inserted. #meeting3
- [ ] **Ch2 & Ch3 — RAG literature review** — survey retrieval-augmented generation (Lewis et al. 2020), hybrid sparse/dense retrieval, and ChromaDB/embedding choices. Write Ch2 background subsection on RAG; inline citations in Ch3 §3.x RAG Design to justify SQL+ChromaDB hybrid. #meeting3

---

## Phase 6 additions (2026-04-12)

New skeleton subsections added to `implementation.tex` and `design-and-architecture.tex`. Each placeholder needs writing — see [[Ch4 – Implementation]] and [[Ch3 – Design and Modelling]] for content guidance per section.

**Ch3 — new placeholders:**

- [ ] **§3.3.x Mistake Clustering** — TF-IDF + K-means + OpenAI labeling design; justify auto-k via silhouette. See [[Ch3 – Design and Modelling#§3.3.x — Mistake Clustering]]
- [ ] **§3.x Advanced Model Design — Measurement Confidence** — length/extremity confidence formula; note not yet displayed in UI
- [ ] **§3.x Advanced Model Design — Item Response Theory** — Rasch 1PL, joint MLE, θ/β interpretation, when preferred over baseline
- [ ] **§3.x Advanced Model Design — Bayesian Knowledge Training** — HMM formulation, 4 parameters + defaults, mastery threshold, feeds improved struggle
- [ ] **§3.x Advanced Model Design — Improved Struggle Model** — 3-component weighted sum, graceful degradation, comparison table vs baseline
- [ ] **§3.4.x Lab Assistant View** — session join screen, waiting state, assigned student card design intent

**Ch4 — new placeholders (System Structure):**

- [ ] **§4.x Instructor System** — `instructor_app.main()`, deferred-actions pattern, sidebar filters, routing to 6 views
- [ ] **§4.x Assistant System** — `lab_app.py`, URL `?aid=` persistence, 5s auto-refresh, 4 view states
- [ ] **§4.x Shared Runtime State** — `lab_session.json`, filelock + atomic tmp-replace, fields stored

**Ch4 — new placeholders (Data Pipeline):**

- [ ] **§4.x Endpoint Retrieval and Parsing** — `fetch_raw_data()`, ttl=10 cache, JSON+XML, auto-detect format
- [ ] **§4.x Data Normalisation and Structuring** — module filter/rename, timestamp parse, academic period labeling, DataFrame schema

**Ch4 — new placeholders (Session Management):**

- [ ] **§4.x Live Session Lifecycle** — start/end flow, session code generation, pending flags
- [ ] **§4.x Saved Session History and Restoration** — CRUD in `data/saved_sessions.json`, academic period filter

**Ch4 — new placeholders (Analytics Implementation):**

- [ ] **§4.x Incorrectness Scoring** — gpt-4o-mini batch 50, in-process cache, fallback
- [ ] **§4.x Baseline Student Struggle Model** — 7 signals, weights, Bayesian shrinkage, 4-level classification
- [ ] **§4.x Baseline Question Difficulty Model** — 5 signals, weights, same classification
- [ ] **§4.x Collaborative Filtering** — cosine similarity, k=3, elevation detection, cold-start guard
- [ ] **§4.x Mistake Clustering** — TF-IDF/K-means/silhouette/OpenAI labeling, Question Detail display

**Ch4 — new placeholders (Advanced Model Implementation):**

- [ ] **§4.x Measurement Confidence** — computed not displayed, future surfacing intent
- [ ] **§4.x IRT Difficulty** — `models/irt.py`, Rasch 1PL, scipy L-BFGS-B
- [ ] **§4.x BKT Mastery** — `models/bkt.py`, HMM, Settings sliders
- [ ] **§4.x Improved Struggle Model** — `models/improved_struggle.py`, 3-component, graceful degradation

**Ch4 — new placeholders (Lab Instructor System):**

- [ ] **§4.x In Class View** — summary cards, leaderboards, distributions, CF panel
- [ ] **§4.x Student Detail View** — metrics, timeline, retry trend, CF similar students, BKT chart
- [ ] **§4.x Question Detail View** — mistake clusters, attempt table, IRT difficulty
- [ ] **§4.x Data Analysis View** — 6 chart types
- [ ] **§4.x Comparison View** — agreement cards, scatter plots, comparison tables; gated by `improved_models_enabled`
- [ ] **§4.x Settings View** — all toggles, sliders, model selectors
- [ ] **§4.x Previous Sessions View** — load/delete, academic period filter

**Ch4 — new placeholders (Lab Assistant System):**

- [ ] **§4.x Session Join Flow** — code + name entry, `?aid=` persistence, validation
- [ ] **§4.x Waiting and Assignment States** — unassigned vs assigned view, transitions
- [ ] **§4.x Live Assistant Allocation** — dropdown assign, self-claim, mark-helped, filelock sync

---

## Phase 5 additions (2026-04-10)

- [x] **Model Comparison view implemented** — `comparison_view()` in `ui/views.py`; three new components in `ui/components.py`. Gated by `improved_models_enabled` session state.
- [ ] **Ch5 — capture Model Comparison screenshots** — run view with real session data; screenshot Agreement summary cards, scatter plots, comparison tables for both tabs (struggle + difficulty).
- [ ] **Ch5 — write model comparison subsection** — report agreement %, discuss systematic disagreements visible in scatter plots (above/below diagonal), explain what high-delta cases reveal.
- [ ] **Ch4 — document Phase 5** — describe the Model Comparison view, the three new component functions, and the Settings sub-panel (sub-toggles + BKT sliders).
- [ ] **Ch6 Future Work — BKT parameter sensitivity** — sliders now exist; mention that formal sensitivity analysis or grid search over P_init/P_learn/P_guess/P_slip is a natural next step once labelled data is available.
