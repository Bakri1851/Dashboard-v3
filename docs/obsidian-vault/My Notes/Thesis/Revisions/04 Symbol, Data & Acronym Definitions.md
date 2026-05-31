# 04 — Symbol, Data & Acronym Definitions (author writes)

Supervisor pt 5: terms and symbols are used before they are defined. Three clusters below + a document-level acronym list. ← [[00 Index]]

## D1. Data Definitions block (module / question / timestamp / session / user)
- **Where:** `design-and-architecture.tex` Data Endpoint subsection, after l123–124, before `fig:data entry` (l128).
- **Write:** define each field once, plainly — **module** (the university course/unit identifier, e.g. 25COA122); **question** (an individual lab task); **timestamp** (submission datetime); **user** (anonymised student identifier); **session** (a contiguous period of student engagement, bounded by submission timestamps). A small definitions table is cleanest. The supervisor explicitly flagged these as undefined.

## D2. Parameters paragraph after the struggle composite
- **Where:** after Equation (3) / `tab: struggle weights` (l228–291).
- **Write:** explain the seven weights (α,β,γ,δ,η,ζ,θ) — non-negative convex weights summing to 1.0 in v1 (hand-set; note η=0.38 dominance because recent incorrectness is the strongest within-session signal, and ζ=0.05 is a small tie-breaker), refit by OLS in v2. Then define the scalars: **K** (Bayesian shrinkage strength / prior pseudo-count, K=5 default), **τ** (correctness threshold, state range τ∈[0,1], 0.5 a neutral midpoint), **λ** (EWMA smoothing rate, 0.3). For each, say whether it is *learned* or *configured* and how it is *normalised*.

## D3. Promote the "v2 weights are signed / break convexity" note
- **Where:** `design-and-architecture.tex` l266 (currently buried mid-paragraph).
- **Write:** a clear sentence right after the v1 defaults (~l256): the v2 OLS-trained vectors are **signed** and do **not** satisfy the convex-combination constraint, and are rescaled by min-max normalisation before band classification.

## D4. Notation bridge (Design hat/tilde ↔ Implementation capitals)
- **Where:** one sentence in `design-and-architecture.tex` ~l204, and one in `implementation.tex` before l638.
- **Write:** state up front that the Implementation chapter's capital-letter shorthand (N, T, I, R, A, D, Rep) denotes the same quantities as Ch3's hat/tilde symbols, pointing to `tab:struggle-7sig` — currently the mapping only appears *after* the formulas.

## D5. IRT / BKT symbol clarifications
- **IRT** (`design-and-architecture.tex` l623–631): add a sentence that θ_s (ability) and β_q (difficulty) are **unbounded on the logit scale**, interpretation is relative, identifiability resolved by anchoring (already at l642).
- **BKT** (`requirements-specification.tex` l107–112): distinguish P(L₀) (initial mastery) from P(L_t) (mastery after t opportunities); rewrite the prediction equation with P(L_t); add a line on the Bayesian posterior update (cross-ref the Appendix F derivation if populated).

## D6. New "Evaluation Metrics" subsection (single fix for a big cluster)
- **Where:** `results-and-evaluation.tex`, new subsection after Scope of Evaluation (~l17), before first metric use at l149.
- **Write:** brief definitions of every metric the chapter uses — **Spearman ρ** (rank correlation, range [−1,+1], higher = better rank agreement); **MAE** (mean absolute band-distance error, units = bands, range [0,4] on the 4-band scale); **linear-weighted Cohen's κ** (band agreement; *linear* weighting penalises off-by-one less than off-by-two, reflecting the ordinal scale — vs *quadratic*); **AUC** (BKT predictive diagnostic). Define **GroupKFold(5)** (keeps same-session rows together across train/validation) vs **leave-one-out**; and first-use of **2PL**, **L1-normalised**, **b_q**, **w_M/w_B**.
- This single subsection clears findings D5-04/12/13, E-09/12/13/14, C1-17.
- **Cite here:** Spearman → `spearmanProofMeasurementAssociation1904`; weighted κ + interpretation bands → `CoefficientAgreementNominal` (Cohen 1960) + `landisMeasurementObserverAgreement1977`; AUC → `fawcettIntroductionROCAnalysis2006` / `hanleyMeaningUseArea1982` (all orphans, see [[07 Citations — wire orphans + Candidate References]]). Weighted-κ definition proper → new ref **Cohen 1968** ([[07 Citations — wire orphans + Candidate References]]).

## D7. Document-level nomenclature / acronym list (examiner gap)
- **Where:** after the ToC / lists of figures in `main.tex`.
- **Write:** a one-page nomenclature table — acronyms (IRT, BKT, RAG, OLS, TPE, EWMA, ANN, HNSW, MLE, AUC, MAE, TF-IDF, CF, FR/NFR, SPA, EdTech) and the core symbols (the struggle/difficulty signal subscripts; α–θ weights; K, τ, λ; P(L₀)/P(T)/P(G)/P(S); θ_s/β_q/α_q). Resolves the abstract-acronym issue (I11 in [[01 Integrity & Consistency Fixes]]) at the document level.
