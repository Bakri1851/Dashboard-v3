# Full Roadmap

Combined coding + writing order for final submission. Work through this top to bottom — each item unblocks the next. For detailed specs see [[Coding Roadmap]] (coding) and [[Writing Roadmap]] (writing).

Related: [[Coding Roadmap]], [[Writing Roadmap]], [[Rewrite Queue]], [[Report Sync]], [[Evidence Bank]]

---

## Why this order

Rewrites of existing chapters (Ch3, Ch1&2, Ch4) must come before new chapters (Ch5, Ch6) so the implementation narrative is settled before evaluation is written. Ch4 is placed after Ch3 and Ch1&2 because the code is still subject to minor change — writing Ch4 last among the rewrites means it describes the final system. All appendices are grouped at the end, once chapter content is complete and stable, so screenshots and test evidence capture the truly final state.

Phases 9, 10, and 11 are explicitly out of scope for this submission. Each will be documented in Ch6 §6.3 Future Work. Attempting large coding phases with 41 days remaining and Ch4/Ch5/Ch6 unwritten would risk the submission. Phase 6 is stretch only.

---

## The order

### 1. Phase 7 — Surface computed-but-hidden data `Coding · Small`

Quick win. Two features are computed every run but produce no visible output — fix this before screenshots so Appendix B captures the live features.

- [x] Add confidence indicator next to incorrectness values in question drill-down (`ui/components.py`)
  - confidence dot added to question drill-down — green/amber/grey by threshold, mean confidence across question's submissions
- [x] Decide on temporal smoothing: activate `SMOOTHING_ENABLED = True` in `config.py` or remove the stub
  - temporal smoothing activated (SMOOTHING_ENABLED = True, α = 0.3); settings toggle added following cf_enabled pattern

*Unblocks: accurate screenshots in step 3.*

---

### 2. Phase 5 — Comparison UI `Coding · Large`

The biggest remaining coding task. Produces the model comparison view needed for Ch5 evaluation evidence.

- [x] `comparison_view()` in `ui/views.py`
- [x] `render_comparison_scatter()`, `render_comparison_table()`, `render_agreement_summary()` in `ui/components.py`
- [x] "Model Comparison" routing in `instructor_app.py`
- [x] Settings sub-panel: `improved_models_enabled` toggle + sub-toggles + BKT sliders

*Unblocks: Ch5 model comparison evidence, Appendix B comparison screenshots.*

---

### 3. Ch3 — Design updates `Writing · Medium`

Surgical edits — the chapter structure is solid, specific sections need updating. Where figures reference Appendix B screenshots, insert `[TODO: insert figure]` placeholders; these will be replaced at step 8.

- [ ] Update struggle formula to 7 components + Bayesian shrinkage (was 5 in thesis)
- [ ] Update difficulty formula to 5 components (was 4 in thesis)
- [ ] Mark Figs 8–10 (Figma mockups) for replacement — add `[TODO: replace with screenshot]` annotations
- [ ] Update CF section — it is implemented, not "to be implemented"
- [ ] Add sections for IRT, BKT, improved struggle, mistake clustering

*Unblocks: Ch1&2 language fixes are easier once Ch3 narrative is settled.*

---

### 4. Ch1 & Ch2 — Language and framing `Writing · Small`

- [ ] Convert future tense in Ch1 §1.2, §1.3, §1.5 to past/present
- [ ] Update Table 1 risk mitigations with actual decisions made
- [ ] Fill Ch2 §2.1.7 research gaps (uncomment and revise draft at lines 121–130)
- [ ] Add implementation status column to FR/NFR tables; clarify FR6 is unimplemented
- [ ] **Add three new Ch2 subsections (Knowledge Tracing, Text Mining, RAG) + citation extensions to §2.1.4/§2.1.6/§2.1.7** — see "Methods lit-review backlog (2026-04-18)" in [[Rewrite Queue]].

*Unblocks: Ch4 — existing chapter framing is now consistent before the implementation chapter is rewritten.*

---

### 5. Ch4 — Implementation rewrite `Writing · Large`

Rewrite the entire chapter — it currently describes V1 only. Cover the full V2 system. Add `[TODO: insert figure]` placeholders for Appendix B screenshots; these will be filled in at step 8.

- [ ] Replace scope/introduction section — remove "proof of concept" framing
- [ ] Update technology stack table to reflect V2 dependencies (filelock, openai, scipy, streamlit-autorefresh)
- [ ] Data pipeline section — describe interval-based polling, JSON+XML parsing, normalization
- [ ] Analytics section — OpenAI incorrectness scoring, 7-signal struggle, 5-signal difficulty, CF, mistake clustering
- [ ] Models section — IRT, BKT, improved struggle, measurement confidence
- [ ] Lab assistant system — join/assign/self-claim/mark-helped flows, shared JSON state
- [ ] Saved sessions and session lifecycle — CRUD, retroactive save, academic period filtering
- [ ] Instructor views — all 6 views + settings + sound effects
- [ ] Mark figure slots for Appendix B screenshots (`[TODO: insert figure]`)
- [ ] **Insert L-BFGS-B / MLE / ROC-AUC citation footnotes in Ch4 §4.9.x and Ch5 §5.1** — see "Methods lit-review backlog (2026-04-18)" in [[Rewrite Queue]].

*Unblocks: Ch5 evaluation framing, Appendix A code snippets.*

---

### 6. Ch5 — Results & Evaluation `Writing · Large`

Write from scratch. Draft structure and prose first; Appendix C evidence slots can be filled in at step 9.

- [ ] §5.1 Evaluation Design — method, scope, what was tested and why
- [ ] §5.2 Functional Testing — FR1–FR7 mapped to smoke test evidence (Appendix C)
- [ ] §5.3 Non-Functional Testing — NFR1–NFR6 (performance, usability, reliability)
- [ ] §5.4 Results — model comparison results (baseline vs IRT, baseline vs improved struggle), what passed/failed
- [ ] §5.5 Discussion — limitations, what results mean, comparison to design intent

*Unblocks: Ch6.*

---

### 7. Ch6 — Conclusion `Writing · Medium`

Write from scratch once Ch5 is drafted.

- [ ] §6.1 Summary — restate objectives, what was built, what was achieved
- [ ] §6.2 Contributions — scoring model advances, lab assistant coordination, real-time analytics
- [ ] §6.3 Future Work — FR6 smart devices, Phase 6 mobile refinement, Phase 9 RAG feedback, Phase 10/11 in-app Help, event-driven architecture, temporal smoothing, BKT parameter tuning, larger evaluation study, export/reporting

---

### 8. Appendix B — UI Screenshots `Evidence · Small`

Take screenshots of every dashboard and mobile view now that all chapters are written and code is stable.

- [ ] All 6 instructor views (in-class, student detail, question detail, data analysis, model comparison, settings)
- [ ] Model comparison view (both student + question tabs)
- [ ] Lab assistant app (join screen, unassigned view, assigned view)
- [ ] Session start/end states
- [ ] Replace all `[TODO: insert figure]` placeholders in Ch3 and Ch4 with actual figures

*Unblocks: Appendix C (screenshots confirm system is in final state for smoke testing).*

---

### 9. Appendix C — Test Results `Evidence · Medium`

Run the full smoke test checklist from [[Setup and Runbook]] and document outcomes. This is the primary evidence base for Ch5.

- [ ] Run every test in the smoke test checklist; record pass/fail
- [ ] Note any observations or edge-case behaviour
- [ ] Capture model comparison results for baseline vs IRT difficulty and baseline vs improved struggle
- [ ] Fill any evidence slots left in Ch5 §5.2 and §5.4

*Unblocks: Appendices E&F and Appendix A (evidence pass confirms formulae and code snippets are final).*

---

### 10. Appendices E & F — Formulae `Writing · Small–Medium`

Collect all model formulas and derivation notes in one place.

- [ ] Appendix E: struggle formula (7 components + weights), difficulty formula (5 components + weights), IRT likelihood, BKT update rule, improved struggle weights, CF cosine similarity
- [ ] Appendix F: derivation notes for non-obvious formulas (BKT update, IRT MLE gradient, Bayesian shrinkage in struggle)

---

### 11. Appendix A — Code Snippets `Writing · Small`

Add key code excerpts to support Ch4.

- [ ] Incorrectness scoring batch call
- [ ] Struggle score function signature
- [ ] Lab state read/write pattern
- [ ] Deferred actions example

---

### 12. Polish pass `Writing · Small`

Final consistency check before submission.

- [ ] Terminology: "incorrectness", "struggle score", level labels ("On Track / Minor Issues / Struggling / Needs Help")
- [ ] Update bibliography for IRT/BKT/improved struggle sources if new citations added
- [ ] Review figure and table numbering after all additions
- [ ] LaTeX compile check — `main.tex` with no errors or warnings

---

### 13. FR6 — Smart device notifications `Coding · Large` (stretch)

Only attempt if time allows after step 8. Otherwise document as future work in Ch6 §6.3.

- [ ] Evaluate feasibility of web push notifications for the assistant app
- [ ] If viable: implement push alert when a new high-struggle student appears
- [ ] Document the decision in Ch6 regardless of outcome

---

### 14. Phase 6 — Mobile app refinement (stretch) `Coding · Medium`

Only attempt after Ch6 is written. Ch5 assistant flow testing can use the current app. BKT badges and session timer are thesis-strengthening but not thesis-critical.

- [ ] BKT mastery badge + progress bar on assigned-student card (`render_assigned_view()`)
- [ ] Per-question mastery labels on the top-3 question list
- [ ] Session elapsed timer in `_render_session_status_strip()`
- [ ] Helped-vs-struggling summary header in `render_unassigned_view()`

---

## Out of scope — document as future work

These phases will not be implemented before the May 20 deadline. Each should be documented in Ch6 §6.3 Future Work. Do not attempt coding on these items.

### Phase 9 — RAG suggested feedback ✅ Implemented (2026-04-14)

Architecture designed by Dr. Batmaz (Meeting 3) — **must be credited in dissertation**.

Implemented as an isolated `rag.py` module:
- `chromadb.PersistentClient` at `data/rag_chroma/`, collection `session_{session_id}`
- `all-MiniLM-L6-v2` embeddings via `sentence-transformers` (local, no API cost)
- Two-layer retrieval: pandas pre-filter by `student_id` + ChromaDB `where=` metadata filter
- GPT-4o-mini generates 2–3 coaching bullets surfaced in the assistant assigned-student card
- Graceful no-op if deps missing; cached per student per session

Ch4 and Ch5 sections needed. See [[RAG Pipeline - Two-Layer Retrieval]] and [[Suggested Focus Areas Panel]].

### Phase 10 — In-app Help system (instructor dashboard)

Help section under Settings covering Quick Tour, Help Centre, Model Guide, contextual tooltips, and reliability indicators. Not feasible to implement before deadline given the writing workload.

*Document in Ch6 §6.3 Future Work.*

### Phase 11 — In-app Help system (assistant app)

Lightweight mobile Help panel for lab assistants covering join guide, student card explainer, action button guide, and RAG suggestion explainer.

*Document in Ch6 §6.3 Future Work.*

---

## At a glance

| Step | Item | Type | Effort | Status |
| --- | --- | --- | --- | --- |
| 1 | Phase 7 — Surface hidden data | Coding | Small | Done |
| 2 | Phase 5 — Comparison UI | Coding | Large | **Done** |
| 3 | Ch3 — Design updates | Writing | Medium | Not started |
| 4 | Ch1 & Ch2 — Language cleanup | Writing | Small | Not started |
| 5 | Ch4 — Implementation rewrite | Writing | Large | Not started |
| 6 | Ch5 — Results & Evaluation | Writing | Large | Not started |
| 7 | Ch6 — Conclusion | Writing | Medium | Not started |
| 8 | Appendix B — Screenshots | Evidence | Small | Not started |
| 9 | Appendix C — Test Results | Evidence | Medium | Not started |
| 10 | Appendices E & F — Formulae | Writing | Small–Medium | Not started |
| 11 | Appendix A — Code Snippets | Writing | Small | Not started |
| 12 | Polish pass | Writing | Small | Not started |
| 13 | FR6 — Smart devices (stretch) | Coding | Large | Not started |
| 14 | Phase 6 — Mobile app refinement | Coding | Medium | Stretch |
| — | Phase 9 — RAG suggested feedback | Coding | Large | **Done** (2026-04-14) |
| — | Phase 10 — In-app Help (instructor) | Coding | Large | Out of scope / Future work |
| — | Phase 11 — In-app Help (assistant) | Coding | Medium | Out of scope / Future work |

---

## Useful links

- [[Coding Roadmap]] — full coding phase status and sub-tasks
- [[Writing Roadmap]] — chapter-by-chapter status and writing notes
- [[Rewrite Queue]] — granular edit checklist for each thesis section
- [[Report Sync]] — where the thesis diverges from the current code
- [[Evidence Bank]] — what evaluation evidence exists or still needs to be collected
- [[Setup and Runbook]] — smoke test checklist for Appendix C
