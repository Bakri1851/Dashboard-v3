# Ch6 – Conclusion

Thesis chapter for summary and future work. Currently completely empty.

Related: [[Thesis Overview]], [[Report Sync]], [[Ch1 – Introduction]], [[Ch5 – Results and Evaluation]]

**Source file:** `main sections/conclusion.tex`
**Status:** Empty (CRITICAL) — 2 subsection headers, no content

---

## Current contents

```latex
\section{Conclusion}
\subsection{Summary}
\subsection{Future Work}
```

No content exists.

---

## What could go in each section

### 6.1 Summary

Should tie back to the 7 objectives from Ch1:

| # | Objective | Outcome |
|---|-----------|---------|
| 1 | Identify relevant literature | Completed — Ch2 reviews LA, dashboards, struggle/difficulty modelling, CF, LLMs |
| 2 | Formalise requirements | Completed — 7 FR, 6 NFR, MoSCoW prioritisation |
| 3 | Design data model | Completed — session-based endpoint parsing, derived metrics |
| 4 | Design system architecture | Completed — 3-layer architecture, modular package structure |
| 5 | Develop struggle/difficulty models | Completed — baseline + IRT + BKT + improved struggle + CF + mistake clustering |
| 6 | Implement dashboard | Completed — full V2 with 6 instructor views, 4 assistant views, lab session management |
| 7 | Evaluate approach | Depends on Ch5 — needs writing |

Key contributions to highlight:
- Real-time session-level monitoring (novel application — gap identified in literature)
- Multi-signal struggle/difficulty models going beyond single-metric thresholds
- LLM-enhanced incorrectness scoring (OpenAI for nuanced answer assessment)
- Practical lab assistant coordination system
- Configurable model comparison (baseline vs improved, toggle in UI)

### 6.2 Future Work

Candidates from unimplemented/incomplete features:

**Unimplemented requirements:**
- FR6: Smart device integration (push notifications to phones/watches/glasses)
- FR7: Full assistant ranking with student satisfaction metric

**Computed but not displayed:**
- BKT mastery visualization — mastery data is computed per-student per-question but never shown in UI
- Measurement confidence display — confidence scores exist but no UI renders them

**Infrastructure gaps:**
- Event-driven architecture — still interval-based polling; could use WebSockets or SSE
- Temporal smoothing — designed (exponential smoothing) but stub only; `SMOOTHING_ENABLED = False`
- Automated test suite — no tests exist
- Export/reporting — no CSV/PDF export capability

**Evaluation gaps:**
- User studies in real classroom settings
- Longitudinal evaluation across multiple lab sessions
- Comparison with existing systems (SAM, EMODA)
- Statistical validation of model effectiveness

**Extensions:**
- Predictive alerts (forward-looking risk prediction)
- Network/social analysis beyond CF's k-NN
- Integration with institutional LMS (e.g., Moodle)

---

## Rewrite items

- [ ] Write summary tying back to objectives and contributions
- [ ] Write future work section — distinguish clearly between "not implemented" and "could be extended"
- [ ] Ensure future work items are honest about what was scoped out vs what would be genuinely novel

## Open questions

- Should the conclusion acknowledge V1→V2 evolution or just present V2 as the final deliverable?
- How much should the summary reference evaluation results (which don't exist yet)?
