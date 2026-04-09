# Coding Roadmap

High-level implementation status and remaining work for Dashboard v3. For full feature specifications see [[Next Steps]]. For thesis writing status see [[Writing Roadmap]].

Related: [[Next Steps]], [[Known Issues]], [[Writing Roadmap]], [[Analytics Engine]], [[Lab Assistant System]]

---

## Implementation status

| Phase | Feature | Status | Key files | Effort |
|---|---|---|---|---|
| Baseline | Core instructor dashboard + mobile lab assistant app | Done | `app.py`, `lab_app.py`, `instructor_app.py`, `assistant_app.py` | — |
| 0 | Bug fixes — sounds, analytics cache keys, assistant data scope, name collision on rejoin | Done | `instructor_app.py`, `analytics.py`, `lab_state.py` | Small |
| 1 | AI measurement confidence wrapping — `incorrectness_confidence` + `incorrectness_source` columns | Done | `models/measurement.py`, `config.py` | Small |
| 2 | IRT difficulty — Rasch 1PL model via MLE, logit scale mapped to [0,1] | Done | `models/irt.py`, `config.py` | Medium |
| 3 | BKT mastery tracking — HMM with 4 parameters, per-student per-question | Done | `models/bkt.py`, `config.py` | Medium |
| 4 | Improved struggle model — behavioral (0.45) + mastery gap (0.30) + difficulty-adjusted (0.25) | Done | `models/improved_struggle.py`, `config.py` | Medium |
| 5 | Comparison UI — baseline vs improved, scatter + delta table + agreement summary + settings toggles | **Not started** | `ui/views.py`, `ui/components.py`, `instructor_app.py` | Large |
| 6 | Mobile app refinement — BKT mastery badge, per-question mastery, session timer, helped/struggling counts | **Not started** | `assistant_app.py`, `ui/theme.py` | Medium |
| 7 | Surface computed-but-hidden data — measurement confidence indicators in UI; temporal smoothing decision | Done | `ui/components.py`, `analytics.py`, `config.py` | Small |
| 8 | FR6 smart device notifications — push alert when high-struggle student appears (stretch) | Not started | new file TBD | Large |
| 9 | RAG suggested feedback — ChromaDB + LLM coaching hints surfaced in assistant assigned-student card | **Not started** | `assistant_app.py`, `analytics.py`, `config.py`, `requirements.txt` | Large |
| 10 | In-app Help system (instructor dashboard) — Help section under Settings: Quick Tour, Help Centre (practical use), Model Guide (methodology), contextual tooltips, reliability indicators, troubleshooting | **Not started** | `ui/views.py`, `ui/components.py`, `instructor_app.py` | Large |
| 11 | In-app Help system (assistant app) — lightweight mobile Help panel: join guide, student card explainer, action button guide, RAG suggestion explainer, mobile-friendly design | **Not started** | `assistant_app.py`, `ui/theme.py` | Medium |

---

## Recommended implementation order

Work through this order to minimise rework — each item unblocks the next.

### 1. Phase 5 — Comparison UI `Large`

Unblocks Ch5 evaluation evidence and model comparison screenshots (Appendix B). Full spec in [[Next Steps]] § Phase 5.

- [ ] Add `comparison_view()` to `code/learning_dashboard/ui/views.py`
- [ ] Add `render_comparison_scatter()` to `ui/components.py` — baseline x-axis, improved y-axis, diagonal reference line
- [ ] Add `render_comparison_table()` to `ui/components.py` — sorted by absolute delta, biggest disagreements first
- [ ] Add `render_agreement_summary()` to `ui/components.py` — summary cards: agreement %, level-change counts, top disagreements
- [ ] Add "Model Comparison" option to view routing radio in `instructor_app.py`
- [ ] Add settings sub-panel: `improved_models_enabled` toggle + per-model sub-toggles + BKT parameter sliders (`P_init`, `P_learn`, `P_guess`, `P_slip`)

*Unblocks: Ch5 functional testing, Appendix B screenshots.*

### 2. Phase 6 — Mobile app refinement `Medium`

The assistant app currently shows only a struggle score and top-3 struggling questions for the assigned student. BKT mastery is computed on every run but is never surfaced anywhere in the mobile app.

- [ ] Add BKT mastery badge + mini progress bar to the assigned-student card in `render_assigned_view()`
- [ ] Show per-question mastery level alongside the top-3 question list (`mastered` / `learning` / `not started`)
- [ ] Add session elapsed timer to `_render_session_status_strip()`
- [ ] Add helped-vs-struggling summary header to the unassigned view (`render_unassigned_view()`)
- [ ] Show "currently attempting" question if derivable from most recent submission timestamp

*Feeds: Ch5 functional testing of assistant flows, Appendix B mobile screenshots.*

### 3. Phase 7 — Surface computed-but-hidden data `Small`

Two features are computed every run but produce no visible output:

- `incorrectness_confidence` (from `models/measurement.py`) — added as a DataFrame column but no UI renders it
- `SMOOTHING_ENABLED = False` in `config.py` — exponential temporal smoothing is fully coded but permanently disabled

- [ ] Add a confidence dot or opacity indicator next to incorrectness values in the question drill-down (`ui/components.py`)
- [ ] Decide on temporal smoothing: activate (`SMOOTHING_ENABLED = True`) or remove the dead stub

*Feeds: Ch4 implementation accuracy — shows features are active, not just coded.*

### 5. Phase 9 — RAG suggested feedback `Large`

Surfaces 2–3 LLM-generated coaching bullets in the assistant assigned-student card, grounded in the student's own submission history via a ChromaDB RAG pipeline. Architecture designed by Dr. Batmaz — full spec in [[Assistant App/Operations/Next Steps]] § Phase 9 and [[Assistant App/Operations/RAG Architecture]].

- [ ] Add `chromadb` and `sentence-transformers` to `requirements.txt`
- [ ] Add RAG config constants to `config.py` (`RAG_EMBEDDING_MODEL`, `RAG_CHROMA_PATH`, `RAG_SUGGESTION_MAX_RESULTS`, `RAG_SUGGESTION_CACHE`)
- [ ] Implement `build_rag_collection(df, session_id)` in `analytics.py` — embeds Q&A + AI feedback per student row into a persistent ChromaDB collection
- [ ] Implement `generate_assistant_suggestions(student_id, df, struggle_row) -> list[str]` in `analytics.py` — pre-filter by student_id, retrieve top-k incorrect Q&A chunks, generate suggestions via OpenAI, cache result in-process
- [ ] Wire into `assistant_app.py` assigned-student view: call once on assignment, cache in `st.session_state`, show spinner on first load, show "Not enough data yet" for < 2 submissions

*Feeds: Ch4 advanced feature implementation, dissertation RAG section; requires [[RAG Architecture]] acknowledgement.*

### 6. Phase 10 — In-app Help system `Large`

Adds a Help area under the existing Settings section covering practical usage guidance, model methodology, contextual explanations, and transparency indicators. Full spec in [[Lab App/Operations/Next Steps]] § Phase 10.

- [ ] Add `help_view()` to `ui/views.py` and wire routing in `instructor_app.py`
- [ ] Implement Quick Tour / onboarding walkthrough sub-section
- [ ] Implement Help Centre sub-section (practical how-to content)
- [ ] Implement Model Guide sub-section (methodology and maths in layered depth)
- [ ] Add contextual tooltips for key metrics in `ui/components.py`
- [ ] Add "Why was this flagged?" explanation panels to student and question detail views
- [ ] Add reliability/transparency indicators (early session, low data, experimental signal)
- [ ] Add troubleshooting/help content for confusing dashboard states
- [ ] Verify Help UI matches dashboard visual style without cluttering live workflow

*Feeds: Ch4 implementation detail, usability evaluation in Ch5.*

### 7. Phase 11 — In-app Help (assistant app) `Medium`

Lightweight mobile-friendly Help panel for lab assistants in `assistant_app.py`. Distinct from Phase 10 (instructor dashboard Help) — the assistant app runs on phones and the UI must stay compact and uncluttered. Full spec in [[Assistant App/Operations/Next Steps]] § Phase 11.

- [ ] Add a collapsible Help panel or "?" button accessible from any assistant app state (join screen, unassigned view, assigned view)
- [ ] Add join guide: how to enter a session code and name, what happens after joining
- [ ] Add student list explainer: what the struggle levels and colour badges mean; how to self-claim a student
- [ ] Add assigned-student card explainer: struggle score, top struggling questions, BKT mastery badge, RAG suggested focus areas
- [ ] Add action button guide: "Mark as Helped" vs "Release Student" — what each does and when to use it
- [ ] Verify Help panel does not interfere with auto-refresh or assignment state

*Feeds: Appendix B mobile screenshots, Ch5 usability evaluation.*

### 4. FR6 — Smart device notifications `Large` (stretch)

Listed as "Should Have" in the requirements (FR6) but completely unimplemented. Should be addressed in the thesis even if not built.

- [ ] Evaluate feasibility: web push via `streamlit-push-notification` or an external webhook
- [ ] Implement assistant notification when a new high-struggle student appears while unassigned
- [ ] Document the decision in Ch6 future work regardless of outcome

*If not implemented: treat as a confirmed future work item in Ch6.*

---

## Verification checklist

After Phase 5:

- Enable improved models in Settings → open Model Comparison → verify both Student Struggle and Question Difficulty tabs render
- Disable improved models → verify the view shows an informative message rather than an empty page
- Click a row in the comparison table → verify click-through to student/question detail still works
- Verify BKT sliders in settings change the model output in the comparison view

After Phase 6:

- Join as assistant, get assigned a student → verify BKT mastery badge and progress bar appear on the student card
- Check per-question mastery labels appear alongside the top-3 question list
- Verify session elapsed timer increments correctly

Syntax check after any phase:

```bash
python -m py_compile code/app.py code/lab_app.py \
  code/learning_dashboard/*.py \
  code/learning_dashboard/ui/*.py \
  code/learning_dashboard/models/*.py
```

---

## Useful links

- [[Next Steps]] — full specification for each phase
- [[Known Issues]] — confirmed bugs and implementation gaps
- [[Writing Roadmap]] — thesis chapter status and writing order
- [[Report Sync]] — where the thesis diverges from the current implementation
- [[Evidence Bank]] — what evaluation evidence exists or needs collecting

---

## Code references

- `code/app.py`, `code/lab_app.py` — app entry points
- `code/learning_dashboard/instructor_app.py` — instructor Streamlit app
- `code/learning_dashboard/assistant_app.py` — mobile lab assistant app
- `code/learning_dashboard/analytics.py` — baseline scoring engine
- `code/learning_dashboard/models/` — IRT, BKT, improved struggle, measurement
- `code/learning_dashboard/ui/views.py` — page-level views
- `code/learning_dashboard/ui/components.py` — reusable UI components
- `code/learning_dashboard/ui/theme.py` — CSS and mobile styles
- `code/learning_dashboard/config.py` — all tunable constants and feature flags
