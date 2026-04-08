# Writing Roadmap

High-level chapter status and recommended writing order for the final thesis submission. For granular task-level detail see [[Rewrite Queue]]. For mismatch analysis between the thesis and the V2 codebase see [[Report Sync]].

---

## Chapter status

| Section | Status | Work needed | Effort |
|---|---|---|---|
| Ch1 — Introduction | Partial | Convert future tense; update risk mitigations | Small |
| Ch2 — Background & Requirements | Partial | Fill research gaps placeholder; add FR/NFR implementation status | Small |
| Ch3 — Design & Modelling | Partial | Update formulas (struggle: 5→7 components, difficulty: 4→5); replace Figma mockups with screenshots; update CF section; add IRT/BKT/improved struggle sections | Medium |
| Ch4 — Implementation | Outdated | Full rewrite — currently describes V1 prototype only; V2 has ~10 new features | Large |
| Ch5 — Results & Evaluation | Empty | Write from scratch — evaluation design, functional testing, NFR testing, results, discussion | Large |
| Ch6 — Conclusion | Empty | Write from scratch — summary of contributions, future work | Medium |
| Appendix A — Code Snippets | Empty | Add key implementation excerpts to support Ch4 | Small |
| Appendix B — UI Screenshots | Empty | Screenshot every dashboard view; needed for Ch4 and Ch5 | Small |
| Appendix C — Test Results | Empty | Document smoke test outcomes and any evaluation evidence | Medium |
| Appendix D — References | Done | Nothing needed | — |
| Appendix E — Formulae | Empty | Collect all model formulas in one reference | Small |
| Appendix F — Formula Derivations | Empty | Derivation steps for struggle, difficulty, IRT, BKT | Medium |
| Ch5 — CF Evaluation | Missing | Draft offline evaluation subsection: RMSE, precision@k, coverage using held-out sessions as proxy ground truth | Medium |

---

## Recommended writing order

Work through this order to minimise rework — each item unblocks the next.

### 1. Ch4 — Implementation rewrite `Large`
Rewrite the entire chapter for V2. Remove all "proof of concept" and "to be implemented" framing. Cover: OpenAI incorrectness scoring, 7-signal struggle model with Bayesian shrinkage, 5-signal difficulty model, collaborative filtering, mistake clustering, IRT, BKT, improved struggle, lab assistant system, saved sessions, all 6 instructor views, settings, sound effects, academic calendar.

*Unblocks: Ch5 evaluation framing, Appendix A.*

### 2. Appendix B — UI Screenshots `Small`
Capture screenshots of all dashboard views while Ch4 is being written — they will be needed for both Ch4 figures and Ch5 evaluation evidence. Do this in parallel with Ch4.

*Unblocks: Ch3 mockup replacement, Ch5 figures.*

### 3. Appendix C — Test Results `Medium`
Run the full smoke test checklist from [[Setup and Runbook]] and document outcomes. Capture evidence (pass/fail per test, any observations) to populate Ch5.

*Unblocks: Ch5.*

### 4. Ch5 — Results & Evaluation `Large`
Write from scratch. Suggested structure:
- 5.1 Evaluation Design — method, scope, what was tested and why
- 5.2 Functional Testing — FR1–FR7 against smoke test evidence (Appendix C)
- 5.3 Non-Functional Testing — NFR1–NFR6 (performance, usability, reliability, etc.)
- 5.4 Results — what passed, what didn't, any observations
- 5.5 Discussion — limitations, what the results mean, comparison to design intent

*Unblocks: Ch6.*

### 5. Ch6 — Conclusion `Medium`
Write from scratch. Suggested structure:
- 6.1 Summary — restate objectives, what was built, what was achieved
- 6.2 Contributions — what this project adds (scoring model, lab assistant coordination, real-time analytics)
- 6.3 Future Work — smart device notifications (FR6), temporal smoothing, event-driven pipeline, larger evaluation study

### 6. Appendices E & F — Formulae `Small–Medium`
Collect all model formulas (struggle, difficulty, IRT, BKT, improved struggle, CF) into Appendix E. Add derivation notes for the non-obvious ones in Appendix F. Can be written alongside Ch4–Ch6.

### 7. Ch3 — Design updates `Medium`
Surgical edits only — the chapter structure is solid:
- Update struggle formula to 7 components + Bayesian shrinkage
- Update difficulty formula to 5 components
- Replace Figs 8–10 (Figma mockups) with actual screenshots from Appendix B
- Update CF section to describe live implementation
- Add sections for IRT, BKT, improved struggle, mistake clustering

### 8. Ch1 & Ch2 — Language and framing `Small`
- Convert future tense in Ch1 §1.2, §1.3, §1.5 to past/present
- Update Table 1 risk mitigations with actual decisions made
- Fill Ch2 §2.1.7 research gaps (uncomment and revise draft at lines 121–130)
- Add implementation status column to FR/NFR tables

### 9. Appendix A — Code Snippets `Small`
Add key code excerpts to support Ch4: incorrectness scoring batch call, struggle score function signature, lab state read/write pattern, deferred actions example.

### 10. Polish pass `Small`
- Terminology consistency (use "incorrectness", "struggle score", "On Track / Minor Issues / Struggling / Needs Help")
- Update bibliography if new sources are cited for IRT/BKT/improved struggle
- Review figure and table numbering after additions
- LaTeX compile check — `main.tex` with no errors

---

## Useful links

- [[Rewrite Queue]] — granular checklist of every specific edit
- [[Report Sync]] — section-by-section mismatch analysis between V2 code and current thesis text
- [[Evidence Bank]] — what evaluation evidence exists or needs to be collected
- [[Figures and Tables]] — inventory of figures and their current state
- [[Thesis Overview]] — full dissertation structure and objectives

---

## Deadline

**Submission deadline: 20 May 2026.** Approximately 6 weeks from now. Ch4, Ch5, and Ch6 are all either empty or require full rewrites. Prioritise in order: Ch4 rewrite → screenshots → test evidence → Ch5 → CF evaluation → Ch6 → remaining Rewrite Queue items.
