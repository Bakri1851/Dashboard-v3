---
phase: writing-brief
status: ready-to-author
created: 2026-05-27
covers: per-section report edits required by the threshold-training + model-class + v1-removal session
companion-of: "[[v2 Threshold Training Handoff]]"
---

# v2 Report Change List — by section (report order)

The **author-from** list: each section gives the brief + the concrete find → replace for the stale lines, with verified numbers. Maps [[v2 Threshold Training Handoff]] (§1–§14) onto the report's *actual* structure. Search by quoted text — line numbers drift. ✓ DONE = already applied.

**Style:** British spelling, declarative, "we propose / we adopt", plain hyphens (`-`, not `---`), no inline `file:line` anchors in prose, no supervisor naming. Design artefacts in Ch3; deployed-system artefacts in Ch4 / Appendix B.

## ⚠ "v1" means two different things — only one is removed
- **V1/V2 = the two STACKS (Streamlit vs React+FastAPI).** The architecture-evolution narrative across `implementation.tex` (tech-stack table, architecture diagram, views-parity, caching, "V2 builds on V1", IRT 1PL→2PL). **Keep it all — the "V2 is the evolution of V1" branding.**
- **v1/v2 = the two MODEL WEIGHT SETS (hand-set vs LLM-trained OLS).** The *only* "v1" being cut from the evaluation. When in doubt: remove the v1 *weights* comparison + the toggle wording — never the stack story.

---

## Ch1 — `introduction.tex`
- ✓ DONE **L108** — "model comparison" dropped from the live-dashboard feature list.
- ✓ DONE **Objective 5 (L64)** — now reads "training the composite weights, scalar hyperparameters and score-to-band thresholds against second-opinion labels…".
- **Contribution bullets** — home in Ch6's "Key Findings Contributions" (not here): (1) systematic empirical validation of *all* v2 pipeline hyperparameters (weights, scalars, AND thresholds) against an LLM 4-band rater, positive + negative findings; (2) the LLM-supervised training methodology + model-class-selection rigour as a core contribution.

## Ch2 — `requirements-specification.tex` (§2.2.4 Modelling Task Difficulty)
- ✓ DONE **IRT one-liner** — added after the IRT sentence: "IRT captures how difficult a question is from the way students respond to it, which is not always the same as how hard the question is to learn or teach." (pre-loads the §5.6 anti-result, plain voice, no jargon.)
- ✓ DONE **Background** — the "Composite Model Training and Optimisation" subsubsection already covers supervised weight-fitting (LR / gradient boosting), LLM-as-rater, and Optuna TPE.

## Ch3 — `design-and-architecture.tex`
- **§3.4.9 Visual Encoding (symbolic tables ~L1028/L1041)** — keep the cutpoints **symbolic** ($t_{s1..3}$); add framing that they are an interpretability-first design choice with empirical calibration deferred to Ch5; forward-reference the §5.4 band-threshold subsection. (Do not paste numbers here.)
- **v1-as-deployed lines (find → replace):**
  - **L265** TAKE OUT: "The weights set above are the baseline model (v1) and remain the system default." → REPLACE: "The weights set above are the initial hand-set values; the deployed system uses the trained v2 weights (Section~\ref{sec:v2-pipeline-design})."
  - **L268** TAKE OUT: "the v1 model is preserved as the deployed default for the system." → REPLACE: "the trained v2 vectors are the deployed default; the hand-set values are retained only as a starting-point baseline."
  - **L796** ("The deployed v1 composite weights …") → past tense: "The original hand-set composite weights … were tuned by trial and error; they were subsequently re-fit (Section~\ref{sec:v2-pipeline-design})."
  - **L798** TAKE OUT: "The v2 weights are exposed through a toggle whilst the v1 vectors remain the deployed default." → REPLACE: "The trained v2 weights are the deployed default; there is no runtime toggle."
- **Expand `sec:v2-pipeline-design` (~L794)** as the canonical home for: the decision to train weights by LLM-supervised OLS vs hand-tuning; the 4-band ordinal target + LLM-rater rationale; forward-ref to the §5.4 model-class validation.

## Ch4 — `implementation.tex`
- ✓ DONE **struggle thresholds (was L664):** now `On Track (0.00-0.102), Minor Issues (0.102-0.203), Struggling (0.203-0.326), Needs Help (0.326-1.00)`.
- ✓ DONE **difficulty thresholds (was L721):** now `Easy (0.00-0.288), Medium (0.288-0.388), Hard (0.388-0.531), Very Hard (0.531-1.00)`.
- **Version-toggle passage (~L954-958, find → replace):** TAKE OUT "Five fields on \texttt{RuntimeConfig} gate the selection: four \texttt{*\_version} string flags … each defaulting to its v1 value." / "When \texttt{hyperparams\_version} is set to \texttt{"v2"} …" / "A missing or corrupt JSON falls back to v1 with a warning logged." / "The toggles are only implemented on the V2 iteration of the dashboard." → REPLACE: "The trained weights and hyperparameters are the deployed default and are applied unconditionally; there is no runtime v1/v2 selector. The shrinkage constant \(K\) and the CF threshold \(\tau\) are seeded on \texttt{RuntimeConfig} from the Optuna-tuned values and remain adjustable. The hand-set v1 weights are retained only as \texttt{config.py} constants for the offline evaluation comparison; a missing or corrupt JSON falls back to those constants with a warning logged." (Keep L961/L967/L970 — V1/V2 *stack* code descriptions.)
- **Settings "Optimised Weights" (~L1254-1256, find → replace):** TAKE OUT "V2 also has an extra Settings section titled "Optimised Weights (v2)", with four select rows … reloads the leaderboard on the next refresh." → REPLACE: "V2 surfaces the trained weights and hyperparameters only as a read-only configuration reference; they are the deployed default and are not user-selectable." Also DELETE L1255 (difficulty-weights selector disabled when irt) and change L1256's "the trained weights replace the v1 defaults at request time once a v2 selection is made" → "the trained weights are applied at request time". (Read-only config card now shows the trained tuples → Appendix B re-shoot.)
- **Views-parity table (~L1133):** TAKE OUT the row `Model Comparison & Baseline vs IRT, baseline vs improved struggle & Yes & Yes \\` → remove it (no longer a shipped view) or set the V2 cell to "Offline notebook".
- **Model Comparison View subsubsection (~L1231-1247):** rewrite to past tense — "built during development, removed from the shipped dashboard, analysis ported to the offline notebook \texttt{model\_comparison.ipynb} on the eval cohort (1306 snapshots / 72 questions)" — and **delete the figure block** (`\IfFileExists{figures/implementation/ui-comparison.png}…` `\begin{figure}`…`\end{figure}`).
- **Expand `sec:v2-training` (~L1014)** as the canonical home for the offline training, citing the **scripts** (not the notebook): weights `optimise_v2_weights.py`; GPT-4o labelling `eval_fetch.py`/`eval_label.py`/`eval_common.py`; Optuna `optimise_hyperparams.py`; thresholds `threshold_search_constrained.py` (+ deployed-composite recalibration `threshold_search_v2composite.py`); bake-offs `model_class_bakeoff.py`/`classifier_bakeoff.py`; plus how trained artefacts load into the live scoring path (config + JSON + `cache.py`). Frame `eval_main.ipynb` as the figure-generation surface, not the training.

## Ch5 — `results-and-evaluation.tex` — largest change (v1 CUT)

**Principle:** v2 is the premiere/deployed model; **§5.4 has NO v1-vs-v2 comparison.** The "better than what?" rigour is the model-class bake-off (trained-vs-trained). The hand-set origin is Ch3/Ch4 design history only.

- **Framing flip:**
  - **L39** TAKE OUT "Whilst the dashboard evaluation is primarily focused on the v1 model, a v2 model is also trained and evaluated…" → REPLACE: "The deployed system is the trained v2 model; this section evaluates it. The hand-set v1 weights are the starting point it evolved from and are not evaluated as a competing model."
  - **§5.4.1 (~L128-141)** — replace the "v1 model outputs / 54% Needs Help / thresholds too aggressive" sentences with the **v2 deployed** band distribution (regenerated `cohort_distributions.png`): struggle **31% On Track / 14% Minor Issues / 15% Struggling / 40% Needs Help**; difficulty **7% Easy / 4% Medium / 22% Hard / 67% Very Hard**. Rename the heading away from "Baseline".
  - **§5.4.2 "Model Comparison" (~L143-228)** — redistribute: baseline-vs-improved struggle → folds into the bake-off / weak-improved-toggle discussion; baseline-vs-IRT difficulty → moves to the §5.6 IRT anti-result. (`comparison_*_scatter.png` are baseline-vs-alternative, not v1-vs-v2 — kept, relocated.)
- **New §5.4 structure:** (1) cohort + inter-rater κ (`kappa.png`); (2) **v2 model outputs + quality** — v2-only weight chart, per-fold ρ (`per_fold_rho_struggle.png`), OLS diagnostic + residuals (`ols_diagnostic_struggle.png`, `residuals_struggle.png`), weight-stability heatmap (`weight_heatmap_struggle.png`), v2-only confusion; (3) **HEADLINE — model-class bake-off** (`model_class_bakeoff.png` + `framing_regression_vs_classification.png`; tables below; combined narrative + "why OLS not RF" defence); (4) Optuna (existing §5.4.3 — keep, reword "v1 default" → "initial hand-set default"); (5) **band-threshold optimisation** (new).
- **Figure swaps (find → replace; the only deletions that touch the build):**
  - **L282** `figures/evaluation/weights_struggle_v1_vs_v2.png` → `figures/evaluation/weights_struggle_v2.png` (+ v2-only signed-weights caption).
  - **L303** `figures/evaluation/pred_vs_obs_v1_v2_struggle.png` → `figures/evaluation/pred_vs_obs_v2_struggle.png` (+ v2-only caption).
  - **L317** `figures/evaluation/negative_findings.png` → `figures/evaluation/negative_findings_v2.png` (+ v2-only caption).
  - (Once swapped, the old `*_v1_vs_v2.png` / paired `negative_findings.png` in `Report/figures/evaluation/` can be deleted.)
- **"why OLS not RF" defence (pre-empt in the bake-off):** RF's edges are within per-fold variance (improved +0.049 gap < 0.5× per-fold std ≈ 0.124-0.136; difficulty +0.011 negligible, RF overfits at n=72 LOO; RF *loses* struggle by −0.023); RF has no interpretable signed weights; improved-struggle is a weak non-default toggle. Frame: OLS is competitive-or-better within noise on every target, wins struggle decisively, and is the only competitive class with interpretable signed weights.
- **NEW band-threshold subsubsection (after the bake-off):** Motivation → Method (brute-force κ-max grid over (c1,c2,c3); GroupKFold(5) struggle n=1306 / LOO difficulty n=72; unconstrained vs constrained) → Findings (4/6 promoted in the original search, Δκ +0.076…+0.175; per-fold std ≤0.03) → cohort caveat. Include the **6-row κ table** (below) as the threshold-training *experiment*, and the framings (constrained-as-default; "pre-registered κ ≥ 0.05" ship rule).
  - **Deployed-threshold recalibration (do not omit):** the deployed dashboard feeds the *v2-OLS composite* (clip(Σ w·signals) ∈ [0,1]) through the thresholds, but the originally-promoted cutpoints were fit on the *v1 baseline* composite — a scale mismatch that classified ~99% below "Needs Help". The shipped `config.py` thresholds were therefore **re-fit on the deployed v2 composite** (`threshold_search_v2composite.py`, constrained CV, every band ≥10% of [0,1]): struggle `(0.102, 0.203, 0.326)` κ +0.038→**+0.384**; difficulty `(0.288, 0.388, 0.531)` κ +0.225→**+0.387**.
  - **Two v2 representations — report the DEPLOYED one (band-consistency decision):** ranking ρ is rank-equivalent across both (rank-corr 0.994), so ρ +0.588 stands. Band agreement is scale-dependent: report the **deployed composite + recalibrated thresholds = 47.3% exact-band / 71.7% within-1 (κ +0.384)**, not the [0,3] StandardScaler predictor's 55.5%. ⏳ *the `confusion_bands` figure switch to the deployed composite is being executed in a separate chat.*
- **NEW IRT-difficulty anti-result in §5.6:** negative κ at hand-set (−0.016) and trained (−0.024); IRT fits response-pattern difficulty, not the LLM's teaching-difficulty; ρ +0.345 vs the composite, top-10 overlap 1/10; IRT toggle retained, baseline composite is the production default. Note IRT is **not** in the bake-off (latent-trait model on the response matrix, not a regression on the composite features).
- **§5.6 Tradeoffs (~L357):** the planned 38%/68% & κ +0.198 are stale; report the deployed-composite band agreement (47.3% / 71.7%) and pull κ from `results.md`. No v1-vs-v2 band comparison.

## Ch6 — `conclusion.tex` (skeleton)
- **Future Work** — (a) joint weight + cutpoint optimisation via ordinal logistic regression (proportional-odds / `mord` / `statsmodels.OrderedModel`); (b) cohort-balanced re-evaluation (0 LLM-labelled "Easy" questions; only 5.8% "On Track" snapshots → lowest bands cohort-specific empty); (c) per-semester threshold re-tuning as a deployment-side ML-maintenance concern.
- **Key Findings / Contributions** — the two Ch1 bullets above.

## Appendix B — `ui-screenshots.tex` (skeleton)
- Re-shoot the Settings-view screenshot (no weight-version card now; the read-only config card shows the trained threshold tuples). Figure-capture task.

## Appendix E — `formulae.tex` (skeleton)
- *(Optional)* linear-weighted Cohen's κ formula + brute-force search pseudo-code.

---

## Reference — paste-ready tables (verified on disk)

**6-row band-threshold κ** — source `data/eval/experiments/threshold_search_cv.json` (the threshold-training *experiment*):

| Model | Hand-set κ | Unconstrained CV κ | Constrained CV κ | Δ |
|---|---|---|---|---|
| Struggle baseline composite | +0.303 | +0.402 | **+0.390** | +0.087 ✓ |
| Struggle improved (BKT+IRT) | +0.105 | +0.134 | +0.103 | −0.002 ✗ retain |
| Struggle v2 OLS [0,3] | +0.380 | +0.483 | **+0.456** | +0.076 ✓ |
| Difficulty baseline composite | +0.065 | +0.465 | **+0.239** | +0.175 ✓ |
| Difficulty IRT Rasch | −0.016 | −0.069 | −0.024 | −0.007 ✗ retain |
| Difficulty v2 OLS [0,3] | +0.225 | +0.436 | **+0.393** | +0.168 ✓ |

**Shipped cutpoints (config.py, recalibrated on the deployed v2 composite):** struggle `(0.102, 0.203, 0.326)` [0,1] (κ +0.384); difficulty `(0.288, 0.388, 0.531)` [0,1] (κ +0.387). The 6-row table's `(0.315,0.505,0.605)`/`(0.363,0.463,0.587)` were the baseline-composite fit (superseded for deployment); the `[0,3]` eval-side cutpoints `(1.22,1.78,2.09)`/`(1.88,2.19,2.69)` drove the old confusion matrix.

**Model-class bake-off** — source `model_class_bakeoff.json` / `classifier_bakeoff.json` (4-dp verified):

| Target | OLS ρ | Best alt ρ | OLS raw κ | Best-classifier κ |
|---|---|---|---|---|
| Struggle | +0.588 | RF +0.565 | +0.380 | RF +0.475 |
| Difficulty | +0.469 | RF +0.479 | +0.225 | GB +0.444 |
| Improved | +0.201 | RF +0.250 | +0.007 | GB +0.129 |

## Reference — number / asset flags
1. **§14.2 difficulty κ inconsistency** — the handoff framing table cites "+0.436" for difficulty OLS-with-trained-thresholds, but that is the *unconstrained* value; the shipped *constrained* value is **+0.393**. Use the constrained value consistently.
2. **Band agreement = deployed composite (47.3% / 71.7%)** — not the [0,3] predictor's 55.5%; the `confusion_bands` figure switch is being done in a separate chat.
3. **§5.6.1 denominator bug is MOOT** — the n=42443 model-disagreement content + `model_disagreement.png` are dropped under the v1-cut; not cited, so no fix needed.
4. **`results.md`** is the canonical eval record, left as-is; its v1-vs-v2 sections stay for provenance but are not lifted into the report.

## Reference — figure status (Parts D/E, done)
- v2-only figures regenerated in `data/eval/figures/` and copied to `Report/figures/evaluation/`: `weights_struggle_v2.png`, `pred_vs_obs_v2_struggle.png`, `negative_findings_v2.png`, v2-only `confusion_bands.png`, `cohort_distributions.png` (v2 deployed model), plus `model_class_bakeoff.png` + `framing_regression_vs_classification.png` + `kappa.png`.
- The three currently-cited v1-vs-v2 PNGs are removed **once the figure-include swaps above are applied** — coordinate so the build never has a dangling `\includegraphics`.

---

## 2026-05-28 — Ch5 session-complete sync

The Ch5 work briefed above has been shipped in addition to the §5.5 survey and §5.6 discussion blocks. The list below records what actually landed in `Report/main-sections/results-and-evaluation.tex` so this note matches the working tree.

### Ch5 status — applied this session

#### §5.4 (Quantitative Results) — DONE

- ✓ Cohort characterisation prose + regenerated 2×2 `cohort_distributions.png` (struggle top row; deployed v2 model + recalibrated thresholds; 31/14/15/40% struggle, 7/4/22/67% difficulty).
- ✓ §5.4.2 Struggle Model Outputs and Quality (weight chart + heatmap + OLS diagnostic + per-fold ρ figures, all v2-only).
- ✓ §5.4.3 Model Comparison (`model_class_bakeoff.png` uniform single-colour bars + `framing_regression_vs_classification.png` with cleaned suptitle + `comparison_struggle_scatter.png` + top-10 table; OLS-vs-classifier framing prose).
- ✓ §5.4.4 Hyperparameter optimisation — prose-vs-table numeric reconciliation (K best 1→0; Δρ K +0.013→+0.009; Δρ τ +0.200→+0.160) + relabel ("v1 default" → "initial hand-set default", "v2 best" → "tuned best") in both prose and `tab:eval-hyperparams` header.
- ✓ §5.4.5 Band-threshold optimisation (NEW subsection): motivation + method + 6-row constrained-CV κ `tab:eval-thresholds` + promotion rule (Δκ ≥ +0.05, 4 of 6 promoted) + deployed-cutpoint recalibration paragraph + cohort caveat.
- ✓ Ch4 anchors `\label{sec:thresholds-struggle}` and `\label{sec:thresholds-difficulty}` added next to the deployed cutpoint sentences at `implementation.tex` L664 / L721, so the §5.4.5 motivation `\ref{}`s resolve.

#### §5.5 (Survey) — DONE

- ✓ Three new figures (replacing the original 2 that covered Q3+Q7+Q9 / Q5+Q6): `eval-survey-baseline.png` (Q2 + Q3 for §5.5.2), `eval-survey-interpretability-trust.png` (Q5 + Q6 matrix + Q7 single Likert, two-panel for §5.5.3), `eval-survey-comfort.png` (Q9 alone for §5.5.4). Generated by the restructured `notebooks/survey_main.ipynb`. Old `eval-survey-likert.png` and `eval-survey-clarity-intuitiveness.png` deleted from `Report/figures/evaluation/`.
- ✓ Prose blocks §5.5.1 (instrument + n=10 demographics), §5.5.2 (Q2 + Q3 + Q4 themes), §5.5.3 (Q5 + Q6 + Q7), §5.5.4 (Q9 + Q8 + Q10), §5.5.5 (Q11 + triangulation back to §5.4 / §5.6). User-authored / user-restyled in their voice.
- ✓ NEW `tab:eval-survey-themes` at end of §5.5.5: Q4 (Staff shortage 4, Identifying student need 3, Help-seeking reluctance 3), Q8 (Surveillance discomfort 3, Quantifiability limits 2), Q10 (Name visibility 2, Consent 1, Lecturer bias 1, Data-use scope 1), Q11 (Cross-session aggregation 1, Criteria transparency 1). Excludes one Q10 meta-comment about Q9 — flagged in caption.

#### §5.6 (Discussion) — DONE

- ✓ §5.6.1 IRT anti-result prose: negative κ at hand-set (−0.016) and trained (−0.024), composite ρ +0.468 vs IRT ρ +0.345, top-10 overlap 1/10. Paragraph 2 explicitly grounded in what `scripts/eval_label.py` actually shows the LLM rater (per-question aggregate signals — NOT question text; a draft that claimed otherwise was caught as a hallucination and corrected before applying).
- ✓ §5.6.2 Tradeoffs prose: `\paragraph{Rater fidelity}` (κ_lin +0.198, κ_quad +0.262, exact 38%, within-1 68% on the 50-snapshot calibration) + `\paragraph{Model-versus-rater band agreement}` (47.3% / 71.7%, κ struggle +0.379, κ difficulty +0.225 against the rater).
- ✓ §5.6.3 Limitations prose: three paragraphs — cohort skew (47% NH / 72% VH); difficulty n=72 forces LOO CV; OpenAI scorer fallback midpoint on most of the 42,443 submissions is the highest-leverage future change.

#### §5.1 / §5.2 / §5.3 — stale TODOs swept

- ✓ Removed 17 stale `% TODO: 5.x.y prose block` comments from across §5.1.1–§5.6.3 where prose now exists. Only the top-of-file `% TODO (Bakri): READ-THROUGH PASS` block remains — that block also points at this vault note as a roadmap-sync reminder.

### What this note does NOT cover (deferred to a separate chat)

- **Ch6 Conclusion** — Future Work bullets, Key Findings, contributions. User is doing this in another chat.
- **Appendix B re-shoot** — Settings-view screenshot still shows the removed weight-version card. Outstanding.
- **Appendix E formulae** — optional κ formula + brute-force search pseudo-code.
- **Cosmetic backlog** in Writing Roadmap (Ch6 §6.2 heading, Ch3 §3.3.4 wordy heading, Ch4 §4.12/§4.13 overlap).
