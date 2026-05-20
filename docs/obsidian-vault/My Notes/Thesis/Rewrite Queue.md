# Rewrite Queue

Specific, actionable rewrite tasks for the thesis, grouped by priority. Each item references an exact chapter/section and describes what to change.

Related: [[Report Sync]], [[Thesis Overview]], [[Evidence Bank]], [[Figures and Tables]]

---

## Critical — chapters that must be written

- [ ] **Write Ch5 Evaluation** — entire chapter is empty (5 subsections: Evaluation Design, Functional Testing, Non-Functional Testing, Results, Discussion). See [[Ch5 – Results and Evaluation]] for suggested content.
- [ ] **Write Ch6 Conclusion** — entire chapter is empty (Summary, Future Work). See [[Ch6 – Conclusion]] for suggested content.
- [~] **Fill research gaps placeholder** — now §2.6 in `requirements-specification.tex:281`. The `[FILL IN]` placeholder is gone; the commented-out draft is wrapped in `\begin{comment}...\end{comment}` at `:285-294`. Brief landed 2026-05-19; user to uncomment, then revise paragraph-by-paragraph per the notes below. The draft predates the Ch2 expansion (KT/BKT, Text Mining, RAG were not yet written) so each existing paragraph needs sharpening and one new synthesis paragraph should be added.

  - **Paragraph 1 — lit-review recap.** Keep the high-level framing (learning analytics + dashboards + real-time). Expand the methods inventory: the draft only names three areas, but the chapter now also reviews struggle modelling (§2.2.1), knowledge tracing and Bayesian student models (§2.2.2), task difficulty including IRT (§2.2.3), collaborative filtering (§2.3.1), text mining and mistake clustering (§2.3.2), retrieval-augmented generation and dense retrieval (§2.4). One sentence acknowledging this broader inventory is enough. Re-tense: replace "we will address" with declarative language ("This chapter has surveyed…"). British spelling throughout.
  - **Paragraph 2 — lab-classroom problem.** Keep the substance (shy students, hand-raising bias, end-of-lab data not actionable mid-session). Single tense fix: "By creating a dashboard…we can…" reads as a proposal; rewrite as a declarative motivation ("A real-time dashboard that integrates these signals during the session can…" or similar — student-authored voice, no first-person plural where avoidable).
  - **Paragraph 3 — AI scoring, struggle, CF gaps.** Sharpen three sub-gaps against the chapter:
    - **LLM-as-judge as a correctness signal.** The draft says "there has been no use of AI to classify data" — that overstates it. §2.2.1 already cites Koutcheme and Pitts for LLM-generated *feedback*. The actual gap is that LLM-judged correctness has not been used as the **primary per-submission incorrectness signal** feeding a live struggle metric — feedback-grading studies treat the LLM as a downstream evaluator, not as an upstream classifier. Phrase the gap that way.
    - **Course-level vs live-session struggle detection.** Keep — supported by Dong / Or / Estey / Piech in §2.2.1, where the temporal scale ranges from within-assignment to course-level but live-session instructor-facing aggregation is unaddressed.
    - **CF unaddressed in real-time labs.** Keep — already framed correctly against §2.3.1 (sparseness + start-of-session unreliability).
  - **Paragraph 4 — new gap to add: knowledge tracing and mistake clustering not deployed live.** Two parts:
    - **BKT instructor-facing aggregate.** §2.2.2 surveys BKT (Corbett & Anderson, Yudelson) and acknowledges deep alternatives (Piech DKT, Khajah) but BKT is consistently studied as an *individualised* tutoring component, not as a cohort-level interpretable signal exposed to instructors during a live session. Frame this as the gap.
    - **Mistake clustering on free-text submissions.** §2.3.2 reviews TF-IDF + $k$-means + silhouette and LLM cluster labelling, but applies to information retrieval and general text clustering — its application to live discovery of cohort-level common-error clusters in computer-lab submissions is novel. Frame this as the gap.
  - **Paragraph 5 — reframed: lightweight on-the-move channel for lab assistants.** The original "lack of dashboards that integrate with smart devices" paragraph needs softening because FR6 was scoped out and the actual delivery was a **mobile-web lab-assistant app** (see Ch1 risk-table Row 4 brief). Re-cast the gap as the **underlying need** — lab assistants need a lightweight, mobile, on-the-move channel that surfaces struggling students in real time without requiring proprietary hardware or extra cognitive load. Smart-device integration itself becomes a Ch6 §6.3 future-work item, not the original-formulation gap.
  - **Paragraph 6 (new, optional) — synthesis.** One paragraph drawing the gaps together into the thesis motivation: live-session timing + interpretable struggle signals + cohort-level mistake patterns + grounded LLM feedback + lightweight assistant channel = the integrated affordance this thesis contributes. Closes the loop back to the Ch1 objectives. Skip if the user prefers a tighter chapter.

  **Verification after uncomment + revision.** `pdflatex` of `Report/main.tex` compiles with no new warnings; §2.6 renders with a numbered subsection heading (no longer empty); cross-references within the new prose (e.g. to §2.2.1, §2.2.2, §2.3.1, §2.3.2, §2.4) all resolve; no inline `\cite{}` is added without a corresponding entry in `references.bib` (the brief intentionally avoids new citations — all gaps lean on works already cited upstream). After transcription, run `python scripts/sync_literature.py` to refresh `coverage.md`.
- [ ] **Populate Appendix B (UI Screenshots)** — empty; needs screenshots of all dashboard views to support Ch4 and Ch5.
- [ ] **Populate Appendix C (Detailed Test Results)** — empty; needs test evidence to support Ch5.
- [ ] **Populate Appendix A (Code Snippets)** — empty; needs key implementation code to support Ch4.
- [ ] **Populate Appendix E (Formulae)** — empty; collect all model formulas in one reference.
- [ ] **Populate Appendix F (Formulae Derivation)** — empty; provide derivation steps for key models.

---

## High — outdated content that misrepresents the system

- [~] **Rewrite Ch4 Implementation for the final system (V1 + V2)** — entire chapter currently describes the old V1-prototype draft. Must describe: OpenAI scoring, 7-signal struggle, 5-signal difficulty, CF, mistake clustering, IRT, BKT, improved struggle, lab assistant system, saved sessions, 6 views, settings, AND the V1 (Streamlit, `code/`) vs V2 (React + FastAPI, `code2/`) evolution. *Brief delivered 2026-05-20 at [[Ch4 Rewrite Brief]] (single vault note, ~12 subsection blocks with maths recap + figure slots + drop-in LaTeX tables); user to author into `Report/main-sections/implementation.tex` against the brief. **Framing decision 2026-05-20: thesis brands the Streamlit stack as V1 and the React+FastAPI stack as V2** — V2 is the evolution of V1's presentation layer, not an "alternative". Both are deployed; V1 is not a prototype. Brief also folds in marker feedback (Marker 1 = no math-modelling → required Maths recap line in every §4.6.x / §4.8.x; Marker 2 = no comparison study → "Why V2?" framing in §4.3.3 naming concrete V1 limitations + V1-vs-V2 parity table `tab:views-comparison` in §4.9.0).* See [[Ch4 – Implementation]] and the brief.
- [~] **Remove V1 prototype framing from Ch4** — replace "at this stage", "proof of concept", "to be implemented in the later iteration", "foundation for what the dashboard will eventually become" with final-system language. *Addressed in [[Ch4 Rewrite Brief]] §4.1 (drop-in replacement for `implementation.tex:11-18`) and in the brief's "Forbidden patterns" list in Part E.*
- [x] **Update Ch3 §3.3.1 struggle formula** — thesis has 5 components (n, t, e, f, A_raw); code has 7 (adds r_hat, d_hat, rep_hat). Update formula, add Bayesian shrinkage description. *Done 2026-05-18 — §3.3.1 closed: 7-signal itemize, uniform min-max paragraph, exponential time-decay $A^{\mathrm{raw}}$, 7-term equation with weights table, Bayesian shrinkage paragraph citing Efron 1977. See [[Ch3 – Design and Modelling]].*
- [x] **Update Ch3 §3.3.2 difficulty formula** — thesis has 4 components; code has 5 (adds p_tilde first-attempt failure). *Done 2026-05-19 — §3.3.3 closed: 5-signal equation with default weights `α=0.28, β=0.12, γ=0.20, δ=0.20, ε=0.20`, accompanying weights table `tab: difficulty weights`, threshold $	au=0.5$ defined.* (Note: numbered §3.3.2 here in the Rewrite Queue, but the actual section in the .tex is §3.3.3 after the Temporal Smoothing subsection was added between Struggle and Difficulty.)
- [~] **Reframe Figma mockups in Ch3 §3.6.2** — *updated 2026-05-19. Previous framing said "replace with screenshots" — that was wrong. Figma mockups are design artifacts and belong in Ch3 as-is; deployed-system screenshots belong in Ch4 (Implementation) and Appendix B (UI Screenshots). Typo pass on §3.6 done (backtick, `is will allow`, `based off`, `have been help`). The `conceptual design rather than a fully implemented system` caveat still needs softening to reposition the mockups as design specification rather than rough concept; deferred to chapter-wide design-vs-implementation reframe pass.*
- [x] **Update Ch3 CF section** — change "is still going to be implemented" to describe actual implementation. *Done 2026-05-19 — §3.3.4 closing paragraph rewritten: "is implemented alongside the parameter-based model", exposed through the Settings panel, default-on with $k=3$ nearest neighbours and a configurable elevation threshold, switchable off. UK spelling, hyphenated "parameter-based". `design-and-architecture.tex:476, 478`.*
- [~] **Update Ch4 deferred features list** — line 58 says "assistant allocation and smart device notifications, are to be implemented in the later iteration." Assistant allocation IS implemented. Only smart devices remain deferred. *Addressed in [[Ch4 Rewrite Brief]] §4.10 (Lab Assistant System described as deployed; smart-device deferral moved to Ch6 §6.3 per Full Roadmap entry 13).*
- [~] **Add missing V2 features to Ch3 or Ch4** — IRT difficulty, BKT mastery, improved struggle model, mistake clustering, measurement confidence, saved sessions, data analysis views, lab assistant system, settings page, sound effects, academic calendar. None appear anywhere in the thesis. *Ch3 side closed 2026-05-19 (§3.3.5 clustering, §3.4.2 IRT, §3.4.3 BKT, §3.4.4 improved struggle). Ch4 side addressed in [[Ch4 Rewrite Brief]] — every missing feature has a dedicated subsection block: §4.6.5 (clustering), §4.8.1 (measurement confidence), §4.8.2 (IRT), §4.8.3 (BKT), §4.8.4 (improved struggle), §4.5.2 (saved sessions), §4.9.4 (data analysis), §4.10 (lab assistant), §4.9.6 (settings), §4.11 (sound effects), academic calendar referenced in §4.9.4.*

---

## Medium — language and framing improvements

- [x] **Convert Ch1 future tense to past/present** — §1.2, §1.3, §1.5 use "we will", "the system will" throughout. Should describe completed work.
- [~] **Update Ch1 risk mitigations** — Table 1 mitigations are generic ("seek constant feedback", "explore smartwatch solutions"). Row-by-row brief landed 2026-05-19; user to transcribe into `introduction.tex:75-95`. Five rows total; rows 1 and 5 are mild rewrites, rows 2–4 are full replacements. Verified against current code in the same session — see "Verified facts" at the end of this entry.

  - **Row 1 — Latency in real-time data processing.** Keep risk + impact. New mitigation: a layered caching strategy — `@st.cache_data(ttl=10)` on the API fetch hides upstream delays; analytics results are memoised for 300 s (`_ANALYTICS_TTL`); OpenAI-judged incorrectness is persisted to `data/incorrectness_cache.json` so a cold boot reuses prior judgements rather than re-paying the LLM round-trip. Lab-assistant app polls on a 5 s interval to keep shared session state coherent without flooding the API.
  - **Row 2 — Unstable struggle/difficulty estimates from insufficient data.** Keep risk + impact (tighten phrasing if desired). New mitigation: **Bayesian shrinkage toward the cohort mean**. Each student's struggle score is blended with the class average using a credibility weight $w_n = n / (n + K)$ with $K = 5$ (`SHRINKAGE_K`), so a student with two submissions is mostly pulled toward the baseline while a student with twenty keeps their own score. The same insufficient-data principle drives the confidence-tagged outputs of the `measurement` model. **Drop** the "use an LLM to identify whether data is suitable" wording — that approach was not the one implemented.
  - **Row 3 — Overly complicated dashboard.** Keep risk + impact. New mitigation: deliberate information architecture rather than ad-hoc UI feedback. Figma mockups were iterated before implementation; the instructor app settled on four focused views (in-class overview, student detail, question detail, data analysis) with threshold-driven colour coding (the configurable `list[tuple[float, float, str, str]]` pattern) to surface attention items rather than overwhelm with raw numbers. The mobile lab-assistant interface was split out into its own app/route to keep the instructor screen uncluttered. Per [[feedback-supervisor-attribution]] — phrase as student-authored design decisions; no inline supervisor attribution.
  - **Row 4 — Unable to implement smart glasses functionality.** Keep risk; reframe impact as "loss of an on-the-move notification channel for lab assistants". New mitigation: **FR6 (smart-device integration) was scoped out as future work** — hardware procurement was outside the project envelope. The on-the-move channel was instead delivered as a **mobile-web lab-assistant app** (Streamlit `lab_app.py` on port 8502; mirrored as the `/assistant` route in the React stack), sharing live session state with the instructor view via the file-locked `data/lab_session.json`. This preserves the original intent (lightweight, on-the-move assistant notifications) without requiring proprietary hardware. Note: this should land alongside the FR-table update (Step 4 item 4 — move FR6 to "Won't Have").
  - **Row 5 — Limited targeting across different modules.** Keep risk + impact. The original "design over generic interaction patterns" line is sound — enrich it with the realised architecture. The `learning_dashboard/models/` package (`irt.py`, `bkt.py`, `measurement.py`, `improved_struggle.py`) operates only on submission/correctness signals common to all CS modules. Signal weights redistribute when a model has insufficient coverage (e.g. if IRT lacks variance, its weight folds into the behavioural composite; see the degradation matrix in §3.4.4), so the dashboard degrades gracefully on smaller or atypical cohorts rather than failing.

  **Verified facts this brief leans on** (re-checked against working code, not just recalled from memory):
  - Bayesian shrinkage with $K = 5$ in `improved_struggle.py` (uses `config.SHRINKAGE_K`), applied as the final transform on struggle scores at the aggregate level.
  - `models/` package has the four modules listed, both in `code/` and `code2/`; the improved models are the only models exported from `models/__init__.py`. There is **no live `improved_models_enabled` toggle** despite the old CLAUDE.md note — do not claim one in the prose.
  - OpenAI failure path returns `None` in `analytics.py`, then a `0.5` default at the call-site; weight redistribution in `improved_struggle.py` covers missing-signal cases.
  - FR6 currently reads "*The system must integrate with smart devices such as phones, watches and glasses…*" in `requirements-specification.tex` and is in the "Should Have" block. Grep finds no smartwatch / smart-glass / wearable code in either stack — safe to say "scoped out / unimplemented".
  - `@st.cache_data(ttl=10)` is on `fetch_raw_data` only; `_ANALYTICS_TTL = 300` is the analytics-layer cache; disk-persisted incorrectness cache lives at `data/incorrectness_cache.json` (per [[project_boot_speed_fix]]).

  **Verification after transcription.** `pdflatex` build of `Report/main.tex` completes without new warnings; Table 1 fits page width (column widths unchanged — only cell text differs); `\ref{tab:risks}` still resolves; no row mentions FR6 as a current commitment; phrasing matches Ch3/§3.4.4 wording for Bayesian shrinkage and the modular models package so the table doesn't contradict the design chapter.
- [ ] **Add implementation status to Ch2 requirements** — FR1-FR7 and NFR1-NFR6 need mapping to current implementation state. Could be inline or in Ch5 evaluation.
- [ ] **Update Ch2 FR6 status** — smart device integration is "Should Have" but completely unimplemented. Either move to "Won't Have" or discuss honestly as future work.
- [x] **Update Ch3 threshold label names** — thesis uses None/Low/Medium/High; code uses On Track/Minor Issues/Struggling/Needs Help. *Done (uncommitted) 2026-05 — Tbl 6 / Tbl 7 in `design-and-architecture.tex:369-393` updated alongside traffic-light recolour.*
- [x] **Address temporal smoothing** — Ch3 proposes exponential smoothing for both models. *Done 2026-05-18 — §3.3.2 Temporal Smoothing now distinguishes the two mechanisms: per-submission exponential time-decay inside $A^{\mathrm{raw}}$ (half-life 1800 s) and EWMA across refresh cycles applied to $S^{\mathrm{shrunk}}$ with `SMOOTHING_ALPHA = 0.3` (active by default). Comparison table inserted (`tab: temporal smoothing`). The §3.3.1 Temporal updating equation updated to smooth $S^{\mathrm{shrunk}}$ rather than $S^{\mathrm{raw}}$.*
- [x] **Remove or update "event-driven pipeline under exploration"** — Ch3 §3.1 mentions this; V2 is still interval-based. *Done 2026-05-18 — sentence deleted in `design-and-architecture.tex:6`.*
- [ ] **Confirm Progress Report exclusion** — `Progress Report.tex` is commented out in `main.tex`. Verify it stays excluded from final submission.
- [~] **Review Ch2 commented-out research gaps** — duplicate of the Critical-block "Fill research gaps placeholder" item; brief landed 2026-05-19 against the actual location (`requirements-specification.tex:285-294`). Track only the Critical-block entry from here on.

---

## Supervisor meeting items — outstanding

- [x] **Document improvement trajectory in report** — linear regression slope is implemented in `analytics.py` but not described anywhere in the thesis. *Done 2026-05-18 — added as $d_{s,\sigma}$ in §3.3.1 Identified Variables and as $\hat{d}_{s,\sigma}$ in the 7-term Struggle Score equation with weight $\zeta = 0.05$. No citation inline yet (Draper & Smith / regression-slope cite still in Ch2 §2.1.4 backlog).*
- [x] **Document answer repetition rate in report** — `rep_hat` is a live signal in the 7-component struggle model but undocumented in the thesis. *Done 2026-05-18 — added as $\mathrm{rep}_{s,\sigma}$ in §3.3.1 Identified Variables, derived as $\tilde{\mathrm{rep}}_{s,\sigma} = \mathrm{rep}/n$, and as $\widehat{\tilde{\mathrm{rep}}}_{s,\sigma}$ in the 7-term equation with weight $\theta = 0.07$.*
- [x] **Document Bayesian shrinkage in report** — shrinkage is applied to all struggle signals but not described in Ch3 or Ch4. *Done 2026-05-18 — new paragraph in §3.3.1 with eq. `eq:struggle-shrunk` showing $S^{\mathrm{shrunk}} = (n/(n+K))S^{\mathrm{raw}} + (K/(n+K))\bar{S}^{\mathrm{raw}}_\sigma$, $K=5$. Cites `efronSteinsParadoxStatistics1977`. Important correction to the original Rewrite Queue framing: the shrinkage is applied to the **aggregate** struggle score, not to every signal individually (confirmed against `analytics.py:346-350`).*
- [x] **Reconcile temporal smoothing (report vs code)** — *Done 2026-05-18 — duplicate of the Medium-block "Address temporal smoothing" item; §3.3.2 now describes both mechanisms as active. Appendix E cross-reference deferred until Appendix E itself is populated (Step 10 of [[Full Roadmap]]).*
- [x] **Align retry rate / feedback requests naming** — report uses "feedback requests"; code uses `retry_rate`. *Done 2026-05-18 in Ch3 §3.3.1 — the `f_{s,\sigma}` "AI feedback requests" variable dropped from the struggle signal list; `r_{s,\sigma}` (retry rate) added as the corresponding signal, matching `STRUGGLE_WEIGHT_R`. Ch4 still to be reconciled when rewritten (Step 5).*
- [ ] **Draft CF evaluation subsection in Ch5** — use held-out historical sessions as proxy ground truth; report RMSE, precision@k, and coverage. This was flagged as an open question by Dr Batmaz.
- [ ] **Add future work item: ML-based weight optimisation** — Ch6 future work should mention that once labelled ground truth data is available, the parametric weights (α, β, γ, δ, η) could be optimised via supervised ML rather than set manually.
- [ ] **Add Ch3 §3.3.1 acknowledgement: missing-feedback fallback** — one sentence in the AI-Based Answer Rating paragraph noting that when `ai_feedback` is absent or the scoring call fails, incorrectness defaults to 0.5; this conservative midpoint causes the submission to be treated as incorrect under $	au = 0.5$, flagging un-evaluable students for attention rather than silently ignoring them.
- [ ] **Add Ch5 §5.5 Limitations paragraph: signal attenuation under missing-feedback** — when a substantial fraction of submissions lack `ai_feedback` and default to 0.5, mean incorrectness $\hat{\imath}$ and $A^{\mathrm{raw}}$ cluster around 0.5, attenuating the struggle signal; the binary threshold also inflates the difficulty $c_q$/$p_q$ counts and contaminates mistake clustering. Quantify (% of submissions affected on the available session data) and discuss honestly. See [[Future Work Inventory#3b]].
- [ ] **Add Ch6 §6.3 Future Work bullet: decouple incorrectness from tutor-feedback availability** — three alternatives: (a) direct LLM grading on `(question, target, student_answer)`; (b) embedding-based semantic similarity to target (cheap, local, deterministic); (c) confidence-weighted aggregation using existing `incorrectness_confidence` from `models/measurement.py` to down-weight low-confidence submissions. (c) is the smallest viable change. Extends the existing "wire measurement confidence to UI" future-work item — not just *display* the confidence, but *use* it in the aggregation.
- [ ] **Insert all pending citations** — new sections added (CF alternative model §3.3.3, weight justification §3.3.4, struggle modelling §2.1.4, recommender systems §2.1.5) have identified sources but no inline `\cite{}` calls yet.

---

## Methods lit-review backlog (2026-04-18)

Mathematical / ML techniques used in the codebase that currently have no corresponding citation in the lit review. Each item names the exact target section(s); most Ch3 subsections already exist and just need `\cite{}` calls, but Ch2 needs three brand-new subsections. See the full audit table at `C:\Users\Bakri\.claude\plans\alright-for-our-lit-indexed-hamming.md`.

**Editorial rule for notation:** Ch2 gets one core equation per technique + citation; Ch3 gets the equations actually used with default parameters from `config.py`; Appendix E holds the consolidated formula reference; Appendix F holds derivations. Do not bloat Ch2 with full notation.

- [x] **Ch2 §2.1.5 (NEW) — Knowledge Tracing and Bayesian Student Models** — create the subsection between current §2.1.4 Struggle and §2.1.5 Task Difficulty; renumber §2.1.5–§2.1.7 accordingly. ~400 words framing KT as latent-trait + HMM. Cite Corbett & Anderson (1995) and Yudelson, Koedinger & Gordon (2013). Show BKT equation (d) — posterior + transition update — as the single representative equation. *Done — landed as §2.2.2 "Knowledge Tracing and Bayesian Student Models" at `requirements-specification.tex:99`. BKT predictive equation `eq:bkt-prediction` displayed; cites `corbettKnowledgeTracingModeling1995`, `yudelsonIndividualizedBayesianKnowledge2013`, plus bonus Khajah, Kim, Piech, and Khajah-DKT-equivalence to round out the field.*
- [x] **Ch2 §2.1.7 (NEW) — Text Mining and Mistake Pattern Discovery** — create the subsection after renumbered CF, before research-gaps summary. Cite Salton & McGill (1983), MacQueen (1967) / Lloyd (1982), Arthur & Vassilvitskii (2007), Rousseeuw (1987), Salton & Lesk (1968). *Done — landed as §2.3.2 "Text Mining and Mistake Pattern Recovery" at `requirements-specification.tex:152` with `\label{sec: text mining}`. TF-IDF (`eq:tfidf`), $k$-means (`eq:kmeans`), and silhouette (`eq:silhouette`) all displayed. Cites Salton 1975, Manning 2006, MacQueen 1967, Arthur & Vassilvitskii (k-means++), Rousseeuw 1987, plus Wang 2023 for LLM cluster labelling.*
- [x] **Ch2 §2.1.8 (NEW) — Retrieval-Augmented Generation for Instructor Feedback** — merges with / supersedes the existing `#meeting3` RAG literature-review item. Cite Lewis et al. (2020), Reimers & Gurevych (2019), Malkov & Yashunin (2020). *Done — landed as §2.4 "Retrieval-Augmented Feedback" with two subsubsections: §2.4.1 "Retrieval-Augmented Generation" at `requirements-specification.tex:186` and §2.4.2 "Dense Retrieval and Approximate Nearest Neighbour Search" at `:197`. Cites Lewis 2020, Reimers & Gurevych 2019, Malkov & Yashunin 2020 (HNSW), plus Kasneci 2023 for the hallucination-grounding motivation.*
- [ ] **Ch2 §2.1.X (NEW — LLM-as-Judge Scoring) OR extend §2.1.4** — gpt-4o-mini is the entry point of the whole pipeline but has zero citations. Cite Zheng et al. (2023) *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*; discuss calibration + fallback behaviour (0.5 default on parse failure). Ch3 §3.3.0 / Ch4 §4.7.1 get matching `\cite{}`.
- [ ] **Ch2 §2.1.4 extension — composite + temporal + shrinkage + regression paragraphs** — insert four short method paragraphs within the existing struggle-modelling subsection. Cite OECD/JRC (2008), Nardo et al. (2005), Ebbinghaus (1885), Wixted & Carpenter (2007), Efron & Morris (1977), Morris (1983), Draper & Smith (1998), Han/Kamber/Pei (2011). Closes the citation half of three existing supervisor items (improvement trajectory / answer repetition / shrinkage).
- [ ] **Ch2 §2.1.6 (renumbered) Task Difficulty extension** — add Rasch (1960), Lord & Novick (1968), Wright & Stone (1979) alongside existing Baucks / Pankiewicz / Baeres.
- [ ] **Ch2 §2.1.7 (renumbered) Collaborative Filtering extension** — add Herlocker et al. (1999), Resnick et al. (1994) alongside existing Schafer 2007.
- [ ] **Ch3 §3.3.1 / §3.3.2 / §3.3.3 / §3.3.x — insert missing `\cite{}` calls** for the references introduced in Ch2 §2.1.4 and the new §2.1.7.
- [ ] **Ch3 §3.3.x (NEW — Temporal Smoothing) OR paragraph in §3.3.1** — distinguish EWMA across snapshot refreshes (`SMOOTHING_ENABLED=True`, α=0.3) from per-submission exponential decay in A_raw. Two different techniques currently conflated. Appendix E lists both recurrences.
- [ ] **Ch3 §3.4.1 Measurement Confidence — add Lord & Novick (1968), Crocker & Algina (1986)** as the classical-test-theory basis for the 3-factor confidence formula.
- [x] **Ch3 §3.4.2 IRT — add Rasch (1960), Fisher (1922) footnote, Byrd et al. (1995) footnote** for 1PL derivation, MLE justification, and L-BFGS-B bounded optimisation. *Done 2026-05-19 — Rasch & Fisher cited; Byrd 1995 placeholder (still missing from `references.bib`).*
- [x] **Ch3 §3.4.3 BKT — add Corbett & Anderson (1995), Yudelson et al. (2013); display equation (d) inline** with default parameter annotation from `config.py` (`BKT_P_INIT`, `BKT_P_LEARN`, `BKT_P_GUESS`, `BKT_P_SLIP`). *Done 2026-05-19 — both citations resolved; update equation displayed inline (eq:bkt-update). **Default parameter values not stated in Ch3** per the chapter-wide constants policy (Option 1); they belong in Ch4 alongside the configuration-module description.*
- [x] **Ch3 §3.4.4 Improved Struggle — document three design mechanics**: (a) coverage-weighted shrinkage; (b) mean-imputation of missing mastery (Little & Rubin); (c) graceful-degradation weight redistribution with sum-to-one invariant. *Done 2026-05-19 — all three documented in §3.4.4 closure; degradation matrix surfaced as `tab: improved struggle degradation`. The invariant-assertion file:line anchor is intentionally not in Ch3 per the chapter-wide constants/anchors policy; it belongs in Ch4.*
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
- [x] **Ch3 — RAG Design** — hybrid SQL + ChromaDB architecture, justification. *Done 2026-05-19 — §3.5 closed. Hybrid two-layer retrieval (structured pre-filter then semantic search) presented at design-register; TikZ flow diagram added (`fig: rag architecture`); citations to Lewis 2020 (RAG), Kasneci 2023 (hallucination grounding), Reimers & Gurevych 2019 (sentence embeddings), Malkov & Yashunin 2020 (ANN/HNSW) all resolve. Library / model / parameter specifics deferred to Ch4 per design-vs-implementation split.* #meeting3
- [x] **Ch2 & Ch3 — RAG literature review** — *Ch3 part done 2026-05-19 — §3.5 cites Lewis 2020, Kasneci 2023, Reimers & Gurevych 2019, Malkov & Yashunin 2020 inline. Ch2 §2.4 RAG background subsections (§2.4.1 Retrieval-Augmented Generation, §2.4.2 Dense Retrieval and ANN Search) were closed earlier in the session.* #meeting3

---

## Phase 6 additions (2026-04-12)

New skeleton subsections added to `implementation.tex` and `design-and-architecture.tex`. Each placeholder needs writing — see [[Ch4 – Implementation]] and [[Ch3 – Design and Modelling]] for content guidance per section.

**Ch3 — new placeholders:**

- [x] **§3.3.x Mistake Clustering** — TF-IDF + K-means + OpenAI labeling design; justify auto-k via silhouette. *Done 2026-05-19 — §3.3.5 closed. Pipeline described with cross-reference to Ch2 §2.3.2 formal definitions; auto-$k$ via silhouette-maximisation displayed as `eq:cluster-auto-k`; parameters $N_{\min}=3$, $K_{\max}=5$ stated; complementary-to-$D_t(q)$ framing in the interpretation paragraph.*
- [x] **§3.x Advanced Model Design — Measurement Confidence** — *Done 2026-05-19 — §3.4.1 closed. Two-factor (length × extremity) + base multiplier formula, with the 0.5+0.5×extremity envelope justified as smooth-degradation design. **Correction to the original Rewrite Queue note**: there is no "agreement" factor in the live code — the formula has 2 factors plus a base, not 3. Also corrected: the UI does display the confidence (green/amber/grey indicator in Question Detail view), contrary to the "not yet displayed" framing.* Cited `lord1968statistical`.
- [x] **§3.x Advanced Model Design — Item Response Theory** — *Done 2026-05-19 — §3.4.2 closed. Rasch 1PL with sigmoid likelihood; joint MLE via L-BFGS-B; ability-centring for identifiability; sigmoid mapping $D^{\mathrm{IRT}}(q) = \sigma(\hateta_q)$ for UI scale parity with baseline; graceful degradation when response matrix sparse. Cited `rasch1960probabilistic`, `lord1968statistical`, `fisherMathematicalFoundationsTheoretical1922`. Byrd 1995 (L-BFGS-B) still missing from `references.bib`.*
- [x] **§3.x Advanced Model Design — Bayesian Knowledge Tracing** — *Done 2026-05-19 — §3.4.3 closed. HMM with 4 parameters; update and predictive equations displayed; global MLE via L-BFGS-B with $[0, 0.5]$ bounds enforcing $P(G)+P(S)<1$; graceful degradation on insufficient or single-class data. Cited `corbettKnowledgeTracingModeling1995` and `yudelsonIndividualizedBayesianKnowledge2013`. Subsection heading typo fixed.* Note: the original Rewrite Queue item header itself had the Training typo too — the corrected spelling is Tracing.
- [x] **§3.x Advanced Model Design — Improved Struggle Model** — *Done 2026-05-19 — §3.4.4 closed. Three-bucket convex combination (behavioural 0.45, mastery gap 0.30, difficulty-adjusted 0.25); one-sided mastery gap; coverage-weighted shrinkage on difficulty-adjusted score; four-scenario graceful-degradation table; mean imputation for missing BKT mastery (Little & Rubin); final Bayesian shrinkage K=5. Closes forward references from IRT (H) and BKT (I).*
- [x] **§3.6.3 Lab Assistant View** — *Done 2026-05-19 — three states (join, waiting, assigned) described in design-register; three mockup figures consolidated into one subfigure row; cross-references to §3.5 RAG. Figma PNGs outstanding.* (Note: numbered §3.4.x in the original Rewrite Queue header but the actual section landed as §3.6.3 under Interaction and UI Designs.)

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
