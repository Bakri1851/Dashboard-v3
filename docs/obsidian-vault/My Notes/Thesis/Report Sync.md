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

## Ch3 Design and Modelling — Status: Partial (in active rewrite — 2026-05-18)

**What the report says:** 3-layer architecture (data generation, ingestion/processing, decision/action). Data endpoint description. Student struggle model with 5 components (n, t, e, f, A_raw) as a convex combination with temporal smoothing. Question difficulty with 4 components (c, t, a, f). CF alternative with cosine similarity and k-NN. Figma mockups of dashboard. Visual encoding tables (threshold colours).

**What the project does:** Architecture matches conceptually. Struggle model has 7 components (adds r_hat retry rate, d_hat trajectory, rep_hat repetition). Difficulty has 5 components (adds p_tilde first-attempt failure). CF is fully implemented as a toggleable secondary feature, not just an alternative. Dashboard is real, not a mockup.

**Active rewrite — Step 3 of [[Full Roadmap]]:**

| Sub-task | Status | Anchor |
| --- | --- | --- |
| §3.1 / §3.3 intro re-tense; drop "event-driven under exploration" | **Done 2026-05-18** | `design-and-architecture.tex:2, 6, 47` |
| Tbl 6 / Tbl 7 visual-encoding label + traffic-light recolour | **Done (uncommitted)** | `design-and-architecture.tex:369-393` |
| `\usepackage[table]{xcolor}` + `tlGreen/tlAmber/tlOrange/tlRed` palette in `main.tex` | **Done (uncommitted)** | `main.tex:17, 23-27` |
| §3.3.1 Identified Variables — add `r_{s,σ}`, `d_{s,σ}`, `rep_{s,σ}`; rename `e → i` (mean incorrectness) | **Done 2026-05-18** | `design-and-architecture.tex:58-67` |
| §3.3.1 Normalisation — derive `\tilde{r}`, `\tilde{rep}`; uniform min-max across all 7 signals | **Done 2026-05-18** | `design-and-architecture.tex:80-111` |
| §3.3.1 Recent submissions paragraph — convex weights → exponential time decay (half-life 1800 s) | **Done 2026-05-18** | `design-and-architecture.tex:114-132` |
| §3.3.1 Struggle Score equation — 5-term → 7-term with default weights + weights table | **Done 2026-05-18** | `design-and-architecture.tex:134-194` |
| §3.3.1 New "Bayesian shrinkage" paragraph — applied to `S^raw`, cite Efron 1977 + Morris 1983 | **Done 2026-05-18** (bib entry for Morris 1983 missing — see housekeeping below) | `design-and-architecture.tex:196-207` |
| §3.3.2 Temporal Smoothing — fill empty stub; distinguish per-submission decay from EWMA across refresh | **Done 2026-05-18** | `design-and-architecture.tex:223-269` |
| §3.3.3 Question Difficulty — 4-signal → 5-signal (add `p̃` first-attempt failure) | **Done 2026-05-19** | `design-and-architecture.tex:266-367` |
| §3.3.4 CF — re-tense "is still going to be implemented" → "is implemented, toggleable" | **Done 2026-05-19** | `design-and-architecture.tex:476, 478` |
| §3.3.5 Mistake Clustering — fill empty stub (TF-IDF + k-means + silhouette + LLM labels) | **Done 2026-05-19** | `design-and-architecture.tex:480-503` |
| §3.4.1 Measurement Confidence — fill empty stub (2 factors + base, not 3; cite Lord & Novick 1968) | **Done 2026-05-19** | `design-and-architecture.tex:506-521` |
| §3.4.2 IRT — fill empty stub (Rasch 1PL via L-BFGS-B) | **Done 2026-05-19** | `design-and-architecture.tex:523-558` |
| §3.4.3 BKT — fill empty stub (typo "Training" was also fixed) | **Done 2026-05-19** | `design-and-architecture.tex:560-601` |
| §3.4.4 Improved Struggle — fill empty stub (3-bucket + graceful-degradation matrix) | **Done 2026-05-19** | `design-and-architecture.tex:603-679` |
| §3.5 RAG Feedback Design — fill empty stub (hybrid pandas + ChromaDB + HNSW) | Pending | `design-and-architecture.tex:320` |
| §3.6.2 Figma figures — annotate `[TODO: replace with screenshot]`; drop "conceptual design" | Pending | `design-and-architecture.tex:334-360` |
| §3.6.3 Lab Assistant View — fill empty stub (Join / Waiting / Assigned states) | Pending | `design-and-architecture.tex:362` |
| §3.1 architecture diagram — redraw for V2 (`models/`, RAG, lab assistant, `lab_session.json`) | Queued for Step 8a | `figures/design-and-architecture/architecture-diagram.png` |

**Standing mismatches still present** (will close as sub-tasks above complete):

- IRT, BKT, improved struggle model, mistake clustering — none in design chapter yet
- No mention of saved sessions, data analysis views, sound effects, academic calendar, settings page (some may be deferred to Ch4 implementation rather than Ch3 design)
- Figma mockups still rendered as designs rather than completed system

**Resolved by the 2026-05-18 work** (no longer mismatches):

- Struggle variable list is 7-signal — matches `STRUGGLE_WEIGHT_*` in `config.py:19-26`
- Normalisation paragraph correctly describes the uniform min-max step that `analytics.py:322-330` applies (raw → `_hat`/`_norm` columns feeding the weighted sum)
- `e` (binary count) replaced by `i` (cumulative mean of LLM incorrectness scores) — symbol now matches `analytics.py:281` (`i_hat = group["incorrectness"].mean()`)
- `A^raw` reframed as exponential time-decay (half-life 1800 s) — replaces the older position-based convex weights `[0.35, 0.25, 0.20, 0.12, 0.08]` superseded in `config.py:30-32`
- 7-term Struggle Score equation displayed with default weights ($\alpha=0.10,\beta=0.10,\gamma=0.20,\delta=0.10,\eta=0.38,\zeta=0.05,\theta=0.07$); accompanying weights table inserted (`tab: struggle weights`)
- Bayesian shrinkage paragraph added: $S^{\mathrm{shrunk}} = (n/(n+K))S^{\mathrm{raw}} + (K/(n+K))\bar{S}^{\mathrm{raw}}_\sigma$ with $K=5$ — matches `analytics.py:346-350` exactly; applied at aggregate level not per-signal; cited `efronSteinsParadoxStatistics1977`
- §3.3.2 Temporal Smoothing stub filled — opening paragraph names the two noise sources; per-submission decay paragraph cross-references `eq:time-decay-weight` and `eq:a-raw`; EWMA paragraph cross-references `eq: temporal struggle` (the single canonical EWMA equation, now in §3.3.1 with `S^{\mathrm{shrunk}}` on the RHS — duplicate equation eliminated). Comparison table `tab: temporal smoothing` contrasts the two mechanisms.
- §3.3.3 Question Difficulty extended from 4-signal to 5-signal — adds first-attempt failure rate `$p_q$` (count) and `$	ilde{p}_q = p_q/n_q$` (rate) as the new fifth signal with weight $\epsilon = 0.20$. New weights table `tab: difficulty weights` mirrors `tab: struggle weights`. Equation labelled `eq:difficulty-raw` (replaces the old duplicate `eq:placeholder_label`). EWMA equation gets `eq: temporal difficulty` label. Threshold definition added: "a submission is treated as correct if $i_{s,\sigma,k} < 	au$ with $	au = 0.5$" — pins down what `$c_q$` and `$p_q$` mean. Pre-existing sentence-fragment after `ef{sec: data endpoint}` fixed in the Identified Variables intro.
- §3.3.4 Collaborative Filtering closing paragraph re-tensed — "is still going to be implemented" replaced with "is implemented alongside the parameter-based model"; UI exposure described in present tense ("exposed through the Settings panel", "is enabled by default with $k=3$ nearest neighbours and a configurable elevation threshold, and can be turned off"); UK spelling ("neighbours"); hyphenated "parameter-based"; redundant final sentence about small-class unreliability dropped (the limitation is already covered in the preceding paragraph). Pre-existing missing-verb error fixed in the same paragraph ("collaborative filtering approach results are not reliable" → "approach produces results that are not reliable").
- §3.3.5 Mistake Clustering empty stub filled — pipeline (TF-IDF vectorisation → $k$-means clustering → silhouette-based auto-$k$ selection → LLM cluster labelling) with cross-reference to Ch2 §2.3.2 for the formal math; auto-$k$ selection equation `eq:cluster-auto-k` displayed; parameter values stated ($N_{\min} = 3$, $K_{\max} = 5$, "up to three representative answers"); interpretation paragraph positions clustering as complementary to the parametric difficulty signal. Six citations resolved: Salton 1975, Manning 2006, MacQueen 1967, Arthur & Vassilvitskii (k-means++), Rousseeuw 1987, Wang 2023.
- **Chapter-wide constants policy decision (Option 1)** — all `	exttt{CONSTANT\_NAME}` references stripped from Ch3 prose and tables. The struggle weights table and difficulty weights table reduced from 4 columns to 3 columns (Symbol / Meaning / Weight); the rightmost "config.py key" column removed. §3.3.5 already authored without constant names. Numeric parameter values ($N_{\min} = 3$, $K_{\max} = 5$, $K = 5$ for shrinkage, $	au = 0.5$, half-life $H = 1800$ s, $\lambda = 0.3$) stay — these are design choices, not implementation names. **Ch4 implementation chapter (Step 5 of [[Full Roadmap]]) is now where these constants should be reintroduced** alongside the configuration-module description.
- §3.4.1 Measurement Confidence empty stub filled. Important correction from the original brief: the live formula has **two factors + base multiplier**, not three. Code reality (`models/measurement.py:46-50`): `confidence = MEASUREMENT_CONFIDENCE_BASE * length_factor * (0.5 + 0.5 * extremity_factor)`. There is **no "model agreement" factor** despite the Rewrite Queue having claimed so — that was a misreading of the code. Section now states $\kappa = \kappa_0 \cdot \mathrm{length} \cdot (	frac{1}{2} + 	frac{1}{2}\,\mathrm{extremity})$ with the empty/missing feedback edge case (forced to 0) called out explicitly. Cite `lord1968statistical`. Half-and-half scaling justified as smooth-degradation design choice. Surfacing as green/amber/grey indicator in Question Detail view described as a colon-delimited list rather than the original "which" pronoun.
- §3.4.2 Item Response Theory empty stub filled. Rasch 1PL model $P(X_{s,q}=1) = \sigma(	heta_s - eta_q)$ presented with the Bernoulli log-likelihood maximised by L-BFGS-B (`models/irt.py:67-163`); ability-centring used to break additive identifiability degeneracy. Logit-scale $\hateta_q$ mapped to $[0,1]$ via sigmoid as $D^{\mathrm{IRT}}(q) = \sigma(\hateta_q)$ for UI comparability with the baseline $D_t(q)$. Graceful degradation when response matrix too sparse — falls back to baseline difficulty. Cited `rasch1960probabilistic`, `lord1968statistical`, `fisherMathematicalFoundationsTheoretical1922`; Byrd 1995 (L-BFGS-B) is still missing from `references.bib`. Forward reference `sec: improved struggle` will resolve when J (§3.4.4) lands.
- §3.4.3 Bayesian Knowledge Tracing empty stub filled. 2-state HMM with 4 parameters per skill: $P(L_0), P(T), P(G), P(S)$, identifiability constraint $P(G) + P(S) < 1$ enforced via $[0, 0.5]$ bounds on guess and slip. Update equation eq:bkt-update combines Bayesian posterior with learning transition; predictive equation eq:bkt-predict gives expected next-attempt correctness. Global parameter fit by L-BFGS-B against forward-algorithm log-likelihood (`models/bkt.py:195-337`); fitting refused when fewer than `BKT_FIT_MIN_OBSERVATIONS` (50) attempts or when all attempts are graded the same way. Per-(student, question) mastery and aggregate summary feed the improved struggle model. Cited `corbettKnowledgeTracingModeling1995`, `yudelsonIndividualizedBayesianKnowledge2013` (the latter for the per-student extension not implemented here). Bonus: §3.4.3 subsection heading typo Training fixed.
- §3.4.4 Improved Struggle Model empty stub filled. Three-bucket convex combination (behavioural composite, mastery gap, difficulty-adjusted score) with default weights 0.45/0.30/0.25; equation eq:improved-struggle. Behavioural composite is the equal-weighted mean of four cohort-normalised baseline sub-signals. Mastery gap is one-sided: max(mean BKT mastery minus recent correctness, 0). Difficulty-adjusted score weights recent incorrectness inversely by IRT difficulty; coverage-weighted shrinkage toward cohort mean for sparse users. Graceful-degradation table (tab: improved struggle degradation) covers four scenarios with weight redistribution preserving the sum-to-one invariant. Mean imputation for missing BKT mastery cites Little & Rubin. Final Bayesian shrinkage toward cohort mean uses the same n/(n+K) form with K=5 as baseline. Closes the cross-references forward from IRT (§3.4.2) and BKT (§3.4.3).
- §3.3.3 follow-up: difficulty model `$	ilde{p}_q$` denominator corrected from `$n_q$` (total attempts) to `$|\mathcal{S}_q|$` (unique students) to match `analytics.py:573` (`p_tilde = failed_first / unique_students`). Equation at line 294 and table description at line 353 both updated; the original brief was wrong about the denominator.
- §3.1 intro and §3.3 intro re-tensed to present tense; "event-driven pipeline under exploration" removed
- Label hygiene: `eq:struggle-raw` and `eq:struggle-shrunk` introduced (replacing the old duplicate `eq:placeholder_label`); pre-existing `eq: temporal sturggle` typo corrected to `eq: temporal struggle`; `S^{raw}` → `S^{\mathrm{raw}}` consistency restored
- **LaTeX build resolved**: stale `Report/main.out` was causing a hyperref `\@@BOOKMARK` runaway-argument error on the "Measurement Confidence" subsubsection bookmark; deleting `.out` (and auxiliary regenerated from scratch on next compile) cleared it. PDF now builds at 52 pages without compile errors.

**Housekeeping carried forward**:

- `\cite{morrisParametricEmpiricalBayes1983}` at `design-and-architecture.tex:206` references a bib key that does not exist in `references.bib`. Will render `[?]` in PDF after `bibtex` pass. Either add the bib entry (Morris, C. N. 1983, JASA 78(381), 47-55) or swap to `[BIB MISSING: Morris 1983]` placeholder for Step 12 polish.

**Code-state correction** (was outdated in this note before 2026-05-18): `SMOOTHING_ENABLED = True` in `config.py:74` (α = 0.3). The previous note claimed it was `False` and unused — that was stale. The stub IS active across refresh cycles. Thesis §3.3.2 should describe it as implemented; per-submission decay inside `A^{\mathrm{raw}}` is a separate mechanism (half-life 1800 s from `DECAY_HALFLIFE_SECONDS`).

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
