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
