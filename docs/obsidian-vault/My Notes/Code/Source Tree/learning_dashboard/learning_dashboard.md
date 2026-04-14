# learning_dashboard/

**Path:** `code/learning_dashboard/`
**Parent:** [[code]]

> The core Python package. Contains every piece of shared logic between the instructor dashboard and the lab assistant app.

## Contents

| Path | Kind | Summary |
|------|------|---------|
| [[__init__]] | file | Package marker. |
| [[config]] | file | All tunable constants — weights, thresholds, API settings, feature flags. |
| [[paths]] | file | Runtime paths + legacy-file migration. |
| [[academic_calendar]] | file | Loughborough 2025/26 calendar → period labels. |
| [[data_loader]] | file | API fetch, JSON/XML parsing, cleaning, filters, saved-session persistence. |
| [[analytics]] | file | Scoring engine — incorrectness, struggle, difficulty, CF, mistake clusters. |
| [[rag]] | file | Two-layer RAG pipeline for lab-assistant coaching suggestions. |
| [[lab_state]] | file | File-locked JSON state shared across apps. |
| [[sound]] | file | Sci-fi SFX via Web Audio API. |
| [[instructor_app]] | file | Instructor dashboard entrypoint (`main()`). |
| [[assistant_app]] | file | Assistant mobile app entrypoint (`main()`). |
| [[ui]] | folder | Streamlit presentation layer — components, views, theme. |
| [[models]] | folder | Advanced scoring models — IRT, BKT, confidence, improved struggle. |

## Purpose

Structured to isolate concerns along three axes:

1. **Headless vs UI.** `data_loader`, `analytics`, `lab_state`, `models/*`, `config`, `paths`, `academic_calendar` are UI-independent — no Streamlit import (`lab_state` deliberately has no `streamlit` import so it can be used safely from both apps). The `ui/` package and the two `*_app.py` files own all Streamlit interaction.
2. **Shared vs app-specific.** Files used by both apps (`config`, `data_loader`, `lab_state`, `sound`, `ui/theme`) sit at the package root. The `instructor_app` and `assistant_app` modules are the only app-specific ones.
3. **Baseline vs advanced models.** Baseline scoring lives in [[analytics]]; the improved models (IRT, BKT, measurement confidence, difficulty-adjusted struggle) live in [[models]] and are gated by `improved_models_enabled` in Settings.

## Related notes

- [[Architecture]] · [[Data Pipeline]] · [[Analytics Engine]]
- [[Lab Assistant System]]
