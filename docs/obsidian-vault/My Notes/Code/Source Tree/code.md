# code/

**Path:** `code/`
**Parent:** [[Source Tree Index]]

> The repository's source root. Everything runnable lives here.

## Contents

| Path | Kind | Summary |
|------|------|---------|
| [[app]] | file | Streamlit wrapper for the instructor dashboard. |
| [[lab_app]] | file | Streamlit wrapper for the mobile lab assistant app. |
| [[requirements]] | file | Python dependency pins. |
| [[learning_dashboard]] | folder | Core package — analytics, data, state, UI, models. |

## Purpose

The two top-level scripts are deliberately minimal — each is a one-line import + `main()` call. All real logic lives inside the `learning_dashboard/` package so both apps can share code (`config`, `data_loader`, `lab_state`, the `ui/` theme, etc.).

The two apps are independent Streamlit processes: the instructor dashboard on port 8501 and the lab assistant portal on port 8502. They communicate only through the file-locked JSON file managed by [[lab_state]].

## Related notes

- [[Architecture]] — system-level picture of the two-app design
- [[Setup and Runbook]] — commands to install and run
