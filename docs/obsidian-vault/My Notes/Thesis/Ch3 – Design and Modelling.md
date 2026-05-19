# Ch3 – Design and Modelling

Thesis chapter covering system architecture, data endpoint, mathematical models, and UI design.

Related: [[Thesis Overview]], [[Report Sync]], [[Architecture]], [[Analytics Engine]], [[Student Struggle Logic]], [[Question Difficulty Logic]], [[IRT Difficulty Logic]]

**Source file:** `main sections/design and architecture.tex`
**Status:** Draft — architecture broadly correct, formulas outdated, Figma mockups need replacing

> **Sync note (2026-04-18):** "Current contents" below reflects the thesis state *before* the Phase 6 tex-skeleton additions (2026-04-12). For the current tex subsection tree and the active writing backlog, see [[Rewrite Queue#Phase 6 additions (2026-04-12)]] and the toolkit's Status panel §6 Source reconciliation.

---

## Current contents

### 3.1 System Architecture (mostly accurate)

Three-layer design:
1. **Data Generation Layer** — student interactions at endpoint
2. **Data Ingestion and Processing Layer** — periodic retrieval, parsing, normalization, metric computation
3. **Decision and Action Layer** — analytics presented to instructor for decision-making

Includes architecture diagram (Fig 6).

**Mismatches with V2:**
- Mentions event-driven pipeline "currently under exploration" — still interval-based in V2
- Does not mention the `models/` package (IRT, BKT, improved struggle, measurement confidence)
- Does not mention saved sessions, academic calendar, or sound system

### 3.2 Data Endpoint (accurate)

Describes JSON format with embedded XML payload. Session-based organization. Derived metrics: attempts per question, time between attempts, AI-based correctness, feedback frequency.

This section is largely version-independent and matches the V2 implementation in `data_loader.py`.

### 3.3 Mathematical Models

#### 3.3.1 Student Struggle — FORMULA MISMATCH

**Thesis formula (5 components):**
`S_raw = alpha*n_hat + beta*t_hat + gamma*e_hat + delta*f_hat + eta*A_raw`

Components: submission count, time active, incorrect submissions, feedback requests, recent incorrectness.

**Actual V2 formula (7 components):**
`S = 0.10*n_hat + 0.10*t_hat + 0.20*i_hat + 0.10*r_hat + 0.38*A_raw + 0.05*d_hat + 0.07*rep_hat`

**Differences:**
| Thesis | Code | Notes |
|--------|------|-------|
| e_hat (incorrect submissions / total) | i_hat (mean incorrectness) | Different metric — thesis uses count ratio, code uses OpenAI score mean |
| f_hat (feedback requests / total) | — | Dropped in V2; replaced by other signals |
| — | r_hat (retry rate) | Added in V2: repeated attempts on same question |
| — | d_hat (trajectory slope) | Added in V2: trend of incorrectness over time |
| — | rep_hat (exact-answer repetition) | Added in V2: submitting identical answers repeatedly |

**Other differences:**

- Thesis proposes exponential smoothing as a *future* step — V2 has two distinct mechanisms that should be described separately: (a) per-submission exponential time-decay inside `A^{raw}` with `DECAY_HALFLIFE_SECONDS = 1800`; (b) EWMA across refresh cycles applied to the final struggle score, gated by `SMOOTHING_ENABLED = True` and `SMOOTHING_ALPHA = 0.3` in `config.py:73-74` (active, not a dead stub — earlier draft of this note had the value wrong).
- Thesis does not mention Bayesian shrinkage — V2 applies `w_n = n / (n + 5)` to pull the final `struggle_score` toward the class mean of `struggle_score` (see `analytics.py:346-349`). The shrinkage is on the *aggregate* score, not per-signal.
- Thesis does not mention score clipping to [0, 1]
- Thesis does not describe the **uniform min-max step across all 7 signals** that `analytics.py:322-330` applies before the weighted sum (raw → `_hat`/`_norm`); without it the configured weights would not match the effective contributions.

**Rewrite progress — 2026-05-18 (Step 3 of [[Full Roadmap]]):**

§3.3.1 **closed**:

- ✅ `Identified Variables` itemize extended to 7 signals (n, t, i, r, d, rep) — `design-and-architecture.tex:58-67`
- ✅ `e` renamed to `i` (mean incorrectness, matching `analytics.py:281`)
- ✅ Normalisation paragraph rewritten with uniform min-max across cohort — `design-and-architecture.tex:80-111`
- ✅ `A^{raw}` reframed as exponential time-decay with $H = 1800$ s half-life — `design-and-architecture.tex:114-132`. Replaces the old position-based convex weights `[0.35, 0.25, 0.20, 0.12, 0.08]` superseded in `config.py:30-32`.
- ✅ Struggle Score equation extended to 7-term form with default weights `α=0.10, β=0.10, γ=0.20, δ=0.10, η=0.38, ζ=0.05, θ=0.07` and accompanying weights table (`tab: struggle weights`) — `design-and-architecture.tex:134-194`
- ✅ Bayesian shrinkage paragraph added — $S^{\mathrm{shrunk}} = (n/(n+K)) S^{\mathrm{raw}} + (K/(n+K)) \bar{S}^{\mathrm{raw}}_\sigma$ with $K = 5$, applied to the aggregate score; cited `efronSteinsParadoxStatistics1977`. Matches `analytics.py:346-350` exactly. — `design-and-architecture.tex:196-207`
- ✅ Label hygiene: `eq:struggle-raw` and `eq:struggle-shrunk` introduced; old duplicate `eq:placeholder_label` resolved on struggle side (difficulty side D will close out the duplicate); pre-existing `eq: temporal sturggle` typo fixed
- ✅ `S^{raw}` → `S^{\mathrm{raw}}` consistency restored across the section

Outstanding housekeeping carried forward:

- ⚠ `\cite{morrisParametricEmpiricalBayes1983}` at `design-and-architecture.tex:206` references a bib key absent from `references.bib`. Decision: add bib entry (Morris, C. N. 1983, JASA 78(381), 47-55) or swap to `[BIB MISSING: Morris 1983]` placeholder for Step 12 polish.

§3.3.2 onwards:

- ✅ §3.3.2 Temporal Smoothing — **closed 2026-05-18**. Opening paragraph names the two noise sources (within-score and across-refresh). Per-submission decay paragraph cross-references `eq:time-decay-weight` and `eq:a-raw` from §3.3.1. EWMA paragraph cross-references `eq: temporal struggle` from §3.3.1 (single canonical EWMA equation; duplicate eliminated by deleting the §3.3.2 displayed copy). Housekeeping completed: §3.3.1 Temporal updating equation now has `S^{\mathrm{shrunk}}` on the RHS, and `\label{eq: temporal struggle}` moved inside the equation environment. Comparison table `tab: temporal smoothing` contrasts the two mechanisms. `labelled truth data` corrected to `labelled ground-truth data` (also in the §3.3.1 Struggle Score Definition).
- ✅ §3.3.3 Question Difficulty — **closed 2026-05-19**. 5-signal extension: $p_q$ added to variable list, $	ilde{p}_q$ derived, equation now $D^{\mathrm{raw}} = lpha	ilde{c} + eta	ilde{t} + \gamma	ilde{a} + \delta	ilde{f} + \epsilon	ilde{p}$ with default weights $0.28, 0.12, 0.20, 0.20, 0.20$. Weights table `tab: difficulty weights` inserted. Labels `eq:difficulty-raw` and `eq: temporal difficulty` added (placeholder label resolved). $	au = 0.5$ threshold defined explicitly.
- ✅ §3.3.4 Collaborative Filtering — **closed 2026-05-19**. Closing paragraph re-tensed to present: CF is "implemented alongside the parameter-based model" rather than "still going to be implemented"; live parameters ($k=3$, configurable elevation threshold, default-on) surfaced; Settings-panel toggle described as live; UK "neighbours"; missing verb in the preceding small-class sentence fixed.
- ✅ §3.3.5 Mistake Clustering — **closed 2026-05-19**. Pipeline (TF-IDF → $k$-means → silhouette auto-$k$ → LLM labelling) described as a design choice with cross-reference to Ch2 §2.3.2 for the math. Auto-$k$ equation `eq:cluster-auto-k` displayed. Parameters $N_{\min} = 3$, $K_{\max} = 5$ stated as values without naming the constants. Interpretation paragraph positions clustering as complementary to the parametric $D_t(q)$ signal.
- ✅ **Chapter-wide constants cleanup (2026-05-19)** — Option 1 applied uniformly: `	exttt{CONSTANT\_NAME}` references removed from §3.3.1 / §3.3.3 weights tables (now 3-column) and §3.3.5 prose. Numeric design values retained. Constants reintroduction deferred to Ch4 (Step 5).
- ✅ §3.4.1 Measurement Confidence — **closed 2026-05-19**. Two-factor + base formula $\kappa = \kappa_0 \cdot \mathrm{length} \cdot (	frac{1}{2} + 	frac{1}{2}\,\mathrm{extremity})$ matching `measurement.py:46-50`. No third "agreement" factor (the Rewrite Queue description was wrong). Empty/missing feedback → $\kappa = 0$ stated. Cited `lord1968statistical`. Surfaced as green/amber/grey indicator in Question Detail view.
- ✅ §3.3.3 follow-up: `$	ilde{p}_q$` denominator corrected to `$|\mathcal{S}_q|$` (unique students) at line 294 and line 353. The original brief gave `$n_q$` (total attempts), which did not match the code.
- ✅ §3.4.2 Item Response Theory — **closed 2026-05-19**. Rasch 1PL with $P(X_{s,q}=1) = \sigma(	heta_s - eta_q)$; joint MLE via L-BFGS-B with ability-centring; sigmoid mapping to $D^{\mathrm{IRT}}(q) \in [0,1]$ for UI consistency; graceful fallback to baseline when response matrix sparse. Bonus: "Bayesian Knowledge **Training**" → "**Tracing**" typo fixed in §3.4.3 header.
- ✅ §3.4.3 Bayesian Knowledge Tracing — **closed 2026-05-19**. Two-state HMM with 4 parameters per skill ($P(L_0), P(T), P(G), P(S)$); update + predictive equations displayed; global MLE via L-BFGS-B with $[0, 0.5]$ bounds on guess/slip to enforce $P(G)+P(S)<1$; graceful degradation on insufficient or single-class data. Cited Corbett & Anderson 1995, Yudelson et al. 2013. Subsection heading Training typo fixed.
- ✅ §3.4.4 Improved Struggle Model — **closed 2026-05-19**. Three-bucket convex combination (behavioural 0.45, mastery gap 0.30, difficulty-adjusted 0.25); mastery gap is one-sided max; difficulty-adjusted uses coverage-weighted shrinkage; graceful-degradation table covers four scenarios; missing-BKT-mastery imputed with cohort mean (Little & Rubin); final Bayesian shrinkage K=5. Closes forward refs from H (IRT) and I (BKT).
- ⏳ §3.5 onwards as previously logged (K / L / M).

See [[Report Sync#Ch3 Design and Modelling — Status Partial (in active rewrite — 2026-05-18)]] for the full sub-task tracker.

#### 3.3.2 Question Difficulty — FORMULA MISMATCH

**Thesis formula (4 components):**
`D_raw = alpha*c_tilde + beta*t_tilde + gamma*a_tilde + delta*f_tilde`

**Actual V2 formula (5 components):**
`D = 0.28*c_tilde + 0.12*t_tilde + 0.20*a_tilde + 0.20*f_tilde + 0.20*p_tilde`

**Missing from thesis:** `p_tilde` — first-attempt failure rate (fraction of students who got it wrong on first try).

#### 3.3.3 Collaborative Filtering (needs update)

Thesis describes CF as an alternative that "is still going to be implemented alongside the parameter-based approach as a secondary indicator."

**V2 reality:** CF IS implemented and enabled by default. Uses 5 normalized behavioral features, cosine similarity, k=3 nearest neighbours, threshold-based elevation detection. Toggleable in Settings. Shows diagnostic panel in In Class View when enabled.

Comparison table in thesis is accurate structurally but the "justification for current approach" framing needs updating — CF is no longer just proposed, it's live.

### 3.4 UI Design

#### 3.4.1 Design Principles (mostly accurate)
- Student struggle and question difficulty as distinct signals — matches V2
- Lab assistant allocation — implemented in V2
- Avoiding raw data exposure — achieved via normalization
- Supporting decision-making — matches V2 leaderboard-first design

#### 3.4.2 Instructor Dashboard — FIGMA MOCKUPS NEED REPLACING

Three Figma mockups (Figs 8-10):
- Fig 8: Student struggle list + question difficulty list
- Fig 9: Lab assistant allocation view
- Fig 10: Assistant leaderboard

All explicitly labeled as "conceptual design rather than a fully implemented system."

**V2 reality:** All three concepts are implemented in the actual dashboard, but the UI looks different from Figma mockups. Screenshots of the real dashboard should replace these.

#### 3.4.3 Visual Encoding (accurate)
Threshold tables for struggle (None/Low/Medium/High with Green/Yellow/Orange/Red) and difficulty (Easy/Medium/Hard/Very Hard) match V2 implementation in `config.py`.

**Note:** V2 uses different label names — "On Track" instead of "None", "Minor Issues" instead of "Low", "Needs Help" instead of "High" for struggle.

---

## AI Assistant — RAG Design

> ⚠️ **Placeholder — not yet written** (Meeting 3, 2026-04-08)

### Architecture: SQL + ChromaDB Hybrid (Dr. Batmaz)

- Layer 1: SQL pre-filter narrows candidate session records
- Layer 2: ChromaDB vector search over filtered set for semantic similarity
- Layer 3: LLM generates contextual recommendation from retrieved context

This reduces pipeline complexity vs standard RAG by using structured metadata
filtering before invoking the vector store.

> ⚠️ Requires literature review: RAG (Lewis et al., 2020), ChromaDB,
> hybrid retrieval approaches. Not yet written.
> 📋 See also: [[Code/Assistant App/Operations/RAG Architecture]]

---

## Missing from design chapter entirely

These V2 features have no design coverage in the thesis:

- **IRT difficulty model** — Rasch 1PL via joint MLE (see [[IRT Difficulty Logic]])
- **BKT mastery tracking** — HMM with 4 parameters (see [[BKT Mastery Logic]])
- **Improved struggle model** — 3-component: behavioral + mastery gap + difficulty-adjusted (see [[Improved Struggle Logic]])
- **Measurement confidence** — confidence scoring for incorrectness estimates
- **Mistake clustering** — TF-IDF + K-means + OpenAI labeling
- **Saved sessions** — CRUD, retroactive save, academic period filtering
- **Data analysis views** — 6 analysis charts
- **Lab assistant system** — join/assign/self-claim/mark-helped flow
- **Settings page** — model toggles, CF threshold, auto-refresh config
- **Sound effects** — event-triggered browser audio
- **Academic calendar** — period labeling for submissions

---

## New placeholder sections (added 2026-04-12)

Skeleton subsections now exist in the tex file but have no content yet. What to write in each:

### §3.3.x — Mistake Clustering

Design of the mistake clustering pipeline: TF-IDF vectorisation of raw student answer strings → K-means clustering with auto-k via silhouette scoring → OpenAI call to label each cluster with a short description. Justify why clustering surfaces systematic error patterns that per-answer inspection misses. Note that auto-k avoids hardcoding the number of misconceptions per question.

### §3.x — Advanced Model Design (new subsection block)

#### Measurement Confidence

Length and extremity-based confidence weighting for AI incorrectness estimates. Short/vague answers produce less reliable scores — the confidence interval shrinks the effective weight of those estimates. Formula: `conf = min(len(answer)/50, 1.0) * (1 - |score - 0.5| * 0)` (or actual formula from `analytics.py`). Note: computed in V2 but not yet displayed — design intent is to surface it alongside incorrectness scores in a future iteration.

#### Item Response Theory (IRT)

Rasch 1PL model: single difficulty parameter β per question, single ability parameter θ per student. Joint MLE optimisation via scipy L-BFGS-B (`models/irt.py`). Describe when IRT is preferred over the baseline difficulty model (larger class sizes, more submissions per question give more reliable MLE). Reference Rasch (1960) and de Ayala (2009).

#### Bayesian Knowledge Training (BKT)

Hidden Markov Model formulation: latent mastery state (learned / not learned) with 4 parameters — P(L0)=0.3 (prior mastery), P(T)=0.1 (learn transition), P(G)=0.2 (guess), P(S)=0.1 (slip). Per-student per-question mastery sequence updated on each submission. Mastery threshold used to feed mastery-gap signal into improved struggle model. Parameters configurable via Settings sliders (`models/bkt.py`).

#### Improved Struggle Model

3-component weighted sum: behavioral (0.45, same signals as baseline) + mastery gap (0.30, from BKT) + difficulty-adjusted (0.25, struggle scaled by IRT difficulty). Graceful degradation: falls back to baseline if BKT/IRT not available. Include a comparison table vs baseline model (inputs, weights, cold-start behaviour). Source file: `models/improved_struggle.py`.

### §3.4.x — Lab Assistant View

Design intent for the mobile lab assistant app: (1) session join screen — enter 6-char code + name; (2) waiting/unassigned state — holding screen until instructor assigns; (3) assigned student card — shows student name, struggle score classification, submission timeline, help-requested flag; (4) mark-helped action returns assistant to waiting state. Discuss design choices: URL `?aid=` persistence avoids login friction; minimal mobile UI reduces cognitive load during lab.

---

## Rewrite items

- [ ] Update struggle formula to 7 components with actual weights
- [ ] Add description of Bayesian shrinkage
- [ ] Update difficulty formula to 5 components with actual weights
- [ ] Add `p_tilde` (first-attempt failure rate) description
- [ ] Update CF section — change from "will be implemented" to "is implemented"
- [ ] Replace 3 Figma mockups (Figs 8-10) with actual dashboard screenshots
- [ ] Update threshold label names (On Track/Minor Issues/Struggling/Needs Help)
- [ ] **Write Mistake Clustering section** — see guidance above
- [ ] **Write Advanced Model Design subsections** (Measurement Confidence, IRT, BKT, Improved Struggle) — see guidance above
- [ ] **Write Lab Assistant View section** — see guidance above
- [ ] Address or remove temporal smoothing claims (not active in V2)
- [ ] Remove "event-driven pipeline currently under exploration" or clarify status

## Open questions

- Should the new models (IRT, BKT, improved struggle) go in Ch3 Design or Ch4 Implementation?
- Should the design chapter describe the final system or the design-then-implementation evolution?
- The temporal smoothing was designed but not implemented — mention it as a design decision that was deferred?
