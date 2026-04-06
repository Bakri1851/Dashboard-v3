# Project Overview

Dashboard-v3 is a Streamlit-based learning analytics dashboard for monitoring student struggle, question difficulty, and live lab support during teaching sessions. It combines remote submission data, OpenAI-derived incorrectness scoring, local aggregation logic, and a second mobile-facing assistant workflow.

Related: [[Architecture]], [[Data Pipeline]], [[Dashboard Pages and UI Flow]], [[Student Struggle Logic]], [[Setup and Runbook]]

## What the project does

- Surfaces struggling students through a ranked leaderboard and drill-down view.
- Surfaces difficult questions through a ranked leaderboard and drill-down view.
- Supports live lab sessions that can be started, ended, and saved locally.
- Lets instructors coordinate human lab assistants through a separate mobile-friendly app.
- Preserves saved sessions so historic lab windows can be reloaded later.

## Main actors

- Instructor: runs the main dashboard, manages live sessions, reviews scores, assigns assistants.
- Lab assistant: joins a session by code, waits for assignment or self-claims students, marks students as helped.
- Student: does not use the dashboard directly, but generates the submission and feedback data that drives it.
- Upstream backend/API: supplies submission payloads in JSON or XML form.

## Runtime modes

- Instructor dashboard: launched from `app.py`, usually on port `8501`.
- Lab assistant portal: launched from `lab_app.py`, usually on port `8502`.
- Live session mode: filters data from the instructor's session start time forward and writes assistant state to disk.
- Saved session mode: replays a stored start/end window from `data/saved_sessions.json`.

## Repo shape

- Thin root wrappers: `app.py`, `lab_app.py`.
- Package code: `learning_dashboard/`.
- Runtime JSON state: `data/`.
- Static assets directory: `static/` exists but is not a major behavior driver in the current codebase.

## Academic context

This project is the subject of a Master's thesis: "Online Dashboard For Lab Assistants To Better Support Students in Labs" (Loughborough University, 25COD290). See [[Thesis Overview]] for the full dissertation structure and [[Ch1 – Introduction]] for the problem statement and objectives.

The thesis was initially written against a V1 prototype. The current codebase (Dashboard v3) is the V2 full system, significantly more capable than what the thesis implementation chapter describes. See [[Report Sync]] for a detailed mismatch analysis.

Formal requirements (FR1-FR7, NFR1-NFR6) and their implementation status are tracked in [[Ch2 – Background and Requirements]].

## Code references

- `app.py`
- `lab_app.py`
- `learning_dashboard/instructor_app.py`
- `learning_dashboard/assistant_app.py`
- `requirements.txt`
- `data/saved_sessions.json`
- `data/lab_session.json`
