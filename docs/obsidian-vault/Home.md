# Home

This vault documents Dashboard-v3 as both a working system and a thesis support tool. The Code sections cover how data enters, how scores are computed, and how the apps behave. The Thesis section tracks the dissertation chapter by chapter, flags mismatches between the report and the implementation, and maintains a rewrite queue for final submission.

Related: [[Project Overview]], [[Architecture]], [[Setup and Runbook]], [[Glossary]]

## Start here

- Read [[Project Overview]] for purpose, users, and runtime modes.
- Read [[Architecture]] and [[Data Pipeline]] to understand control flow and data ownership.
- Read [[Lab App/Flows/Pages and UI Flow]] and [[Assistant App/Flows/UI Flow]] to follow the instructor and assistant journeys.
- Read [[Student Struggle Logic]] and [[Question Difficulty Logic]] to understand the scoring model behind the UI.
- Read [[Known Issues]] before changing analytics, caching, or assistant behavior.
- Read [[Report Sync]] before revising the dissertation — it tracks mismatches between the thesis and the code.

## Vault map

### Code — Overview

- [[Project Overview]]
- [[Architecture]]
- [[Data Pipeline]]

### Code — Modules

- [[Lab App/Modules/App Entrypoint]] / [[Assistant App/Modules/App Entrypoint]]
- [[Configuration and Runtime Paths]]
- [[Data Loading and Session Persistence]]
- [[Analytics Engine]]
- [[Instructor Dashboard]]
- [[Lab Assistant System]]
- [[UI System]]

### Code — Flows and logic

- [[Lab App/Flows/Pages and UI Flow]] / [[Assistant App/Flows/UI Flow]]
- [[Lab App/Flows/Student Detail]] / [[Lab App/Flows/Question Detail]]
- [[Lab App/Flows/Live Assistant Assignment]] / [[Lab App/Flows/Saved Session History]]
- [[Student Struggle Logic]]
- [[Question Difficulty Logic]]
- [[IRT Difficulty Logic]]
- [[BKT Mastery Logic]]

### Code — Operations and reference

- [[Setup and Runbook]]
- [[Known Issues]]
- [[Next Steps]]
- [[Coding Roadmap]]
- [[Glossary]]
- [[Academic Period Converter]]

### Literature

- [[Literature/index|Literature Index]]

### Thesis

- [[Thesis Overview]]
- [[Full Roadmap]]
- [[Report Sync]]
- [[Rewrite Queue]]
- [[Evidence Bank]]
- [[Figures and Tables]]
- [[Ch1 – Introduction]]
- [[Ch2 – Background and Requirements]]
- [[Ch3 – Design and Modelling]]
- [[Ch4 – Implementation]]
- [[Ch5 – Results and Evaluation]]
- [[Ch6 – Conclusion]]

## Code references

- `code/app.py` and `code/lab_app.py` are the stable launch points.
- `code/learning_dashboard/instructor_app.py` and `code/learning_dashboard/assistant_app.py` contain the two Streamlit apps.
- `code/learning_dashboard/data_loader.py`, `code/learning_dashboard/analytics.py`, and `code/learning_dashboard/lab_state.py` hold the main non-UI logic.
- `data/saved_sessions.json` and `data/lab_session.json` are the local runtime stores.
