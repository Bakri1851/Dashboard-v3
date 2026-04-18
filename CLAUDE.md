# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Streamlit-based learning analytics dashboard for monitoring student struggle and question difficulty during university lab sessions. Two cooperating apps share live state through a file-locked JSON file on disk.

## Commands

Run all commands from the repo root (`Dashboard v3/`).

```bash
# Install dependencies
pip install -r code/requirements.txt

# Run instructor dashboard (port 8501)
python -m streamlit run code/app.py

# Run mobile lab assistant app (port 8502)
streamlit run code/lab_app.py --server.port 8502

# Syntax check all source files
python -m py_compile code/app.py code/lab_app.py code/learning_dashboard/*.py code/learning_dashboard/ui/*.py
```

There are no automated tests. Validation is manual smoke testing (see README.md checklist).

## Architecture

### Two-app system
- `code/app.py` and `code/lab_app.py` are thin wrappers delegating to `code/learning_dashboard/instructor_app.py` and `code/learning_dashboard/assistant_app.py`
- Both share state via `data/lab_session.json`, managed through `code/learning_dashboard/lab_state.py` with `filelock`

### Package layout (`code/learning_dashboard/`)
- `config.py` — all tunable constants (weights, thresholds, colors, API config). Start here for parameter changes.
- `data_loader.py` — API fetch, JSON/XML parsing, normalization, saved-session persistence. API returns newline-delimited JSON where each record has an `xml` field containing embedded XML for submission details.
- `analytics.py` — scoring engine: incorrectness (OpenAI), student struggle, question difficulty, collaborative filtering, mistake clustering
- `models/` — alternative/improved models: IRT difficulty (`irt.py`), BKT mastery (`bkt.py`), improved struggle (`improved_struggle.py`), measurement confidence (`measurement.py`). Toggled via `improved_models_enabled` in Settings.
- `lab_state.py` — file-locked shared lab-session state (no Streamlit imports)
- `paths.py` — project/runtime paths and legacy-file migration
- `academic_calendar.py` — maps calendar dates to Loughborough 2025/26 academic week labels (used in data analysis view)
- `sound.py` — sci-fi sound effects via Web Audio API injected through `st.components.v1.html()` zero-height iframes
- `ui/views.py` — page-level views (in_class, student_detail, question_detail, data_analysis, settings, previous_sessions)
- `ui/components.py` — reusable Streamlit UI building blocks
- `ui/theme.py` — CSS and Plotly theme defaults (sci-fi neon dark theme)

### Key data flow
1. `instructor_app.main()` initializes session state and applies deferred actions (before widgets)
2. `data_loader.load_data()` fetches from API with `@st.cache_data(ttl=10)`, parses, normalizes
3. Sidebar filters applied in order: manual time → live session start → saved session window
4. Routing sends filtered DataFrame to the appropriate view

The lab assistant app has its own independent `@st.cache_data(ttl=10)` cache on `_load_student_data()` — it does not share the instructor app's cache. Both caches are process-local, so running both apps means two separate fetch cycles.

### Deferred actions pattern
Streamlit cannot mutate `st.session_state` after widget instantiation in the same run. This repo uses `pending_*` flags (e.g., `pending_session_load_record`, `pending_return_to_live_data`) applied at the top of `main()` before sidebar widgets render.

## Important Conventions

- Thresholds are `list[tuple[float, float, str, str]]` — (low, high, label, color) for dynamic classification
- Scoring uses min-max normalization that returns 0 when min==max
- Substring matching: "correct" intentionally matches inside "incorrect" (by design)
- `_incorrectness_cache` in analytics.py avoids repeat OpenAI calls within a process
- Session code is 6-char alphanumeric excluding O/0/I/1 to avoid confusion
- Lab assistant identity persisted via URL `?aid=` query param
- OpenAI API key stored in `.streamlit/secrets.toml`
- Runtime data lives in `data/` (auto-migrated from repo root on first run)

## Context Navigation

1. ALWAYS query the knowledge graph first
2. Only read raw files if I explicitly say so
3. Use graphify-out/wiki/index.md

## Obsidian Vault

Keep updated with code and report changes, male new notes if needed, this is the user's knowledge base

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- After modifying code files in this session, run `python3 -c "from graphify.watch import _rebuild_code; from pathlib import Path; _rebuild_code(Path('.'))"` to keep the graph current

## HTML Recap Toolkit

`docs/recap_toolkit/dashboard_v3_toolkit.html` is the canonical unified reference. It mirrors the code, the thesis, AND the vault — it is the primary intuitive navigation surface, more flexible than the Obsidian vault for exploring how methods work.

Panels (10 tabs):

- **Overview** — what the system does, who uses it, architecture
- **Code reference** — searchable function list
- **Glossary** — project + math terms, tagged
- **Literature** — bibtex keys + grouping, mirrors `Literature/index.md`; ⚠ flags citations still needed
- **Operations** — install / run / smoke test / troubleshooting (mirrors `Setup and Runbook.md`)
- **Status** — implementation status + evidence gaps + report-alignment + figure audit (mirrors `Evidence Bank.md`, `Report Sync.md`, `Figures and Tables.md`)
- **Deep dive** — per-method walkthroughs with citation footers
- **Roadmap** — CODE-LEARNING stages 1–6 ending with Stage 6 defence-prep Q&A. Distinct from Plan.
- **Plan** — SUBMISSION roadmap (14 steps, mirrors `Full Roadmap.md`) + 6-week schedule (mirrors `Weekly Plan.md`). Distinct from Roadmap.
- **Report guide** — per-chapter writing guide

Keep it in sync after any of the following:

- **Code change** — method names, default parameter values in `config.py`, new signals/models, removed features.
- **Thesis change** — new Ch2 citations, Ch3 design decisions, Ch4 implementation details, Appendix E/F formulae, Ch5 evaluation framing.
- **Literature change** — new bibtex entry, new grouping in `docs/obsidian-vault/My Notes/Literature/index.md`.
- **Vault change** — updates to `Setup and Runbook.md`, `Evidence Bank.md`, `Report Sync.md`, `Figures and Tables.md`, `Full Roadmap.md`, or `Weekly Plan.md` — the toolkit mirrors these; update the corresponding panel.

Every deep-dive carries a citation footer: `Cite: [bibkeys] · Thesis: [section, appendix] · Code: [file:lines]`. Every glossary formula has a 1:1 mapping to an Appendix E entry. When a method lacks a citation, the toolkit is the first place to flag it (Literature panel shows "citation needed").

The Obsidian vault remains the long-form writing workspace; the toolkit is the reference surface. Update both, but prioritise toolkit freshness.
