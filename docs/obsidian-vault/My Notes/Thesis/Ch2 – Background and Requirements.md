# Ch2 – Background and Requirements

Thesis chapter covering the literature review, existing system analysis, and formal requirements specification.

Related: [[Thesis Overview]], [[Report Sync]], [[Student Struggle Logic]], [[Question Difficulty Logic]], [[IRT Difficulty Logic]], [[BKT Mastery Logic]]

**Source file:** `main sections/requirements specification.tex`
**Status:** Draft — literature review solid, requirements need implementation mapping, research gaps placeholder

> **Sync note (2026-04-18):** "Current contents" below reflects the thesis state *before* the Phase 6 tex-skeleton additions (2026-04-12). For the current tex subsection tree and the active writing backlog, see [[Rewrite Queue#Phase 6 additions (2026-04-12)]] and the toolkit's Status panel §6 Source reconciliation.

---

## Current contents

### 2.1 Literature Review

#### 2.1.1 Learning Analytics in Higher Education (accurate)
- LA defined as measurement/collection/analysis/reporting of learner data
- Data sources: MOOCs, clickstream, course content
- Outputs: personalisation, feedback, curriculum design
- Limitations: focuses on observable behaviours not cognition; privacy concerns
- Gap identified: no approach leveraging smart devices in computer labs

#### 2.1.2 Dashboards for Learning Analytics (accurate)
- **SAM** — early dashboard; separates students doing well from at-risk based on time/resource use
- **EMODA** — emotion-aware dashboard using audio/video/self-reports
- **Edsight** — responsive web design; filters by date/classroom; supports multiple device types
- Gap: most dashboards are course-level, not session-level

#### 2.1.3 Real-Time Data Analytics and Visualisation (accurate)
- Netflix, Walmart, Amazon examples of real-time analytics value
- Education example: attention-level detection from sensory data
- Argument: real-time analytics in labs better than post-session review

#### 2.1.4 Modelling Student Struggle (accurate, good foundation)
- [[dong_using|Dong et al.]] — session-level struggle detection (77% accuracy vs expert judgement)
- [[or_2024_exploring|Or]] — novice programmer testing behaviour; 4+ consecutive failures as threshold
- [[estey_2017_automatically|Estey et al.]] — trajectory metric over 4 semesters; reduced false-positive rate to 11%
- [[piech_modeling|Piech et al.]] — graphical model of student progression paths
- BKT: [[khajah_supercharging|Khajah]] shows BKT can be strengthened with IRT-like structure
- [[kim_knowledge|Kim et al.]] — knowledge tracing with student questions and auto-extracted skills
- LLMs: [[koutcheme_using|Koutcheme]] (repair quality correlates with explanation quality), [[pitts_a|Pitts]] (LLMs best with human oversight)
- Conclusion: struggle best captured through temporal + correctness + behavioural signals

#### 2.1.5 Modelling Task Difficulty (accurate)
- [[dannath_evaluating|Dannath et al.]] — task-level struggle in ITS; separation from student ability important
- IRT: [[frederikbaucks_2024_gaining|Baucks et al.]] — latent variable models uncover hidden difficulty patterns
- [[pankiewicz_measuring|Pankiewicz]] — multi-attempt environments complicate difficulty measurement
- Conclusion: difficulty should combine correctness, time, attempts, and progression

#### 2.1.6 Collaborative Filtering (accurate)
- k-NN based approach using cosine similarity over student profiles
- Effective in sparse datasets with implicit signals
- Limitation: cold start with limited interaction history
- Conclusion: strong alternative to parametric scoring, but constrained by session start data sparsity

#### 2.1.7 Summary of Identified Research Gaps — `[FILL IN]` PLACEHOLDER
- A commented-out draft exists below the placeholder (lines 121-130) covering:
  - No smart device leveraging in computer labs
  - No AI-based metric classification
  - Course-level focus rather than session-level
  - CF not applied to real-time lab struggle detection
- **Action:** Review the commented draft, update it, and uncomment

### 2.2 Existing Systems

#### 2.2.1 Learning Management Systems (accurate)
- Moodle as example; analytics typically post-session; not optimised for in-lab support

#### 2.2.2 Instructor Facing Dashboards (accurate)
- Blocks: Progress Bar — student progress, not struggle
- Piwik Analytics — general analytics dashboard
- MM Dashboard — multi-modal (eye trackers, wristbands, cameras); main issue is teacher unfamiliarity with measurements
- Gap: existing dashboards unintuitive, metrics hard to interpret

#### 2.2.3 Early Warning and At-Risk Student Systems (accurate)
- edInsight EWS — course-level grade-based scoring
- Not suitable for live lab sessions but provides framework for approach

### 2.3 Requirements Specification

#### FR1-FR7 and NFR1-NFR6

| Req | Description | MoSCoW | Implementation Status |
|-----|-------------|--------|----------------------|
| FR1 | Live ingestion of lab data | Must | IMPLEMENTED — `data_loader.py` fetches from PHP endpoint with 10s cache |
| FR2 | Computation of student struggle | Must | IMPLEMENTED — 7-signal model in `analytics.py` + improved model in `models/improved_struggle.py` |
| FR3 | Computation of question difficulty | Must | IMPLEMENTED — 5-signal model in `analytics.py` + IRT in `models/irt.py` |
| FR4 | Real-time prioritisation | Must | IMPLEMENTED — leaderboards ranked by score, color-coded thresholds |
| FR5 | Present relevant analytics | Should | IMPLEMENTED — 6 instructor views, 4 assistant views, data analysis charts |
| FR6 | Smart device integration | Should | NOT IMPLEMENTED — mobile-responsive assistant app exists but no push notifications, no watch/glasses |
| FR7 | Lab assistant ranking system | Could | PARTIAL — assistant leaderboard concept exists in lab assistant system (helped count) but no student satisfaction metric |
| NFR1 | Real-time performance | Must | IMPLEMENTED — 10s cache TTL, configurable refresh (5-300s) |
| NFR2 | Interpretability | Must | IMPLEMENTED — color-coded thresholds, leaderboard-first design, no specialist knowledge needed |
| NFR3 | Robustness to noisy data | Should | IMPLEMENTED — Bayesian shrinkage, min-max normalization handles edge cases, empty feedback defaults |
| NFR4 | Scalability | Should | PARTIAL — works for lab-sized cohorts; no load testing done |
| NFR5 | Privacy and ethical | Must | IMPLEMENTED — read-only API, no PII stored, data used only for analytics |
| NFR6 | Extensibility | Should | IMPLEMENTED — modular package structure, model toggle system, config-driven thresholds |

#### MoSCoW Table (from thesis)

| Must Have | Should Have | Could Have | Won't Have |
|-----------|------------|------------|------------|
| FR1, FR2, FR3, FR4 | FR5, FR6 | FR7 | Long-term outcomes |
| NFR1, NFR2, NFR5 | NFR3, NFR4, NFR6 | | Fully AI decision-making |
| | | | Avatar-based AI assistance |

---

## Rewrite items

- [ ] Uncomment and finalise research gaps subsection (2.1.7) — draft exists, needs review
- [ ] Add implementation status column to requirements (as shown above) or discuss in Ch5 evaluation
- [ ] Consider whether FR6 should be moved to "Won't Have" or discussed as future work
- [ ] FR7 needs clearer definition — does the current helped-count leaderboard satisfy it?
- [ ] Literature review is mostly version-independent and likely needs minimal changes

## Open questions

- Should the requirements section include implementation status, or should that mapping live only in Ch5 (evaluation)?
- The commented-out research gaps draft — is it still accurate given V2 implementation?
