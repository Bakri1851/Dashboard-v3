# 06 — Background Lit-Review Expansion (author writes)

Supervisor pt 15: a lot of model-training content was added to Ch3–5 that Ch2 barely covers. Expand/​add the subsections below. Most sources already exist in `references.bib` (see [[07 Citations — wire orphans + Candidate References]]); only a few are genuinely new. ← [[00 Index]]

## B1. Expand §2.2.4 "Composite Model Training and Optimisation"
Currently ~5 sentences (`requirements-specification.tex` l139–144). Expand to cover, with citations:
- **Supervised refinement of composite weights** — that hand-set weights can be refit against labels; introduce **linear regression / ordinary least squares (OLS)** as the chosen estimator (the user specifically wants OLS named here, since it trained the deployed model). Cite **Hastie, Tibshirani & Friedman, ESL (2009)** (new — [[07 Citations — wire orphans + Candidate References]]) for OLS / linear regression.
- **Model-class alternatives** — random forest and gradient boosting as non-linear baselines benchmarked against OLS. Cite **Breiman (2001)** and **Friedman (2001)** (new). (This also retro-grounds the §5.4.3 bake-off — see [[07 Citations — wire orphans + Candidate References]].)
- **LLM-as-judge / second-opinion labelling** — already cited (`gilardiChatGPTOutperformsCrowd2023`, `chiangCanLargeLanguage2023`, `zhengJudgingLLMasaJudgeMTBench2023`); add `liuGEvalNLGEvaluation2023` (orphan) as the on-point "LLM as graded-rubric evaluator" reference.
- **Bayesian hyperparameter optimisation (TPE)** — already cited (`NIPS2011_86e8f7ab`, `akibaOptunaNextgenerationHyperparameter2019`); add 1–2 sentences on *why* TPE over grid/random search (models the hyperparameter→objective relationship, samples promising candidates, efficient at small N).

## B2. New subsection: "Shrinkage, Measurement Confidence & Missing Data"
After §2.2.4. Three short parts, mostly orphan-wiring:
- **Empirical-Bayes / James–Stein shrinkage** — open with a plain-language sentence (shrinkage pulls noisy, sparse estimates toward a prior / class mean to stabilise them), then the fixed n/(n+K) pseudo-count form. Cite `efronSteinsParadoxStatistics1977`, `morrisParametricEmpiricalBayes1983` (both already cited in Ch3) + `gelmanBayesianDataAnalysis2013` (orphan) for the conjugate-prior framing.
- **Classical test theory / measurement confidence** — explain CTT as a framework for quantifying score uncertainty, and that the dashboard's κ-confidence derives from it. Cite `lord1968statistical` (already cited).
- **Missing-data handling** — why missing data arises in lab sessions (BKT mastery uncovered for some students), mean imputation as the chosen baseline (vs zero imputation, which biases the mastery gap upward), under a missing-at-random assumption, with alternatives (forward-fill, kNN, multiple imputation). Cite `little2014statistical` (currently cited once at design l783) by name and connect to the MAR assumption.

## B3. New subsection: "Threshold Optimisation & Agreement Metrics"
After B2 (or fold into B1). Cover:
- **Cohen's κ — standard vs linear-weighted** — ordinal distance-aware penalties; why linear weighting suits the 4-band scale. Cite **Cohen (1968)** (new — weighted variant; the `.bib` currently has only Cohen 1960 `CoefficientAgreementNominal`) + `landisMeasurementObserverAgreement1977` (orphan) for the interpretation bands ("fair/moderate").
- **Threshold / cutpoint search methodology** — grid search maximising weighted κ under monotonicity + min-band-width constraints, cross-validated; ties to §5.4.5.
- **Composite-indicator sensitivity** — that cutpoints are cohort-dependent and should be re-tuned. Cite `oecdHandbookConstructingComposite2008` + `saisanaUncertaintySensitivityAnalysis2005` (both orphans).

## B4. Help-seeking grounding (load-bearing in Intro + Survey)
- The "students hesitate to ask for help" claim recurs in the Introduction and as a validated survey theme (§5.5). Ground it once in Ch2 (or Intro) with **Ryan, Pintrich & Midgley (2001)** (new — [[07 Citations — wire orphans + Candidate References]]).

## B5. Software-architecture grounding (optional)
- The layered/three-tier architecture claim (Ch3 l6–7) is currently uncited. Optionally cite **Bass, Clements & Kazman (2012)** (new) for layered-style benefits. Low priority.

> Themes appendix (Table D) must gain rows for all of the above — handled in [[02 Proposed Report Edits — structural]] S6.
