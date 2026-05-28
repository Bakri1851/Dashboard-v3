---
phase: writing-brief
status: draft-prose
created: 2026-05-28
covers: thesis abstract for Report/main.tex (currently empty at L91-93)
companion-of: "[[Ch6 Conclusion Draft]]"
---

# Abstract - Draft Prose

Author-from draft for the `\begin{abstract}...\end{abstract}` block at `Report/main.tex` L91-93. Restyle into voice; paste in place of the empty block.

Target length is ~300 words across two paragraphs: paragraph 1 = problem + system; paragraph 2 = methodology + key results + contribution framing. All numbers verbatim from `Report/main-sections/results-and-evaluation.tex` / `Report/main-sections/conclusion.tex` §6.1 Para 3.

---

```tex
\begin{abstract}

University computer labs are fast-paced environments in which instructors and lab assistants cannot reliably see, in real time, which students are struggling and which questions are causing the most difficulty across a session of several dozen to over a hundred concurrent learners.
This thesis presents a real-time learning analytics dashboard, deployed as a React and FastAPI application, that ingests live submission data and surfaces interpretable struggle and difficulty rankings alongside a mistake-cluster view, a collaborative-filtering recommender, advanced models based on Item Response Theory and Bayesian Knowledge Tracing, and a Retrieval-Augmented Generation feedback panel.
A second route on the same process hosts a mobile lab-assistant interface, with cross-component coordination through a file-locked shared session state.

The composite scoring pipeline was validated end-to-end against second-opinion labels from a large language model rater, covering composite weights, two scalar hyperparameters, and the score-to-band thresholds.
The composite weights were refit by ordinary least-squares regression chosen on the basis of a model-class bake-off against random forest, gradient boosting, and histogram gradient boosting; the Bayesian shrinkage constant and the collaborative-filtering threshold were tuned by Tree-structured Parzen Estimator across fifty-trial Optuna studies; and the band thresholds were trained by brute-force linear-weighted Cohen's $\kappa$ maximisation under constrained cross-validation.
Against the rater's four-band rating, the deployed composite achieved Spearman $\rho = +0.588$ on the struggle target and $\rho = +0.469$ on difficulty, with linear-weighted Cohen's $\kappa = +0.384$ for struggle and $\kappa = +0.387$ for difficulty at the recalibrated cutpoints.
A 2PL Item Response Theory difficulty model was evaluated alongside the composite and retained as a complementary view but not promoted to the deployed scorer; its negative finding, with $\kappa = -0.024$ at trained thresholds and a top-ten hardest overlap of one question in ten against the composite, is reported as a positive contribution of the systematic methodology rather than as a failure.

\end{abstract}
```

---

## Notes on what's in and what isn't

- **In:** problem framing (Ch1 §1.1), deployed-system summary (Ch6 §6.1 Para 1), full validation methodology (weights + scalars + thresholds), headline ρ and κ numbers (Ch6 §6.1 Para 3 + §6.2 Contribution 1), IRT anti-result as positive-contribution framing.
- **Out:** survey results (Q3/Q5/Q6/Q7 distributions are §5.5 territory and would inflate the abstract); RAG-feedback evaluation specifics; V1/V2 stack-evolution narrative (one passing mention of "React and FastAPI" carries it); cohort sample sizes ($n=1{,}306$, $n=72$) - left for §5.4; specific package names like Optuna are kept because they are technique-identifying, while sklearn / FastAPI internals are not.
- **British spellings used:** "modelling", "behaviour" not present but watch on restyle; "recognise" not present; "optimisation" via Optuna only as proper noun.
- **House-style adherence:** single hyphens, semicolons where chained clauses warrant them, no hedging, no supervisor naming, V2 named once without dwelling on the V1 contrast.

## If you want it shorter (one paragraph, ~180-220 words)

Two trims that hold the load-bearing content:
1. Drop the mobile-route sentence (last sentence of paragraph 1).
2. Compress the methodology sentence into a single clause: "validated end-to-end against second-opinion labels from a large language model rater across weights, two scalar hyperparameters, and the score-to-band thresholds, with model-class selection via a bake-off against random forest and gradient-boosting alternatives."

## If you want it longer (~400 words, three paragraphs)

Add a third paragraph between the existing two, covering Ch5 §5.5 survey corroboration: "An eleven-question survey of ten respondents corroborated three of the four quantitative findings: 60% of respondents found identifying struggling students 'not easy' in current labs, 9 of 10 rated both the underlying scores and the four-band labels intuitive, and a 70/10/20 split on trust supported the advisory rather than autonomous use the dashboard is designed for."
