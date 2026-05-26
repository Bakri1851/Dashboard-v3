# Figures and Tables

<!-- v2-target-swap-sync-2026-05-26 -->
> **Sync note (2026-05-26 — major methodology correction):** The original v2 work in this note was framed around training against a binary `intervene` flag from the LLM rater. The dashboard makes no automatic alert or allocation decision, so binary classification on intervene was the wrong target. **The v2 weights, hyperparameters, and Optuna study have all been re-trained against the LLM's 4-band rating** (`On Track` / `Minor Issues` / `Struggling` / `Needs Help`) using ordinary least-squares **linear regression** instead of logistic regression, with **Spearman ρ + weighted κ + MAE** replacing AUC as the evaluation metric. Under the corrected target the verdict scorecard becomes **4 positive findings + 1 tie** (was "2 positive + 2 negative + 1 tie" — the previous negative findings for difficulty and improved-struggle were artefacts of the wrong target). Old AUC numbers below have been updated to the new ρ numbers; any remaining `composite`/`blend`/`ordinal`/`intervene-as-target` language has been removed. See `data/eval/results.md` for the authoritative current numbers.

Inventory of all visual elements in the thesis with their current status and recommended actions.

Related: [[Report Sync]], [[Rewrite Queue]], [[Evidence Bank]], [[Thesis Overview]]

---

## Figures (11 total)

| # | Location | Caption/Description | Source | Action |
|---|----------|-------------------|--------|--------|
| 1 | Ch2 §2.1.2 | Edsight Dashboard — "Overview," "Report," and "Activity List" modes | Literature (external) | Keep |
| 2 | Ch2 §2.1.2 | Edsight Dashboard — single-event report and Multi-Day view | Literature (external) | Keep |
| 3 | Ch2 §2.1.3 | Attention Dashboard — Learning Analytics Interface | Literature (external) | Keep |
| 4 | Ch2 §2.2.2 | Piwik Analytics dashboard | Literature (external) | Keep |
| 5 | Ch2 §2.2.2 | MM Dashboard — SSV, ASV, RSV views | Literature (external) | Keep |
| 6 | Ch3 §3.1 | System Architecture Diagram | Original — TikZ inline at `design-and-architecture.tex:9-93` | **Done 2026-05-20** — V2 TikZ inline replaces the V1 Streamlit-only PNG. PNG file kept on disk but no longer referenced. Spec note [[V2 Architecture Diagram Spec]] retained for posterity. |
| 7 | Ch3 §3.2 | Data Entry Structure (session-based interaction data) | Original — `figures/design and architecture/data entry.png` | Keep — data format unchanged |
| 8 | Ch3 §3.4.2 | Figma mockup — student struggle + question difficulty views | Figma design — `figures/design and architecture/figma1.png` | **Replace** with actual dashboard screenshot |
| 9 | Ch3 §3.4.2 | Figma mockup — lab assistant allocation | Figma design — `figures/design and architecture/figma2.png` | **Replace** with actual dashboard screenshot |
| 10 | Ch3 §3.4.2 | Figma mockup — assistant leaderboard | Figma design — `figures/design and architecture/figma3.png` | **Replace** with actual dashboard screenshot |
| 11 | Progress Report | Gantt Chart — project timeline Jan-May 2026 | Original | **Remove** if Progress Report stays excluded |

### Figures to add

New figures needed for the rewritten Ch4 and Ch5:

| Proposed | Description | Source |
|----------|-------------|--------|
| V2 In Class view | Student/question leaderboards with summary cards | Screenshot |
| V2 Student detail | Drill-down with metrics, timeline, retry trend | Screenshot |
| V2 Question detail | Mistake clusters with labels | Screenshot |
| V2 Data analysis | Example analysis chart | Screenshot |
| V2 Settings | Model toggles and CF configuration | Screenshot |
| V2 Lab assistant views | Join, waiting, assigned screens | Screenshot |
| V2 Architecture diagram | Three-layer pipeline: ingest + caches → baseline + advanced + RAG → instructor + lab-assistant surfaces with file-locked shared state | **Done 2026-05-20** — TikZ inline in `design-and-architecture.tex` keeps the `\label{fig: system architecture}` Figure 6 slot. |

---

## Tables (9 total)

| # | Location | Caption/Description | Action |
|---|----------|-------------------|--------|
| 1 | Ch1 §1.4 | Identified Risks and Mitigation Strategies (5 risks) | **Update** mitigations to reflect actual V2 decisions |
| 2 | Ch2 §2.2.3 | Grade Scoring System (edInsight EWS) | Keep — literature reference |
| 3 | Ch2 §2.3.3 | MoSCoW Requirements Prioritisation | **Review** — FR6 is "Should Have" but unimplemented |
| 4 | Ch3 §4.2 | Technology Stack and Software Selection (7 rows) | **Update** — add OpenAI API, filelock, scikit-learn, scipy; update justifications |
| 5 | Ch3 §3.3.3 | Parametric Model vs Collaborative Filtering Comparison | **Update** — CF is now implemented, not just proposed |
| 6 | Ch3 §3.4.3 | Visual Encoding for Struggle Thresholds | **Update** label names: None→On Track, Low→Minor Issues, Medium→Struggling, High→Needs Help |
| 7 | Ch3 §3.4.3 | Visual Encoding for Difficulty Thresholds | Keep — labels match (Easy/Medium/Hard/Very Hard) |
| 8 | Progress Report | Gantt Chart Summary Table | **Remove** if Progress Report stays excluded |
| 9 | Appendix D | Themes and References (36 citations mapped to themes) | Keep — may need additions if new references added |

### Tables to add

| Proposed | Description | Location |
|----------|-------------|----------|
| Requirements traceability | FR/NFR mapped to implementation status | Ch5 or Ch2 |
| Model comparison results | Baseline vs IRT, baseline vs improved struggle | Ch5 |
| Struggle formula components | All 7 components with weights and descriptions | Ch3 (updated) |
| Difficulty formula components | All 5 components with weights and descriptions | Ch3 (updated) |

---

## Summary of actions

- **Keep as-is:** 5 literature figures (1-5), data entry diagram (7), difficulty thresholds table (7), grade scoring table (2), Appendix D table (9)
- **Update:** Architecture diagram (6), risk table (1), MoSCoW table (3), tech stack table (4), CF comparison table (5), struggle thresholds table (6)
- **Replace:** 3 Figma mockups (8-10) with actual screenshots
- **Remove:** Gantt chart (11) and Gantt summary table (8) if Progress Report excluded
- **Add:** ~7 new screenshots + ~4 new tables

---

## Alternative React (Vite) frontend — figures / tables to add (optional, Ch4 or Ch6)

Only needed if the thesis names the alternative frontend explicitly. All screenshots captured from `http://localhost:8000/` after the FastAPI backend is running.

| Proposed | Description | Source | Destination |
|----------|-------------|--------|-------------|
| V3 architecture diagram | 3 frontends + 1 shared core + 1 shared state file, drawn as ASCII block in `code2/CHECKLIST.md` or redrawn in draw.io | Plan §4 (at `~/.claude/plans/c-users-bakri-downloads-alternative-das-majestic-garden.md`) | Ch4 Implementation |
| V3 In Class (paper theme) | Default editorial theme — leaderboards + hero stats + distribution histograms + 24h timeline | Screenshot | Ch4 |
| V3 theme gallery | Single figure, 7 thumbnails: paper / newsprint / solar / scifi / blueprint / matrix / cyberpunk | Screenshots (7, cropped) | Ch4 or Appendix |
| V3 Student detail | Trajectory sparkline + score components HBar + top questions | Screenshot | Ch4 |
| V3 Question detail | Mistake clusters + top strugglers (new section) + RAG suggestions | Screenshot | Ch4 |
| V3 Lab coordination | Session banner + dispatch queue + active assignments, showing the same state mirrored on a Streamlit tab | Side-by-side screenshot | Ch4 or Ch6 |
| Swagger UI | `/docs` view listing all endpoints grouped by tag | Screenshot | Appendix |

| Proposed table | Description | Destination |
|----------------|-------------|-------------|
| V3 endpoint map | 20+ REST endpoints with the `learning_dashboard.*` function each delegates to | Ch4 or Appendix |
| V3 refactor log | 2 lines: `analytics.py:25` and `data_loader.py:16`, with before/after | Ch4 — demonstrates minimal blast radius |

---

## 2026-04-24 additions — post-Phase-11 figures and tables

New figures and tables prompted by post-Phase-11 code surface (commits `54d45b7`, `17173a8`, `8c4c13c`, `72ce45c`, `5ea4d21`). See [[Rewrite Queue#2026-04-24 additions — post-Phase-11 polish]] for narrative context.

### Figures to add (post-Phase-11)

| Proposed | Description | Source | Destination |
|---|---|---|---|
| SessionProgression timeline | Animated state progression across a live session — the new 9th instructor view | Screenshot (`code2/frontend/src/views/SessionProgression.tsx`) | Ch4 Lab Instructor System |
| Theme × accent matrix | 7 themes (paper / newsprint / solar / scifi / blueprint / matrix / cyberpunk) × 5 accents (indigo / teal / terracotta / forest / crimson) in one grid; single figure per the Ch4 "Interaction design" subsection | Screenshot composite | Ch4 or Appendix B |
| Model Comparison panel | Rank Concordance card (`spearman_rho`) + Top-10 Overlap + Agreement split (upgraded / downgraded / unchanged) + scatter plot for either struggle or difficulty | Screenshot from `/api/models/compare` → ComparisonView | Ch5 §5.4 Results |
| Tooltip in action | One chart with on-hover explanation visible | Screenshot | Ch4 Interaction design |
| Graceful-degradation trace | Screenshot of improved-struggle score with mastery data sparse: shows behavioral-only fallback cell colouring | Screenshot (run with partial data) | Ch3 §3.4.4 or Ch5 §5.5 |

### Tables to add (post-Phase-11)

| Proposed | Description | Location | Source |
|---|---|---|---|
| Struggle formula (7 signals) | Signal × weight × min-max scope × `config.py` key × rationale. Use maths-fix values from commit `8c4c13c`: 0.10 / 0.10 / 0.20 / 0.10 / 0.38 / 0.05 / 0.07. | Ch3 §3.3.1 + Appendix E | `config.py:17-25` |
| Difficulty formula (5 signals) | Signal × weight × min-max scope × `config.py` key × rationale. Weights: 0.28 / 0.12 / 0.20 / 0.20 / 0.20. | Ch3 §3.3.2 + Appendix E | `config.py:44-49` |
| Improved-struggle weight redistribution | Full matrix: base weights + 3 collapse cases (mastery missing, IRT missing, both missing). Invariant: rows always sum to 1.00. | Ch3 §3.4.4 | `improved_struggle.py:168-171` |
| BKT parameter defaults vs fitted | Default (live) values × fitted (unused) values — the two-mode decision Ch3 §3.4.3 should document. | Ch3 §3.4.3 or Ch6 Future Work | `config.py` + `models/bkt.py:fit_bkt_parameters()` |
| Theme × accent combinations | Enumeration of the 35 valid combinations with accessibility class (dark / light / high-contrast). | Ch4 Interaction design or Appendix | `code2/frontend/src/theme/tokens.ts` |
| API endpoint map (≥22 routes) | `/api/*` route × HTTP method × `learning_dashboard.*` delegate × cache TTL. Cache TTL column is new (reflects cache hardening). | Ch4 or Appendix | `code2/backend/routers/` |

### Tables to update with authoritative values

| Target | What to change |
|---|---|
| Ch3 Tbl 6 (Struggle visual encoding) | Use current thresholds: On Track [0.00, 0.20] · Minor Issues [0.20, 0.35] · Struggling [0.35, 0.50] · Needs Help [0.50, 1.00] — matches `config.py` after maths-fix. |
| Ch3 Tbl 7 (Difficulty visual encoding) | Use current thresholds: Easy [0.00, 0.35] · Medium [0.35, 0.50] · Hard [0.50, 0.75] · Very Hard [0.75, 1.00]. |
| Ch3 Tbl 4 (Tech stack) | Add to "Key libraries": openai, filelock, scikit-learn, scipy, streamlit-autorefresh, chromadb, sentence-transformers, fastapi, uvicorn, react, vite, typescript. Drop any V1-only rows. |
| Ch1 Tbl 1 (Risks and mitigations) | Replace generic mitigations with actual ones: Bayesian shrinkage for small-n; modular `models/` package for extensibility; graceful-degradation for missing inputs; FR6 scoped out honestly. |

---

## 2026-05-21 — Ch4 implementation chapter pinned figure inventory

Authoritative list per [Ch4 Rewrite Brief Part C](Ch4%20Rewrite%20Brief.md). All `\label{}` names match the figure-pass step (Brief Roadmap Step 8). Captured here so each figure has a known slot, label, version target, and current status. Status updates as figures land.

### Family 1 — UI screenshots (12)

| § | Slot | Label | Version | Status |
|---|---|---|---|---|
| 4.3.3 | V2 In-Class view (scifi theme) | `fig:v2-inclass` | V2 | TODO |
| 4.5.1 | Instructor sidebar during live session | `fig:session-live` | V1 (per Brief) | TODO |
| 4.9.1 | In-Class view | `fig:ui-inclass` | open question (see below) | TODO |
| 4.9.2 | Student Detail view | `fig:ui-studentdetail` | open question | TODO |
| 4.9.3 | Question Detail view (with clusters) | `fig:ui-questiondetail` | open question | TODO |
| 4.9.4 | Data Analysis view | `fig:ui-dataanalysis` | open question | TODO |
| 4.9.5 | Model Comparison view (both tabs) | `fig:ui-comparison` | open question | TODO |
| 4.9.6 | Settings view | `fig:ui-settings` | open question | TODO |
| 4.9.7 | Previous Sessions view | `fig:ui-previoussessions` | open question | TODO |
| 4.10.1 | Assistant join screen | `fig:asst-join` | open question | TODO |
| 4.10.2 | Assistant unassigned / waiting queue | `fig:asst-unassigned` | open question | TODO |
| 4.10.3 | Assistant assigned card (with RAG) | `fig:asst-assigned` | open question | TODO |

### Family 2 — Architecture / data-flow diagrams (2)

| § | Slot | Label | Type | Status |
|---|---|---|---|---|
| 4.3 opening | System architecture: V1 instructor (Streamlit, 8501) + V1 assistant (Streamlit, 8502) + V2 FastAPI (8000), shared `data/lab_session.json` in the centre via filelock, external lab endpoint + OpenAI + ChromaDB on the perimeter | `fig:arch-v2` | TikZ | **Placeholder in place** at `implementation.tex:92-98`. Real TikZ diagram pending Step 8. |
| 4.4 opening | Data pipeline flow: endpoint → parse → normalise → cache → scoring | `fig:pipeline-flow` | TikZ | TODO |

### Family 3 — Code-snippet images (4)

Editor screenshots (dark theme, syntax highlighting), not `lstlisting`. Take after the de-AI cleanup pass (Brief Part F).

| § | Slot | Label | Source | Status |
|---|---|---|---|---|
| 4.3.4 | `lab_state` filelock read/write pattern | `fig:code-lablock` | `code/learning_dashboard/lab_state.py` (`_lock()` helper + one read + one write call) | TODO |
| 4.3.5 | Deferred-actions pattern | `fig:code-deferred` | `code/learning_dashboard/instructor_app.py` (one `pending_*` flag set in a callback + the apply-and-clear at top of `main()`) | TODO |
| 4.6.1 | OpenAI batch incorrectness call | `fig:code-openai` | `code/learning_dashboard/analytics.py` (`_call_openai_batch` or wrapper) | TODO |
| 4.8.3 | RAG generation prompt | `fig:code-ragprompt` | `code/learning_dashboard/rag.py` (the prompt template inside `generate_assistant_suggestions`) | TODO |

### Family 4 — Tables (6 + 2 optional)

| § | Slot | Label | Status |
|---|---|---|---|
| 4.2 | Technology stack (V1 + V2) | `tab:techstack-v2` | **Done** — pasted at `implementation.tex:42-82` (with React 19 + 2PL/Rasch corrections) |
| 4.6.2 | 7-signal struggle | `tab:struggle-7sig` | TODO |
| 4.6.3 | 5-signal difficulty | `tab:difficulty-5sig` | TODO |
| 4.7.3 | BKT parameter defaults | `tab:bkt-defaults` | TODO (Brief has paste-ready block) |
| 4.9.0 | V1 vs V2 views comparison | `tab:views-comparison` | TODO (Marker-2 anchor) |
| 4.11 | Problems and resolutions | `tab:problems` | TODO |
| 4.4.3 (optional) | Cache hierarchy | `tab:cache-hierarchy` | optional |
| 4.7.4 (optional) | Improved struggle weight redistribution | `tab:improved-redistribution` | optional |

### Family 5 — Optional UML (1)

| § | Slot | Label | Status |
|---|---|---|---|
| 4.3.3 paragraph 4 | Package diagram: V1 `learning_dashboard/` package vs V2 flat `backend/` modules, side-by-side | `fig:pkg-structure` | Optional. Skip if prose-only is enough. |

### Open question — V1 vs V2 capture for §4.9 / §4.10 screenshots

Brief doesn't specify which version each `fig:ui-*` and `fig:asst-*` comes from. Three options:

1. **All V2** (recommended): seven-theme polish, analytical-layer reuse surfaced verbally per subsection. `tab:views-comparison` at §4.9.0 covers the V1 side.
2. **All V1**: keeps canonical demo visible. V2 then has just `fig:v2-inclass` for visual continuity.
3. **Side-by-side V1 + V2 per view**: doubles count to 24. Strongest Marker-2 answer but expensive.

Defer the decision until §4.9 is being authored.

### Capture-time order (figure pass, Step 8)

When figures get drawn / captured in one sitting, the suggested order is:

1. **TikZ first** — `fig:arch-v2` (replaces the placeholder), then `fig:pipeline-flow`, then the optional `fig:pkg-structure`. Drawing one TikZ figure unlocks style reuse for the others.
2. **Code-snippet images** — `fig:code-lablock`, `fig:code-deferred`, `fig:code-openai`, `fig:code-ragprompt`. Take all four in one editor session for consistent theming.
3. **UI screenshots** — last, since the V1-vs-V2 decision above needs to be settled first. Take per the chosen option in one capture session per app (V1 instructor port 8501, V1 assistant port 8502, V2 unified on port 8000).

### Cross-references

- Brief Part C inventory: [Ch4 Rewrite Brief.md §Part C](Ch4%20Rewrite%20Brief.md)
- Plan file with the chat-level details: `~/.claude/plans/i-m-continuing-work-on-reactive-goblet.md`
- Implementation file: `Report/main-sections/implementation.tex`

---

## 2026-05-25 — Ch5 §5.4 v2 empirical-refinement figures (auto-generated)

Eleven PNGs produced by `notebooks/eval_main.ipynb` and saved under `data/eval/figures/` at ≥200 DPI. They support the new §5.4.2 (κ), §5.4.3–§5.4.4 (struggle headline), §5.4.9 (negative findings: difficulty + improved model), §5.4.10 (Optuna), and §5.6.1 (v1↔v2 disagreement). Brief at [[v2 Empirical Refinement Brief]] specifies target subsubsections + LaTeX label suggestions.

**Action:** copy each PNG from `data/eval/figures/` into `Report/figures/evaluation/` (folder may need creating) and add `\includegraphics` lines under the matching `\subsubsection` blocks in `results-and-evaluation.tex`.

| Source file (`data/eval/figures/`) | Target § | Suggested LaTeX label | Subject |
|---|---|---|---|
| `band_distributions.png` | 5.4.1 | `fig:eval-cohort-bands` | 4-panel cohort characteristics: v1 struggle bands + v1 difficulty bands + LLM struggle band distribution + LLM difficulty band distribution |
| `kappa_block.png` | 5.4.2 | `fig:eval-kappa` | 3-bar κ values (binary intervene + linear-weighted band + quadratic-weighted band) with Landis–Koch thresholds overlay |
| `weights_struggle_v1_v2.png` | 5.4.3 | `fig:eval-weights-struggle` | Paired horizontal bar chart, 7 signals, v1 (left) vs v2 (right) with per-fold std error bars; HEADLINE positive finding |
| `auc_per_fold_struggle.png` | 5.4.4 | `fig:eval-auc-perfold-struggle` | 5-bar per-fold AUC with mean horizontal line + 95% CI band; per-fold AUC table also lifted from `results.md` |
| `roc_struggle_v1_v2.png` | 5.4.3 | `fig:eval-roc-struggle` | v1 ROC overlaid with v2 ROC; AUC in legend |
| `calibration_struggle_v2.png` | 5.4.3 | `fig:eval-calibration-struggle` | 10-bin reliability diagram for v2 struggle; diagonal reference for perfect calibration |
| `weight_stability_heatmap_struggle.png` | 5.4.3 | `fig:eval-stability-struggle` | 7 signals (rows) × 5 folds (cols) signed-weight heatmap, annotated; shows whether folds agree on sign |
| `confusion_bands_v1_v2.png` | 5.4.3 / 5.6.1 | `fig:eval-confusion-bands` | Side-by-side 4×4 confusion matrices: v1 predicted bands vs LLM, v2 predicted bands vs LLM; `RdGy` cmap |
| `weights_difficulty_v1_v2.png` | 5.4.9 | `fig:eval-weights-difficulty` | Paired bar chart, 5 signals, difficulty v1 vs v2; NEGATIVE finding (2 sign flips, ρ +0.287 < random) |
| `weights_improved_v1_v2.png` | 5.4.9 | `fig:eval-weights-improved` | Paired bar chart, 3 weights, improved model v1 vs v2; NEGATIVE finding (w_M and w_D flipped negative) |
| `disagreement_matrix.png` | 5.6.1 | `fig:eval-disagreement-matrix` | 4×4 v1 bands vs v2 bands confusion; HEADLINE: 31.2% of snapshots reclassified |

### Tables to lift directly from `data/eval/results.md`

Seven Markdown tables ready to convert to LaTeX `tabular` / `tabularx`. Source: `data/eval/results.md` (auto-generated; re-run notebook to refresh).

| Table | Target § | Suggested LaTeX label | Lifted from |
|---|---|---|---|
| Cohort | 5.4.1 | `tab:eval-cohort` | `results.md` § Cohort |
| Cohen's κ (n=50) | 5.4.2 | `tab:eval-kappa` | `results.md` § §5.4.2 |
| Struggle v1 vs v2 weights (7 signals + signs) | 5.4.3 | `tab:eval-weights-struggle` | `results.md` § §5.4.3 |
| Per-fold AUC (struggle, 5 folds) | 5.4.4 | `tab:eval-auc-perfold-struggle` | `results.md` § §5.4.4 |
| Difficulty v1 vs v2 weights (5 signals + signs) | 5.4.9 | `tab:eval-weights-difficulty` | `results.md` § §5.4.9 (first table) |
| Improved-struggle model v1 vs v2 weights (3 weights + signs) | 5.4.9 | `tab:eval-weights-improved` | `results.md` § §5.4.9 (second table) |
| Hyperparam optimisation (Optuna TPE: K + τ) | 5.4.10 | `tab:eval-hyperparams-optuna` | `results.md` § §5.4.10 |

### Verdict scorecard table (lift from [[Evaluation PoC Handoff]] §13)

| Target § | Suggested LaTeX label | Subject |
|---|---|---|
| 5.6.1 | `tab:eval-verdict-scorecard` | 5-row table: component × winner × numbers × phase; lifted verbatim from [[Evaluation PoC Handoff]] §13 |
