# 07 — Citations: wire orphans + Candidate References

Two-step. **Step 1** needs no new references at all — 16 already-present entries in `references.bib` are uncited and several are the exact methods the chapters use. **Step 2** is a small set of genuinely-new refs for you to validate in Zotero (I do **not** edit `references.bib`). ← [[00 Index]]

## Step 1 — Wire orphaned references into prose (no Zotero, no `.bib` edit)
All 16 keys confirmed present in `references.bib` (line numbers given) with **0 current citations**. Attach each at the point of use, then they stop being dead entries (`ieeetr` silently drops uncited ones).

| Orphan key (`.bib` line) | Attach at |
|---|---|
| `spearmanProofMeasurementAssociation1904` (984) | first Spearman ρ use, Eval Metrics subsection / §5.4 ~l149 |
| `CoefficientAgreementNominal` (171, Cohen 1960) | first Cohen's κ use ~l255 (unweighted basis) |
| `landisMeasurementObserverAgreement1977` (570) | "fair-to-moderate" κ band reading ~l503 |
| `fawcettIntroductionROCAnalysis2006` (261) | BKT ROC-AUC, design l705 + §5.3 per-skill AUC |
| `hanleyMeaningUseArea1982` (357) | alongside Fawcett at the AUC mentions |
| `oecdHandbookConstructingComposite2008` (788) | composite normalisation (Ch3 §3.3) + threshold sensitivity (§5.4.5) |
| `saisanaUncertaintySensitivityAnalysis2005` (920) | cohort-dependence of cutpoints (§5.4.5, §5.6.3; conclusion l59–69) |
| `hunterExponentiallyWeightedMoving1986` (442) | EWMA / time-decay definitions (Ch3 l209–215, l336–338) |
| `korenCollaborativeFilteringTemporal2010` (545) | CF cold-start (Ch3 l156) **and** the Netflix claim (req §2.1.3 l62) |
| `liuGEvalNLGEvaluation2023` (641) | LLM-as-rater first mention (§5.4 l24) + §2.2.4 |
| `gelmanBayesianDataAnalysis2013` (317) | Bayesian shrinkage conjugate-prior framing (Ch3 l293–303; Ch2 B2) |
| `hattiePowerFeedback2007` (373) | feedback-value framing (Intro / Ch2 struggle) |
| `blackAssessmentClassroomLearning1998` (108) | formative-assessment framing (Intro / Ch2) |
| `bakerDevelopingGeneralizableDetector2008` (74) | struggle/affect-detector context (Ch2 §2.2.1) |
| `beckWheelSpinningStudentsWho2013` (91) | "wheel-spinning"/repeated-failure struggle context (Ch2 §2.2.1) |
| `fisherMathematicalFoundationsTheoretical1922` (278) | correlation/statistics grounding (Eval Metrics) — or drop if no clean home |

- Any orphan with no natural home (likely `fisherMathematicalFoundationsTheoretical1922`) should be **deleted** from `.bib` rather than left padding the bibliography — an examiner may probe uncited entries.

## Step 2 — Candidate references to validate in Zotero (web-verified metadata)
**Workflow:** add each to Zotero → check the DOI/details → Better BibTeX export updates `references.bib`. I will **not** touch `.bib`. Suggested citekey shown; adjust to your BBT convention.

1. **Cohen, J. (1968).** Weighted kappa: Nominal scale agreement with provision for scaled disagreement or partial credit. *Psychological Bulletin* 70(4), 213–220. DOI `10.1037/h0026256`. → `cohenWeightedKappaNominal1968`. **Why:** the chapter uses *linear-weighted* κ; the `.bib` only has Cohen 1960 (unweighted). Attach at §5.4.5 first weighted-κ use + Ch2 B3.
2. **Breiman, L. (2001).** Random Forests. *Machine Learning* 45(1), 5–32. DOI `10.1023/A:1010933404324`. → `breimanRandomForests2001`. **Why:** named in the §5.4.3 bake-off; Ch2 B1.
3. **Friedman, J. H. (2001).** Greedy function approximation: A gradient boosting machine. *The Annals of Statistics* 29(5), 1189–1232. DOI `10.1214/aos/1013203451`. → `friedmanGreedyFunctionApproximation2001`. **Why:** gradient boosting in the bake-off; Ch2 B1.
4. **Ryan, A. M., Pintrich, P. R., & Midgley, C. (2001).** Avoiding seeking help in the classroom: Who and why? *Educational Psychology Review* 13(2), 93–114. DOI `10.1023/A:1009013420053`. → `ryanAvoidingSeekingHelp2001`. **Why:** grounds the help-seeking-reluctance claim (Intro l10 + survey theme §5.5).
5. **Hastie, T., Tibshirani, R., & Friedman, J. (2009).** *The Elements of Statistical Learning* (2nd ed.). Springer. DOI `10.1007/978-0-387-84858-7`, ISBN 9780387848570. → `hastieElementsStatisticalLearning2009`. **Why:** anchors OLS / linear-regression and the model-class discussion (Ch2 B1; Ch3 R5).
6. **Bass, L., Clements, P., & Kazman, R. (2012).** *Software Architecture in Practice* (3rd ed.). Addison-Wesley. ISBN 9780321815736. → `bassSoftwareArchitecturePractice2012`. **Why:** optional grounding for the layered-architecture rationale (Ch3 l6–7). Low priority.

**Footnote URLs (not Zotero papers):**
- `all-MiniLM-L6-v2` model card → `https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2` (cite as a footnote at the embedding-model choice, `implementation.tex` l1053).
- `gpt-4o-mini` → OpenAI model docs (`https://platform.openai.com/docs/models`) as a footnote at the incorrectness-scorer model choice.

**Reframed, not cited:** the class-size→monitoring-difficulty claim (Intro l15–16) — reframe as a design premise rather than chase a possibly-shaky citation (no confidently-canonical source found).

> After any `.bib` change, re-run `python scripts/sync_literature.py` (keeps the vault literature notes + `coverage.md` in sync). Verify every newly-cited key resolves with a clean `bibtex` pass.
