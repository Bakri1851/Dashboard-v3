# Ch5 – Results and Evaluation

<!-- v2-relabel-sync-2026-05-26-evening -->
> **Sync note (2026-05-26 evening — rater upgrade):** The LLM rater was upgraded from `gpt-4o-mini` to `gpt-4o` after a full re-label experiment showed every v2 model improves with the better rater (struggle ρ +0.573 → **+0.588**; difficulty ρ +0.287 → **+0.468** — biggest single gain; improved-struggle ρ +0.168 → **+0.201**, now matching the non-linear RandomForest ceiling). All ρ values below reflect the upgraded labels. Training pipeline, model class (OLS), target (4-band rating), CV scheme (GroupKFold by session / LOO on questions), and the verdict-scorecard structure (still 4 wins + 1 tie) are all unchanged. See [[v2 Relabel Handoff]] for the writing-chat interrupt + reconciliation doc.

<!-- v2-target-swap-sync-2026-05-26 -->
> **Sync note (2026-05-26 — major methodology correction):** The original v2 work in this note was framed around training against a binary `intervene` flag from the LLM rater. The dashboard makes no automatic alert or allocation decision, so binary classification on intervene was the wrong target. **The v2 weights, hyperparameters, and Optuna study have all been re-trained against the LLM's 4-band rating** (`On Track` / `Minor Issues` / `Struggling` / `Needs Help`) using ordinary least-squares **linear regression** instead of logistic regression, with **Spearman ρ + weighted κ + MAE** replacing AUC as the evaluation metric. Under the corrected target the verdict scorecard becomes **4 positive findings + 1 tie** (was "2 positive + 2 negative + 1 tie" — the previous negative findings for difficulty and improved-struggle were artefacts of the wrong target). Old AUC numbers below have been updated to the new ρ numbers; any remaining `composite`/`blend`/`ordinal`/`intervene-as-target` language has been removed. See `data/eval/results.md` for the authoritative current numbers.

Thesis chapter for evaluation design, testing, results, discussion. ToC restructured 2026-05-24 (Hybrid layout); §5.1 prose drafted; **§5.4 v2 empirical-refinement brief delivered 2026-05-25** with numbers + 7 essential figures (pruned from 11, then swapped the 4-panel Optuna figure for the two-figure joint-study pair on 2026-05-25 PM) + tables ready; **cross-chapter training-methodology drafting plan added 2026-05-25 covering Ch1/Ch2/Ch3/Ch4/Ch5**; survey collected at n=8 with 2 more pending.

Related: [[Thesis Overview]], [[Report Sync]], [[Evidence Bank]], [[Evaluation Plan]], [[Setup and Runbook]], [[Known Issues]], [[Ch2 – Background and Requirements]], [[Ch5 §5.1 Drafting Plan]], [[Ch5 §5.4 + cross-chapter training-methodology Drafting Plan]], [[Ch5 §5.4 v2 Empirical Refinement Brief]], [[Evaluation PoC Handoff]], [[v2 Methodology Journal]]

**Source file:** [`Report/main-sections/results-and-evaluation.tex`](../../../../Report/main-sections/results-and-evaluation.tex)
**Status:** ToC in place; §5.1 drafted (awaiting paste); §5.4 brief ready + numbers + 11 figures auto-generated; §5.2 / §5.3.2 / §5.3.3 / §5.5 / §5.6.2 / §5.6.3 writable now from data in hand; §5.3.1 still deferred for prewarm capture; §5.6.1 unblocked by §5.4 numbers.

> **Sync note (2026-05-24):** This note now reflects the restructured ToC and the eval-design handoff. The older "What could go in each section" sketch is superseded by [[Evaluation Plan]] (operational protocol) and [[Ch5 §5.1 Drafting Plan]] (drafted prose). The Dr-Batmaz attribution in the prior version has been removed in line with the supervisor-attribution convention for body chapters.

> **Sync note (2026-05-25):** §5.4 deferral lifted. The v2 evaluation pipeline (scripts/eval_*.py + scripts/optimise_*.py + notebooks/eval_main.ipynb) produced all the headline numbers needed for §5.4 — see [[Ch5 §5.4 v2 Empirical Refinement Brief]] for the writing-chat handoff and [[Evaluation PoC Handoff]] §13 for the verdict scorecard. The "PoC deliverables expected from parallel chat" block below is superseded; the actual deliverables are listed in §5.4 evidence section of this note.

> **Sync note (2026-05-25 PM):** Cross-chapter training-methodology coverage expanded. Coverage audit found that the v2 training process was thinly covered (one sentence in §5.4.3 prose). Four additional insertions added on top of the brief's three: Ch1 Objective 5 extension, Ch2 §2.2.4 "Empirical Refinement of Composite Models", Ch4 §4.7.5 "V2 Empirical Refinement Pipeline", Ch5 §5.1.5 "V2 Training Methodology". See [[Ch5 §5.4 + cross-chapter training-methodology Drafting Plan]] for all seven paste-ready prose blocks, the §5.4 ToC restructure instructions (rename 5.4.2 + 5.4.3, add 5.4.9 + 5.4.10 + 5.1.5 with labels), and the 6-figure pruned inventory. Three already-made `% TODO` stub edits in Report/ files (Ch1/Ch2/Ch4) are flagged at the top of that note for revert vs keep decision.

## §5.4 evidence (delivered 2026-05-25)

Numbers, figures, and tables for the new v2 empirical-refinement narrative are all on disk:

- **Brief**: [[Ch5 §5.4 v2 Empirical Refinement Brief]] — original three-insertion brief from the eval chat
- **Drafting plan**: [[Ch5 §5.4 + cross-chapter training-methodology Drafting Plan]] — paste-ready prose for all seven insertions + figure inventory + ToC restructure instructions
- **Numbers**: `data/eval/results.md` (87 lines, 7 tables, auto-generated by the notebook)
- **Figures**: 7 PNGs in [`Report/figures/evaluation/`](../../../../Report/figures/evaluation/) — pruned from 11 candidates to 6 essentials on 2026-05-25 morning, then swapped the 4-panel `hyperparams_optuna.png` for the two-figure joint-study pair (`optuna_joint_contour.png`, `optuna_joint_importances.png`) on 2026-05-25 PM after the user generated additional Optuna plots in the notebook. Inventory in the drafting plan.
- **Verdict scorecard** (lifted from [[Evaluation PoC Handoff]] §13):

| Component | Winner | Numbers | Phase |
|---|---|---|---|
| Struggle model (7 OLS weights) | **v2** | ρ +0.588 [+0.490, +0.686] (v1 ρ +0.471) | 4a |
| Difficulty model (5 OLS weights) | **v2** | ρ +0.468 (v1 baseline near-flat) — weak but positive | 4b |
| Improved-struggle model (3 OLS weights) | **v2** | ρ +0.201 (v1 baseline near-flat); still weaker than struggle alone | 4c |
| Shrinkage K (scalar) | **tied** | Δ +0.009 within noise (K=0 best) | 4d |
| CF threshold τ (scalar) | **v2** | Δ +0.160 (ρ +0.306 → +0.466, τ=0.900 best) | 4d |

Four positive findings + one tie. The v2 weights and the τ tuning each measurably improve rank quality against the LLM 4-band rating; only the shrinkage K is within noise. (The previous "two negative findings" framing was an artefact of training against a 4-band rating the dashboard never actually uses.)

**Ch5 ToC restructure — APPLIED 2026-05-25 (user's variant):**

- §5.1.3 gained `\label{sec:eval-retro}` ✓
- §5.1.5 NEW — "V2 Training Methodology" with `\label{sec:eval-v2-methodology}` ✓
- §5.4.2 renamed from "Model Comparison - Struggle" → "Inter-rater Agreement (Cohen's $\kappa$)" (label `sec:eval-compare-struggle` preserved) ✓
- §5.4.3 renamed from "Model Comparison - Difficulty" → "Model Comparison" (label `sec:eval-compare-difficulty` preserved); **scope merged** to cover both struggle and difficulty baseline-vs-improved/IRT comparisons
- §5.4.9 NEW — "Hyperparameter optimisation" with `\label{sec:eval-hyperopt}` (user's swap: optimisation BEFORE findings)
- §5.4.10 NEW — "Findings" with `\label{sec:eval-findings}`; **scope consolidated** to hold all three v2 weight-refit findings (positive struggle + 2 negatives) + verdict scorecard

The other existing §5.4 subsubsections (5.4.1, 5.4.4–5.4.8) keep their titles and labels.

**Cross-chapter training-methodology insertions (added 2026-05-25 PM; expanded to 8 insertions):**

- **Ch1 Objective 5** — extend with empirical-refinement clause
- **Ch2 §2.2.4** NEW — "Empirical Refinement of Composite Models" (supervised weight optimisation + LLM-as-rater literature)
- **Ch3 amendment** near line 263 — frame v1 as deployed baseline, v2 as iterative refinement (trimmed to forward-ref §3.5 + §5.4 only; mechanics moved to §3.5)
- **Ch3 §3.5** NEW — "Empirical Refinement Pipeline Design" (~290 words + TikZ data-flow figure `fig:v2-pipeline-design`). Existing RAG and Interaction/UI subsections renumber to §3.6 / §3.7. Carries the **pipeline design** as a design artefact.
- **Ch4 §4.7.4 +after-line-952** — toggle wiring (five `RuntimeConfig` fields: four `*_version` flags + one `shrinkage_k` direct override)
- **Ch4 §4.9.6** — Settings UI selectors
- **Ch4 §4.7.5** NEW — "V2 Empirical Refinement Pipeline" (operational implementation; five phases under scripts/ + notebooks/eval_main.ipynb; opens with back-refs to Ch3 §3.5 for design and Ch5 §5.1.5 for evaluation methodology)
- **Ch5 §5.1.5** NEW — "V2 Training Methodology" (~210 words; evaluation-side framing only; what was trained vs not + label source + forward refs to §3.5 and §4.7.5)
- **Ch5 §5.4 + §5.6.1** — all the numbers per the original brief

**Three-layer scope split** (clean separation, minimal duplication):

| Layer | Where | Carries |
|---|---|---|
| Pipeline design + data flow figure | Ch3 §3.5 `sec:v2-pipeline-design` | Why five phases; why frozen on-disk artefacts; why deployment-ready JSON; data-flow figure |
| Operational implementation | Ch4 §4.7.5 `sec:v2-training` | Scripts, code, scikit-learn calls, file paths, reproducibility |
| Evaluation-side methodology framing | Ch5 §5.1.5 `sec:eval-v2-methodology` | What was trained vs not; label source; forward refs to §3.5 + §4.7.5 |

---

## Current ToC (post-restructure 2026-05-24)

```latex
5.0 Chapter preamble            [bare prose between \section and \subsection]  — DRAFTED
    (two-dimensions framing; cohort; three converging strands;
     section-by-section chapter roadmap)
    [matches Ch4's line-3 % TODO pattern in implementation.tex]

5.1 Evaluation Design           [5 subsubs] — 4 DRAFTED + 1 PASTED (user-rewritten)
    5.1.1 Scope of Evaluation
    5.1.2 Evidence Sources
    5.1.3 Retrospective Evaluation Protocol  [\label{sec:eval-retro} ✓ applied]
    5.1.4 V2 Training Methodology            [NEW — user-swapped 2026-05-25 from §5.1.5 to land BEFORE Limitations; \label{sec:eval-v2-methodology} ✓]
    5.1.5 Limitations of Evaluation          [moved from §5.1.4 in the user's swap]

5.2 Functional Testing          [4 subsubs] — WRITABLE NOW
    5.2.1 Data Ingestion and Session Handling
    5.2.2 Analytics and Model Behaviour
    5.2.3 Instructor Dashboard Features
    5.2.4 Lab Assistant Workflow

5.3 Non-Functional Testing      [3 subsubs] — MIXED
    5.3.1 Performance and Refresh Behaviour          — DEFERRED (needs prewarm capture)
    5.3.2 Usability and Interpretability             — WRITABLE NOW (survey-driven)
    5.3.3 Robustness and Failure Handling            — WRITABLE NOW (qualitative)

5.4 Results                     [10 subsubs after restructure applied 2026-05-25] — v2 BLOCKS DRAFTING-PLAN READY
    5.4.1 Baseline System Outputs              [drafting plan: cohort + 54%-Needs-Help finding]
    5.4.2 Inter-rater Agreement (Cohen's κ)    [RENAMED from "Model Comparison - Struggle"; label sec:eval-compare-struggle kept]
    5.4.3 Model Comparison                     [RENAMED from "Model Comparison - Difficulty"; MERGED scope: baseline vs improved struggle AND baseline vs IRT difficulty; label sec:eval-compare-difficulty kept; \todo{} markers for /api/models/compare numbers]
    5.4.4 BKT Predictive AUC per Skill         [unchanged; still needs prewarm AUC capture]
    5.4.5 Per-Module Normalisation Effect      [unchanged]
    5.4.6 Latency and Prewarm Evidence         [unchanged]
    5.4.7 Graceful-Degradation Evidence        [unchanged]
    5.4.8 Observed Strengths and Weaknesses    [unchanged]
    5.4.9 Hyperparameter optimisation          [NEW; \label{sec:eval-hyperopt}; user-chosen swap places optimisation BEFORE findings]
    5.4.10 Findings                            [NEW; \label{sec:eval-findings}; CONSOLIDATED: positive struggle v1↔v2 + negative difficulty + negative improved model + verdict scorecard + two-regime recommendation]

5.5 Survey                      [5 subsubs] — WRITABLE NOW (n=8 collected)
    5.5.1 Instrument, Audience, Ethical Approval
    5.5.2 Baseline Perception of Lab Support
    5.5.3 Dashboard Interpretability and Trust
    5.5.4 Student Comfort and Ethical Concerns
    5.5.5 Change Requests and Triangulation with Quantitative Results

5.6 Discussion                  [3 subsubs] — MIXED
    5.6.1 Model Disagreement                          — DEFERRED (needs deltas)
    5.6.2 Tradeoffs and Threats to Validity          — WRITABLE NOW
    5.6.3 Limitations                                 — WRITABLE NOW
```

---

## Evaluation methodology (eval-design handoff 2026-05-24)

Latent struggle is unobservable; operationalise as future observable behaviour over horizon \(\Delta\). At time \(t\) the dashboard outputs \(S_t(s)\), \(D_t(q)\) from data in \([0, t]\); validated against outcomes in \([t, t+\Delta]\). Default \(\Delta = 15\) min.

**Three converging strands:**

1. **Direct predictive** — IRT and BKT against held-out next-attempt correctness. Metrics: AUC, log-loss, Brier. Baselines: majority-class, per-question mean, per-student mean.
2. **Horizon-shifted** — composite \(S_t(s)\) and \(D_t(q)\) against the three labels below. Metrics: Spearman \(\rho\), top-\(k\) P/R, NDCG@\(k\), AUC. Cutoff schedule \(T\) spanning the session.
3. **Structural** — drop-one ablation on the 7 struggle signals; \(\pm 20\%\) weight perturbation (Spearman rank stability vs nominal); V1/V2 Spearman convergence on replayed sessions.

**Three labels (self-derived from submission data, no external annotation):**

- \(L_{\text{top20}}(s, t, \Delta) = 1\) iff \(s\) is in the top-20 by mean incorrectness in \([t, t+\Delta]\).
- \(L_{\text{needs\_help}}(s, t, \Delta) = 1\) iff \(s\) exhibits a retry spiral (\(\geq 3\) near-duplicate wrong submissions) OR abandonment (inter-submission gap \(> 3\times\) personal baseline) in \([t, t+\Delta]\).
- \(L_{\text{struggling\_plus}} = L_{\text{top20}} \vee L_{\text{needs\_help}}\).

**Self-derived label justification:** anonymised IDs ruled out grade linkage; deployment scope ruled out instructor flagging and expert annotation; framed as deliberate methodological choice, not missing dataset.

These supersede the older `score >= 0.50` / `score >= 0.35` thresholds in [[Evaluation Plan]] — see the audit table in [[Ch5 §5.1 Drafting Plan]].

---

## PoC deliverables expected from parallel chat

The §5.4 subsections unblock when the PoC produces:

- IRT and BKT held-out AUC (direct predictive strand)
- Horizon-shifted AUC for \(S_t(s)\) against the three labels above
- V1 vs V2 Spearman convergence on replayed sessions
- Drop-one ablation results on the 7 struggle signals
- Coarse sweep of CF \(\tau \in \{0.5, 0.6, 0.7, 0.8\}\)

Plus the local instrumentation (already scoped):

- BKT predictive AUC per skill persisted to `data/bkt_fit_metrics.json` (logged at [`bkt.py:247`](../../../../code2/backend/models/bkt.py#L247) but not currently written; add a one-line summary write at [`main.py:144`](../../../../code2/backend/main.py#L144))
- Prewarm latency breakdown persisted to `data/prewarm_summary.json` ([`main.py:177`](../../../../code2/backend/main.py#L177))

---

## Drafting status

| Section | State | Source / next step |
|---|---|---|
| 5.1.1 Scope | Drafted | [[Ch5 §5.1 Drafting Plan]] — paste-ready |
| 5.1.2 Evidence Sources | Drafted | same |
| 5.1.3 Retrospective Protocol | Drafted | same |
| 5.1.4 Limitations of Evaluation | Drafted | same |
| 5.2.1 Data Ingestion | Pending | qualitative smoke-test summary; body keeps headline only, full FR1–FR7 in Appendix C |
| 5.2.2 Analytics & Model Behaviour | Pending | same pattern |
| 5.2.3 Instructor Features | Pending | same |
| 5.2.4 Lab Assistant Workflow | Pending | same |
| 5.3.1 Performance & Refresh | Deferred | needs prewarm capture (see PoC deliverables) |
| 5.3.2 Usability & Interpretability | Pending | survey-driven (Q5 / Q6 / Q7 from n=8) |
| 5.3.3 Robustness & Failure | Pending | qualitative; NFR1–NFR6 detail to Appendix C |
| 5.4.1 Baseline System Outputs | Deferred | placeholder paragraph describing planned figures |
| 5.4.2 Model Comparison – Struggle | Deferred | placeholder; figures `fig:eval-baseline-vs-improved`, `fig:eval-disagreement-heatmap`, `fig:eval-cf-vs-parametric`, `tab:eval-largest-mover` |
| 5.4.3 Model Comparison – Difficulty | Deferred | placeholder; `fig:eval-irt-discrimination`, `tab:eval-largest-mover` |
| 5.4.4 BKT Predictive AUC per Skill | Deferred | placeholder; `fig:eval-roc-bkt` |
| 5.4.5 Per-Module Normalisation Effect | Deferred | placeholder; `fig:eval-permodule-normalisation`, `fig:eval-violin-permodule-difficulty` |
| 5.4.6 Latency & Prewarm Evidence | Deferred | placeholder; `fig:eval-latency-prewarm` |
| 5.4.7 Graceful-Degradation Evidence | Deferred | placeholder; references `tab:problems` rows 5 and 7 |
| 5.4.8 Strengths & Weaknesses | Deferred | placeholder |
| 5.5.1 Instrument, Audience, Ethics | Pending | 11 questions, Microsoft Forms, n=8 of ~10; `tab:eval-survey-summary` |
| 5.5.2 Baseline Perception | Pending | Q2 + Q3 + Q4; `fig:eval-survey-baseline` |
| 5.5.3 Interpretability & Trust | Pending | Q5 + Q6 + Q7; `fig:eval-survey-clarity`, `fig:eval-survey-trust`; needs raw export for Q5/Q6 per-band counts |
| 5.5.4 Comfort & Ethical Concerns | Pending | Q8 + Q9 + Q10; `fig:eval-survey-comfort`, `fig:eval-survey-themes` |
| 5.5.5 Change Requests & Triangulation | Pending | Q11; triangulation with §5.4 findings (once available) |
| 5.6.1 Model Disagreement | Deferred | placeholder; needs §5.4 numbers |
| 5.6.2 Tradeoffs & Threats to Validity | Pending | methodological |
| 5.6.3 Limitations | Pending | system limitations (distinct from 5.1.4 protocol limitations) |

---

## Section briefs

### 5.1 Evaluation Design

Drafted. See [[Ch5 §5.1 Drafting Plan]] for the four prose blocks and audit notes against [[Evaluation Plan]].

### 5.2 Functional Testing

Qualitative smoke-test summary in the body; full FR1–FR7 row-by-row checklist (steps, expected, actual, evidence pointer) lives in **Appendix C**. Each body subsubsection (5.2.1–5.2.4) covers one functional area, summarises the outcome, names the appendix table, and points to the relevant screenshot in **Appendix B**.

Per-subsubsection coverage:

- **5.2.1 Data Ingestion and Session Handling** — submission API fetch, JSON+XML normalisation, session start/end, lab-state file-lock behaviour.
- **5.2.2 Analytics and Model Behaviour** — struggle / difficulty / CF / mistake clustering / BKT / IRT / improved struggle / measurement confidence pipelines run end-to-end on a replayed session without error.
- **5.2.3 Instructor Dashboard Features** — all eight instructor views render with the correct data; cross-view navigation works; filter persistence works.
- **5.2.4 Lab Assistant Workflow** — assistant joins via code, identity persists in URL, mark-helped round-trips through `lab_session.json`, instructor sidebar shows joined assistants and assignments.

### 5.3 Non-Functional Testing

- **5.3.1 Performance and Refresh Behaviour** — DEFERRED; underpinned by `data/prewarm_summary.json` once instrumented and by the V2 lifespan latency capture. The body subsubsection will state the headline first-request latency and refresh cadence; the per-phase breakdown lives in §5.4.6.
- **5.3.2 Usability and Interpretability** — WRITABLE; draws on survey Q5 (clarity of struggle / difficulty scores), Q6 (band intuitiveness), Q7 (trust). The body subsubsection summarises the Likert distributions; the underlying stacked bars are figures in §5.5.3 (not duplicated here).
- **5.3.3 Robustness and Failure Handling** — WRITABLE qualitative; covers BKT degeneracy fallback ([`bkt.py`](../../../../code2/backend/models/bkt.py)), IRT minimum-attempt filter ([`models/irt.py`](../../../../code2/backend/models/irt.py)), CF k-NN cold-start, lab-state file-lock under three-process contention, RAG `asyncio.to_thread` offload, prewarm cache short-circuit. NFR1–NFR6 detail lives in Appendix C.

### 5.4 Results — ALL DEFERRED

Placeholder paragraphs describe what each subsubsection will report:

- **5.4.1 Baseline System Outputs** — distributions of \(S(s)\), \(D(q)\), incorrectness from a representative replayed session. Headline numbers from `data/incorrectness_cache.json` (3,935 cached scores).
- **5.4.2 Model Comparison – Struggle** — `/api/models/compare` headline metrics (Spearman \(\rho\), top-10 overlap, level-agreement breakdown, largest-mover table) plus the baseline-vs-improved scatter and the disagreement heatmap.
- **5.4.3 Model Comparison – Difficulty** — same four metrics for baseline vs IRT; 2PL discrimination scatter (β_q vs α_q) to flag low-discrimination items.
- **5.4.4 BKT Predictive AUC per Skill** — per-skill AUC bar / ROC curves from `data/bkt_fit_metrics.json` once written.
- **5.4.5 Per-Module Normalisation Effect** — distribution histograms (or violins) comparing per-module vs global normalisation on the same raw difficulty signals; demonstrates that per-module restored within-module sensitivity.
- **5.4.6 Latency and Prewarm Evidence** — V2 prewarm phase-by-phase bar; first-request P50/P95; comparison against V1 lazy-fit baseline if captured.
- **5.4.7 Graceful-Degradation Evidence** — BKT fallback (Problem 5 from `tab:problems`); improved-struggle weight redistribution under partial signals (Problem 7).
- **5.4.8 Observed Strengths and Weaknesses** — qualitative synthesis across the preceding subsubsections; optional per-student case studies (3 students: clear struggler, borderline, clear non-struggler).

### 5.5 Survey

n=8 of ~10 expected as of 2026-05-24. Microsoft Forms, Active, 30-day window, average completion 6:15.

- **5.5.1 Instrument, Audience, Ethical Approval** — 11 questions (4 free-text, 5 Likert, 2 categorical); UG 5 / PGR 2 / Staff 1. Ethical approval status to be confirmed.
- **5.5.2 Baseline Perception of Lab Support** — Q2 (51% Sometimes-or-Rarely receive timely help), Q3 (63% find struggler identification hard), Q4 free-text themes (staff shortage, quiet students, help-seeking reluctance).
- **5.5.3 Dashboard Interpretability and Trust** — Q5 / Q6 Likert (per-band counts pending raw export), Q7 trust (75% net-positive, 25% sceptical).
- **5.5.4 Student Comfort and Ethical Concerns** — Q8 concerns free-text (4 of 8), Q9 comfort-as-scored (63% comfortable, 25% uncomfortable), Q10 ethics free-text (5 of 8).
- **5.5.5 Change Requests and Triangulation** — Q11 (2 of 8); triangulates survey perception with §5.4 quantitative findings once available.

Raw export from Microsoft Forms still needed for Q5/Q6 per-band counts and full Q4/Q8/Q10/Q11 free-text.

### 5.6 Discussion

- **5.6.1 Model Disagreement** — DEFERRED; needs §5.4.2 / §5.4.3 deltas.
- **5.6.2 Tradeoffs and Threats to Validity** — WRITABLE; methodological tradeoffs (parametric simplicity vs probabilistic richness, hand-tuned vs learned weights, per-module vs global normalisation, real-time vs deeper-fit accuracy).
- **5.6.3 Limitations** — WRITABLE; system-level limitations distinct from §5.1.4 protocol limitations (BKT degeneracy windows, IRT 2-attempt minimum, mistake-clustering n-min threshold, CF k+1 cold start, privacy / comfort tradeoff per survey Q8 / Q9 / Q10).

---

## Body-vs-appendix split convention

Adopted 2026-05-24. Body subsubsection presents the **headline number + one diagnostic figure**; appendix carries the **full underlying table**. Example: §5.4.4 says "BKT AUC ranged from 0.XX to 0.YY across N skills (Appendix C, Table C.x); the ROC curve is shown in Figure 5.x"; appendix carries the per-skill row table.

Logic: a thesis evaluation chapter is judged on insight density, not row count. Moving FR / NFR detail to an appendix is conventional in software-engineering MSc work and reduces body length without dropping evidence.

---

## Appendix candidates (Ch5 overflow)

| Appendix | File | Ch5 overflow it absorbs |
|---|---|---|
| **A — Code Snippets** | [`code-snippets.tex`](../../../../Report/appendix-sections/code-snippets.tex) | Instrumentation diff for `main.py` (BKT AUC + prewarm latency capture); ablation runner; calibration generator; bootstrap CI runner |
| **B — UI Screenshots** | [`ui-screenshots.tex`](../../../../Report/appendix-sections/ui-screenshots.tex) | FR-evidence screenshots; theme gallery; lab-assistant screens; CF diagnostic panel |
| **C — Detailed Test Results** | [`detailed-test-results.tex`](../../../../Report/appendix-sections/detailed-test-results.tex) | Full FR1–FR7 + NFR1–NFR6 tables; ablation matrix; per-skill BKT detail; per-question IRT detail; confusion matrices; bootstrap CI tables; calibration-bin tables; full survey instrument + free-text quotes |
| **E — Formulae** | [`formulae.tex`](../../../../Report/appendix-sections/formulae.tex) | Spearman \(\rho\) formula; weighted-kappa formula; NDCG@\(k\) formula; bootstrap CI procedure; calibration-bin definition; lift / cumulative-gain definition |
| **F — Formulae Derivation** | [`formulae-derivation.tex`](../../../../Report/appendix-sections/formulae-derivation.tex) | Min-max normalisation zero-on-degenerate derivation; BKT 0.95 mastery-threshold implication |

`\label{app:detailed-test-results}` needs adding to the top of the empty `detailed-test-results.tex` so §5.1.2 references resolve in the build.

---

## Plot inventory

| Label | Subsection | Status | Source |
|---|---|---|---|
| `fig:eval-baseline-vs-improved` | 5.4.2 | DATA EXISTS | `/api/models/compare` |
| `fig:eval-disagreement-heatmap` | 5.4.2 | DATA EXISTS | same endpoint |
| `fig:eval-cf-vs-parametric` | 5.4.2 | DATA EXISTS | CF diagnostics dict |
| `fig:eval-irt-discrimination` | 5.4.3 | DATA EXISTS | IRT model dict (β_q vs α_q) |
| `fig:eval-roc-bkt` | 5.4.4 | NEEDS LOG CAPTURE | AUC logged but not persisted |
| `fig:eval-permodule-normalisation` | 5.4.5 | DATA EXISTS | difficulty.py raw + normalised columns |
| `fig:eval-violin-permodule-difficulty` | 5.4.5 | DATA EXISTS | same; violin earns its place here |
| `fig:eval-violin-perweek-struggle` | 5.4.1 | DATA EXISTS | per-week struggle replay |
| `fig:eval-violin-perskill-mastery` | 5.4.4 | NEEDS REFACTOR | BKT emits final state only |
| `fig:eval-latency-prewarm` | 5.4.6 | NEEDS INSTRUMENTATION | stderr-only today |
| `fig:eval-latency-v1-vs-v2` | 5.4.6 | NEEDS INSTRUMENTATION | not captured |
| `tab:eval-largest-mover` | 5.4.2 / 5.4.3 | DATA EXISTS | `/api/models/compare` |
| `fig:eval-survey-baseline` | 5.5.2 | DATA EXISTS (n=8) | Q2 + Q3 |
| `fig:eval-survey-clarity` | 5.5.3 | NEEDS RAW EXPORT | Q5 + Q6 per-band counts |
| `fig:eval-survey-trust` | 5.5.3 | DATA EXISTS (n=8) | Q7 |
| `fig:eval-survey-comfort` | 5.5.4 | DATA EXISTS (n=8) | Q9 |
| `fig:eval-survey-themes` | 5.5.2 / 5.5.4 / 5.5.5 | NEEDS RAW EXPORT | Q4 / Q8 / Q10 / Q11 free-text |
| `tab:eval-survey-summary` | 5.5.1 | DATA EXISTS (n=8) | instrument + response counts |

Violin verdict (full table in [[Ch5 §5.1 Drafting Plan]] and the working plan): violins for per-module / per-week / per-skill distributions only; NOT for Likert (n=8 discrete), NOT for baseline-vs-improved scatter (per-student identity matters), NOT for single-number metrics.

---

## Evidence status (updated 2026-05-24)

- **Screenshots:** None captured. Evidence Bank tracks 11 needed (instructor views + lab-assistant flows + theme gallery).
- **Functional / non-functional test logs:** Manual smoke-testing plan in [[Setup and Runbook]]; FR1–FR7 + NFR1–NFR6 row-by-row results to live in Appendix C; body keeps qualitative summary only.
- **Model-comparison data:** `/api/models/compare` endpoint live (Spearman \(\rho\), top-10 overlap, level agreement, largest mover for both struggle and difficulty); per-session JSON capture pending PoC.
- **Performance metrics:** Prewarm logs to stderr today ([`main.py:79`](../../../../code2/backend/main.py#L79), [`:115`](../../../../code2/backend/main.py#L115), [`:156`](../../../../code2/backend/main.py#L156), [`:162`](../../../../code2/backend/main.py#L162), [`:165`](../../../../code2/backend/main.py#L165), [`:177`](../../../../code2/backend/main.py#L177)); summary JSON write needed for §5.4.6.
- **BKT per-skill AUC:** Logged at [`bkt.py:247`](../../../../code2/backend/models/bkt.py#L247); summary JSON write needed for §5.4.4.
- **User feedback:** Survey n=8 of ~10 (Microsoft Forms, Active); raw Excel export still needed for full free-text and Q5/Q6 per-band counts.
- **Incorrectness cache:** `data/incorrectness_cache.json` has 3,935 cached scores supporting §5.4.1 incorrectness distribution.

See [[Evidence Bank]] for the full per-artefact tracker.

---

## Rewrite items

- [x] Restructure ToC (Hybrid layout, 2026-05-24)
- [x] Lock evaluation methodology (three strands, three labels, \(\Delta = 15\) min)
- [x] Draft §5.1.1 – §5.1.4 ([[Ch5 §5.1 Drafting Plan]])
- [ ] Draft §5.2.1 – §5.2.4 (qualitative smoke-test summary)
- [ ] Draft §5.3.2 (survey-driven usability)
- [ ] Draft §5.3.3 (qualitative robustness)
- [ ] Draft §5.5.1 – §5.5.5 (survey n=8; refresh once raw export in)
- [ ] Draft §5.6.2 (methodological tradeoffs)
- [ ] Draft §5.6.3 (system limitations)
- [ ] Write placeholder paragraphs for §5.3.1, §5.4.1 – §5.4.8, §5.6.1 (with `\todo{}` for numbers)
- [ ] Instrument [`main.py:144`](../../../../code2/backend/main.py#L144) and [`:177`](../../../../code2/backend/main.py#L177) to persist `data/bkt_fit_metrics.json` and `data/prewarm_summary.json`
- [ ] Receive PoC numbers: IRT/BKT held-out AUC; horizon-shifted AUC for \(S\) against the three labels; V1/V2 Spearman; ablation on 7 struggle signals; CF \(\tau\) sweep
- [ ] Capture screenshots for Appendix B (11 listed in [[Evidence Bank]])
- [ ] Stub Appendix C with FR1–FR7 + NFR1–NFR6 tables + survey instrument + free-text
- [ ] Add `\label{app:detailed-test-results}` to `detailed-test-results.tex` so §5.1.2 references resolve
- [ ] Audit pass after each section pasted (hallucination check against live source)

---

## Open questions (updated)

- **User study?** Yes — survey at n=8 of ~10 expected (ethically approved status to be confirmed). Question is whether n=10 is enough or whether to extend the response window.
- **V1 vs V2 comparison?** Yes — structural strand includes V1/V2 Spearman convergence on replayed sessions.
- **"Enough" evidence for a master's?** Three converging strands (direct predictive + horizon-shifted + structural) plus a survey constitute the required breadth; per-strand depth is bounded by PoC numbers.
- **Δ choice rationale beyond 15 min?** Need to confirm whether to run sensitivity at \(\Delta \in \{5, 10, 15, 30\}\) min as a robustness check in §5.4 or §5.1.4.
- **Ethics approval route?** §5.5.1 needs to state whether the survey is via Loughborough ethics committee, exempt, opt-in consent on the Form, etc. Vault doesn't currently say.
- **Hypothesis-based ranking model?** Designed in [[Evaluation Plan]] but not built; carry as future work in §5.6.2 or §5.6.3 unless reinstated.
