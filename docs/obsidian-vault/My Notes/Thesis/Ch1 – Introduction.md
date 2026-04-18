# Ch1 – Introduction

Thesis chapter covering the problem statement, proposed solution, aims and objectives, risks, and project approach.

Related: [[Thesis Overview]], [[Report Sync]], [[Project Overview]], [[Known Issues]]

**Source file:** `main sections/introduction.tex`
**Status:** Draft — mostly accurate framing, but future-tense language throughout

> **Sync note (2026-04-18):** "Current contents" below reflects the thesis state *before* the Phase 6 tex-skeleton additions (2026-04-12). For the current tex subsection tree and the active writing backlog, see [[Rewrite Queue#Phase 6 additions (2026-04-12)]] and the toolkit's Status panel §6 Source reconciliation.

---

## Current contents

### 1.1 Problem (accurate)

Three limitations of current lab support:

1. **Shy students** — hesitant to ask for help in lab environments
2. **Prioritisation** — harder to identify who is struggling most
3. **Passive lab assistants** — may walk around without actively helping; need directed tasks

Core argument: in large modules (40+ students), real-time pattern detection (repeated failures, long time on questions, hardest questions) would enable more efficient support.

### 1.2 Proposed Solution (future-facing)

Proposes a real-time learning analytics dashboard that:
- Complements human support with LLM-based identification of struggling students and complex questions
- Uses mathematical/statistical modelling for struggle and difficulty metrics
- Extends to mobile phones, smartwatches, and smart glasses for assistant notifications

### 1.3 Aims and Objectives (accurate content, future-facing language)

**Primary aim:** Enable lab teachers/assistants to make real-time, informed decisions during lab sessions.
**Secondary aim:** Extend to smart devices.

**7 Objectives:**

| # | Objective | Implementation status |
|---|-----------|----------------------|
| 1 | Identify relevant literature and existing systems | Done — Ch2 literature review |
| 2 | Formalise system requirements (FR/NFR) | Done — Ch2 requirements |
| 3 | Design data model for meaningful metrics | Done — data pipeline in `data_loader.py` |
| 4 | Design system architecture for live ingestion | Done — 3-layer architecture |
| 5 | Develop struggle and difficulty models | Done — 7-signal struggle, 5-signal difficulty, IRT, BKT, improved struggle |
| 6 | Implement live data analytics dashboard | Done — full V2 dashboard with 6 views |
| 7 | Evaluate approach (functional + non-functional) | Not done — Ch5 is empty |

### 1.4 Risks and Mitigation (needs update)

| Risk | Impact (thesis) | Mitigation (thesis) | Actual V2 status |
|------|----------------|--------------------|--------------------|
| Latency in real-time processing | Delays reduce usefulness | Lightweight analytics, incremental updates | 10-sec cache TTL, polling-based refresh — latency is low in practice |
| Unstable estimates from insufficient data | Incorrectly identifying struggling students | Baseline for suitable data or LLM identification | Bayesian shrinkage (k=5) pulls low-data students toward mean; measurement confidence module exists |
| Overly complicated dashboard | Distracting and unintuitive | Seek constant feedback on UI | Sci-fi neon theme, leaderboard-first design, sound effects — needs verification |
| Unable to implement smart glasses | Technical constraints | Explore smartwatch or simplify | Not implemented at all — should be honest about this |
| Limited module generalisability | Model works for one module but not others | Design over generic interaction patterns | Generic by design — uses submission/time/incorrectness patterns, not module-specific features |

### 1.5 Project Approach (future-facing)

Describes agile incremental approach. Written entirely in future tense. The approach described is what was actually followed, but the language needs updating to past tense for a final dissertation.

---

## Rewrite items

- [ ] Convert future tense to past/present tense throughout (especially 1.2, 1.3, 1.5)
- [ ] Update risk mitigations in Table 1 to describe actual decisions made (e.g., Bayesian shrinkage for insufficient data, not "use an LLM to identify")
- [ ] Be honest about smart device integration — acknowledge it was scoped out, not just "technical constraints"
- [ ] Consider whether Objective 7 framing needs to acknowledge evaluation is pending

## Open questions

- Should the introduction be rewritten to describe the project as completed, or is future-tense acceptable for a dissertation introduction?
- The "lazy lab assistants" framing (point 3) — is this appropriate for a final submission, or should it be softened?
