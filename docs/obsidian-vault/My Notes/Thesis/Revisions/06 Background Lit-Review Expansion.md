# 06 — Background Lit-Review Expansion (author writes)

Supervisor pt 15: model-training content was added to Ch3–5 that Ch2 barely covers. **Scoped 2026-06-01:** *evaluation methodology is not lit-reviewed* — the model-class bake-off baselines, weighted Cohen's κ, cutpoint/threshold search, composite-indicator sensitivity, and Optuna/TPE tuning are cited *where they are used in Ch5*, not surveyed here (relocated to [[07 Citations — wire orphans + Candidate References]]). After that filter the one Ch2 addition is **A1** the deployed estimator (OLS). **A2** (help-seeking grounding) was **dropped 2026-06-01** — the claim is empirically validated by the survey (§5.5), so an external citation is optional. ← [[00 Index]]

> **Background voice (not implementation/eval).** Both additions are declarative grounding — no "we", no fitted coefficients, no result numbers. Each carries a *keep-out* line marking what belongs in Ch3/Ch5 instead.

## A1 — Name OLS in §2.2.4 "Composite Model Training and Optimisation"
`requirements-specification.tex` l150–156 (edit at l152). **✅ Applied 2026-06-01** — `ordinary least squares (OLS) regression \cite{hastieElementsStatisticalLearning2009}`. The subsection already framed supervised refinement of composite weights against labels in background voice; it just lacked the named estimator.
- **Add:** name **ordinary least squares (OLS)** as the standard linear estimator for refitting composite weights against labels — one clause, e.g. "…through supervised estimators such as ordinary least squares \cite{hastieElementsStatisticalLearning2009}". Cite `hastieElementsStatisticalLearning2009` (new → [[07 Citations — wire orphans + Candidate References]] candidate 5; validate in Zotero first).
- **Leave as-is:** the existing LLM-rater sentence (`gilardiChatGPTOutperformsCrowd2023, chiangCanLargeLanguage2023, zhengJudgingLLMasaJudgeMTBench2023`) and the Optuna/TPE sentence (`NIPS2011_86e8f7ab, akibaOptunaNextgenerationHyperparameter2019`) — do **not** expand them (TPE justification is eval tuning).
- **Keep out → elsewhere:** fitted coefficients / deployed weight vector → Ch3–4; the RF/GB bake-off comparison and κ deltas → Ch5 `sec:eval-comparison`; "why TPE beats grid/random" → Ch5 `sec:eval-hyperopt`.

## A2 — Help-seeking grounding in §2.2.1 — ❌ dropped 2026-06-01
**Dropped (author's call):** the "students hesitate to ask for help" claim recurs in the Introduction and is empirically validated as a survey theme (§5.5), so it is grounded by first-party evidence; an external citation (`ryanAvoidingSeekingHelp2001`) is optional and was not added. Re-open if a literature anchor is wanted later (citekey ready in [[07 Citations — wire orphans + Candidate References]]).
- **Add:** one grounding sentence/citation, e.g. "…students are often reluctant to seek help even when they would benefit from it \cite{ryanAvoidingSeekingHelp2001}". Cite `ryanAvoidingSeekingHelp2001` (new → [[07 Citations — wire orphans + Candidate References]] candidate 4; validate in Zotero first). Primary home §2.2.1; optional one-line echo at the Intro motivating claim (l10) — author's call.
- **Keep out:** nothing implementation here — purely a grounding citation.

## Relocated to Ch5 — wired under [[07 Citations — wire orphans + Candidate References]], not here
- **`breimanRandomForests2001` + `friedmanGreedyFunctionApproximation2001`** (new) → bake-off baselines at `sec:eval-comparison`.
- **`cohenWeightedKappaNominal1968`** (new, weighted κ) → first weighted-κ use at `sec:eval-metrics`.
- **`oecdHandbookConstructingComposite2008` + `saisanaUncertaintySensitivityAnalysis2005`** (orphans) → cutpoint cohort-dependence at `sec:eval-thresholds` / limitations.
- **`liuGEvalNLGEvaluation2023`** (orphan) → LLM-as-rater first mention in §5.4.

## Parked / dropped
- **B2** (empirical-Bayes shrinkage / measurement confidence / missing-data imputation) — *parked*. These are deployed methods, not eval, and already grounded in Ch3 (shrinkage at design l552–563 `\cite{efronSteinsParadoxStatistics1977, morrisParametricEmpiricalBayes1983}`; mean-vs-zero imputation at design l1049 `\cite{little2014statistical}`). Re-open if a fuller §2.2 deployed-method background is wanted; that would wire `gelmanBayesianDataAnalysis2013` (orphan, conjugate-prior framing) + `lord1968statistical` (CTT / measurement confidence).
- **B3** (κ / threshold / agreement-metrics subsection) — *dropped*: pure eval methodology.
- **B5** (Bass layered-architecture grounding, `bassSoftwareArchitecturePractice2012`) — *dropped*: optional, low priority.

## Corrections to earlier drafts of this note
- §2.2.4 is at **l150–156** (not l139–144); A1 is an *edit*, not a new subsection.
- Ch5 cross-refs resolve to labels **`sec:eval-comparison`** (bake-off) and **`sec:eval-thresholds`** (threshold) — not literal "§5.4.3 / §5.4.5".
- `landisMeasurementObserverAgreement1977` and `CoefficientAgreementNominal` (Cohen 1960) are each *already cited once* in `results-and-evaluation.tex` — not pure orphans (a [[07 Citations — wire orphans + Candidate References]] Step-1 detail, no longer a Ch2 concern).

## Themes appendix (Table D) follow-up
With A2 dropped, the only Table D change is: add `hastieElementsStatisticalLearning2009` to the "Model Training and Numerical Optimisation" row, then re-run `python scripts/sync_literature.py`. (Supersedes the earlier "handled in [[02 Proposed Report Edits — structural]] S6" line — S6 predates this ref.)
