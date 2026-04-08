# Full Roadmap

Combined coding + writing order for final submission. Work through this top to bottom — each item unblocks the next. For detailed specs see [[Coding Roadmap]] (coding) and [[Writing Roadmap]] (writing).

Related: [[Coding Roadmap]], [[Writing Roadmap]], [[Rewrite Queue]], [[Report Sync]], [[Evidence Bank]]

---

## Why this order

Coding must come before screenshots, screenshots before Ch4 figures, Ch4 before Ch5 evaluation framing, and Ch5 before Ch6. The three remaining coding tasks are therefore the first three items regardless of effort.

---

## The order

### 1. Phase 7 — Surface computed-but-hidden data `Coding · Small`

Quick win. Two features are computed every run but produce no visible output — fix this before screenshots so Appendix B captures the live features.

- [ ] Add confidence indicator next to incorrectness values in question drill-down (`ui/components.py`)
- [ ] Decide on temporal smoothing: activate `SMOOTHING_ENABLED = True` in `config.py` or remove the stub

*Unblocks: accurate screenshots in step 4.*

---

### 2. Phase 5 — Comparison UI `Coding · Large`

The biggest remaining coding task. Produces the model comparison view needed for Ch5 evaluation evidence.

- [ ] `comparison_view()` in `ui/views.py`
- [ ] `render_comparison_scatter()`, `render_comparison_table()`, `render_agreement_summary()` in `ui/components.py`
- [ ] "Model Comparison" routing in `instructor_app.py`
- [ ] Settings sub-panel: `improved_models_enabled` toggle + sub-toggles + BKT sliders

*Unblocks: Ch5 model comparison evidence, Appendix B comparison screenshots.*

---

### 3. Phase 6 — Mobile app refinement `Coding · Medium`

Polish the lab assistant app so Appendix B mobile screenshots show the full feature set and Ch5 functional testing covers the assistant flows properly.

- [ ] BKT mastery badge + progress bar on assigned-student card (`render_assigned_view()`)
- [ ] Per-question mastery labels on the top-3 question list
- [ ] Session elapsed timer in `_render_session_status_strip()`
- [ ] Helped-vs-struggling summary header in `render_unassigned_view()`

*Unblocks: complete Appendix B mobile screenshots, Ch5 assistant flow testing.*

---

### 4. Appendix B — UI Screenshots `Evidence · Small`

Take screenshots of every dashboard and mobile view now that the code is stable. Needed for Ch3 mockup replacement, Ch4 figures, and Ch5 evaluation evidence.

- [ ] All 6 instructor views (in-class, student detail, question detail, data analysis, model comparison, settings)
- [ ] Model comparison view (both student + question tabs)
- [ ] Lab assistant app (join screen, unassigned view, assigned view with BKT badge)
- [ ] Session start/end states

*Unblocks: Ch3 figure replacements, Ch4 implementation figures, Ch5 evidence.*

---

### 5. Appendix C — Test Results `Evidence · Medium`

Run the full smoke test checklist from [[Setup and Runbook]] and document outcomes. This is the primary evidence base for Ch5.

- [ ] Run every test in the smoke test checklist; record pass/fail
- [ ] Note any observations or edge-case behaviour
- [ ] Capture model comparison results for baseline vs IRT difficulty and baseline vs improved struggle

*Unblocks: Ch5 §5.2 Functional Testing and §5.4 Results.*

---

### 6. Ch4 — Implementation rewrite `Writing · Large`

Rewrite the entire chapter — it currently describes V1 only. Cover the full V2 system.

- [ ] Replace scope/introduction section — remove "proof of concept" framing
- [ ] Update technology stack table to reflect V2 dependencies (filelock, openai, scipy, streamlit-autorefresh)
- [ ] Data pipeline section — describe interval-based polling, JSON+XML parsing, normalization
- [ ] Analytics section — OpenAI incorrectness scoring, 7-signal struggle, 5-signal difficulty, CF, mistake clustering
- [ ] Models section — IRT, BKT, improved struggle, measurement confidence
- [ ] Lab assistant system — join/assign/self-claim/mark-helped flows, shared JSON state
- [ ] Saved sessions and session lifecycle — CRUD, retroactive save, academic period filtering
- [ ] Instructor views — all 6 views + settings + sound effects
- [ ] Add Appendix B screenshots as figures

*Unblocks: Ch5 evaluation framing, Appendix A code snippets.*

---

### 7. Appendices E & F — Formulae `Writing · Small–Medium`

Can be written alongside Ch4. Collect all model formulas and derivation notes in one place.

- [ ] Appendix E: struggle formula (7 components + weights), difficulty formula (5 components + weights), IRT likelihood, BKT update rule, improved struggle weights, CF cosine similarity
- [ ] Appendix F: derivation notes for non-obvious formulas (BKT update, IRT MLE gradient, Bayesian shrinkage in struggle)

*Can be written in parallel with Ch4–Ch6.*

---

### 8. Ch5 — Results & Evaluation `Writing · Large`

Write from scratch using Appendix B screenshots and Appendix C test results as evidence.

- [ ] §5.1 Evaluation Design — method, scope, what was tested and why
- [ ] §5.2 Functional Testing — FR1–FR7 mapped to smoke test evidence (Appendix C)
- [ ] §5.3 Non-Functional Testing — NFR1–NFR6 (performance, usability, reliability)
- [ ] §5.4 Results — model comparison results (baseline vs IRT, baseline vs improved struggle), what passed/failed
- [ ] §5.5 Discussion — limitations, what results mean, comparison to design intent

*Unblocks: Ch6.*

---

### 9. Ch6 — Conclusion `Writing · Medium`

Write from scratch once Ch5 is drafted.

- [ ] §6.1 Summary — restate objectives, what was built, what was achieved
- [ ] §6.2 Contributions — scoring model advances, lab assistant coordination, real-time analytics
- [ ] §6.3 Future Work — FR6 smart devices, event-driven architecture, temporal smoothing, BKT parameter tuning, larger evaluation study, export/reporting

---

### 10. Ch3 — Design updates `Writing · Medium`

Surgical edits — the chapter structure is solid, specific sections need updating.

- [ ] Update struggle formula to 7 components + Bayesian shrinkage (was 5 in thesis)
- [ ] Update difficulty formula to 5 components (was 4 in thesis)
- [ ] Replace Figs 8–10 (Figma mockups) with actual screenshots from Appendix B
- [ ] Update CF section — it is implemented, not "to be implemented"
- [ ] Add sections for IRT, BKT, improved struggle, mistake clustering

---

### 11. Ch1 & Ch2 — Language and framing `Writing · Small`

- [ ] Convert future tense in Ch1 §1.2, §1.3, §1.5 to past/present
- [ ] Update Table 1 risk mitigations with actual decisions made
- [ ] Fill Ch2 §2.1.7 research gaps (uncomment and revise draft at lines 121–130)
- [ ] Add implementation status column to FR/NFR tables; clarify FR6 is unimplemented

---

### 12. Appendix A — Code Snippets `Writing · Small`

Add key code excerpts to support Ch4.

- [ ] Incorrectness scoring batch call
- [ ] Struggle score function signature
- [ ] Lab state read/write pattern
- [ ] Deferred actions example

---

### 13. Polish pass `Writing · Small`

Final consistency check before submission.

- [ ] Terminology: "incorrectness", "struggle score", level labels ("On Track / Minor Issues / Struggling / Needs Help")
- [ ] Update bibliography for IRT/BKT/improved struggle sources if new citations added
- [ ] Review figure and table numbering after all additions
- [ ] LaTeX compile check — `main.tex` with no errors or warnings

---

### 14. FR6 — Smart device notifications `Coding · Large` (stretch)

Only attempt if time allows after step 9. Otherwise document as future work in Ch6 §6.3.

- [ ] Evaluate feasibility of web push notifications for the assistant app
- [ ] If viable: implement push alert when a new high-struggle student appears
- [ ] Document the decision in Ch6 regardless of outcome

---

## At a glance

| Step | Item | Type | Effort | Status |
|---|---|---|---|---|
| 1 | Phase 7 — Surface hidden data | Coding | Small | Not started |
| 2 | Phase 5 — Comparison UI | Coding | Large | Not started |
| 3 | Phase 6 — Mobile app refinement | Coding | Medium | Not started |
| 4 | Appendix B — Screenshots | Evidence | Small | Not started |
| 5 | Appendix C — Test Results | Evidence | Medium | Not started |
| 6 | Ch4 — Implementation rewrite | Writing | Large | Not started |
| 7 | Appendices E & F — Formulae | Writing | Small–Medium | Not started |
| 8 | Ch5 — Results & Evaluation | Writing | Large | Not started |
| 9 | Ch6 — Conclusion | Writing | Medium | Not started |
| 10 | Ch3 — Design updates | Writing | Medium | Not started |
| 11 | Ch1 & Ch2 — Language cleanup | Writing | Small | Not started |
| 12 | Appendix A — Code Snippets | Writing | Small | Not started |
| 13 | Polish pass | Writing | Small | Not started |
| 14 | FR6 — Smart devices (stretch) | Coding | Large | Not started |

---

## Useful links

- [[Coding Roadmap]] — full coding phase status and sub-tasks
- [[Writing Roadmap]] — chapter-by-chapter status and writing notes
- [[Rewrite Queue]] — granular edit checklist for each thesis section
- [[Report Sync]] — where the thesis diverges from the current code
- [[Evidence Bank]] — what evaluation evidence exists or still needs to be collected
- [[Setup and Runbook]] — smoke test checklist for Appendix C
