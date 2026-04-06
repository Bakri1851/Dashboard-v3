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

- [ ] **Convert Ch1 future tense to past/present** — §1.2, §1.3, §1.5 use "we will", "the system will" throughout. Should describe completed work.
- [ ] **Update Ch1 risk mitigations** — Table 1 mitigations are generic ("seek constant feedback", "explore smartwatch solutions"). Update to describe actual decisions (Bayesian shrinkage for insufficient data, modular design for extensibility, smart devices scoped out).
- [ ] **Add implementation status to Ch2 requirements** — FR1-FR7 and NFR1-NFR6 need mapping to current implementation state. Could be inline or in Ch5 evaluation.
- [ ] **Update Ch2 FR6 status** — smart device integration is "Should Have" but completely unimplemented. Either move to "Won't Have" or discuss honestly as future work.
- [ ] **Update Ch3 threshold label names** — thesis uses None/Low/Medium/High; code uses On Track/Minor Issues/Struggling/Needs Help.
- [ ] **Address temporal smoothing** — Ch3 proposes exponential smoothing for both models. Code has `SMOOTHING_ENABLED = False` stub. Either remove from design or explain why it was deferred.
- [ ] **Remove or update "event-driven pipeline under exploration"** — Ch3 §3.1 mentions this; V2 is still interval-based. Either remove claim or discuss as future work.
- [ ] **Confirm Progress Report exclusion** — `Progress Report.tex` is commented out in `main.tex`. Verify it stays excluded from final submission.
- [ ] **Review Ch2 commented-out research gaps** — lines 121-130 have a draft that may be suitable with minor updates.

---

## Low — polish and consistency

- [ ] **Terminology consistency check** — ensure thesis terms match codebase terms (e.g., "incorrectness" not "wrongness", "struggle score" not "struggle metric").
- [ ] **Update bibliography** — 36 references currently; may need additions for IRT, BKT, or new features if they get dedicated sections.
- [ ] **Review figure/table numbering** — after adding/replacing figures, ensure captions and cross-references are correct.
- [ ] **Check LaTeX compilation** — after all edits, verify `main.tex` compiles without errors.
