---
type: community
cohesion: 0.10
members: 44
---

# Project Architecture & Modules

**Cohesion:** 0.10 - loosely connected
**Members:** 44 nodes

## Members
- [[Academic Calendar Module]] - concept - docs/obsidian-vault/Code/Reference/Academic Period Converter.md
- [[Academic Period Converter]] - document - docs/obsidian-vault/Code/Reference/Academic Period Converter.md
- [[Analytics Engine]] - document - docs/obsidian-vault/Code/Lab App/Modules/Analytics Engine.md
- [[Architecture]] - document - docs/obsidian-vault/Code/Overview/Architecture.md
- [[BKT Mastery Logic]] - document - docs/obsidian-vault/Code/Lab App/Logic/BKT Mastery Logic.md
- [[Baseline Question Difficulty Model]] - concept - docs/obsidian-vault/Code/Lab App/Logic/Question Difficulty Logic.md
- [[Baseline Student Struggle Model]] - concept - docs/obsidian-vault/Code/Lab App/Logic/Student Struggle Logic.md
- [[Bayesian Knowledge Tracing (BKT) Algorithm]] - concept - docs/obsidian-vault/Code/Lab App/Logic/BKT Mastery Logic.md
- [[Bayesian Shrinkage for Low-Volume Students]] - concept - docs/obsidian-vault/Code/Lab App/Logic/Student Struggle Logic.md
- [[Behavioral Composite Signal]] - concept - docs/obsidian-vault/Code/Lab App/Logic/Improved Struggle Logic.md
- [[Coding Roadmap]] - document - docs/obsidian-vault/Code/Lab App/Operations/Coding Roadmap.md
- [[Collaborative Filtering (CF) Diagnostic]] - concept - docs/obsidian-vault/Code/Lab App/Logic/Student Struggle Logic.md
- [[Configuration and Runtime Paths]] - document - docs/obsidian-vault/Code/Lab App/Modules/Configuration and Runtime Paths.md
- [[Data Loading and Session Persistence]] - document - docs/obsidian-vault/Code/Lab App/Modules/Data Loading and Session Persistence.md
- [[Data Pipeline]] - document - docs/obsidian-vault/Code/Overview/Data Pipeline.md
- [[Deferred Actions Pattern]] - concept - docs/obsidian-vault/Code/Lab App/Modules/Instructor Dashboard.md
- [[Difficulty-Adjusted Incorrectness Signal]] - concept - docs/obsidian-vault/Code/Lab App/Logic/Improved Struggle Logic.md
- [[Evaluation Strategy]] - document - docs/obsidian-vault/Code/Lab App/Operations/Evaluation Strategy.md
- [[Filter Precedence Rules]] - concept - docs/obsidian-vault/Code/Overview/Data Pipeline.md
- [[IRT Difficulty Logic]] - document - docs/obsidian-vault/Code/Lab App/Logic/IRT Difficulty Logic.md
- [[IRT Output Min-Max Normalization]] - concept - docs/obsidian-vault/Code/Lab App/Logic/IRT Difficulty Logic.md
- [[IRT Rasch 1PL Model]] - concept - docs/obsidian-vault/Code/Lab App/Logic/IRT Difficulty Logic.md
- [[Improved Struggle Logic]] - document - docs/obsidian-vault/Code/Lab App/Logic/Improved Struggle Logic.md
- [[Improved Struggle Model]] - concept - docs/obsidian-vault/Code/Lab App/Logic/Improved Struggle Logic.md
- [[Instructor Dashboard]] - document - docs/obsidian-vault/Code/Lab App/Modules/Instructor Dashboard.md
- [[Known Issues]] - document - docs/obsidian-vault/Code/Lab App/Operations/Known Issues.md
- [[Lab App Entrypoint]] - document - docs/obsidian-vault/Code/Lab App/Modules/App Entrypoint.md
- [[Mastery Gap Signal]] - concept - docs/obsidian-vault/Code/Lab App/Logic/Improved Struggle Logic.md
- [[Measurement Confidence Metadata]] - concept - docs/obsidian-vault/Code/Lab App/Operations/Next Steps.md
- [[Mistake Clustering (TF-IDF + K-Means)]] - concept - docs/obsidian-vault/Code/Lab App/Logic/Question Difficulty Logic.md
- [[Model Comparison View (Phase 5)]] - concept - docs/obsidian-vault/Code/Lab App/Modules/UI System.md
- [[Next Steps]] - document - docs/obsidian-vault/Code/Lab App/Operations/Next Steps.md
- [[OpenAI-derived Incorrectness Scoring]] - concept - docs/obsidian-vault/Code/Lab App/Modules/Analytics Engine.md
- [[Overview Index]] - document - docs/obsidian-vault/Code/Overview/Overview Index.md
- [[Project Overview]] - document - docs/obsidian-vault/Code/Overview/Project Overview.md
- [[Question Difficulty Logic]] - document - docs/obsidian-vault/Code/Lab App/Logic/Question Difficulty Logic.md
- [[RAG Suggested Feedback (Phase 9)]] - concept - docs/obsidian-vault/Code/Lab App/Operations/Coding Roadmap.md
- [[Setup and Runbook]] - document - docs/obsidian-vault/Code/Lab App/Operations/Setup and Runbook.md
- [[Shared Lab Session JSON State]] - concept - docs/obsidian-vault/Code/Overview/Architecture.md
- [[Struggle Score Thresholds]] - concept - docs/obsidian-vault/Code/Lab App/Logic/Student Struggle Logic.md
- [[Student Detail Flow]] - document - docs/obsidian-vault/Code/Lab App/Flows/Student Detail.md
- [[Student Struggle Logic]] - document - docs/obsidian-vault/Code/Lab App/Logic/Student Struggle Logic.md
- [[UI System]] - document - docs/obsidian-vault/Code/Lab App/Modules/UI System.md
- [[improved_models_enabled Feature Flag]] - concept - docs/obsidian-vault/Code/Lab App/Modules/Analytics Engine.md

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Project_Architecture_&_Modules
SORT file.name ASC
```
