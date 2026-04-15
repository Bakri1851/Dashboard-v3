# Meeting Log

Supervisor: Dr. Batmaz
Frequency: Wednesdays 1pm
Location: University office

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
