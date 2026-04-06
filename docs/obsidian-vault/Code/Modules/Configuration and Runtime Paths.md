# Configuration and Runtime Paths

This project centralizes tunable behavior in `config.py` and centralizes runtime file locations in `paths.py`. Together they define the dashboard's scoring weights, thresholds, UI defaults, runtime file layout, and backward-compatible JSON migration behavior.

Related: [[Architecture]], [[Data Pipeline]], [[Student Struggle Logic]], [[Question Difficulty Logic]], [[Setup and Runbook]]

## What is configurable

- API endpoint, timeout, and cache TTL.
- Excluded and renamed modules during normalization.
- OpenAI model and batch size for incorrectness scoring and cluster labeling.
- Struggle and difficulty weights, thresholds, and correction threshold.
- UI limits such as leaderboard size, histogram bins, and example-answer caps.
- Auto-refresh, sound, and lab session defaults.

## Runtime path rules

- Preferred runtime files live under `data/`.
- Legacy root files are still recognized and copied into `data/` if present.
- `lab_session.lock` follows the effective lab-session file location so both apps lock the same state file.

## Practical implications

- Threshold or weight tuning should happen in `config.py`, not inside analytics formulas.
- Saved-session and lab-state path decisions should go through `paths.py`, not hard-coded literals.
- The repo root `saved_sessions.json` is effectively a legacy artifact once migration has happened.

## Code references

- `learning_dashboard/config.py`
- `learning_dashboard/paths.py`
- `data/saved_sessions.json`
- `data/lab_session.json`
