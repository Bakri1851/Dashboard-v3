# 08 — Examiner-Expected Sections (author writes)

Things an MSc examiner expects that are currently absent. Lists are mechanical ([[02 Proposed Report Edits — structural]]); the rest are short authored sections. ← [[00 Index]]

## E1. Ethics approval reference (HIGH — ties to [[01 Integrity & Consistency Fixes]] I3)
- The survey collects human-subject data (10 respondents incl. staff/students) and the replay uses student submission logs, yet no ethics board ID / approval date / exemption statement appears anywhere — and §5.5.1's heading even promises "Ethical Approval".
- **Write:** the Loughborough ethics approval (or exemption) reference + date, under §5.5.1 and/or a methods/ethics statement. If none was obtained, state the basis (e.g. anonymised secondary data, voluntary anonymous survey) explicitly.

## E2. GDPR / data-protection statement
- The survey itself surfaced re-identification and data-use-scope concerns (§5.5.4). 
- **Write:** a short data-protection paragraph — controller, lawful basis, what is stored, retention, anonymisation of student IDs, and that the dashboard is instructor-facing only (students are not shown their scores). Natural home: Ethics/Methods or a Limitations subsection.

## E3. Reproducibility / code-and-data availability
- The thesis describes `config.py`, trained weight JSONs, Optuna studies, eval scripts and notebooks but never states whether code/weights/anonymised data are available.
- **Write:** a one-paragraph statement — what is released, where (repo/archive), under what licence, and which artefacts reproduce which figures (e.g. `notebooks/eval_main.ipynb` → §5.4 figures).

## E4. Prior-systems comparison table (HIGH for positioning)
- SAM/EMODA/Edsight/Blocks/MM Dashboard and the requirements-era dashboards are described in prose only.
- **Write:** a feature-by-feature matrix (rows = systems incl. *this* dashboard; columns = real-time, in-lab vs post-hoc, instructor-facing, struggle modelling, question difficulty, assistant dispatch, advanced models IRT/BKT, RAG feedback) so the contribution is visible at a glance. **This connects directly to [[10 Related Work & Research-Gap Expansion]] — populate the table from that scan.**

## E5. Threats-to-validity framework
- §5.6 covers only rater fidelity, module skew, and the scorer fallback.
- **Write:** name the four standard categories — **construct** (does the LLM-rated 4-band target measure "struggle"/"difficulty"?), **internal** (retrospective replay, no intervention), **external** (single module/institution; cohort skew), **statistical-conclusion** (n=72 LOO variance; n=10 survey). Fold the existing caveats under these headings.

## E6. Sample-size / power note
- The thesis acknowledges small samples but states no bound on what they support.
- **Write:** one or two sentences on what the n=10 survey and n=50 calibration set can and cannot support (qualitative triangulation only; no statistical inference), and why the difficulty n=72 LOO results are "directional".

## E7. Accessibility / colour-blindness note
- The traffic-light (green/amber/orange/red) scheme is central to the interpretability claim; §5 states no accessibility audit was run.
- **Write:** acknowledge the gap and offer a mitigation (redundant cue — band label/position/icon alongside colour; a colour-blind-safe palette option). Ties to the visual-encoding rationale in [[03 Design Rationale & Missing Views]] R1.

## E8. List of Figures / List of Tables
- 30+ numbered floats, no `\listoffigures`/`\listoftables`. Mechanical — handled in [[02 Proposed Report Edits — structural]] S6.
