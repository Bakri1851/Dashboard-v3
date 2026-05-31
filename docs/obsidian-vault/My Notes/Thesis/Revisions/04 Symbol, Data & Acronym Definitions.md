# 04 — Symbol, Data & Acronym Definitions

Supervisor pt 5: terms and symbols are used before they are defined. ← [[00 Index]]

> **Status — closed 2026-05-31.** Every D-item anchor was re-verified against the live `.tex`; all items (D1–D7) are now applied and the report compiles clean.
>
> **Appendix lettering (compiled PDF, verified via `main.toc`):** `code-snippets` is commented out, so the appendices render as **A** ui-screenshots · **B** detailed-test-results · **C** Notation and Formulae · **D** formulae-derivation · **E** themes-and-references. The Formulae appendix is **Appendix C**.
>
> - **Applied this pass:** **D7a** (front-matter Nomenclature); **D7b** (Appendix-C notation table — fixes the previously-blank Appendix C); **comprehensive Appendix-C formulae** (every model/method, each tagged with the section it is used in); **D6** (Evaluation Metrics subsection added to the body of Ch5); **D5-IRT** (logit-scale clause).
> - **Already present (verified, no edit):** **D2** K/τ/λ (defined at first use), **D3** (signed-weights note), **D4** (forward-ref at `implementation.tex:645`).
> - **Applied this pass (cont.):** **D1** (six data fields), **D2** (configured-scalar paragraph), **D5-BKT** (prior vs running mastery), the **τ split**, and the **cf_threshold=0.90 deployment reconciliation** + K=5 seeding fix (see below).

## ✅ Applied this pass (review-gated, in `Report/`)

### D7a — front-matter Nomenclature (`main.tex`, after `\listoftables`)
`\section*{Nomenclature}` page (acronyms + symbols, one symbol per row, lowercase `p(·)`), with `\addcontentsline`. Symbols verified against the live `.tex`.

### D7b — Appendix-C notation table (`appendix-sections/formulae.tex`)
Bare `\section{Formulae}` → `\section{Notation and Formulae}` (`\label{app:formulae}`) + `tab:notation` parameter dictionary (K=5, τ=0.5, λ=0.3, weights `[0,1]` sum=1 v1 → signed/OLS v2, BKT/IRT learned-MLE; one symbol per row). Defaults verified against `config.py`. **Clears the blank-Appendix-C integrity gap.**

### Comprehensive Appendix-C formulae (`appendix-sections/formulae.tex`)
After `tab:notation`, one `\subsection` per area, each opened with an *"Used in Section~\ref{…}"* tag: Data & derived signals · Baseline struggle · Baseline difficulty · Collaborative filtering · Mistake clustering (TF-IDF/k-means/silhouette/auto-k) · Measurement confidence · IRT (1PL/log-lik/sigmoid-map/2PL) · BKT · Improved struggle · Evaluation metrics. Equations transcribed verbatim from the body, **unlabelled** (no clash). Added `\label{sec: collaborative filtering}` to the CF subsection so it could be cross-referenced.

### D6 — Evaluation Metrics subsection (body, `results-and-evaluation.tex`, `\label{sec:eval-metrics}`)
New `\subsubsection{Evaluation Metrics}` between "Scope of Evaluation" and "Evidence Sources" (before first use, AUC l32). Defines Spearman ρ, MAE (bands, range [0,3]), linear-weighted Cohen's κ, AUC with formulae + glosses + GroupKFold(5)/LOO; cites `spearmanProofMeasurementAssociation1904`, `CoefficientAgreementNominal`, `landisMeasurementObserverAgreement1977`, `fawcettIntroductionROCAnalysis2006`, `hanleyMeaningUseArea1982` (also wires these orphans). Fixes the "metrics appear out of nowhere" concern; the appendix restates the same formulae.

### D5-IRT — logit-scale clause (`design-and-architecture.tex:858`)
"…both are unbounded on the logit (log-odds) scale, so each value is interpretable only relative to the other…". Confirmed against `irt.py:200` (`logit = a·(θ−b)`) and `:302` (`expit(b_raw)→[0,1]`).

## ✅ Already satisfied before this pass (verified live — no edit)
- **D2 — K/τ/λ defined at first use:** `K` `design-and-architecture.tex:531–536` (default 5); `λ` l542 + l564–571 (=0.3, `SMOOTHING_ALPHA`); `τ` l607–608 (=0.5). Weights/η-dominance/ζ-tie-breaker/OLS-refit explained 474–499.
- **D3 — signed v2 weights:** `design-and-architecture.tex:499`.
- **D4 — notation bridge:** `implementation.tex:645` points the capital-letter equation to `tab:struggle-7sig`.

## ✅ Applied (2026-05-31, cont.) — Note 04 closed

### D1 — Data-field definitions (`design-and-architecture.tex`, after l359)
Itemize defining the six record fields from Figure~\ref{fig: data entry}: **module** (the university module), **question** (the lab task), **timestamp** (most recent submission), **user** (anonymised student id), **session** (first-submission time), **XML** payload (a sequence of `<submission>` → `<srep>` student answer + `<feedback>` AI responses).

### D2 — Configured scalar hyper-parameters (`design-and-architecture.tex`, before the CF subsection)
New `\paragraph` gathering K=5, λ=0.3, τ=0.5 (correctness), all hand-set; points to `tab:notation`; cross-refs the Optuna study (K retained at 5; CF elevation τ tuned to ≈0.90).

### D5-BKT (`requirements-specification.tex`, after l112)
Sentence distinguishing the prior `p(L₀)` from the running `p(L)` (updated by Bayes' rule + transition `p(T)`), cross-ref `sec: bkt`. (No "recurrence" wording, per request.)

### τ split (notation table + nomenclature)
The overloaded `τ` is now two rows in both `tab:notation` and the front Nomenclature: **correctness threshold** (incorrectness < τ, 0.5, configured) and **CF elevation threshold** (struggle ≥ τ, deployed 0.90, tuned by Optuna).

### cf_threshold = 0.90 deployment reconciliation (code + whole report)
The deployed dashboard already seeds `cf_threshold ≈ 0.90` from `data/eval/optimised_hyperparams_v2.json` (`runtime_config.defaults()` → `cf.py` → `collab.py`). The report previously said 0.7 in places; now states **0.90 deployed/adopted** throughout (impl §4 l767/l952, eval l320/l341/l361, conclusion l27, design CF l810, `tab:notation`). **Code fix:** the same JSON also seeded `shrinkage_k=0`, which the baseline scorer consumed (`cache.py:196`→`struggle.py:341`); `runtime_config.defaults()` now drops `shrinkage_k` so deployed **K stays 5** — matching the eval recommendation, the design's shrinkage rationale, and the improved model (`improved_struggle.py:297`). Comments in `runtime_config.py`/`schemas.py` updated to match.

## Corrections folded in (2026-05-31)
- **Appendix lettering:** in the compiled PDF the Formulae appendix is **C**, the derivation appendix is **D**, themes is **E** (code-snippets commented out; verified via `main.toc`). The old note's B/C/D/E/F scheme was wrong.
- **MAE is used** (eval l171; abbrev defined `implementation.tex:1027`; also `conclusion.tex:38`) — kept in D6. **Range is [0,3]** on a four-band scale (max band distance = 3), not [0,4].
- **Eval metrics were never written as equations** anywhere — D6 now defines them in the body **and** the appendix lists their formulae, so they no longer appear "out of nowhere".
- **BKT notation is lowercase** `p(·)` in the report — D7a/D7b/appendix lowercased accordingly.
- **Cohen 1968** weighted-κ *proper definition* is **MISSING** from `references.bib` → candidate ref in [[07 Citations — wire orphans + Candidate References]] (#1). D6 cites Cohen 1960 + Landis 1977 for now.
- **Appendix D (formulae-derivation) still empty & `\include`d** → renders blank; populate-or-remove deferred to end of pass per [[00 Index]] open decision.
