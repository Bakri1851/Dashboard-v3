# Figures and Tables

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
| 6 | Ch3 §3.1 | System Architecture Diagram | Original — `figures/design and architecture/architecture diagram.png` | Review — may need updating if architecture section changes |
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
| V2 Architecture diagram | Updated to show models/ package | New diagram (optional) |

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
