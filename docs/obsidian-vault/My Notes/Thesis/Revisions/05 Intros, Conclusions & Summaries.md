# 05 — Intros, Conclusions & Summaries (author writes)

Supervisor pts 11–14, 16: don't end sections/chapters abruptly on a figure; open each top-level section with a short framing paragraph (but check the existing ones first); summarise big tables; finish the abandoned sentences. ← [[00 Index]]

> **Re-anchored + reconciled 2026-05-31** against the live `Report/main-sections/*.tex`. Roughly nine items already done (writing landed during the Notes 01–04 passes); about thirteen remain. Delivery is chapter-by-chapter (Ch1 → Ch5; Ch6 needs no change); Ch2 gets the full treatment (intros + composite framing + glossary + §2.6 gaps). Status legend: ✅ done · ⬜ to write.

## Status reconciliation (verified anchors, 2026-05-31)
**✅ Already done (verified, no action):**
- Ch1 garbled first sentence (Note 01 I10) — `introduction.tex` reads clean now (l4 "at their own pace"; l18 "The central problem addressed … is therefore").
- §5.4 Results intro — exists, `results-and-evaluation.tex` l147–156.
- Eval abandoned "bayesian shrinkage" sentence — completed at l319 (full sentence, inline comment gone).
- Eval threshold-bias fragment — completed (no trailing fragment found).
- Eval Optuna summary after `tab:eval-hyperparams` — exists at l361.
- Eval prewarm interpretation — exists at l115–121 (**keep the "five-second polling" claim scoped to the lab-assistant app**: code-verified that only the mobile portal polls at 5 s; the instructor console uses 3 s / 10 s and the config default is 60 s).
- Fig 3.6 `fig:context-stakeholders` discussion — exists (fuller lead-in, names C1–C3).
- §4.9 instructor-views closer — exists at l1201–1210 (Session Progression view).
- Ch6 conclusion opener — fine, no change.
- Composite-metric formal definition — exists in the Design chapter (l471–587) + Appendix C / Nomenclature.

**⬜ Remaining (current anchors):**
- **Ch1** opener — `introduction.tex` l1–2.
- **Ch2** intros §2.2/§2.3/§2.4/§2.5 ✅ applied by author; composite framing + glossary dropped after review (see the supervisor-pt-16 section below). **Remaining:** §2.6 Research Gaps cleanup (heading l313; TODOs at l317/320/323/331; P3/P5 source paras l327–329) + the l151 Optuna accuracy fix (I13).
- **Ch3** §3.1 walkthrough five DRAFT-only figures (l111/124/139/154/168), lead-in l5, bridge; §3.5 closer after `fig:v2-pipeline-design` (l1094–1095); chapter-end summary after visual-encoding tables (l1341–1346).
- **Ch4** chapter intro (TODO near top); chapter summary (chapter ends on the problems table, l1254–1303); problems-table intro (l1257) + post-table summary; impl→design back-refs in the UI/view subsections (FC-02).
- **Ch5** chapter closer after `fig:eval-incorrectness-distribution` (l541–547); §5.2 intro (l80), §5.5 intro (l363), §5.6 intro (l462).

## Accuracy audit (code-verified, 2026-05-31)
Deep read of the live `code2/backend/` source agtainst the report's quantitative claims (the facts these briefs lean on). **All verified accurate** except one:
- **DISCREPANCY → logged as [[01 Integrity & Consistency Fixes]] I12:** `design-and-architecture.tex` l448 says min-max normalisation is "conventionally set to **0**" when `x_min = x_max`, but the deployed code (`code2/backend/analytics.py:50`) returns **0.5** (neutral midpoint, with a documented rationale: it preserves the signal's weight contribution on a degenerate cohort; rankings are unchanged). The "0" is a stale V1-era convention. Fix gated for Ch3.
- **τ symbol reuse (not an error):** τ = 0.5 is the correctness threshold (l618); τ ≈ 0.90 is the CF elevation threshold. The report already flags the reuse at l712; confirm Appendix C `tab:notation` lists both.
- **IRT is 2PL — confirmed in the report:** the design chapter presents Rasch 1PL for V1 (l870–879) then an explicit 2PL extension for V2 (l902–913: discrimination $\alpha_q$, $\sigma(\alpha_q(\theta_s-\beta_q))$, log-reparam, identifiability anchoring), matching `models/irt.py`. No fix needed.
- **§2.6 references audit (2026-05-31):** all 9 citekeys in the rewritten Research-Gaps section verified relevant + correct (koutcheme/pitts → LLM feedback; estey → course-level; dong → 4-consecutive-fail threshold; li_2020/schafer → CF recommendation; herlocker → CF sparsity; corbett/yudelson → BKT; salton/macqueen → text mining; kasneci/lewis → hallucination/RAG). Each accurately represents the prior work and the gap is framed as what that work did not do. No reference changes. (Minor prose typos flagged to author: l317 agreement/comma-splice, l320 "suport", l328 "retrieval-augemented", l333 "a future work", l335 stray comma.)
- **Ch3 references audit (2026-05-31):** all 14 design-chapter `\cite` keys exist in `references.bib` and are the correct canonical sources, with three actioned: (1) `lord1968statistical` at design l853 **removed** (the κ confidence heuristic is not classical test theory); (2) `little2014statistical` at l1031 **reframed** (correct missing-data authority but it does not endorse mean imputation); (3) `efron…1977` at l546 **left** (acceptable popular James-Stein ref; `morris…1983` anchors it). `lord1968statistical` stays valid for IRT (Ch2 l133, design l868).
- **Confirmed accurate against code:** 7 struggle signals + weights 0.10/0.10/0.20/0.10/0.38/0.05/0.07 (`config.py`, `struggle.py:327`); 5 difficulty signals + weights 0.28/0.12/0.20/0.20/0.20 (`difficulty.py:170`); EWMA λ=0.3 (`SMOOTHING_ALPHA`); shrinkage K=5 + formula (`struggle.py:337`); CF τ=0.8998≈0.90 seeded from `optimised_hyperparams_v2.json` via `runtime_config`, used in `cf.py`; **K-retention fix** `runtime_config.py:99` `.pop("shrinkage_k")` so the JSON's 0 is *not* applied; Optuna deltas (K Δρ≈+0.009 on +0.471→+0.481; τ Δρ≈+0.160 on +0.306→+0.466); BKT 4 params 0.3/0.1/0.2/0.1 with P(G)+P(S)<1 bounded ≤0.5; prewarm 7 stages + disk-persisted incorrectness cache; single FastAPI process + `/mobile`; filelock atomic state; SessionProgression 12 buckets / 4 bands / four per-bucket metrics / V2-only.

## Chapter-intro audit (keep / tweak / add) — supervisor pt 12
Check each chapter opener before adding — some already have one:
- **Ch1 Introduction** — opens straight into "Problem"; add a 2–3 sentence chapter framing, and fix the garbled first sentence (see [[01 Integrity & Consistency Fixes]] I10).
- **Ch2 Background** — has a top line but the four sub-sections jump straight into subsubsections; **add x.0 intros** to §2.2 Modelling Student Behaviour (struggle vs difficulty as complementary targets), §2.3 Data-Driven Personalisation (CF + text mining as complementary), §2.4 Retrieval-Augmented Feedback (RAG grounding to prevent hallucination), §2.5 Existing Systems (why survey them; course-level vs session-level gap).
- **Ch3 Design** — has an opener (l2); a new **§3.1 System Walkthrough** subsection (storyboard `fig:storyboard`) and the stakeholder context diagram (`fig:context-stakeholders`) were added at the top but sit nearly bare (one lead-in sentence each) — see *System Walkthrough + context-figure framing* below.
- **Ch4 Implementation** — has a strong Overview but the chapter-intro TODO at l3 is unresolved; **write the 2–3 sentence intro** (V1 Streamlit → V2 React/FastAPI framing).
- **Ch5 Evaluation** — opens well at section level, but **add x.0 intros** to §5.2 Functional Testing, §5.4 Results, §5.5 Survey, §5.6 Discussion (each currently jumps into its first subsubsection).
- **Ch6 Conclusion** — opens fine; no change.

## System Walkthrough + context-figure framing
The Walkthrough storyboard and the stakeholder context diagram open Ch3 and need surrounding prose so they read as argument, not decoration. **Decision: keep both; they are complementary, not redundant** — the storyboard is the *usage scenario*, the context diagram is the *component model* the chapter references (and the supervisor-requested context diagram).
- **§3.1 System Walkthrough** — now structured as **five per-step figures**, each under a run-in `\paragraph{}` heading: **Monitor** (`fig:storyboard`), **Detect** (`fig:sb-detect`), **Dispatch** (`fig:sb-dispatch`), **Cross the room** (`fig:sb-cross`), **Helped** (`fig:sb-helped`). Each step currently carries a **DRAFT scenario sentence** (tagged `% DRAFT` in the source) — refine or replace in your voice; keep them scenario-level (defer mechanism to later sections). **Flesh out each step:** under (or beside) each of the five walkthrough figures, write a short discussion — a couple of sentences on what that step shows and why it matters — so every figure is accompanied by real prose and the full-page figures don't sit half-empty; this expands the single placeholder sentence currently above each one. Optionally expand the lead-in into a fuller framing paragraph (why a concrete in-lab scenario opens the chapter; it motivates the monitor-and-dispatch contribution).
- **System Architecture — Figure 3.6** (context diagram `fig:context-stakeholders`): currently has only a one-line lead-in, so **write its accompanying discussion** (same treatment as the walkthrough figures). Add a sentence or two that *distinguishes* it from the storyboard — the storyboard shows how the system is used; the context diagram names the three system components (C1 quiz/AI platform, C2 instructor dashboard, C3 assistant view), their read-only data flow, and the human-in-the-loop dispatch + "helps in person" return path. State that C1–C3 are the reference labels used through the rest of the chapter (ties to the component cross-references, [[02 Proposed Report Edits — structural]] S3).
- **Bridge**: one sentence linking them — the storyboard motivates; the context diagram formalises the components the architecture and analytics sections then build on.

## Section/chapter closers — supervisor pt 11 / 14
- **Evaluation chapter** (`results-and-evaluation.tex`, after `fig:eval-incorrectness-distribution` l523) — chapter ends on a figure. **Add a 3–4 sentence closing synthesis**: headline ρ=+0.588 (struggle), the rater-fidelity ceiling, and the case for advisory (not autonomous) use.
- **Implementation chapter** (`implementation.tex`, end l1431) — ends on the problems table with only a TODO. **Add a 0.5–1 page chapter summary**: decisions carried V1→V2 (shared analytical core, filelock coordination), the major V2 gains (FastAPI scalability, React responsiveness, prewarm), and readiness for evaluation.
- **Design §3.5 Model Training Pipeline** (after `fig:v2-pipeline-design` l847) — ends on a figure. **Add 2–4 sentences**: how Phase 4 outputs (trained weights, calibrated thresholds) load at V2 runtime, then bridge into the RAG section.
- **Implementation §4.9 Instructor Views** (after `fig:ui-progression` l1286) — ends on a figure. **Add 2–3 sentences** on the session-progression view's role before the Lab Assistant section.
- **Design chapter end** (l1051) — ends after the visual-encoding tables. **Add 2–3 sentences** summarising the layered information architecture.

## Big-table summaries — supervisor pt 13
- **Problems table** (`implementation.tex` §4.11, `tab:problems` l1382–1423): expand the one-line intro (l1385) to say *why* these eight problems mattered, and **add a post-table summary** drawing out the lessons (concurrency, cold-start, graceful degradation as recurring themes).

## Finish abandoned sentences / mid-thought TODOs — supervisor pt 16
- `results-and-evaluation.tex` **l338**: "Results suggest that the bayesian shrinkage offers no real gain to the modelling % only part of conclusion add to it" → complete it (shrinkage gives no real gain; K could be dropped from future tuning) and delete the inline comment.
- `results-and-evaluation.tex` **l290**: threshold-bias sentence trails off without punctuation → finish it (why the cohort skew may generalise across modules — students only enter the log when they attempt a submission).
- `results-and-evaluation.tex` **after `tab:eval-hyperparams` l322**: add the Optuna summary paragraph (K negligible Δρ≈+0.009, hand-set near-optimal; τ substantial Δρ≈+0.160, 0.7 too permissive).
- `results-and-evaluation.tex` **l87–98**: after the prewarm timing list, add interpretation — ~650 s cold-start is once-per-deployment, steady-state 5 s polling meets NFR1 (sub-millisecond in-memory lookups thereafter).
- **Research Gaps §2.6** (`requirements-specification.tex` l288–307): resolve the four embedded TODOs, fix the trailing fragment, split into coherent paragraphs (AI/struggle/CF gaps; BKT instructor-facing + mistake clustering; smart-device assistant channel), and add an optional synthesis paragraph tying the gaps to the thesis motivation.

## Background composite-metric & glossary — supervisor pt 16 (RESOLVED 2026-05-31: both dropped, replaced by an l145 accuracy fix)
**Decision after review (author, 2026-05-31): both dropped.**
- The composite *concept* is already established and properly hedged in the lit review (l97, l136, l138: "combination of … signals rather than a single measure"). A new Background "weighted composite" paragraph would sit in the wrong register (it describes the Ch3 system, not prior work) and would misattribute the specific weighted/normalised formulation to `estey_2017_automatically` / `dannath_evaluating` / `piech_modeling`, who proposed a trajectory metric, a multi-indicator difficulty scheme, and a graphical solution-path model respectively. The formal composite definition stays in Ch3.
- The glossary line was also dropped; the symbols live in the front-matter Nomenclature page (Note 04).
- **Replaced by an accuracy fix → [[01 Integrity & Consistency Fixes]] I13 (gated before→after):** §2.2.4 l151 says Optuna's TPE is used "to … find optimal weights for our composite metrics", but the deployed pipeline learns the weights by OLS regression (`scripts/optimise_v2_weights.py`, `LinearRegression`) and uses Optuna only to tune the scalar hyperparameters K and τ (`scripts/optimise_hyperparams.py`, two TPE studies). Fix: "find optimal weights for our composite metrics" → "tune the scalar hyperparameters that govern these composite models".

## Impl → Design back-references — FC-02
- Where Ch4 describes each deployed view, add "as designed in §3.7, Figure [figma-N]" so the conceptual design and deployed implementation are traceable (currently zero such back-references).
