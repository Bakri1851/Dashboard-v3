# 07 — Citations: wire orphans + Candidate References

✅ **Closed 2026-06-01.** Re-audited against the live report with `scripts/sync_literature.py` (authoritative). **12 orphaned keys wired** into the `.tex` (gated, verbatim — `references.bib` never hand-edited); **4 keys recommended for Zotero removal**. Result: **0 broken cites**; the only remaining orphans are those 4 deliberate cuts. ← [[00 Index]]

> Method: I do **not** edit `references.bib` (Zotero/Better BibTeX is source of truth). Cuts are actioned by you in Zotero; every wiring was previewed as a `.tex` diff and applied after sign-off.

## Final coverage (`coverage.md`, 2026-06-01)

90 bib entries · 228 `\cite{}` calls across 86 keys · **0 broken** · **4 orphans** (the cuts below). Backend: `\usepackage{cite}` + `\bibliographystyle{ieeetr}` (plain `\cite{}`).

## Wired (12) — applied

| # | Key | File:line | Grounds the claim |
|---|---|---|---|
| 1 | `cohenWeightedKappaNominal1968` | `results-and-evaluation.tex:33` | weighted κ (linear-vs-quadratic weighting) — the weighted-κ source |
| 2 | `breimanRandomForests2001` | `results-and-evaluation.tex:220` | "random forest" in the model-class bake-off |
| 3 | `friedmanGreedyFunctionApproximation2001` | `results-and-evaluation.tex:220` | "gradient boosting" in the bake-off |
| 4 | `pedregosaScikitlearnMachineLearning2012` | `implementation.tex:68` | scikit-learn dependency row |
| 5 | `hunterExponentiallyWeightedMoving1986` | `design-and-architecture.tex:593` | EWMA temporal smoothing |
| 6 | `gelmanBayesianDataAnalysis2013` | `design-and-architecture.tex:562` | conjugate-prior Bayesian shrinkage |
| 7 | `oecdHandbookConstructingComposite2008` | `design-and-architecture.tex:443` | composite-indicator normalisation |
| 8 | `saisanaUncertaintySensitivityAnalysis2005` | `results-and-evaluation.tex:325` | cohort-sensitivity of the cutpoints |
| 9 | `liuGEvalNLGEvaluation2023` | `requirements-specification.tex:154` | LLM-as-rater cluster (G-Eval) |
| 10 | `beckWheelSpinningStudentsWho2013` | `requirements-specification.tex:93` | wheel-spinning / repeated failure |
| 11 | `hattiePowerFeedback2007` | `requirements-specification.tex:13` | feedback improves learning |
| 12 | `blackAssessmentClassroomLearning1998` | `requirements-specification.tex:13` | formative-assessment grounding |

## Cut (4) — remove in Zotero, then re-export

| Key | Why |
|---|---|
| `bakerDevelopingGeneralizableDetector2008` | Paper is about students *gaming the system*, not struggle — no honest home in the current text. |
| `korenCollaborativeFilteringTemporal2010` | *Temporal-dynamics* CF; no claim invokes it (briefly wired at `:168`, reverted on review). |
| `LimitedMemoryAlgorithm` | Exact duplicate of the already-cited `byrdLimitedMemoryAlgorithm1995` (`design:908`, `implementation.tex:66`/`:842`). |
| `fisherMathematicalFoundationsTheoretical1922` | Redundant with `spearman…1904`. *(Optional keep: MLE home at `design:899`.)* |

## Already resolved before this pass (verify only)

`spearmanProofMeasurementAssociation1904` (`results:25`), `CoefficientAgreementNominal` / Cohen 1960 (`results:33`), `landisMeasurementObserverAgreement1977` (`results:33`), `fawcettIntroductionROCAnalysis2006` + `hanleyMeaningUseArea1982` (`results:35`).

## Candidate references (Step 2) — status

- **Cohen-1968 / Breiman / Friedman / scikit-learn** → were added to Zotero, now wired above (#1–4).
- **Hastie ESL** (`hastieElementsStatisticalLearning2009`) → in bib + cited at `requirements:152`. Done.
- **Ryan help-seeking** (`ryanAvoidingSeekingHelp2001`), **Bass architecture** (`bassSoftwareArchitecturePractice2012`) → not added; optional only.
- **Outstanding (planned, not in Zotero):** `khajah_2014_incorporating` (add only if citing); `manningIntroductionInformationRetrieval2008` — **edition clash** with the already-cited `manningIntroductionInformationRetrieval2006` (`requirements:186`); pick one.

## Hygiene flags (author's call — not silently changed)

- `results:33` still phrases it "quadratic-weighted" while now citing the weighted-κ source — confirm the wording matches the deployed metric (linear-weighted).
- Typo "simated alternatives" at `results-and-evaluation.tex:176`.
- 10 bib entries have **no literature note** (`coverage.md` → *no literature note*), several of them cited (`landis…1977`, `akiba…2019`, `hastie…2009`, `morris…1983`, `NIPS2011_86e8f7ab`). Run the Zotero Integration import so `sync_literature.py` tracks them. Non-blocking.
- Footnote URLs (not Zotero papers): `all-MiniLM-L6-v2` model card, `gpt-4o`/`gpt-4o-mini` docs — cite as footnotes at the model-choice mentions in `implementation.tex`.

## Definition of done

- ✅ 12 wirings applied; `sync_literature.py` clean — **0 broken cites**.
- ⬜ **You (Zotero):** remove the 4 cuts → re-export `references.bib` → re-run `python scripts/sync_literature.py` → **0 orphans**.
- ⬜ Flip Note 07 in [[00 Index]] to ✅ once the Zotero cuts land.

> This (07) is the sole reference-reform note. (An earlier draft referenced "22/23 reference reform"; those files do not exist.)
