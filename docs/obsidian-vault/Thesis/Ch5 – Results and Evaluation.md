# Ch5 – Results and Evaluation

Thesis chapter for evaluation design, testing, results, and discussion. Currently completely empty.

Related: [[Thesis Overview]], [[Report Sync]], [[Evidence Bank]], [[Setup and Runbook]], [[Known Issues]], [[Ch2 – Background and Requirements]]

**Source file:** `main sections/results and evaluation.tex`
**Status:** Empty (CRITICAL) — 5 subsection headers, no content

---

## Current contents

```latex
\section{Evaluation}
\subsection{Evaluation Design}
\subsection{Functional Testing}
\subsection{Non-Functional Testing}
\subsection{Results}
\subsection{Discussion}
```

No content exists.

---

## What could go in each section

### 5.1 Evaluation Design

- Define evaluation goals: does the system meet FR1-FR7 and NFR1-NFR6?
- Methodology: manual functional testing, performance measurement, model comparison
- Limitations: no user study conducted, no controlled classroom experiment
- Reference requirements from [[Ch2 – Background and Requirements]]

### 5.2 Functional Testing

Test each functional requirement:

| FR | Test approach | Evidence source |
|----|--------------|-----------------|
| FR1 (live ingestion) | Verify data loads from endpoint, parses correctly, updates on refresh | Run dashboard, confirm data appears |
| FR2 (struggle metrics) | Verify 7-signal model produces scores in [0,1], classification labels correct | Screenshots of leaderboard with varying scores |
| FR3 (difficulty metrics) | Verify 5-signal model + IRT produce scores, labels correct | Screenshots of question leaderboard |
| FR4 (prioritisation) | Verify leaderboards rank by score, color coding matches thresholds | Screenshots of In Class view |
| FR5 (present analytics) | Walk through all 6 instructor views, verify charts render | Screenshots of each view |
| FR6 (smart devices) | NOT IMPLEMENTED — document as future work | N/A |
| FR7 (assistant ranking) | Verify helped count visible in lab session state | Screenshot of assistant system |

### 5.3 Non-Functional Testing

| NFR | Test approach | Evidence source |
|-----|--------------|-----------------|
| NFR1 (performance) | Measure refresh latency, API response time, dashboard load time | Timing measurements |
| NFR2 (interpretability) | Verify no specialist knowledge needed; color coding intuitive | UI walkthrough |
| NFR3 (robustness) | Test with empty data, single student, no AI feedback, corrupt sessions | Edge case testing |
| NFR4 (scalability) | Test with varying class sizes | Load observations |
| NFR5 (privacy) | Confirm read-only API, no PII storage | Architecture review |
| NFR6 (extensibility) | Demonstrate model toggle system, config-driven thresholds | Settings page screenshot |

### 5.4 Results

Potential results to present:
- Model output examples (struggle scores, difficulty scores for real session data)
- Baseline vs IRT difficulty comparison
- Baseline vs improved struggle comparison
- CF elevation rate (how many students get flagged by CF that baseline missed)
- Mistake clustering examples with auto-generated labels
- Performance benchmarks (refresh cycle timing)

### 5.5 Discussion

- How well does the system address the original problem?
- Which requirements are fully satisfied vs partial vs unmet?
- Strengths of the approach (multi-signal, configurable, extensible)
- Limitations (no user study, no long-term evaluation, no smart devices)
- Comparison with related systems (SAM, EMODA, Edsight, edInsight)

---

## Evidence status

See [[Evidence Bank]] for detailed tracking. Summary:

- **Screenshots:** None captured yet — need all 6 instructor views + 4 assistant views
- **Test results:** No automated tests exist; manual smoke testing only (checklist in [[Setup and Runbook]])
- **Model comparisons:** No evaluation data generated
- **Performance metrics:** No measurements taken
- **User feedback:** None collected

---

## Rewrite items

- [ ] Write evaluation design section
- [ ] Conduct and document functional testing against FR1-FR7
- [ ] Conduct and document non-functional testing against NFR1-NFR6
- [ ] Generate model comparison data (baseline vs IRT, baseline vs improved struggle)
- [ ] Capture screenshots for all dashboard views
- [ ] Write results section with evidence
- [ ] Write discussion section
- [ ] Populate Appendix C (detailed test results)

## Open questions

- Is a user study expected for this thesis, or is manual testing + model evaluation sufficient?
- Should evaluation compare V1 vs V2 to show progression?
- What constitutes "enough" evidence for a master's thesis evaluation chapter?
