# Meeting Log

Supervisor: Dr. Batmaz
Frequency: Wednesdays 1pm
Location: University office

---

## Meeting 5 — Fri 29 May 2026 (draft review)

**Status:** 🔄 Actioned into [[Revisions/00 Index|Revisions Roadmap]]

### Discussed (supervisor reviewed the finished draft on screen)
- **Stickman context diagram** — add a simple bird's-eye stakeholder diagram (student / lab assistant / coordinator → assessment env / phone / dashboard) near System Architecture; keep the existing technical diagram too; number the components.
- **Component-level cross-references** — cite "Component A on Figure 3.1", not just the whole figure; refer back to the big diagram when discussing details.
- **Reads like a user manual** — add engineering *rationale* (why each design choice; what iterations led to it), backed by literature not preference. Examples named: tabular layout, visual encoding/colour.
- **Screenshots → appendix** — live software screenshots move to Appendix B and are cross-referenced; conceptual design drawings (Figma) stay in Ch3. Implementation keeps code segments, colour/framework decisions, problems.
- **Design completeness** — Settings view was left out of Ch3; state student-detail and question-detail interface designs in Ch3.
- **Define symbols** — module/question/timestamp/session never defined; parameters/weights need explaining.
- **RAG** — state why it's in the thesis (proof-of-concept) and how many systems were surveyed (~three or four).
- **Figure 3.2** (data-entry) — credit the module technician, **Charlotte Barnes**, by role+name.
- **Captions** — figure number + short title only; move explanations to body.
- **Section intros / conclusions** — small intro para per section; don't end sections/chapters abruptly on a figure; summary para after big tables; summary para at end of Implementation.
- **More lit review** — newer model-training content (OLS/bake-off, shrinkage, thresholds, missing data) needs background + references.
- **High-leverage follow-up (29 May):** check who else is doing this (prior art) and whether Research Gaps (§2.7) needs expanding → [[Revisions/10 Related Work & Research-Gap Expansion]].

### Audit + actions
- Two read-only audits run over the whole report (verified against `.tex`/`data/eval/`): 86 + 96 findings. Highest-impact net-new: a phantom "histogram gradient boosting" benchmark claim in the abstract/conclusion (not in `model_class_bakeoff.json`); difficulty ρ printed +0.469 but data is +0.468; §5.5.1 heading promises "Ethical Approval" with none given; Introduction claims smart-device integration as delivered (contradicts FR6 future-work).
- All actions captured in the **Revisions/** folder; nothing applied to `Report/` yet — every edit is previewed for sign-off. No new features built this pass.

---

## Meeting 4 — Wed 16 Apr 2026

**Status:** ✅ Complete

### Discussed
- RAG pipeline walkthrough — Dr. Batmaz now understands the full K-means → ChromaDB → OpenAI pipeline. Suggested caching generated feedback by cluster signature to avoid repeated API calls on identical clusters.
- IRT/BKT model disagreement — improved models produce ~0% agreement with baseline. Dr. Batmaz's guidance: don't fix, write about it. Discuss causes as a limitation in Ch5 §5.5.
- Collaborative filtering — CF is supplementary, mathematical modelling is the primary contribution. CF evaluation subsection (RMSE, precision@k, coverage) still outstanding from Meeting 3.
- Evaluation — retrospective temporal evaluation method agreed. Use 28,000 records from Dr. Batmaz's module. Label students from end-of-session outcome; test whether model predicts them at minute 20/30/40. Compare parametric vs CF vs hypothesis-based ranking. **Must be ready by Wed 23 Apr.**
- Dataset — Dr. Batmaz confirmed ~28,000 records available (his module, Weeks 1–12, ~57–62 students). "You can publish so much."
- Guest lecture — arranged with colleague Vanessa's MSc Ethics/Legal/Professional Issues class. Mon 27 Apr, 2pm. 5–6 slides, sell the idea not the implementation, optional demo. Dr. Batmaz will be present. May record for Discussion chapter.
- Extension — recommended filing the extension application (A&E evidence available) as a safety net even if submission stays on 20 May.

### Action items
- [ ] Implement retrospective evaluation pipeline — before Wed 23 Apr
- [ ] Prepare guest lecture slides (5–6) — send to Dr. Batmaz before 27 Apr
- [ ] Add RAG feedback caching to code + document in Ch4
- [ ] Write IRT/BKT disagreement discussion paragraph — Ch5 §5.5
- [ ] Draft CF evaluation subsection — Ch5 (outstanding from Meeting 3)
- [ ] File extension application

---

## Meeting 3 — Wed 8 Apr 2026

**Status:** ✅ Complete

### Key decisions
- Phase 6 (mobile refinement) → stretch only
- Phases 9/10/11 (RAG, help system) → scoped out; document as future work in Ch6
- Evaluation required: mathematical model comparison, no human subjects
- CF evaluation needed: use held-out sessions, report RMSE + precision@k + coverage
- RAG design to appear in Ch3 with literature; implementation goes to Ch6 future work

### Action items (carried to Meeting 4 where unresolved)
- [x] Phase 5 comparison UI — complete
- [ ] CF evaluation subsection in Ch5
- [ ] Ch5 model evaluation section (parametric vs alternative)
- [ ] Ch5 limitation: manual weight-setting, absent ground truth
- [ ] Ch3 RAG design section with literature

---

## Meeting 2 — (prior)

No detailed log recorded.

---

## Meeting 1 — (prior)

No detailed log recorded.
