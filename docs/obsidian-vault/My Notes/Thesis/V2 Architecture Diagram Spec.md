# V2 Architecture Diagram Spec

Spec for redrawing **Figure 6** in Ch3 §3.1 (`Report/figures/design-and-architecture/architecture-diagram.png`). The current PNG is the V1 Streamlit-only render from April; the §3.1 prose still uses the correct 3-layer framing but the figure body needs full repopulation with V2 components.

Related: [[Figures and Tables]], [[Report Sync]], [[Ch3 – Design and Modelling]], [[feedback-design-artifacts-in-design-chapter]]

---

## Design-register principles

The Ch3 architecture diagram is a **design artifact**, not an implementation snapshot. Concrete framework names, port numbers, and file paths belong in the Ch4 implementation-register diagram (separate task, lands with the Ch4 rewrite). For this figure:

- **Use** generic module names that match the §3.3–§3.5 subsection headings (Data Ingestion, Baseline Analytics, Advanced Models, RAG Pipeline, Instructor Dashboard, Lab Assistant Interface, Shared Session State).
- **Do not use** "Streamlit", "React", "FastAPI", "Vite", "ChromaDB", port numbers (`8000` / `8501` / `8502` / `5173`), or stack-specific path prefixes (`code/` / `code2/`).
- **OpenAI** can be named explicitly because it is a single external service, not a stack choice; alternatively rename it "LLM service" to keep it generic.

Keep the three top-level layers from the existing §3.1 prose intact — they still describe V2 correctly.

---

## Layer 1 — Data Generation

| Box | Role | Notes |
|-----|------|-------|
| Students (multiple, stacked) | External source | Submit attempts, request feedback |
| AI Feedback Platform | External system | Hosts the upstream data endpoint; read-only integration |

**Edges in Layer 1:**

- Students → AI Feedback Platform (submission events; existing arrow in the current diagram, retain)

---

## Layer 2 — Ingestion & Processing

This is the layer that has changed most. Six boxes plus an external dependency.

| Box | Role | Maps to |
|-----|------|---------|
| Data Ingestion | Processing | `data_loader` — periodic polling, JSON+XML parsing, normalisation |
| Raw Data Cache | Data store | TTL-bounded in-process cache for the endpoint payload |
| Persisted Incorrectness Cache | Data store | Disk-backed JSON store, peer of the raw cache; reused across cold boots |
| Baseline Analytics | Processing | `analytics` — 7-signal struggle (§3.3.1), 5-signal difficulty (§3.3.3), CF (§3.3.4), mistake clustering (§3.3.5) |
| Advanced Models Package | Processing (swappable subsystem) | `models/` — Measurement Confidence (§3.4.1), IRT (§3.4.2), BKT (§3.4.3), Improved Struggle (§3.4.4). Draw with a dashed group box. |
| RAG Pipeline | Processing | Vector store + embedding model + ANN index + LLM generator (§3.5). One composite box is enough; subcomponents do not need to appear in this diagram. |
| Shared Session State | Data store | `lab_session.json` — file-locked, atomic tmp-replace; written by both UI surfaces |
| LLM Service (OpenAI) | External service | Used by Baseline Analytics for incorrectness scoring and by the RAG Pipeline for generation. Draw at the edge of Layer 2. |

**Edges in Layer 2:**

- AI Feedback Platform → Data Ingestion (HTTP poll)
- Data Ingestion → Raw Data Cache (normalised DataFrame)
- Raw Data Cache → Baseline Analytics (input)
- Baseline Analytics → Advanced Models Package (struggle / difficulty as inputs to the improved model)
- Advanced Models Package → Baseline Analytics (mastery posteriors fed back into the improved struggle composite — optional bidirectional or a return arrow)
- Baseline Analytics → Persisted Incorrectness Cache (write/lookup, both directions)
- Baseline Analytics + Advanced Models → RAG Pipeline (struggle context, mistake-cluster summaries)
- Baseline Analytics → LLM Service (incorrectness scoring; dashed if external arrows are distinguished)
- RAG Pipeline → LLM Service (generation call; dashed)

**Edges that should NOT appear:** raw OpenAI key wiring, Settings page interactions (those are user-facing, belong in Layer 3 only).

---

## Layer 3 — Decision & Action

| Box | Role | Maps to |
|-----|------|---------|
| Instructor Dashboard | UI surface | Multiple views described in §3.6.1: in-class overview, student detail, question detail, data analysis, settings, previous sessions |
| Lab Assistant Interface | UI surface | Three states described in §3.6.3: join, waiting, assigned |

**Edges in Layer 3:**

- Baseline Analytics → Instructor Dashboard (struggle / difficulty / CF / clusters for visualisation)
- Advanced Models Package → Instructor Dashboard (model comparison, mastery, IRT difficulty)
- RAG Pipeline → Instructor Dashboard (RAG-grounded coaching prompts on the question-detail view)
- RAG Pipeline → Lab Assistant Interface (assistant-side coaching prompts)
- Shared Session State ↔ Instructor Dashboard (read/write — start/end session, assign assistants)
- Shared Session State ↔ Lab Assistant Interface (read/write — join, claim student, mark helped)

The shared-state bidirectional arrows are the **key visual** that explains how the two surfaces stay in sync without direct coupling — make them visually prominent.

---

## ASCII sketch

A rough layout for orientation. Boxes stack within each layer; arrows cross layer boundaries cleanly when possible.

```
┌─────────────────────────────── Layer 1 — Data Generation ───────────────────────────────┐
│                                                                                          │
│   [ Students ] ─────────────► [ AI Feedback Platform ]                                   │
│                                            │                                             │
└────────────────────────────────────────────┼─────────────────────────────────────────────┘
                                             │ poll
┌────────────────────────────────────────────▼──── Layer 2 — Ingestion & Processing ──────┐
│                                                                                          │
│   [ Data Ingestion ] ───► [ Raw Data Cache ] ───► [ Baseline Analytics ] ◄───────┐       │
│                                                          │   ▲                   │       │
│                                                          │   │                   │       │
│                                ┌─── (dashed group) ──────┼───┼───────────────┐   │       │
│                                │ [ Advanced Models Package: Measurement │    │   │       │
│                                │   Confidence · IRT · BKT · Improved    │    │   │       │
│                                │   Struggle ]                           │    │   │       │
│                                └────────────────────────┬──────────────┬┘    │   │       │
│                                                         │              │     │   │       │
│                                                         ▼              ▼     │   │       │
│                                              [ RAG Pipeline ]   [ Persisted Incorrectness │
│                                                         │         Cache ]                 │
│                                                         │                                 │
│                                  ──────► [ LLM Service (OpenAI) ] ◄───────                │
│                                                                                           │
│                            [ Shared Session State (lab_session.json) ]                    │
│                                            ▲                  ▲                           │
└────────────────────────────────────────────┼──────────────────┼───────────────────────────┘
                                             │                  │
┌────────────────────────────────────────────▼──── Layer 3 — Decision & Action ────────────┐
│                                                                                           │
│   [ Instructor Dashboard ]  ◄──── analytics + models + RAG ────►  [ Lab Assistant         │
│           ▲                                                          Interface ]          │
│           └──────────────── shared session state ──────────────────────────►              │
│                                                                                           │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

The sketch is intentionally rough — the redrawn diagram should use a proper grid layout and clean orthogonal routing.

---

## Style guidance

| Element | Convention |
|---------|------------|
| Box colour by role | Data store = blue, Processing module = green, External service = orange, UI surface = purple. Pick your own palette but keep the role distinction visible. |
| Box shape | Rectangles for processing/UI, cylinders or stacked-rectangles for data stores, hexagon or rounded-rectangle for external services. |
| Arrow direction | Always directional. Bidirectional arrows only for genuine read/write loops (e.g. Shared Session State ↔ both UI surfaces). |
| Arrow labels | Label only non-obvious edges (e.g. "scored incorrectness", "mastery posterior", "assignment event"). Skip labels on obvious data flow. |
| Grouping | Single dashed grouping box around the four `models/` modules — signals a swappable subsystem and matches the §3.4 framing. |
| Layer separation | Horizontal bands with subtle background tint or a thin separator line; layer labels in the left margin or as a small header bar. |
| Typography | Single sans-serif font; box title bold, role hint (one word) in italics underneath if useful. |
| Width | Final PNG at the same aspect ratio as the current Figure 6 — fits `width=1\linewidth` in LaTeX without margin clipping. |

---

## Things to deliberately exclude

- Port numbers (`:8000`, `:8501`, `:8502`, `:5173`) — implementation detail
- Framework / library names (Streamlit, React, FastAPI, ChromaDB, Sentence-BERT, HNSW) — Ch4 territory
- Config-file paths (`config.py`, `.streamlit/secrets.toml`) — Ch4 territory
- The two-stack split (Streamlit vs React) — design-register diagram is stack-agnostic; the Ch4 implementation diagram covers stack choices
- Individual chart names or per-view UI details — those belong in §3.6 (mockups) and Ch4 (deployed screenshots)
- Authentication / auth flow — out of scope for the current system
- Backup / persistence beyond `lab_session.json` and the incorrectness cache — saved-sessions store can be omitted from the main diagram, or shown as a small adjunct to Shared Session State if space allows

---

## Workflow after this spec lands

1. Open the existing diagram source (Lucidchart / draw.io / Figma / TikZ — whichever the V1 PNG was authored in). If the source is lost, the ASCII sketch above plus the box/edge tables are enough to redraw from scratch.
2. Redraw with the V2 components listed.
3. Export to `Report/figures/design-and-architecture/architecture-diagram.png` (overwrite — keep the path).
4. Recompile `Report/main.tex`. Confirm Figure 6 still renders and that `\ref{fig: system architecture}` resolves at `design-and-architecture.tex:17` and `:28`.
5. Flip the [[Figures and Tables]] Figure 6 row from "spec'd, awaiting redraw" to "done"; bump [[Report Sync]] §3.1 line.

---

## Cross-reference: what each layer/box maps to in the report

This is for the redrawer's reference — the diagram should visually echo subsection structure so the reader feels continuity between the figure and the next four pages of prose.

| Diagram element | Thesis subsection | Code module(s) |
|-----------------|-------------------|----------------|
| Data Ingestion | §3.2 Data Endpoint | `data_loader` |
| Baseline Analytics | §3.3 Baseline Analytics Design (§3.3.1–§3.3.5) | `analytics` |
| Advanced Models Package | §3.4 Advanced Model Design (§3.4.1–§3.4.4) | `models/` |
| RAG Pipeline | §3.5 RAG Feedback Design | `rag` |
| Instructor Dashboard | §3.6.1, §3.6.2 (Figma mockups) | dashboard views |
| Lab Assistant Interface | §3.6.3 (Lab Assistant View) | lab-assistant app/route |
| Shared Session State | (described in Ch3 prose; full implementation detail in Ch4) | `lab_state` |
| LLM Service | §3.3.1 (incorrectness scoring), §3.5 (RAG generation) | external |
