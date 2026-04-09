# Weekly Plan

## Honest assessment

The schedule is achievable but carries real risk and leaves no slack. Total estimated work across 12 steps is approximately 98–110 hours over 41 days — roughly 17 hours per week, or 2.5 hours of focused work every single day with no rest days. The critical path runs through Phase 5 (Comparison UI, the largest single task) → Appendix B screenshots → Ch4 rewrite → Ch5, in that order; any slip in Phase 5 compresses every downstream step. Phase 5 is classified Large (≈16hrs) but is a full new UI view with four components, routing changes, and a settings sub-panel — real-world time including debugging and verification is likely 20–25hrs. Week 2 is intentionally lighter (~16hrs) to absorb Phase 5 overflow; if Phase 5 finishes on time, Week 2 becomes a comfortable catch-up week. Weeks 3–4 carry the heaviest writing load (Ch4 + Ch5, both Large, both starting from scratch or near-scratch), and both depend entirely on evidence produced in Week 2. The schedule survives a two- or three-day slip on any single step, but not a full-week slip on Phase 5 or Ch4. Phase 6 (mobile app refinement) and FR13/FR6 (smart devices) are listed in Week 6 as stretch items only — do not start either unless steps 1–12 are complete by 17 May.

---

## Schedule at a glance

| Week | Dates | Steps targeted | Cumulative effort |
| --- | --- | --- | --- |
| 1 | Apr 9–15 | 1 (Phase 7), 2 (Phase 5) | ~20hrs |
| 2 | Apr 16–22 | 3 (App B), 4 (App C), begin 5 (Ch4) | ~16hrs |
| 3 | Apr 23–29 | Complete 5 (Ch4), 6 (App E&F), begin 7 (Ch5) | ~22hrs |
| 4 | Apr 30–May 6 | Complete 7 (Ch5) | ~20hrs |
| 5 | May 7–13 | 8 (Ch6), 9 (Ch3), 10 (Ch1&2), begin 11 (App A) | ~24hrs |
| 6 | May 14–20 | 11 (App A), 12 (Polish), buffer, stretch | ~12hrs |

**Critical dependencies:**
- Steps 1 + 2 must be done before Step 3 (screenshots need the comparison UI to exist)
- Step 3 must be done before Step 5 (Ch4 needs screenshots as figures)
- Step 4 must be done before Step 7 (Ch5 §5.2 Functional Testing needs Appendix C evidence)
- Step 5 must be done before Step 7 (Ch5 framing follows Ch4 narrative)
- Step 7 must be done before Step 8 (Ch6 follows from Ch5 conclusions)

---

## Week 1: Apr 9–15 (~20hrs)

**Target:** Complete both coding steps. All implementation work done by end of week.

> **Supervisor checkpoint — Wed 9 Apr, 1pm (kickoff)**
> Show: Updated Full Roadmap with scope decisions (Phase 6 stretch, Phases 9/10/11 explicitly out of scope, Phases 9/10/11 documented as future work). Present the plan for Phase 5 implementation — confirm Dr. Batmaz is satisfied with the scoping before any code is written.
> Agenda: Roadmap walk-through; Phase 5 design sanity check; confirm RAG goes into Ch6 §6.3 as a written design only.

---

### Step 1 — Phase 7: Surface computed-but-hidden data `Coding · Small (~4hrs)`

*From Full Roadmap.md:*
- [ ] Add confidence indicator next to incorrectness values in question drill-down (`ui/components.py`)
- [ ] Decide on temporal smoothing: activate `SMOOTHING_ENABLED = True` in `config.py` or remove the stub

*Unblocks: Appendix B will capture the live confidence indicator in the question drill-down screenshot.*

---

### Step 2 — Phase 5: Comparison UI `Coding · Large (~16hrs)`

*From Full Roadmap.md:*
- [ ] `comparison_view()` in `ui/views.py`
- [ ] `render_comparison_scatter()`, `render_comparison_table()`, `render_agreement_summary()` in `ui/components.py`
- [ ] "Model Comparison" routing in `instructor_app.py`
- [ ] Settings sub-panel: `improved_models_enabled` toggle + sub-toggles + BKT sliders

*From Coding Roadmap.md (Phase 5 detailed sub-tasks):*
- [ ] Add `comparison_view()` to `code/learning_dashboard/ui/views.py`
- [ ] Add `render_comparison_scatter()` to `ui/components.py` — baseline x-axis, improved y-axis, diagonal reference line
- [ ] Add `render_comparison_table()` to `ui/components.py` — sorted by absolute delta, biggest disagreements first
- [ ] Add `render_agreement_summary()` to `ui/components.py` — summary cards: agreement %, level-change counts, top disagreements
- [ ] Add "Model Comparison" option to view routing radio in `instructor_app.py`
- [ ] Add settings sub-panel: `improved_models_enabled` toggle + per-model sub-toggles + BKT parameter sliders (`P_init`, `P_learn`, `P_guess`, `P_slip`)

*Verification after Phase 5 (from Coding Roadmap.md):*
- [ ] Enable improved models in Settings → open Model Comparison → verify both Student Struggle and Question Difficulty tabs render
- [ ] Disable improved models → verify the view shows an informative message rather than an empty page
- [ ] Click a row in the comparison table → verify click-through to student/question detail still works
- [ ] Verify BKT sliders in settings change the model output in the comparison view
- [ ] Syntax check: `python -m py_compile code/app.py code/lab_app.py code/learning_dashboard/*.py code/learning_dashboard/ui/*.py code/learning_dashboard/models/*.py`

*Unblocks: Step 3 (screenshots require the comparison UI to exist); Step 4 (test results include model comparison evidence); Step 7 (Ch5 model comparison section).*

---

## Week 2: Apr 16–22 (~16hrs)

**Target:** Complete steps 3 and 4. Begin step 5 (Ch4 introduction + technology stack section). If Phase 5 spilled from Week 1, absorb the overflow before moving to screenshots.

> **Supervisor checkpoint — Wed 16 Apr, 1pm**
> Show: Completed comparison UI (live demo). First pass of Appendix B screenshots. Smoke test results (Appendix C pass/fail table). Discuss Ch4 structure — confirm which sections need the most expansion and whether the lab assistant system warrants its own subsection.
> Agenda: Demo comparison UI; screenshot review; Ch4 outline approval.

---

### Step 3 — Appendix B: UI Screenshots `Evidence · Small (~4hrs)`

*From Full Roadmap.md:*
- [ ] All 6 instructor views (in-class, student detail, question detail, data analysis, model comparison, settings)
- [ ] Model comparison view (both student + question tabs)
- [ ] Lab assistant app (join screen, unassigned view, assigned view)
- [ ] Session start/end states

*From Rewrite Queue.md (Critical):*
- [ ] **Populate Appendix B (UI Screenshots)** — empty; needs screenshots of all dashboard views to support Ch4 and Ch5.

*Unblocks: Step 5 (Ch4 needs Appendix B screenshots as figures); Step 9 (Ch3 Figma mockup replacements use Appendix B).*

---

### Step 4 — Appendix C: Test Results `Evidence · Medium (~8hrs)`

*From Full Roadmap.md:*
- [ ] Run every test in the smoke test checklist; record pass/fail
- [ ] Note any observations or edge-case behaviour
- [ ] Capture model comparison results for baseline vs IRT difficulty and baseline vs improved struggle

*From Rewrite Queue.md (Critical):*
- [ ] **Populate Appendix C (Detailed Test Results)** — empty; needs test evidence to support Ch5.

*Unblocks: Step 7 (Ch5 §5.2 Functional Testing maps FR1–FR7 to Appendix C results; §5.4 Results uses model comparison captures).*

---

### Step 5 — Ch4 (begin, ~4hrs this week): Implementation rewrite `Writing · Large`

Begin with the two sections that do not require screenshots to write:

*From Full Roadmap.md:*
- [ ] Replace scope/introduction section — remove "proof of concept" framing
- [ ] Update technology stack table to reflect V2 dependencies (filelock, openai, scipy, streamlit-autorefresh)

*From Rewrite Queue.md (High priority):*
- [ ] **Remove V1 prototype framing from Ch4** — replace "at this stage", "proof of concept", "to be implemented in the later iteration", "foundation for what the dashboard will eventually become" with final-system language.
- [ ] **Update Ch4 deferred features list** — line 58 says "assistant allocation and smart device notifications, are to be implemented in the later iteration." Assistant allocation IS implemented. Only smart devices remain deferred.

---

## Week 3: Apr 23–29 (~22hrs)

**Target:** Complete step 5 (Ch4 all remaining sections). Complete step 6 (Appendices E&F). Begin step 7 (Ch5 §5.1 Evaluation Design).

> **Supervisor checkpoint — Wed 23 Apr, 1pm**
> Show: Ch4 draft (all sections present, even if rough). Appendices E&F complete. §5.1 Evaluation Design outline. Discuss Ch5 model evaluation section (Meeting 3 priority item) — confirm framing of parametric vs alternative model comparison, and how to present the CF evaluation.
> Agenda: Ch4 review; Ch5 structure approval; confirm limitation section wording on manual weight-setting.

---

### Step 5 (continued) — Ch4: Implementation rewrite `Writing · Large (~12hrs this week)`

*From Full Roadmap.md (remaining sections):*
- [ ] Data pipeline section — describe interval-based polling, JSON+XML parsing, normalization
- [ ] Analytics section — OpenAI incorrectness scoring, 7-signal struggle, 5-signal difficulty, CF, mistake clustering
- [ ] Models section — IRT, BKT, improved struggle, measurement confidence
- [ ] Lab assistant system — join/assign/self-claim/mark-helped flows, shared JSON state
- [ ] Saved sessions and session lifecycle — CRUD, retroactive save, academic period filtering
- [ ] Instructor views — all 6 views + settings + sound effects
- [ ] Add Appendix B screenshots as figures

*From Rewrite Queue.md (High priority):*
- [ ] **Rewrite Ch4 Implementation for V2** — entire chapter describes V1 prototype. Must describe: OpenAI scoring, 7-signal struggle, 5-signal difficulty, CF, mistake clustering, IRT, BKT, improved struggle, lab assistant system, saved sessions, 6 views, settings. See [[Ch4 – Implementation]].
- [ ] **Add missing V2 features to Ch3 or Ch4** — IRT difficulty, BKT mastery, improved struggle model, mistake clustering, measurement confidence, saved sessions, data analysis views, lab assistant system, settings page, sound effects, academic calendar. None appear anywhere in the thesis.

*From Rewrite Queue.md (Supervisor meeting items — to be resolved during Ch4 writing):*
- [ ] **Document improvement trajectory in report** — linear regression slope is implemented in `analytics.py` but not described anywhere in the thesis. Add to Ch3 §3.3.1 or Ch4 with citation.
- [ ] **Document answer repetition rate in report** — `rep_hat` is a live signal in the 7-component struggle model but undocumented in the thesis. Add formula component and citation.
- [ ] **Document Bayesian shrinkage in report** — shrinkage is applied to all struggle signals but not described in Ch3 or Ch4. Add formal description with citation.
- [ ] **Align retry rate / feedback requests naming** — report uses "feedback requests"; code uses `retry_rate`. Pick one term and apply consistently across Ch3, Ch4, and config comments.
- [ ] **Insert all pending citations** — new sections added (CF alternative model §3.3.3, weight justification §3.3.4, struggle modelling §2.1.4, recommender systems §2.1.5) have identified sources but no inline `\cite{}` calls yet.

---

### Step 6 — Appendices E & F: Formulae `Writing · Small–Medium (~6hrs)`

*From Full Roadmap.md:*
- [ ] Appendix E: struggle formula (7 components + weights), difficulty formula (5 components + weights), IRT likelihood, BKT update rule, improved struggle weights, CF cosine similarity
- [ ] Appendix F: derivation notes for non-obvious formulas (BKT update, IRT MLE gradient, Bayesian shrinkage in struggle)

*From Rewrite Queue.md (Critical):*
- [ ] **Populate Appendix E (Formulae)** — empty; collect all model formulas in one reference.
- [ ] **Populate Appendix F (Formulae Derivation)** — empty; provide derivation steps for key models.

*Note: Appendix E and F can be written in the gaps between Ch4 sections — the formulae are already in the code; this is transcription and typesetting work, not composition.*

---

### Step 7 — Ch5 (begin, ~4hrs this week): §5.1 Evaluation Design

*From Full Roadmap.md:*
- [ ] §5.1 Evaluation Design — method, scope, what was tested and why

*Unblocks: Writing §5.1 first allows the supervisor to review the evaluation methodology framing before the heavier §5.2–§5.5 sections are written in Week 4.*

---

## Week 4: Apr 30–May 6 (~20hrs)

**Target:** Complete step 7 (Ch5, all remaining sections).

> **Supervisor checkpoint — Wed 30 Apr, 1pm**
> Show: Ch4 complete. Ch5 §5.1–§5.2 draft. Appendices E&F complete. Discuss the results presentation in §5.4 — particularly how to frame model comparison outcomes and what a fair limitation statement looks like for the weight-setting process.
> Agenda: Ch4 sign-off; Ch5 §5.2 review; discuss §5.4 results framing.

---

### Step 7 (continued) — Ch5: Results & Evaluation `Writing · Large (~16hrs total, ~12hrs this week)`

*From Full Roadmap.md:*
- [ ] §5.1 Evaluation Design — method, scope, what was tested and why (begun Week 3)
- [ ] §5.2 Functional Testing — FR1–FR7 mapped to smoke test evidence (Appendix C)
- [ ] §5.3 Non-Functional Testing — NFR1–NFR6 (performance, usability, reliability)
- [ ] §5.4 Results — model comparison results (baseline vs IRT, baseline vs improved struggle), what passed/failed
- [ ] §5.5 Discussion — limitations, what results mean, comparison to design intent

*From Rewrite Queue.md (Critical):*
- [ ] **Write Ch5 Evaluation** — entire chapter is empty (5 subsections: Evaluation Design, Functional Testing, Non-Functional Testing, Results, Discussion). See [[Ch5 – Results and Evaluation]] for suggested content.

*From Rewrite Queue.md (Meeting 3 additions — #meeting3, Dr. Batmaz priority):*
- [ ] **Ch5 — Model Evaluation** — mathematical model comparison, parametric vs alternative. Dr. Batmaz priority. #meeting3
- [ ] **Ch5 — Limitation** — state explicitly that α β γ δ η were set by trial and error due to absence of labeled ground truth. #meeting3
- [ ] **Ch5 — Future Work** — ML-based weight optimisation (Optuna, logistic regression, gradient boosting) once labeled data available. #future-work

*From Rewrite Queue.md (Supervisor meeting item):*
- [ ] **Draft CF evaluation subsection in Ch5** — use held-out historical sessions as proxy ground truth; report RMSE, precision@k, and coverage. This was flagged as an open question by Dr Batmaz.

*Unblocks: Step 8 (Ch6 must come after Ch5 is drafted — summary and contributions follow from what Ch5 establishes).*

---

## Week 5: May 7–13 (~24hrs)

**Target:** Complete steps 8, 9, and 10. Begin step 11 if the week runs ahead.

> **Supervisor checkpoint — Wed 7 May, 1pm**
> Show: Ch5 complete. Ch6 draft (all three sections present). Discuss Ch3 formula updates — confirm the updated weights and component counts match what Dr. Batmaz expects. Raise any open citation gaps identified during Ch4 writing.
> Agenda: Ch5 sign-off; Ch6 review; Ch3 update plan; citation status.

---

### Step 8 — Ch6: Conclusion `Writing · Medium (~8hrs)`

*From Full Roadmap.md:*
- [ ] §6.1 Summary — restate objectives, what was built, what was achieved
- [ ] §6.2 Contributions — scoring model advances, lab assistant coordination, real-time analytics
- [ ] §6.3 Future Work — FR6 smart devices, Phase 6 mobile refinement, Phase 9 RAG feedback, Phase 10/11 in-app Help, event-driven architecture, temporal smoothing, BKT parameter tuning, larger evaluation study, export/reporting

*From Rewrite Queue.md (Critical):*
- [ ] **Write Ch6 Conclusion** — entire chapter is empty (Summary, Future Work). See [[Ch6 – Conclusion]] for suggested content.

*From Rewrite Queue.md (Supervisor meeting item):*
- [ ] **Add future work item: ML-based weight optimisation** — Ch6 future work should mention that once labelled ground truth data is available, the parametric weights (α, β, γ, δ, η) could be optimised via supervised ML rather than set manually.

---

### Step 9 — Ch3: Design updates `Writing · Medium (~8hrs)`

*From Full Roadmap.md:*
- [ ] Update struggle formula to 7 components + Bayesian shrinkage (was 5 in thesis)
- [ ] Update difficulty formula to 5 components (was 4 in thesis)
- [ ] Replace Figs 8–10 (Figma mockups) with actual screenshots from Appendix B
- [ ] Update CF section — it is implemented, not "to be implemented"
- [ ] Add sections for IRT, BKT, improved struggle, mistake clustering

*From Rewrite Queue.md (High priority):*
- [ ] **Update Ch3 §3.3.1 struggle formula** — thesis has 5 components (n, t, e, f, A_raw); code has 7 (adds r_hat, d_hat, rep_hat). Update formula, add Bayesian shrinkage description. See [[Ch3 – Design and Modelling]].
- [ ] **Update Ch3 §3.3.2 difficulty formula** — thesis has 4 components; code has 5 (adds p_tilde first-attempt failure). Update formula and weights.
- [ ] **Replace Figma mockups in Ch3 §3.4.2** — Figs 8, 9, 10 are Figma conceptual designs. Replace with actual dashboard screenshots. Remove "conceptual design rather than a fully implemented system" caveat.
- [ ] **Update Ch3 CF section** — change "is still going to be implemented" to describe actual implementation. CF is live, toggleable, enabled by default with k=3, threshold configurable.

*From Rewrite Queue.md (Medium priority):*
- [ ] **Update Ch3 threshold label names** — thesis uses None/Low/Medium/High; code uses On Track/Minor Issues/Struggling/Needs Help.
- [ ] **Address temporal smoothing** — Ch3 proposes exponential smoothing for both models. Code has `SMOOTHING_ENABLED = False` stub. Either remove from design or explain why it was deferred.
- [ ] **Remove or update "event-driven pipeline under exploration"** — Ch3 §3.1 mentions this; V2 is still interval-based. Either remove claim or discuss as future work.

*From Rewrite Queue.md (Meeting 3 addition):*
- [ ] **Ch3 — RAG Design** — hybrid SQL + ChromaDB architecture, justification and literature. Placeholder inserted. #meeting3

*From Rewrite Queue.md (Supervisor meeting item):*
- [ ] **Reconcile temporal smoothing (report vs code)** — Ch3 proposes exponential smoothing; `SMOOTHING_ENABLED = False` in config. Either remove from Ch3 design or explain deferral explicitly.

---

### Step 10 — Ch1 & Ch2: Language and framing `Writing · Small (~4hrs)`

*From Full Roadmap.md:*
- [ ] Convert future tense in Ch1 §1.2, §1.3, §1.5 to past/present
- [ ] Update Table 1 risk mitigations with actual decisions made
- [ ] Fill Ch2 §2.1.7 research gaps (uncomment and revise draft at lines 121–130)
- [ ] Add implementation status column to FR/NFR tables; clarify FR6 is unimplemented

*From Rewrite Queue.md (Critical):*
- [ ] **Fill research gaps placeholder** — Ch2 §2.1.7 has `[FILL IN]` at line 119 of `requirements specification.tex`. A commented-out draft exists at lines 121-130 — review, update, and uncomment.

*From Rewrite Queue.md (Medium priority):*
- [ ] **Convert Ch1 future tense to past/present** — §1.2, §1.3, §1.5 use "we will", "the system will" throughout. Should describe completed work.
- [ ] **Update Ch1 risk mitigations** — Table 1 mitigations are generic ("seek constant feedback", "explore smartwatch solutions"). Update to describe actual decisions (Bayesian shrinkage for insufficient data, modular design for extensibility, smart devices scoped out).
- [ ] **Add implementation status to Ch2 requirements** — FR1-FR7 and NFR1-NFR6 need mapping to current implementation state. Could be inline or in Ch5 evaluation.
- [ ] **Update Ch2 FR6 status** — smart device integration is "Should Have" but completely unimplemented. Either move to "Won't Have" or discuss honestly as future work.

---

## Week 6: May 14–20 (~12hrs)

**Target:** Complete steps 11 and 12. Four hours of buffer for LaTeX compilation, figure numbering, and any unexpected issues. Stretch items only if steps 1–12 are fully done by 17 May.

> **Supervisor checkpoint — Wed 14 May, 1pm (final meeting)**
> Show: All chapters drafted and reviewed. Appendix A outline or draft. Raise any outstanding issues — citations, figure numbering, cross-references. This is the last meeting before submission.
> Agenda: Final review of open items; confirm nothing is missing from Ch6 future work; discuss submission logistics.

---

### Step 11 — Appendix A: Code Snippets `Writing · Small (~4hrs)`

*From Full Roadmap.md:*
- [ ] Incorrectness scoring batch call
- [ ] Struggle score function signature
- [ ] Lab state read/write pattern
- [ ] Deferred actions example

*From Rewrite Queue.md (Critical):*
- [ ] **Populate Appendix A (Code Snippets)** — empty; needs key implementation code to support Ch4.

---

### Step 12 — Polish pass `Writing · Small (~4hrs)`

*From Full Roadmap.md:*
- [ ] Terminology: "incorrectness", "struggle score", level labels ("On Track / Minor Issues / Struggling / Needs Help")
- [ ] Update bibliography for IRT/BKT/improved struggle sources if new citations added
- [ ] Review figure and table numbering after all additions
- [ ] LaTeX compile check — `main.tex` with no errors or warnings

*From Rewrite Queue.md (Low priority):*
- [ ] **Terminology consistency check** — ensure thesis terms match codebase terms (e.g., "incorrectness" not "wrongness", "struggle score" not "struggle metric").
- [ ] **Update bibliography** — 36 references currently; may need additions for IRT, BKT, or new features if they get dedicated sections.
- [ ] **Review figure/table numbering** — after adding/replacing figures, ensure captions and cross-references are correct.
- [ ] **Check LaTeX compilation** — after all edits, verify `main.tex` compiles without errors.
- [ ] **Confirm Progress Report exclusion** — `Progress Report.tex` is commented out in `main.tex`. Verify it stays excluded from final submission.

---

### Stretch — Week 6 only, do not start before 17 May

These items are thesis-strengthening but not thesis-critical. Do not begin either unless steps 1–12 are fully and cleanly complete.

**Step 13 — FR6: Smart device notifications `Coding · Large` (stretch)**

*From Full Roadmap.md:*
- [ ] Evaluate feasibility of web push notifications for the assistant app
- [ ] If viable: implement push alert when a new high-struggle student appears
- [ ] Document the decision in Ch6 regardless of outcome

**Step 14 — Phase 6: Mobile app refinement `Coding · Medium` (stretch)**

*From Full Roadmap.md:*
- [ ] BKT mastery badge + progress bar on assigned-student card (`render_assigned_view()`)
- [ ] Per-question mastery labels on the top-3 question list
- [ ] Session elapsed timer in `_render_session_status_strip()`
- [ ] Helped-vs-struggling summary header in `render_unassigned_view()`

*Verification after Phase 6 (from Coding Roadmap.md):*
- [ ] Join as assistant, get assigned a student → verify BKT mastery badge and progress bar appear on the student card
- [ ] Check per-question mastery labels appear alongside the top-3 question list
- [ ] Verify session elapsed timer increments correctly

---

## Useful links

- [[Full Roadmap]] — canonical step order and scope decisions
- [[Coding Roadmap]] — Phase 5 and Phase 6 detailed sub-tasks and verification checklists
- [[Writing Roadmap]] — chapter-by-chapter status summary
- [[Rewrite Queue]] — granular edit checklist with all specific changes per chapter
- [[Report Sync]] — mismatch analysis between V2 code and current thesis text
- [[Evidence Bank]] — what evaluation evidence exists or needs collecting
- [[Setup and Runbook]] — smoke test checklist used for Appendix C
