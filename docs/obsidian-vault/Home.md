# Home

This vault explains Dashboard-v3 as a working system: how data enters, how scores are computed, how the instructor and assistant apps behave, and where the main risks sit. It is meant to be quick to navigate during development, debugging, or thesis write-up.

Related: [[Project Overview]], [[Architecture]], [[Setup and Runbook]], [[Glossary]]

## Start here

- Read [[Project Overview]] for purpose, users, and runtime modes.
- Read [[Architecture]] and [[Data Pipeline]] to understand control flow and data ownership.
- Read [[Dashboard Pages and UI Flow]] to follow the instructor and assistant journeys.
- Read [[Student Struggle Logic]] and [[Question Difficulty Logic]] to understand the scoring model behind the UI.
- Read [[Known Issues]] before changing analytics, caching, or assistant behavior.

## Vault map

### Overview

- [[Project Overview]]
- [[Architecture]]
- [[Data Pipeline]]

### Modules

- [[App Entrypoints and Packaging]]
- [[Configuration and Runtime Paths]]
- [[Data Loading and Session Persistence]]
- [[Analytics Engine]]
- [[Instructor Dashboard]]
- [[Lab Assistant System]]
- [[UI System]]

### Flows and logic

- [[Dashboard Pages and UI Flow]]
- [[Student Struggle Logic]]
- [[Question Difficulty Logic]]
- [[IRT Difficulty Logic]]

### Operations and reference

- [[Setup and Runbook]]
- [[Known Issues]]
- [[Next Steps]]
- [[Glossary]]
- [[Academic Period Converter]]

## Code references

- `app.py` and `lab_app.py` are the stable launch points.
- `learning_dashboard/instructor_app.py` and `learning_dashboard/assistant_app.py` contain the two Streamlit apps.
- `learning_dashboard/data_loader.py`, `learning_dashboard/analytics.py`, and `learning_dashboard/lab_state.py` hold the main non-UI logic.
- `data/saved_sessions.json` and `data/lab_session.json` are the local runtime stores.
