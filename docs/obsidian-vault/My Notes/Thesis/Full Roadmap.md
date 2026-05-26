# Full Roadmap

<!-- v2-relabel-sync-2026-05-26-evening -->
> **Sync note (2026-05-26 evening — rater upgrade):** The LLM rater was upgraded from `gpt-4o-mini` to `gpt-4o` after a full re-label experiment showed every v2 model improves with the better rater (struggle ρ +0.573 → **+0.588**; difficulty ρ +0.287 → **+0.468** — biggest single gain; improved-struggle ρ +0.168 → **+0.201**, now matching the non-linear RandomForest ceiling). All ρ values below reflect the upgraded labels. Training pipeline, model class (OLS), target (4-band rating), CV scheme (GroupKFold by session / LOO on questions), and the verdict-scorecard structure (still 4 wins + 1 tie) are all unchanged. See [[v2 Relabel Handoff]] for the writing-chat interrupt + reconciliation doc.

<!-- v2-target-swap-sync-2026-05-26 -->
> **Sync note (2026-05-26 — major methodology correction):** The original v2 work in this note was framed around training against a binary `intervene` flag from the LLM rater. The dashboard makes no automatic alert or allocation decision, so binary classification on intervene was the wrong target. **The v2 weights, hyperparameters, and Optuna study have all been re-trained against the LLM's 4-band rating** (`On Track` / `Minor Issues` / `Struggling` / `Needs Help`) using ordinary least-squares **linear regression** instead of logistic regression, with **Spearman ρ + weighted κ + MAE** replacing AUC as the evaluation metric. Under the corrected target the verdict scorecard becomes **4 positive findings + 1 tie** (was "2 positive + 2 negative + 1 tie" — the previous negative findings for difficulty and improved-struggle were artefacts of the wrong target). Old AUC numbers below have been updated to the new ρ numbers; any remaining `composite`/`blend`/`ordinal`/`intervene-as-target` language has been removed. See `data/eval/results.md` for the authoritative current numbers.

Combined coding + writing order for final submission. Work through this top to bottom — each item unblocks the next. For detailed specs see [[Coding Roadmap]] (coding) and [[Writing Roadmap]] (writing).

Related: [[Coding Roadmap]], [[Writing Roadmap]], [[Rewrite Queue]], [[Report Sync]], [[Evidence Bank]]

---

## Phase 0-8 v2 evaluation additions (2026-05-25)

Single index of every new line item that arose from the v2 weights + Optuna + Settings-toggle work. Each entry is also embedded in its natural step below; this block exists so a reviewer can scan the Phase 0-8 backlog at a glance. Master spec for **every cross-chapter addition** (Ch2 + Ch3 + Ch4 + Ch5 + Ch6): [[v2 Empirical Refinement Brief]]. Supporting ledgers: [[Evaluation PoC Handoff]] §13 (verdict scorecard), [[Evidence Bank]] §2026-05-25 (artefact register), [[Figures and Tables]] §2026-05-25 (figure + table inventory, trimmed 11→6 figures), [[Future Work Inventory]] items #3 / #1a / #1b (closed + new residual entries).

| Step | New line item | Brief reference | Status |
| --- | --- | --- | --- |
| 3 | Ch3: ~120-word v2 empirical-refinement paragraph after `design-and-architecture.tex:259` | Brief §1 | Pending writing chat |
| 4 | Ch1: optional 1-sentence iterative-refinement note in §1.2 Proposed Solution or §1.5 Project Approach | — | Optional |
| 4 | Ch2: ~120-word paragraph in §2.2.1 (or new §2.2.x) on supervised weight fitting + Bayesian hyperparam search + LLM-as-rater methodology with specific bibkeys | Brief §5 | Pending writing chat |
| 5 | Ch4: ~90-word v2 toggle paragraph after `implementation.tex:952` (improved model defaults) | Brief §2 insertion 1 | Pending writing chat |
| 5 | Ch4: 3-sentence "Optimised Weights (v2)" Settings paragraph near §4.9.6 | Brief §2 insertion 2 | Pending writing chat |
| 6 | Ch5 §5.4 **methodology preamble** (~150 words) — which models trained vs evaluated only, CV scheme rationale, LR + L2 default, two-Ks footnote | Brief §4 | Pending writing chat |
| 6 | Ch5 §5.4.9: new `\subsubsection` for weaker positive findings (difficulty + improved model) with `\label{sec:eval-v2-negative}` | Brief §3 | Pending writing chat |
| 6 | Ch5 §5.4.10: new `\subsubsection` for Optuna TPE hyperparams with `\label{sec:eval-v2-hyperparams}` | Brief §3 | Pending writing chat |
| 6 | Ch5 §5.4.1 / §5.4.2 / §5.4.3 / §5.6.1: prose for cohort band-calibration finding, κ block, struggle headline ρ +0.588, v1↔v2 disagreement + verdict scorecard | Brief §3 | Pending writing chat |
| 6 | Ch5 figures: copy **6 essential PNGs** (trimmed from 11) from `data/eval/figures/` → `Report/figures/evaluation/`; insert `\includegraphics` lines | Brief §3 figures inventory + [[Figures and Tables]] §2026-05-25 | Pending |
| 6 | Ch5 tables: lift 6 tables verbatim from `data/eval/results.md` + 1 verdict scorecard from [[Evaluation PoC Handoff]] §13; convert Markdown → `tabularx` | Brief §3 tables inventory | Pending writing chat |
| 7 | Ch6 §6.2 Contributions: add iterative empirical refinement of weights as a named contribution (verdict scorecard as evidence) | Brief §6a | Pending writing chat |
| 7 | Ch6 §6.3 Future Work: close item #3 (supervised weight optimisation now done); add #1a (LLM-rater κ limitation) + #1b (Optuna τ boundary + deferred BKT priors) | Brief §6b + [[Future Work Inventory]] §1, §1a, §1b | Pending writing chat |
| 8 | Appendix B: SettingsView "Optimised Weights (v2)" screenshot with all four toggles visible (ok/warn variants per Phase 4 findings) | — | Pending screenshot |
| 8a | Figures backlog: 11-figure Ch5 evaluation sub-block | [[Figures and Tables]] §2026-05-25 | Pending |
| 9 | Appendix C: add missing `\label{app:detailed-test-results}` at top of `detailed-test-results.tex` (Ch5 §5.1.2 references it) | — | One-line fix |
| 9 | Appendix C: lift v2 evaluation tables — per-fold AUC detail, full κ report, Optuna per-trial highlights, full v2 weight vectors with std | Brief §3 | Pending writing chat |
| 10 | Appendix E: L2-regularised LR objective; GroupKFold CV procedure; Cohen's κ family (unweighted + linear-weighted + quadratic-weighted) | — | Pending writing chat |
| 10 | Appendix F: note that v2 LR weights are signed (do not satisfy the v1 convex-combination constraint); brief derivation of why this is deliberate | — | Pending writing chat |
| 11 | Appendix A: 4 new Phase 0-8 code-snippet candidates (LR fit, Optuna study, runtime_config v2 loader, SettingsView toggle pattern) | — | Pending |
| 12 | Polish: Zotero imports for 3 pending bibkeys (Landis & Koch 1977, Bergstra 2011 TPE, Akiba 2019 Optuna) | — | User does via Better BibTeX |
| 12 | Polish: run `python scripts/sync_literature.py` after the new `\cite{}` calls land in `.tex` to flip 🟡 → ✅ | — | One command |
| 12 | Polish: refresh `docs/recap_toolkit/dashboard_v3_toolkit.html` panels (Status, Section Plan, Roadmap, Literature) | — | Pending |
| 12 | Polish: rebuild `graphify-out/` after `code2/backend/` changes | — | One command |

**Verdict scorecard headline** (referenced everywhere above):

| Component | Winner | Numbers | Phase |
| --- | --- | --- | --- |
| Struggle model (7 OLS weights) | **v2** | ρ +0.588 [+0.490, +0.686] (v1 ρ +0.471) | 4a |
| Difficulty model (5 OLS weights) | **v2** | ρ +0.468 (v1 baseline near-flat) — weak but positive | 4b |
| Improved-struggle model (3 OLS weights) | **v2** | ρ +0.201 (v1 baseline near-flat); still weaker than struggle alone | 4c |
| Shrinkage K (scalar) | **tied** | Δ +0.009 within noise (K=0 best) | 4d |
| CF threshold τ (scalar) | **v2** | Δ +0.160 (ρ +0.306 → +0.466, τ=0.900 best) | 4d |

Four positive findings (struggle weights, difficulty weights, improved-struggle weights, CF τ) + one tie (K). All three trained weight vectors outrank their v1 defaults on the 4-band rating; the τ tuning lifts CF rank correlation by Δ +0.160; only K is within fold-variance noise.

---

## Why this order

Rewrites of existing chapters (Ch3, Ch1&2, Ch4) must come before new chapters (Ch5, Ch6) so the implementation narrative is settled before evaluation is written. Ch4 is placed after Ch3 and Ch1&2 because the code is still subject to minor change — writing Ch4 last among the rewrites means it describes the final system. All appendices are grouped at the end, once chapter content is complete and stable, so screenshots and test evidence capture the truly final state.

Phases 10 and 11 are explicitly out of scope for this submission and will be documented in Ch6 §6.3 Future Work. Phase 9 (RAG + ChromaDB) is a special case — *code* is complete (`rag.py`), so its *written coverage* (Ch4 implementation description + Ch2 RAG literature review subsection) is in scope; only its *empirical evaluation* is deferred to Ch6 §6.3. Attempting large new coding phases with 41 days remaining and Ch4/Ch5/Ch6 unwritten would risk the submission. Phase 6 is stretch only.

---

## The order

### 1. Phase 7 — Surface computed-but-hidden data `Coding · Small`

Quick win. Two features are computed every run but produce no visible output — fix this before screenshots so Appendix B captures the live features.

- [x] Add confidence indicator next to incorrectness values in question drill-down (`ui/components.py`)
  - confidence dot added to question drill-down — green/amber/grey by threshold, mean confidence across question's submissions
- [x] Decide on temporal smoothing: activate `SMOOTHING_ENABLED = True` in `config.py` or remove the stub
  - temporal smoothing activated (SMOOTHING_ENABLED = True, α = 0.3); settings toggle added following cf_enabled pattern

*Unblocks: accurate screenshots in step 3.*

---

### 2. Phase 5 — Comparison UI `Coding · Large`

The biggest remaining coding task. Produces the model comparison view needed for Ch5 evaluation evidence.

- [x] `comparison_view()` in `ui/views.py`
- [x] `render_comparison_scatter()`, `render_comparison_table()`, `render_agreement_summary()` in `ui/components.py`
- [x] "Model Comparison" routing in `instructor_app.py`
- [x] Settings sub-panel: `improved_models_enabled` toggle + sub-toggles + BKT sliders

*Unblocks: Ch5 model comparison evidence, Appendix B comparison screenshots.*

---

### 3. Ch3 — Design updates `Writing · Medium`

Surgical edits — the chapter structure is solid, specific sections need updating. Where figures reference Appendix B screenshots, insert `[TODO: insert figure]` placeholders; these will be replaced at step 8.

- [x] Update struggle formula to 7 components + Bayesian shrinkage (was 5 in thesis) — *Done 2026-05-18; §3.3.1 closed.*
- [x] Update difficulty formula to 5 components (was 4 in thesis) — *Done 2026-05-19; §3.3.3 closed.*
- [~] Reframe §3.6.2 Figma mockups — *updated 2026-05-19. Mockups stay in Ch3 as design artifacts (correct placement); not replaced by screenshots. Typo pass on §3.6 done; caveat-softening deferred to chapter-wide design-vs-implementation reframe pass after Step 3 closes.*
- [x] Update CF section — it is implemented, not "to be implemented" — *Done 2026-05-19; §3.3.4 closed.*
- [x] Add sections for IRT, BKT, improved struggle, mistake clustering — *All four done 2026-05-19. §3.3.5 (clustering), §3.4.2 (IRT), §3.4.3 (BKT), §3.4.4 (improved struggle) all closed.*
- [x] Fill §3.3.2 Temporal Smoothing stub (distinguish per-submission decay from EWMA across refresh) — *Done 2026-05-18.*
- [ ] **NEW (Phase 0-8)**: insert ~120-word v2 empirical-refinement paragraph after `design-and-architecture.tex:259` (the existing "trial and error in the absence of labelled ground-truth data" sentence) — frames v2 as iterative refinement, signposts to §5.4, notes that v2 LR weights are signed and do not satisfy the v1 convex-combination constraint. Full brief + optional LaTeX draft at [[v2 Empirical Refinement Brief]] §1.

*Unblocks: Ch1&2 language fixes are easier once Ch3 narrative is settled.*

---

### 4. Ch1 & Ch2 — Language and framing `Writing · Small`

- [x] Convert future tense in Ch1 §1.2, §1.3, §1.5 to past/present
- [ ] Update Table 1 risk mitigations with actual decisions made
- [ ] Fill Ch2 §2.1.7 research gaps (uncomment and revise draft at lines 121–130)
- [ ] Add implementation status column to FR/NFR tables; clarify FR6 is unimplemented
- [x] **Add three new Ch2 subsections (Knowledge Tracing, Text Mining, RAG) + citation extensions to §2.1.4/§2.1.6/§2.1.7** — see "Methods lit-review backlog (2026-04-18)" in [[Rewrite Queue]]. *Done — KT at `requirements-specification.tex:99`, Text Mining at `:152`, RAG at `:186`, bonus Dense Retrieval & ANN at `:197`. Citation extensions to §2.1.4/§2.1.6/§2.1.7 still tracked separately in the Rewrite Queue methods lit-review backlog.*
- [ ] **NEW (Phase 0-8, optional)**: insert one sentence in Ch1 §1.2 Proposed Solution or §1.5 Project Approach noting iterative empirical refinement of struggle/difficulty weights. Foreshadows §5.4 without overclaiming. Optional — current Ch1 reads fine without it.
- [ ] **NEW (Phase 0-8)**: insert ~120-word paragraph in Ch2 §2.2.1 Modelling Struggle (or new §2.2.x titled "Empirical refinement of struggle and difficulty models") on supervised weight optimisation + Bayesian hyperparameter search + LLM-as-second-opinion rater methodology. Uses cites already in bib (`gilardiChatGPTOutperformsCrowd2023`, `chiangCanLargeLanguage2023`, `liuGEvalNLGEvaluation2023`, `zhengJudgingLLMasaJudgeMTBench2023`, `CoefficientAgreementNominal`) plus 3 pending Phase 8 Zotero imports (`landisMeasurementObserverAgreement1977`, `bergstraAlgorithmsHyperParameterOptimization2011`, `akibaOptunaNextgenerationHyperparameter2019`). Sets up §5.4 methodology without restating it. Full brief at [[v2 Empirical Refinement Brief]] §5.

*Unblocks: Ch4 — existing chapter framing is now consistent before the implementation chapter is rewritten.*

---

### 5. Ch4 — Implementation rewrite `Writing · Large`

Rewrite the entire chapter — it currently describes V1 only. Cover the full V2 system. Add `[TODO: insert figure]` placeholders for Appendix B screenshots; these will be filled in at step 8.

*Brief delivered 2026-05-20 at [[Ch4 Rewrite Brief]] — single vault note, ~12 subsection blocks, drop-in LaTeX for tables, 11 figure slots with pre-written captions + `\label{}` keys, citation hooks listed, Marker 1 (no math-modelling) and Marker 2 (no comparison study) lessons from F221611 folded in. **Thesis branding decision 2026-05-20: Streamlit stack (`code/`) = V1, React + FastAPI stack (`code2/`) = V2.** V2 is presented as evolution of V1, not "alternative"; both are deployed and V1 is not a prototype. User authors `Report/main-sections/implementation.tex` against the brief; tick the items below as each subsection lands.*

- [ ] Replace scope/introduction section — remove "proof of concept" framing
- [ ] Update technology stack table to reflect V2 dependencies (filelock, openai, scipy, streamlit-autorefresh)
- [ ] Data pipeline section — describe interval-based polling, JSON+XML parsing, normalization
- [ ] Analytics section — OpenAI incorrectness scoring, 7-signal struggle, 5-signal difficulty, CF, mistake clustering
- [ ] Models section — IRT, BKT, improved struggle, measurement confidence
- [ ] Lab assistant system — join/assign/self-claim/mark-helped flows, shared JSON state
- [ ] Saved sessions and session lifecycle — CRUD, retroactive save, academic period filtering
- [ ] Instructor views — all 6 views + settings + sound effects
- [ ] Mark figure slots for Appendix B screenshots (`[TODO: insert figure]`)
- [ ] **Insert L-BFGS-B / MLE / ROC-AUC citation footnotes in Ch4 §4.9.x and Ch5 §5.1** — see "Methods lit-review backlog (2026-04-18)" in [[Rewrite Queue]].
- [ ] **NEW (Phase 0-8 insertion 1)**: insert ~90-word v2 toggle paragraph after `implementation.tex:952` (the improved model defaults sentence). Documents the four `*_version` flags in `runtime_config.py` (`struggle_weights_version`, `difficulty_weights_version`, `improved_struggle_weights_version`, `hyperparams_version`) + the v2 JSON fallback semantics + the V2-only restriction (V1 Streamlit retains v1 as reference). Full brief at [[v2 Empirical Refinement Brief]] §2.
- [ ] **NEW (Phase 0-8 insertion 2)**: insert 3-sentence "Optimised Weights (v2)" Settings paragraph near §4.9.6 (Settings view). Describes the new fifth section in the V2 React Settings UI with its four `<ToggleRow>` selects + warn-variant `V2InfoBlock` subcomponent reflecting Phase 4 findings; notes the disable-logic (difficulty toggle disabled when `difficulty_model == "irt"`; improved model toggle disabled when `struggle_model != "improved"`). Full brief at [[v2 Empirical Refinement Brief]] §2.

*Unblocks: Ch5 evaluation framing, Appendix A code snippets.*

---

### 6. Ch5 — Results & Evaluation `Writing · Large`

Restructured 2026-05-24 to Hybrid layout (§5.1 Design, §5.2 Functional, §5.3 Non-Functional, §5.4 Results, §5.5 Survey, §5.6 Discussion). §5.1 drafted in [[Ch5 §5.1 Drafting Plan]]; **§5.4 v2 empirical-refinement brief delivered 2026-05-25 at [[v2 Empirical Refinement Brief]]** with numbers + 11 figures + tables auto-generated to `data/eval/results.md` and `data/eval/figures/`.

- [x] §5.1 Evaluation Design — drafted in [[Ch5 §5.1 Drafting Plan]] (paste-ready)
- [ ] §5.2 Functional Testing — FR1–FR7 mapped to smoke test evidence (Appendix C)
- [ ] §5.3 Non-Functional Testing — NFR1–NFR6 (performance, usability, reliability)
- [x] §5.4 Results — **v2 empirical-refinement brief ready** (struggle headline ρ +0.588 positive; difficulty ρ +0.468 and improved model ρ +0.201 negative findings; Optuna K tied + τ Δ +0.160 positive). Writing chat task to draft §5.4.2 / §5.4.3 / §5.4.9 / §5.4.10 from the brief
- [ ] §5.5 Survey — n=8 of ~10 (Microsoft Forms); writable now from data in hand
- [ ] §5.6 Discussion — v1↔v2 disagreement (31.2%), tradeoffs, limitations; §5.6.1 needs the §5.4 numbers (now ready)

**Phase 0-8 §5.4 / §5.6 detail (per [[v2 Empirical Refinement Brief]] §3):**

- [ ] **NEW §5.4 methodology preamble (~150 words)** — lands at the top of `\subsection{Results}` before §5.4.1. Establishes: (a) which models we trained (4 v2 weight artefacts) vs evaluated only (IRT, BKT, mistake clustering, measurement confidence); (b) GroupKFold-by-session for struggle/blend vs LOO-by-question for difficulty; (c) LR + L2 default with gradient-boosting fallback rationale; (d) two-Ks footnote (CV-K vs shrinkage-K naming clash). Full brief + optional LaTeX draft at [[v2 Empirical Refinement Brief]] §4.
- [ ] **NEW §5.4.2 prose** — Cohen's κ block on the 50 shared snapshots; κ_intervene = 0.250, κ_band_linear = 0.198, κ_band_quad = 0.262 (all "slight" by Landis–Koch); within-1-band agreement 70%; methodological limitation framing
- [ ] **NEW §5.4.3 prose** — struggle model v1 vs v2 headline; v2 mean ρ +0.588 [+0.490, +0.686] across 5 session-grouped folds; 3 weight sign flips (`n_hat`, `t_hat`, `rep_norm`); 2 magnitude bumps (`i_norm`, `d_hat`); v1 dominant signal `A_norm` retained but trimmed
- [ ] **NEW `\subsubsection{Honest Negative Findings — Difficulty and Improved-Blend}` (§5.4.9)** with `\label{sec:eval-v2-negative}`; difficulty v2 LOO-pooled ρ +0.468 (< random); improved model v2 ρ +0.201 with w_M = −0.444 and w_D = −0.137; conclusion: v1 stays the recommended default for both
- [ ] **NEW `\subsubsection{Hyperparameter Optimisation (Optuna TPE)}` (§5.4.10)** with `\label{sec:eval-v2-hyperparams}`; K tied (Δ +0.009 within noise (K=0), v1 K=5 near-optimal); τ substantial positive (Δ +0.160, best 0.899 at upper boundary — flag for §5.6 follow-up); BKT priors + mastery threshold deferred to future work
- [ ] **NEW §5.6.1 prose** — v1↔v2 struggle band disagreement: 31.2% reclassified (15.9% upgraded + 15.3% downgraded); insert verdict scorecard table; "two regimes" framing (keep v1 for difficulty + blend; switch to v2 for struggle + τ; K is a no-op)
- [ ] **Figures pass**: copy 11 PNGs from `data/eval/figures/` → `Report/figures/evaluation/` (new folder); insert `\includegraphics` lines under matching subsubsections per [[Figures and Tables]] §2026-05-25 (11-figure source→target table with suggested labels)
- [ ] **Tables pass**: lift 7 tables verbatim from `data/eval/results.md` (cohort, κ, struggle weights, per-fold AUC, difficulty weights, improved model weights, Optuna hyperparams); convert Markdown → `tabularx`; LaTeX label suggestions in [[Figures and Tables]] §2026-05-25

*Unblocks: Ch6.*

---

### 7. Ch6 — Conclusion `Writing · Medium`

Write from scratch once Ch5 is drafted.

- [ ] §6.1 Summary — restate objectives, what was built, what was achieved
- [ ] §6.2 Contributions — scoring model advances, lab assistant coordination, real-time analytics
- [ ] §6.3 Future Work — FR6 smart devices, Phase 6 mobile refinement, Phase 9 RAG feedback, Phase 10/11 in-app Help, event-driven architecture, temporal smoothing, BKT parameter tuning, larger evaluation study, export/reporting

**Phase 0-8 contribution / future-work additions (per [[v2 Empirical Refinement Brief]] §6 and [[Future Work Inventory]] items #3 / #1a / #1b):**

- [ ] **NEW §6.2 Contributions item (per brief §6a)** — iterative empirical refinement of struggle/difficulty signals: v1 hand-set composites validated against second-opinion LLM labels and refit under OLS + GroupKFold CV (struggle, difficulty, improved model) and Optuna TPE (shrinkage K, CF τ); deployed as runtime-toggleable v2 options. Verdict scorecard (4 v2 wins + 1 tie) lifted from [[Evaluation PoC Handoff]] §13 as supporting evidence. Optional LaTeX draft in brief §6a
- [ ] **§6.3 Future Work — close item #3** (supervised weight optimisation) since Phase 0-8 closed it; reframe as "extended in this work" rather than "deferred". Full phrasing in brief §6b
- [ ] **NEW §6.3 Future Work item #1a (per brief §6b)** — LLM-rater limitation: v2 weights trained against GPT-4o-mini labels rather than instructor flags; Cohen's κ vs author at n=50 is poor by Landis–Koch (0.10–0.11) though within-1-band agreement is 70%. Future work: instructor-flag ground truth (requires ethics extension) or multi-rater consensus
- [ ] **NEW §6.3 Future Work item #1b (per brief §6b)** — Optuna τ optimum landed at upper boundary of [0.4, 0.9] search range (finer search at τ ∈ [0.85, 0.95] may improve further); BKT priors `(p_init, p_learn, p_guess, p_slip)` + mastery threshold deferred from Phase 4d because each trial requires ~30 minutes of BKT refits; a reduced-fold TPE study over them is the natural follow-on

---

### 8. Appendix B — UI Screenshots `Evidence · Small`

Take screenshots of every dashboard and mobile view now that all chapters are written and code is stable.

- [ ] All 6 instructor views (in-class, student detail, question detail, data analysis, model comparison, settings)
- [ ] Model comparison view (both student + question tabs)
- [ ] Lab assistant app (join screen, unassigned view, assigned view)
- [ ] Session start/end states
- [ ] Replace all `[TODO: insert figure]` placeholders in Ch3 and Ch4 with actual figures
- [ ] **NEW (Phase 0-8)**: SettingsView "Optimised Weights (v2)" section screenshot with all four toggles visible (struggle + hyperparams use the green-ok `V2InfoBlock` variant; difficulty + improved model use the red-warn variant per Phase 4 findings); demonstrates the iterative-refinement framing live in the UI

*Unblocks: Appendix C (screenshots confirm system is in final state for smoke testing).*

---

### 8a. Figures backlog `Evidence · Medium`

Per-chapter figure work consolidated from [[Figures and Tables]] (which holds the full inventory and rationale). Tackle each block in the order the parent writing step needs it — Ch3 figures during Step 3, Ch4 screenshots during Step 5, etc. The Step 8 screenshot pass produces the raw assets; this section is the per-chapter insertion checklist.

**Verification basis:** every non-optional / non-conditional figure below is justified by either (a) an existing `\includegraphics` placeholder in the `.tex` source, or (b) an existing subsection header whose subject is intrinsically visual (a UI view, a model-output panel, a workflow state). Nothing speculative.

**Ch1 — Introduction (Step 4)**

- [ ] Tbl 1 (Risks) — update mitigations to actual V2 decisions (Bayesian shrinkage, modular `models/`, graceful degradation, FR6 scoped out)

**Ch2 — Requirements Specification (Step 4)**

- [ ] Tbl 3 (MoSCoW) — review FR6 status (currently "Should Have", unimplemented)
- Figures 1–5 (literature dashboards): no action, keep as-is

**Ch3 — Design (Step 3)**

- [ ] Fig 6 (architecture diagram) — update to show `models/` package, RAG, lab assistant
- [ ] Fig 8 — replace Figma mockup 1 with V2 In Class view screenshot (`design-and-architecture.tex:339`)
- [ ] Fig 9 — replace Figma mockup 2 with V2 lab-assistant allocation screenshot (`design-and-architecture.tex:347`)
- [ ] Fig 10 — replace Figma mockup 3 with V2 assistant leaderboard screenshot (`design-and-architecture.tex:356`)
- [ ] NEW Tbl — Struggle formula 7-signal table (signal × symbol × weight × `config.py` key)
- [ ] NEW Tbl — Difficulty formula 5-signal table (signal × symbol × weight × `config.py` key)
- [ ] NEW Tbl — Improved-struggle weight redistribution matrix (4 collapse cases, rows sum to 1.00)
- [ ] NEW Tbl — BKT parameter defaults vs fitted values
- [ ] Tbl 4 (Tech stack) — add OpenAI, filelock, scikit-learn, scipy, streamlit-autorefresh, chromadb, sentence-transformers
- [ ] Tbl 5 (CF comparison) — change wording to "implemented" not "proposed"
- [ ] Tbl 6 (Struggle thresholds) — update labels (None/Low/Medium/High → On Track / Minor Issues / Struggling / Needs Help) and values [0.00–0.20 / 0.20–0.35 / 0.35–0.50 / 0.50–1.00]
- [ ] (optional) Graceful-degradation trace screenshot — improved-struggle with mastery data sparse; place in §3.4.4 or Ch5 §5.5

**Ch4 — Implementation (Step 5)** — each maps 1:1 to an existing subsection header in `implementation.tex`

- [ ] Screenshot: In Class view → §4.4.1
- [ ] Screenshot: Student Detail view → §4.4.2
- [ ] Screenshot: Question Detail view (with mistake clusters labelled) → §4.4.3
- [ ] Screenshot: Data Analysis view → §4.4.4
- [ ] Screenshot: Model Comparison view (student + question tabs) → §4.4.5
- [ ] Screenshot: Settings view (model toggles + CF config + BKT sliders) → §4.4.6
- [ ] Screenshot: Previous Sessions view → §4.4.7
- [ ] Screenshot: Lab assistant — Session Join → §4.5.1
- [ ] Screenshot: Lab assistant — Waiting / Unassigned → §4.5.2
- [ ] Screenshot: Lab assistant — Assigned (with student card + RAG suggestions) → §4.5.3
- [ ] (optional) Tooltip-in-action screenshot — one chart with on-hover explanation visible

**Ch5 — Results & Evaluation (Step 6)**

- [ ] Model Comparison panel screenshot — Rank Concordance (Spearman ρ) + Top-10 Overlap + Agreement split + scatter plot. Capture from `/api/models/compare` → ComparisonView → §5.4.2
- [ ] NEW Tbl — Requirements traceability (FR1–FR7 / NFR1–NFR6 mapped to implementation status + evidence location) → §5.2 / §5.3
- [ ] NEW Tbl — Model comparison results (baseline vs IRT, baseline vs improved struggle: ρ, top-k overlap, agreement %) → §5.4
- [ ] (optional) Performance / refresh-latency chart → §5.3
- [ ] (optional) Test results summary — pass/fail by FR + NFR; could be a table instead of a chart
- [ ] **NEW (Phase 0-8) — 11 auto-generated v2 evaluation figures**: copy from `data/eval/figures/` → `Report/figures/evaluation/` (new folder); per-figure target §, suggested `\label{}`, and subject are inventoried in [[Figures and Tables]] §2026-05-25. Figures: `band_distributions.png` (§5.4.1), `kappa_block.png` (§5.4.2), `weights_struggle_v1_v2.png` (§5.4.3 — HEADLINE), `auc_per_fold_struggle.png` (§5.4.4), `roc_struggle_v1_v2.png` (§5.4.3), `calibration_struggle_v2.png` (§5.4.3), `weight_stability_heatmap_struggle.png` (§5.4.3), `confusion_bands_v1_v2.png` (§5.4.3 / §5.6.1), `weights_difficulty_v1_v2.png` (§5.4.9), `weights_improved_v1_v2.png` (§5.4.9), `disagreement_matrix.png` (§5.6.1)
- [ ] **NEW (Phase 0-8) — 7 auto-generated v2 evaluation tables**: lift verbatim from `data/eval/results.md`; convert Markdown → `tabularx`; LaTeX label suggestions in [[Figures and Tables]] §2026-05-25 (cohort, κ, struggle weights, per-fold AUC, difficulty weights, improved model weights, Optuna hyperparams)
- [ ] **NEW (Phase 0-8) — verdict scorecard table**: 5-row table (component × winner × numbers × phase) lifted from [[Evaluation PoC Handoff]] §13 → §5.6.1 with `\label{tab:eval-verdict-scorecard}`

**Ch6 — Conclusion (Step 7)**

- No new figures expected. If Ch6 §6.3 names the React/FastAPI alternative as future work, the V3 architecture diagram from the conditional block below could be reused.

**Appendix B — UI Screenshots (Step 8)**

- This appendix is the host for the screenshots above. Decide policy: each figure appears in Appendix B as the full gallery AND once in-chapter, OR each appears only once. Apply consistently across all 10+ screenshots.

**Removed if Progress Report stays excluded (already commented out in `main.tex:62`)**

- Fig 11 (Gantt chart) — remove
- Tbl 8 (Gantt summary) — remove

**Cross-cutting**

- [ ] After all chapter screenshots are inserted, run a renumbering pass — figure count goes from 11 → ~20, so `\ref{fig:...}` calls and the List of Figures need a clean compile check.
- [ ] Update [[Figures and Tables]] after each batch so it stays the source of truth.

**Table colouring backlog (extra polish, not blocking)**

Add `\usepackage[table]{xcolor}` to `main.tex` once; then colour the following tables traffic-light style. Palette: `tlGreen #10A15D · tlAmber #FFCC00 · tlOrange #FF6600 · tlRed #FF2D55` (matches dashboard UI hex codes from [config.py:39-42](code/learning_dashboard/config.py#L39-L42) and [config.py:54-57](code/learning_dashboard/config.py#L54-L57)). For non-traffic-light tables, define ad-hoc named colours alongside.

- [ ] Tbl 6 (Ch3 §3.6.4 Struggle visual encoding) — colour Colour row with `tlGreen/tlAmber/tlOrange/tlRed`
- [ ] Tbl 7 (Ch3 §3.6.4 Difficulty visual encoding) — same palette mapped Easy → Very Hard
- [ ] Tbl 1 (Ch1 §1.4 Risks) — severity column: `tlRed` high · `tlAmber` medium · `tlGreen` accepted
- [ ] Tbl 3 (Ch2 §2.3.3 MoSCoW) — priority column: `tlGreen` Must · light blue (`#BBDEFB`) Should · light grey (`#E0E0E0`) Could · light red (`#FFCDD2`) Won't
- [ ] NEW Tbl Requirements Traceability (Ch5 §5.2) — status column: `tlGreen` implemented + tested · `tlAmber` implemented partial evidence · `tlRed` not implemented (FR6)
- [ ] (optional) NEW Tbl Model comparison results (Ch5 §5.4) — agreement % column: `tlGreen` ≥0.8 · `tlAmber` 0.5–0.8 · `tlRed` <0.5

Skip: Tbl 2 (Grade Scoring — literature reproduction), Tbl 4 (Tech Stack — no ordinal), Tbl 5 (CF Comparison — qualitative), Tbl 9 (Themes — reference only), and the new formula tables (Struggle 7-signal / Difficulty 5-signal / Weight redistribution / BKT params) where colour would obscure the numbers.

**Deferred extras — visual polish on tables**

Pulled out as a separate pass so it doesn't block chapter writing. Needs `\usepackage[table]{xcolor}` in `main.tex` and a 4-colour traffic-light palette (`tlGreen #10A15D`, `tlAmber #FFCC00`, `tlOrange #FF6600`, `tlRed #FF2D55`) matching `config.py` UI hexes.

- [ ] Ch3 §3.6.4 Visual Encoding tables (struggle + difficulty) — colour the threshold cells / column headers using the traffic-light palette. Most natural fit since the tables are literally about colour encoding.
- [ ] Ch1 Tbl 1 (Risks) — colour the severity column (red / amber / green).
- [ ] Ch2 Tbl 3 (MoSCoW) — colour the priority column (Must / Should / Could / Won't); needs two extra named colours outside the traffic-light set (`#BBDEFB` light blue for Should, `#E0E0E0` grey for Could).
- [ ] Ch5 NEW Requirements Traceability table — colour the status column once the table is drafted.
- [ ] Ch5 NEW Model comparison results table — conditional formatting on the agreement % column if the numbers split usefully.

*Skip on purpose: Tech Stack, CF comparison, Tech-themes appendix table, the new formula tables — colour would be noise on neutral / numerical content.*

**Conditional — only if Ch4 or Ch6 explicitly names the React/FastAPI `code2/` frontend**

- [ ] V3 architecture diagram (3 frontends + 1 shared core + 1 shared state file)
- [ ] V3 theme gallery (7 themes: paper / newsprint / solar / scifi / blueprint / matrix / cyberpunk)
- [ ] V3 In Class / Student detail / Question detail / Lab coordination screenshots
- [ ] SessionProgression timeline screenshot (`code2/` 9th view, no V2 equivalent)
- [ ] Swagger UI screenshot — `/docs` endpoint listing
- [ ] Theme × accent matrix (7 themes × 5 accents in one grid)
- [ ] NEW Tbl — API endpoint map (≥22 routes × HTTP method × `learning_dashboard.*` delegate × cache TTL)
- [ ] NEW Tbl — Theme × accent combinations (35 valid pairs with accessibility class)

*Unblocks: Step 9 (Appendix C) can begin once the screenshot batch is captured, since the smoke test runs on the same final UI state.*

---

### 9. Appendix C — Test Results `Evidence · Medium`

Run the full smoke test checklist from [[Setup and Runbook]] and document outcomes. This is the primary evidence base for Ch5.

- [ ] Run every test in the smoke test checklist; record pass/fail
- [ ] Note any observations or edge-case behaviour
- [ ] Capture model comparison results for baseline vs IRT difficulty and baseline vs improved struggle
- [ ] Fill any evidence slots left in Ch5 §5.2 and §5.4
- [ ] **NEW (Phase 0-8) — one-line fix**: insert `\label{app:detailed-test-results}` at the top of `Report/appendix-sections/detailed-test-results.tex` (currently empty header). Ch5 §5.1.2 references this label twice; without it `pdflatex` emits two undefined-reference warnings on every compile.
- [ ] **NEW (Phase 0-8) — v2 evaluation overflow tables**: lift the v2 tables that don't fit in the body of §5.4 into Appendix C — per-fold AUC detail (5 rows × multiple folds), full Cohen's κ report (8 rows including exact + within-1-band agreement + intervene rates), Optuna per-trial highlights (~10 rows × 2 studies for K and τ), full v2 weight vectors with per-fold std for all three weight families (struggle 7-signal, difficulty 5-signal, improved model 3-weight). Source: `data/eval/results.md`, `data/eval/kappa_report.json`, `data/eval/optimised_hyperparams_v2.json`, the three `data/eval/optimised_*_weights_v2.json` files.

*Unblocks: Appendices E&F and Appendix A (evidence pass confirms formulae and code snippets are final).*

---

### 10. Appendices E & F — Formulae `Writing · Small–Medium`

Collect all model formulas and derivation notes in one place.

- [ ] Appendix E: struggle formula (7 components + weights), difficulty formula (5 components + weights), IRT likelihood, BKT update rule, improved struggle weights, CF cosine similarity
- [ ] Appendix F: derivation notes for non-obvious formulas (BKT update, IRT MLE gradient, Bayesian shrinkage in struggle)
- [ ] **NEW (Phase 0-8) Appendix E**: ordinary least-squares linear regression objective (used to train all three v2 weight vectors — struggle, difficulty, improved model); GroupKFold cross-validation procedure (5 folds, session as group cluster — prevents student leakage); Cohen's κ family (unweighted binary + linear-weighted + quadratic-weighted ordinal variants — formula implicit in `data/eval/kappa_report.json`); Optuna TPE acquisition-function sketch (or just a one-line cite to Bergstra 2011 if space is tight)
- [ ] **NEW (Phase 0-8) Appendix F**: note that v2 LR-trained weights are signed and do NOT satisfy the v1 convex-combination constraint (Eq. `struggle-raw` / `difficulty-raw`); brief derivation of why this is a deliberate consequence of the linear-classifier framing and how v1 is preserved as the deployed default (the v2 toggle is opt-in, fallback to v1 on missing/malformed JSON)

---

### 11. Appendix A — Code Snippets `Writing · Small`

Add key code excerpts to support Ch4.

- [ ] Incorrectness scoring batch call
- [ ] Struggle score function signature
- [ ] Lab state read/write pattern
- [ ] Deferred actions example
- [ ] **NEW (Phase 0-8)** — `scripts/optimise_v2_weights.py` core fit loop: LR + L2 + GroupKFold per fold, ~40 lines (demonstrates the empirical-refinement methodology end-to-end)
- [ ] **NEW (Phase 0-8)** — `scripts/optimise_hyperparams.py` Optuna study setup: TPE sampler + two parallel studies (K and τ) + objective function signature, ~30 lines (demonstrates Bayesian hyperparameter search)
- [ ] **NEW (Phase 0-8)** — `code2/backend/runtime_config.py::_load_optimised_hyperparams()` helper + the four `*_version` field declarations + `update()` side-effects on hyperparams_version flip, ~20 lines (demonstrates runtime-toggle plumbing)
- [ ] **NEW (Phase 0-8)** — `code2/frontend/src/views/SettingsView.tsx` "Optimised Weights (v2)" section with `<ToggleRow>` pattern + `V2InfoBlock` ok/warn variant, ~15 lines (demonstrates the user-facing toggle UX)

---

### 12. Polish pass `Writing · Small`

Final consistency check before submission.

- [ ] Terminology: "incorrectness", "struggle score", level labels ("On Track / Minor Issues / Struggling / Needs Help")
- [ ] Update bibliography for IRT/BKT/improved struggle sources if new citations added
- [ ] Review figure and table numbering after all additions
- [ ] LaTeX compile check — `main.tex` with no errors or warnings
- [ ] **NEW (Phase 0-8) — Zotero imports for 3 pending bibkeys** (user-side via Better BibTeX): `landisMeasurementObserverAgreement1977` (DOI 10.2307/2529310), `bergstraAlgorithmsHyperParameterOptimization2011` (NeurIPS 24 paper, hash `86e8f7ab32cfd12577bc2619bc635690`), `akibaOptunaNextgenerationHyperparameter2019` (DOI 10.1145/3292500.3330701, arXiv 1907.10902). After import: re-export `references.bib` and run Obsidian Zotero Integration "Import & Replace" to generate the 3 `.md` notes
- [ ] **NEW (Phase 0-8)** — run `python scripts/sync_literature.py` once the new `\cite{}` calls land in §2.2 / §5.4.2 / §5.4.10 to flip 🟡 → ✅ on the 3 new entries in [[Literature/index.md]] §5 Evaluation Metrics
- [ ] **NEW (Phase 0-8)** — refresh `docs/recap_toolkit/dashboard_v3_toolkit.html` panels per CLAUDE.md after the v2-toggle work and the §5.4 brief delivery: Status panel (Phase 4 findings + verdict scorecard), Section Plan panel (Ch3/Ch4/Ch5 amendments), Roadmap panel (this section's new line items), Literature panel (3 pending entries marked ⚠ citation-needed until Zotero imports complete)
- [ ] **NEW (Phase 0-8)** — rebuild `graphify-out/` after the `code2/backend/` changes (per CLAUDE.md): `python3 -c "from graphify.watch import _rebuild_code; from pathlib import Path; _rebuild_code(Path('.'))"`

---

### 13. FR6 — Smart device notifications `Coding · Large` (stretch)

Only attempt if time allows after step 8. Otherwise document as future work in Ch6 §6.3.

- [ ] Evaluate feasibility of web push notifications for the assistant app
- [ ] If viable: implement push alert when a new high-struggle student appears
- [ ] Document the decision in Ch6 regardless of outcome

---

### 14. Phase 6 — Mobile app refinement (stretch) `Coding · Medium`

Only attempt after Ch6 is written. Ch5 assistant flow testing can use the current app. BKT badges and session timer are thesis-strengthening but not thesis-critical.

- [ ] BKT mastery badge + progress bar on assigned-student card (`render_assigned_view()`)
- [ ] Per-question mastery labels on the top-3 question list
- [ ] Session elapsed timer in `_render_session_status_strip()`
- [ ] Helped-vs-struggling summary header in `render_unassigned_view()`

---

## Out of scope — document as future work

These phases will not be implemented before the May 20 deadline. Each should be documented in Ch6 §6.3 Future Work. Do not attempt coding on these items.

### Phase 9 — RAG suggested feedback ✅ Implemented (2026-04-14)

Architecture designed by Dr. Batmaz (Meeting 3) — **must be credited in dissertation**.

Implemented as an isolated `rag.py` module:
- `chromadb.PersistentClient` at `data/rag_chroma/`, collection `session_{session_id}`
- `all-MiniLM-L6-v2` embeddings via `sentence-transformers` (local, no API cost)
- Two-layer retrieval: pandas pre-filter by `student_id` + ChromaDB `where=` metadata filter
- GPT-4o-mini generates 2–3 coaching bullets surfaced in the assistant assigned-student card
- Graceful no-op if deps missing; cached per student per session

Ch4 and Ch5 sections needed. See [[RAG Pipeline - Two-Layer Retrieval]] and [[Suggested Focus Areas Panel]].

### Labelled data collection + supervised weight optimisation `Research · Done (2026-05-25)`

> **Status update 2026-05-25:** Originally framed as out-of-scope future work. **Completed during the Phase 4 v2 evaluation pipeline** — LLM second-opinion labels (GPT-4o) replaced the instructor-flagging prerequisite, allowing the four weight vectors (7-signal struggle, 5-signal difficulty, 3-weight improved model, scalar hyperparams K and τ) to be empirically refit with ordinary least-squares linear regression + session-grouped 5-fold CV (and Optuna TPE for the scalars). All four v2 artefacts live as runtime-toggleable Settings in the V2 React stack (defaults stay v1). Findings reported honestly in Ch5 §5.4 — 2 positive (struggle weights, CF τ) + 2 negative (difficulty weights, improved model) + 1 tie (shrinkage K). See [[Evaluation PoC Handoff]] §13 for the verdict scorecard and [[v2 Empirical Refinement Brief]] for the writing-chat handoff.

The original out-of-scope framing (retained below for historical record):

The seven struggle weights (`α=0.10, β=0.10, γ=0.20, δ=0.10, η=0.38, ζ=0.05, θ=0.07`), the five difficulty weights (`0.28, 0.12, 0.20, 0.20, 0.20`), and the three improved-struggle bucket weights (`0.45, 0.30, 0.25`) are set by trial and error. With labelled ground truth available — instructor annotations of "this student is struggling / not struggling" captured during real sessions, or post-hoc retrospective labelling of recorded sessions — the same weights could be fitted by supervised ML (logistic regression, gradient boosting, or Bayesian hyperparameter search such as Optuna), giving the model a proper empirical foundation. *The 2026-05-25 implementation used a GPT-4o second-opinion labelling proxy in place of instructor flagging; Cohen's κ between the LLM rater and the author at n=50 is poor by Landis–Koch (0.10–0.11), framed as a methodological limitation rather than a barrier.*

### Phase 10 — In-app Help system (instructor dashboard)

Help section under Settings covering Quick Tour, Help Centre, Model Guide, contextual tooltips, and reliability indicators. Not feasible to implement before deadline given the writing workload.

*Document in Ch6 §6.3 Future Work.*

### Phase 11 — In-app Help system (assistant app)

Lightweight mobile Help panel for lab assistants covering join guide, student card explainer, action button guide, and RAG suggestion explainer.

*Document in Ch6 §6.3 Future Work.*

---

## At a glance

| Step | Item | Type | Effort | Status |
| --- | --- | --- | --- | --- |
| 1 | Phase 7 — Surface hidden data | Coding | Small | Done |
| 2 | Phase 5 — Comparison UI | Coding | Large | **Done** |
| 3 | Ch3 — Design updates | Writing | Medium | **Done 2026-05-19** (Figma PNGs + design-vs-implementation reframe deferred; **+ 1 Phase 0-8 amendment pending** at line 259) |
| 4 | Ch1 & Ch2 — Language cleanup | Writing | Small | Partially done; **+ 1 optional Ch1 sentence + 1 Ch2 §2.2 methodology paragraph from Phase 0-8** |
| 5 | Ch4 — Implementation rewrite | Writing | Large | **Brief delivered 2026-05-20** — [[Ch4 Rewrite Brief]] ready; user authoring; **+ 2 Phase 0-8 insertions pending** (line 952 + §4.9.6) |
| 6 | Ch5 — Results & Evaluation | Writing | Large | **Brief delivered 2026-05-25** — [[v2 Empirical Refinement Brief]] + [[Ch5 §5.1 Drafting Plan]] ready; numbers + 11 figures + 7 tables auto-generated to `data/eval/`; writing chat to draft §5.4.2 / §5.4.3 / §5.4.9 / §5.4.10 / §5.6.1 |
| 7 | Ch6 — Conclusion | Writing | Medium | Not started; **+ Phase 0-8 contribution + future-work items #1a / #1b ready to slot in** |
| 8 | Appendix B — Screenshots | Evidence | Small | Not started; **+ 1 Phase 0-8 SettingsView v2 screenshot pending** |
| 8a | Figures backlog (per-chapter insertion) | Evidence | Medium | Not started; **+ 11 Phase 0-8 Ch5 evaluation figures + 7 tables ready to copy/lift** |
| 9 | Appendix C — Test Results | Evidence | Medium | Not started; **+ Phase 0-8 `\label{}` fix (one line) + v2 overflow tables pending** |
| 10 | Appendices E & F — Formulae | Writing | Small–Medium | Not started; **+ Phase 0-8 LR objective + GroupKFold + κ family + signed-weights note pending** |
| 11 | Appendix A — Code Snippets | Writing | Small | Not started; **+ 4 Phase 0-8 snippet candidates added** |
| 12 | Polish pass | Writing | Small | Not started; **+ Phase 0-8 Zotero imports (3) + sync_literature + toolkit + graphify rebuild pending** |
| 13 | FR6 — Smart devices (stretch) | Coding | Large | Not started |
| 14 | Phase 6 — Mobile app refinement | Coding | Medium | Stretch |
| — | Phase 9 — RAG suggested feedback | Coding | Large | **Done** (2026-04-14) |
| — | Phase 10 — In-app Help (instructor) | Coding | Large | Out of scope / Future work |
| — | Phase 11 — In-app Help (assistant) | Coding | Medium | Out of scope / Future work |
| — | Labelled data + supervised weight optimisation | Research | Ambitious | ✅ **Done 2026-05-25** via Phase 0-8 (LLM second-opinion labels + OLS + Optuna TPE; see [[Evaluation PoC Handoff]] §13 verdict scorecard) |

---

## Alternative React (Vite) frontend — `code2/` shadow workspace

Additive track kicked off after the core Streamlit app was feature-complete. **`code/` stays pristine** throughout; everything happens in the `code2/` shadow copy. The thesis contribution (analytics, IRT, BKT, improved struggle, CF, RAG) is unchanged — only the presentation layer differs.

| Phase | Description | Status |
|---|---|---|
| 0 | Bootstrap — `cp -r code code2`, create `code2/CHECKLIST.md` resumable log | **Done** (2026-04-19) |
| 1 | FastAPI backend skeleton — `code2/backend/` + two 4-line `learning_dashboard/` refactors (`analytics.py:25` OpenAI-key guard, `data_loader.py:16` cached/uncached split) | **Done** (2026-04-19) |
| 2 | Vite + React + TypeScript scaffold — 7 themes (paper / newsprint / solar / scifi / blueprint / matrix / cyberpunk) extracted verbatim from `Alternative Dashboard _standalone_.html`, runtime theme + accent swap with `localStorage` persistence | **Done** (2026-04-19) |
| 3 | Port 7 non-lab views — InClassView, StudentDetail, QuestionDetail (+ new "Top Strugglers on this Question" table), DataAnalysisView, SettingsView, PreviousSessionsView, ComparisonView. Cold-start analytics mitigation via 5-min cache + `lifespan` prewarm. | **Done** (2026-04-19) |
| 4 | Lab state parity — 11 `/api/lab/*` endpoints, LabAssistantView with dispatch queue. Verified curl cycle: join → assign → mark helped → remove, state mutates through the same `FileLock`-protected `lab_session.json` that the Streamlit apps use. | **Done** (2026-04-19) |
| 5 | Sessions + settings + RAG — `/api/sessions` (read-only), `/api/settings` (read-only config snapshot), `/api/rag/{student,question}/{id}` (`async` + `to_thread` so the first-time Chroma build doesn't block the event loop). RagPanel integrated into detail views. | **Done** (2026-04-19) |
| 6 | Build + polish — ErrorBoundary, loading skeletons, `npm run build` → `dist/` (≈260 KB / 74 KB gzipped), `StaticFiles` mount at `/`, `/docs` Swagger UI, custom editorial favicon | **Done** (2026-04-19) |
| 7 | Documentation sync — this block, Evidence Bank, Report Sync, Figures and Tables, Weekly Plan, Setup and Runbook, recap toolkit panels | **In progress** |
| 8 | Defence rehearsal — 5-process smoke test, thesis screenshots, demo script | Not started |

Plan file (full context, resumable across context loss): `C:\Users\Bakri\.claude\plans\c-users-bakri-downloads-alternative-das-majestic-garden.md`.
Execution log with decision history: `code2/CHECKLIST.md`.

---

## Useful links

- [[Coding Roadmap]] — full coding phase status and sub-tasks
- [[Writing Roadmap]] — chapter-by-chapter status and writing notes
- [[Rewrite Queue]] — granular edit checklist for each thesis section
- [[Report Sync]] — where the thesis diverges from the current code
- [[Evidence Bank]] — what evaluation evidence exists or still needs to be collected
- [[Setup and Runbook]] — smoke test checklist for Appendix C
