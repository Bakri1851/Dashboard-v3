# Lab App

Instructor dashboard running on port 8501 (`code/app.py` → `instructor_app.main()`). Displays student struggle and question difficulty leaderboards, 6 analytics views, and a live lab session panel.

---

## Notes index

| Note | Folder | Summary |
|------|--------|---------|
| [[Pages and UI Flow]] | Flows | Page list, routing transitions, sound triggers for the instructor app |
| [[Student Detail]] | Flows | Student drill-down page: baseline struggle score, descriptive charts, and CF cosine-similarity context |
| [[Question Detail]] | Flows | Question drill-down page: weighted difficulty, confidence heuristic, and TF-IDF/K-means mistake clustering |
| [[Live Assistant Assignment]] | Flows | Instructor sidebar flow for assigning, releasing, and removing assistants during live sessions |
| [[Saved Session History]] | Flows | Save/load/delete behavior for live and retroactive session records |
| [[Analytics Engine]] | Modules | Scoring engine: incorrectness, struggle, difficulty, CF, mistake clustering |
| [[App Entrypoint]] | Modules | `app.py` → `instructor_app.main()`; package layout; why the two-app split exists |
| [[Configuration and Runtime Paths]] | Modules | `config.py` weights/thresholds/colors; `paths.py` runtime file locations |
| [[Data Loading and Session Persistence]] | Modules | `data_loader.py`: API fetch, parse, normalise, saved sessions, filters |
| [[Instructor Dashboard]] | Modules | Session state categories, filter precedence, routing, live-session panel |
| [[UI System]] | Modules | `views.py`, `components.py`, `theme.py` (get_main_css), Plotly defaults, interaction patterns |
| [[BKT Mastery Logic]] | Logic | BKT HMM model: 4 parameters, forward algorithm, mastery output table |
| [[IRT Difficulty Logic]] | Logic | Rasch 1PL via joint MLE, sigmoid mapping, min-max normalisation |
| [[Improved Struggle Logic]] | Logic | 3-component improved model: behavioral (0.45) + mastery gap (0.30) + difficulty-adjusted (0.25) |
| [[Question Difficulty Logic]] | Logic | 5-component difficulty formula with weights; mistake clustering integration |
| [[Student Struggle Logic]] | Logic | 7-component struggle formula with Bayesian shrinkage and score clipping |
| [[Coding Roadmap]] | Operations | Phase status table (0–7), recommended execution order, verification checklist |
| [[Evaluation Strategy]] | Operations | Meeting 3 placeholder: model comparison approach, Option A/B, weight optimisation future work |
| [[Known Issues]] | Operations | 4 active known issues (CF diagnostic, analytics cache, cluster cache, sound miswiring) + resolved BKT/IRT |
| [[Next Steps]] | Operations | Phases 0a–0c, 1–5, 7; conceptual additions; documentation follow-up; code refs |
| [[Setup and Runbook]] | Operations | Prerequisites, install, run commands, smoke test checklist, troubleshooting |

---

Part of [[Code Index]] · see also [[Assistant App]]
