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
- [ ] **Address temporal smoothing** — Ch3 proposes exponential smoothing for both models. `SMOOTHING_ENABLED = True` in `config.py` (α = 0.3) as of 2026-04-10 (Full Roadmap step 1). Thesis should now describe temporal smoothing as *active* in the baseline struggle model, not deferred.
- [ ] **Remove or update "event-driven pipeline under exploration"** — Ch3 §3.1 mentions this; V2 is still interval-based. Either remove claim or discuss as future work.
- [ ] **Confirm Progress Report exclusion** — `Progress Report.tex` is commented out in `main.tex`. Verify it stays excluded from final submission.
- [ ] **Review Ch2 commented-out research gaps** — lines 121-130 have a draft that may be suitable with minor updates.

---

## Supervisor meeting items — outstanding

- [ ] **Document improvement trajectory in report** — linear regression slope is implemented in `analytics.py` but not described anywhere in the thesis. Add to Ch3 §3.3.1 or Ch4 with citation.
- [ ] **Document answer repetition rate in report** — `rep_hat` is a live signal in the 7-component struggle model but undocumented in the thesis. Add formula component and citation.
- [ ] **Document Bayesian shrinkage in report** — shrinkage is applied to all struggle signals but not described in Ch3 or Ch4. Add formal description with citation.
- [ ] **Reconcile temporal smoothing (report vs code)** — Ch3 proposes exponential smoothing; `SMOOTHING_ENABLED = True` in config as of 2026-04-10 (α = 0.3). Update Ch3 to describe smoothing as implemented and active; cite EWMA recurrence from Appendix E.
- [ ] **Align retry rate / feedback requests naming** — report uses "feedback requests"; code uses `retry_rate`. Pick one term and apply consistently across Ch3, Ch4, and config comments.
- [ ] **Draft CF evaluation subsection in Ch5** — use held-out historical sessions as proxy ground truth; report RMSE, precision@k, and coverage. This was flagged as an open question by Dr Batmaz.
- [ ] **Add future work item: ML-based weight optimisation** — Ch6 future work should mention that once labelled ground truth data is available, the parametric weights (α, β, γ, δ, η) could be optimised via supervised ML rather than set manually.
- [ ] **Insert all pending citations** — new sections added (CF alternative model §3.3.3, weight justification §3.3.4, struggle modelling §2.1.4, recommender systems §2.1.5) have identified sources but no inline `\cite{}` calls yet.

---

## Methods lit-review backlog (2026-04-18)

Mathematical / ML techniques used in the codebase that currently have no corresponding citation in the lit review. Each item names the exact target section(s); most Ch3 subsections already exist and just need `\cite{}` calls, but Ch2 needs three brand-new subsections. See the full audit table at `C:\Users\Bakri\.claude\plans\alright-for-our-lit-indexed-hamming.md`.

**Editorial rule for notation:** Ch2 gets one core equation per technique + citation; Ch3 gets the equations actually used with default parameters from `config.py`; Appendix E holds the consolidated formula reference; Appendix F holds derivations. Do not bloat Ch2 with full notation.

- [ ] **Ch2 §2.1.5 (NEW) — Knowledge Tracing and Bayesian Student Models** — create the subsection between current §2.1.4 Struggle and §2.1.5 Task Difficulty; renumber §2.1.5–§2.1.7 accordingly. ~400 words framing KT as latent-trait + HMM. Cite Corbett & Anderson (1995) and Yudelson, Koedinger & Gordon (2013). Show BKT equation (d) — posterior + transition update — as the single representative equation.
- [ ] **Ch2 §2.1.7 (NEW) — Text Mining and Mistake Pattern Discovery** — create the subsection after renumbered CF, before research-gaps summary. Cite Salton & McGill (1983), MacQueen (1967) / Lloyd (1982), Arthur & Vassilvitskii (2007), Rousseeuw (1987), Salton & Lesk (1968).
- [ ] **Ch2 §2.1.8 (NEW) — Retrieval-Augmented Generation for Instructor Feedback** — merges with / supersedes the existing `#meeting3` RAG literature-review item. Cite Lewis et al. (2020), Reimers & Gurevych (2019), Malkov & Yashunin (2020).
- [ ] **Ch2 §2.1.X (NEW — LLM-as-Judge Scoring) OR extend §2.1.4** — gpt-4o-mini is the entry point of the whole pipeline but has zero citations. Cite Zheng et al. (2023) *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*; discuss calibration + fallback behaviour (0.5 default on parse failure). Ch3 §3.3.0 / Ch4 §4.7.1 get matching `\cite{}`.
- [ ] **Ch2 §2.1.4 extension — composite + temporal + shrinkage + regression paragraphs** — insert four short method paragraphs within the existing struggle-modelling subsection. Cite OECD/JRC (2008), Nardo et al. (2005), Ebbinghaus (1885), Wixted & Carpenter (2007), Efron & Morris (1977), Morris (1983), Draper & Smith (1998), Han/Kamber/Pei (2011). Closes the citation half of three existing supervisor items (improvement trajectory / answer repetition / shrinkage).
- [ ] **Ch2 §2.1.6 (renumbered) Task Difficulty extension** — add Rasch (1960), Lord & Novick (1968), Wright & Stone (1979) alongside existing Baucks / Pankiewicz / Baeres.
- [ ] **Ch2 §2.1.7 (renumbered) Collaborative Filtering extension** — add Herlocker et al. (1999), Resnick et al. (1994) alongside existing Schafer 2007.
- [ ] **Ch3 §3.3.1 / §3.3.2 / §3.3.3 / §3.3.x — insert missing `\cite{}` calls** for the references introduced in Ch2 §2.1.4 and the new §2.1.7.
- [ ] **Ch3 §3.3.x (NEW — Temporal Smoothing) OR paragraph in §3.3.1** — distinguish EWMA across snapshot refreshes (`SMOOTHING_ENABLED=True`, α=0.3) from per-submission exponential decay in A_raw. Two different techniques currently conflated. Appendix E lists both recurrences.
- [ ] **Ch3 §3.4.1 Measurement Confidence — add Lord & Novick (1968), Crocker & Algina (1986)** as the classical-test-theory basis for the 3-factor confidence formula.
- [ ] **Ch3 §3.4.2 IRT — add Rasch (1960), Fisher (1922) footnote, Byrd et al. (1995) footnote** for 1PL derivation, MLE justification, and L-BFGS-B bounded optimisation.
- [ ] **Ch3 §3.4.3 BKT — add Corbett & Anderson (1995), Yudelson et al. (2013); display equation (d) inline** with default parameter annotation from `config.py` (`BKT_P_INIT`, `BKT_P_LEARN`, `BKT_P_GUESS`, `BKT_P_SLIP`).
- [ ] **Ch3 §3.4.4 Improved Struggle — document three design mechanics**: (a) coverage-weighted shrinkage in `_compute_difficulty_adjusted` (distinct from classical `n/(n+K)` shrinkage); (b) mean-imputation of missing mastery (cite Little & Rubin 2002); (c) graceful-degradation weight redistribution with the weight-sum invariant assertion at [improved_struggle.py:168-171](code/learning_dashboard/models/improved_struggle.py#L168-L171). None currently appear in the thesis.
- [ ] **Ch4 §4.9.2 / §4.9.3 — one-line cite of L-BFGS-B (Byrd et al. 1995)** at each call-site narration.
- [ ] **Ch5 §5.1 Evaluation Design — cite Fawcett (2006), Hanley & McNeil (1982)** when introducing ROC-AUC as the BKT discrimination metric.
- [ ] **Ch5 §5.4 Model Comparison — agreement metric decision**: currently uses raw `agreed/total` percentage. Decide: (a) keep raw and acknowledge it as uncorrected, or (b) implement Cohen's κ (Cohen 1960) for chance-corrected agreement and report both. Supervisor-grade review will expect the discussion either way.
- [ ] **Appendix E — formulae table must list** struggle (weighted sum + shrinkage), difficulty, BKT equations (a)–(e), Rasch 1PL, TF-IDF, cosine, silhouette, measurement-confidence 3-factor formula, EWMA recurrence.
- [ ] **Appendix F — derivations must derive** BKT (b) and (c) from Bayes' rule, Rasch MLE gradient, Bayesian-shrinkage posterior, Bernoulli log-likelihood for IRT.
- [ ] **Literature/index.md — add new groupings** once the individual notes are written: Composite Scoring & Indicators; Memory & Time-Decay Models; Bayesian Shrinkage; Text Clustering & Similarity; Estimation & Optimisation; Evaluation Metrics; Retrieval-Augmented Generation & Embeddings; Classical Test & Measurement Theory. Extend existing groups "BKT and Knowledge Tracing", "Task and Question Difficulty", and "Collaborative Filtering" with the new foundational citations.

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

---

## Meeting 4 Additions (2026-04-16)

- [ ] **Ch5 §5.5 — IRT/BKT model disagreement discussion** — improved models produce ~0% agreement with baseline (everything collapses to red/max struggle). Write a paragraph explaining possible causes: IRT difficulty collapsing under sparse data per question; BKT mastery threshold sensitivity with default parameters; improved struggle model depending on both. Frame as a known limitation, not a failure. #meeting4
- [ ] **Ch4 — RAG feedback caching** — the current pipeline regenerates OpenAI feedback on every click. Dr. Batmaz suggested caching by cluster signature (question ID + cluster centroid hash) so repeated identical clusters don't re-call the API. Implement and document the caching design decision in Ch4. #meeting4
- [ ] **Ch5 — Retrospective evaluation results** — once the evaluation pipeline is implemented, capture results (accuracy vs time cutoff for parametric / CF / hypothesis-based ranking) and write up as §5.4. See [[Evaluation Strategy]]. #meeting4
- [ ] **Discussion chapter / ethics appendix — guest lecture notes** — Dr. Batmaz suggested recording the MSc ethics class session (Mon 27 Apr) and using the student Q&A as material for the Discussion chapter. Transcribe key questions raised and develop answers collaboratively with Dr. Batmaz. #meeting4

---

## 2026-04-24 additions — post-Phase-11 polish

Triggered by commits `54d45b7` (filter fixing), `17173a8` (hover tooltips), `8c4c13c` (maths fix), `092f20f` (bug fixers), `72ce45c` (assistant themes), `5ea4d21` (animated UI), `462de20` (code2 cleanup). Adds content to Ch3, Ch4, and Ch6. See [[Report Sync#2026-04-24 refresh — post-Phase-11 polish audit]] for divergence table.

### Authoritative weight values (lock these into Ch3 + Appendix E)

Current `config.py` values after maths-fix commit `8c4c13c`. These are the values the thesis should cite; earlier tuning drafts are superseded.

- **Struggle (7 signals, sum = 1.00):** `STRUGGLE_WEIGHT_N=0.10`, `_T=0.10`, `_I=0.20`, `_R=0.10`, `_A=0.38`, `_D=0.05`, `_REP=0.07`.
- **Difficulty (5 signals, sum = 1.00):** `DIFFICULTY_WEIGHT_C=0.28`, `_T=0.12`, `_A=0.20`, `_F=0.20`, `_P=0.20`.
- **Improved struggle (3 buckets, sum = 1.00):** `IMPROVED_STRUGGLE_WEIGHT_BEHAVIORAL=0.45`, `_MASTERY_GAP=0.30`, `_DIFFICULTY_ADJ=0.25`.
- **Shrinkage constant:** `SHRINKAGE_K=5` (pull toward class mean with weight `n/(n+K)`).

### Ch3 additions

- [ ] **§3.4.4 Improved Struggle — graceful-degradation weight-redistribution rules** — if `mastery_summary` coverage < 50%, the `mastery_gap` weight collapses and redistributes to behavioral (effective 0.75/0.00/0.25). If IRT has < 2 distinct difficulty values, `difficulty_adjusted` collapses and redistributes to behavioral (effective 0.70/0.30/0.00). If both collapse, effective 1.00/0.00/0.00. Invariant assertion at `improved_struggle.py:168-171` guarantees weights always sum to 1.0. Cite Little & Rubin (2002) for the mean-imputation pattern.
- [ ] **§3.x — Presentation layer: animation and theming** — 7 themes × 5 accents as a deliberate accessibility / preference choice, not cosmetic. Animated transitions (`motion.ts`, `AnimatedCard`, `ViewTransition`) keep the dashboard legible when data refreshes; no "jump cuts" between views. Cite a minimal usability source (existing Gelan 2018 or Verbert 2020 is enough) rather than adding new lit.

### Ch4 additions (post-Phase-11 surface)

- [ ] **§4.x Animated UI layer** — `code2/frontend/src/animation/motion.ts`, `AnimatedCard.tsx`, `ViewTransition.tsx`. Describe as a presentation-only concern (no analytics impact); quote the 2–3 places it's used (page transitions, card mount).
- [ ] **§4.x SessionProgression view** — new 9th instructor view (`code2/frontend/src/views/SessionProgression.tsx`). Describe its purpose, sidebar entry, and relationship to the other views. **Not in CHECKLIST** — needs a short paragraph explaining what problem it solves.
- [ ] **§4.x Tooltip layer** — Commit `17173a8` added on-hover explanations to charts and stat cards. Justify: reduces the cognitive load of dense dashboards (fits NFR2 interpretability). Screenshot one chart with tooltip visible for Appendix B.
- [ ] **§4.x Cache and filter hardening** — commits `54d45b7` and `462de20`. Per-window cache key is `(from_, to_, module)`; TTL 10 s for raw data, 300 s for computed analytics. Describe as NFR1 performance evidence: warm clicks drop from multi-second to sub-second.
- [ ] **§4.x Theme system** — 7 themes × 5 accents in `code2/frontend/src/theme/tokens.ts`. Document OKLch token layer; note that themes are consumer-chosen per session, do not reset on refresh.
- [ ] **§4.x Assistant-app theme parity** — commit `72ce45c`. Lab assistant app now uses same theme tokens as instructor app. Cross-reference Ch4 Lab Assistant System section.
- [ ] **§4.x "Maths fix" note** — commit `8c4c13c` tuned struggle/difficulty normalization. Include one-paragraph history: "weights were trial-and-error through April 2026; values cited in this section are the final set." Paired with Ch5 limitations discussion.

### Ch6 Future Work additions

- [ ] **§6.3 Wire measurement confidence to UI** — `compute_incorrectness_with_confidence()` in `models/measurement.py` already produces `incorrectness_confidence` and `incorrectness_source`. Nothing displays them. Propose a confidence-badge component (grey/amber/green) next to struggle scores.
- [ ] **§6.3 Enable BKT MLE fitting in live runs** — `fit_bkt_parameters()` exists but is never called. Live pipeline uses `BKT_P_INIT=0.3`, `_LEARN=0.1`, `_GUESS=0.2`, `_SLIP=0.1` defaults. Once `BKT_FIT_MIN_OBSERVATIONS=50` is routinely met, enabling the fit would give per-session parameter estimates.
- [ ] **§6.3 Temporal smoothing decision** — `apply_temporal_smoothing()` exists with `SMOOTHING_ENABLED=True` but is never invoked. Either wire it into the compute pipeline (EMA across refresh cycles, α=0.3) or retire the stub. Either way, make the state explicit.
- [ ] **§6.3 Animate state transitions across sessions** — current animation is per-view. Could extend to "student moves from Struggling to Needs Help" with an inline trail, making changes visible without the instructor staring.

### Method-note housekeeping

- [x] **`Student Struggle Logic.md` — authoritative weights** — updated to reflect maths-fix commit `8c4c13c`; temporal-smoothing cross-ref added as not-invoked (see #16 in Report Sync).
- [x] **`Question Difficulty Logic.md` — add mistake-clustering section** — TF-IDF + K-means + silhouette auto-k + OpenAI labelling (cite Salton & McGill 1983, MacQueen 1967, Arthur & Vassilvitskii 2007, Rousseeuw 1987 once bibkeys exist).
- [x] **`Improved Struggle Logic.md` — document graceful-degradation** — weight-redistribution invariant assertion at `improved_struggle.py:168-171`; add the three fallback rows (0.75/0.00/0.25; 0.70/0.30/0.00; 1.00/0.00/0.00).

### Source Tree documentation to create

- [ ] **`Source Tree/code2-frontend-animation.md`** — describe `src/animation/motion.ts`, `AnimatedCard.tsx`, `ViewTransition.tsx`; list the 2–3 places they're used.
- [ ] **`Source Tree/code2-frontend-views-session-progression.md`** — document `SessionProgression.tsx` purpose / data-source / sidebar entry.
- [ ] **`Lab App/Flows/Session Progression.md`** — flow-level description.
