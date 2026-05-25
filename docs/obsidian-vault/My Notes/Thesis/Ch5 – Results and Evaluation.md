# Ch5 – Results and Evaluation

Thesis chapter for evaluation design, testing, results, discussion. ToC restructured 2026-05-24 (Hybrid layout); §5.1 prose drafted; survey collected at n=8 with 2 more pending; remaining writable batch in progress.

Related: [[Thesis Overview]], [[Report Sync]], [[Evidence Bank]], [[Evaluation Plan]], [[Setup and Runbook]], [[Known Issues]], [[Ch2 – Background and Requirements]], [[Ch5 §5.1 Drafting Plan]]

**Source file:** [`Report/main-sections/results-and-evaluation.tex`](../../../../Report/main-sections/results-and-evaluation.tex)
**Status:** ToC in place; §5.1 drafted (awaiting paste); §5.2 / §5.3.2 / §5.3.3 / §5.5 / §5.6.2 / §5.6.3 writable now from data in hand; §5.3.1 / §5.4.* / §5.6.1 deferred for PoC numbers from parallel chat.

> **Sync note (2026-05-24):** This note now reflects the restructured ToC and the eval-design handoff. The older "What could go in each section" sketch is superseded by [[Evaluation Plan]] (operational protocol) and [[Ch5 §5.1 Drafting Plan]] (drafted prose). The Dr-Batmaz attribution in the prior version has been removed in line with the supervisor-attribution convention for body chapters.

---

## Current ToC (post-restructure 2026-05-24)

```latex
5.0 Chapter preamble            [bare prose between \section and \subsection]  — DRAFTED
    (two-dimensions framing; cohort; three converging strands;
     section-by-section chapter roadmap)
    [matches Ch4's line-3 % TODO pattern in implementation.tex]

5.1 Evaluation Design           [4 subsubs] — DRAFTED
    5.1.1 Scope of Evaluation
    5.1.2 Evidence Sources
    5.1.3 Retrospective Evaluation Protocol
    5.1.4 Limitations of Evaluation

5.2 Functional Testing          [4 subsubs] — WRITABLE NOW
    5.2.1 Data Ingestion and Session Handling
    5.2.2 Analytics and Model Behaviour
    5.2.3 Instructor Dashboard Features
    5.2.4 Lab Assistant Workflow

5.3 Non-Functional Testing      [3 subsubs] — MIXED
    5.3.1 Performance and Refresh Behaviour          — DEFERRED (needs prewarm capture)
    5.3.2 Usability and Interpretability             — WRITABLE NOW (survey-driven)
    5.3.3 Robustness and Failure Handling            — WRITABLE NOW (qualitative)

5.4 Results                     [8 subsubs] — ALL DEFERRED (PoC numbers needed)
    5.4.1 Baseline System Outputs
    5.4.2 Model Comparison - Struggle
    5.4.3 Model Comparison - Difficulty
    5.4.4 BKT Predictive AUC per Skill
    5.4.5 Per-Module Normalisation Effect
    5.4.6 Latency and Prewarm Evidence
    5.4.7 Graceful-Degradation Evidence
    5.4.8 Observed Strengths and Weaknesses

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
