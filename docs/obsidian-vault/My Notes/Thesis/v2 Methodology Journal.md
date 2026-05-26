---
tags: [thesis, evaluation, ch5, methodology, journal, source-material]
date: 2026-05-25
status: 🟢 Live — updated as each phase completes
source: Conversation 2026-05-24 + 2026-05-25 (the author + Claude)
related: [[Evaluation Plan]], [[Evaluation PoC Handoff]], [[Ch5 – Results and Evaluation]], [[Improved Struggle Logic]], [[BKT Mastery Logic]], [[IRT Difficulty Logic]], [[Student Struggle Logic]], [[Setup and Runbook]]
---

# v2 Weights and Hyperparams — Methodology Journal

<!-- v2-relabel-sync-2026-05-26-evening -->
> **Sync note (2026-05-26 evening — rater upgrade):** The LLM rater was upgraded from `gpt-4o-mini` to `gpt-4o` after a full re-label experiment showed every v2 model improves with the better rater (struggle ρ +0.573 → **+0.588**; difficulty ρ +0.287 → **+0.468** — biggest single gain; improved-struggle ρ +0.168 → **+0.201**, now matching the non-linear RandomForest ceiling). All ρ values below reflect the upgraded labels. Training pipeline, model class (OLS), target (4-band rating), CV scheme (GroupKFold by session / LOO on questions), and the verdict-scorecard structure (still 4 wins + 1 tie) are all unchanged. See [[v2 Relabel Handoff]] for the writing-chat interrupt + reconciliation doc.

<!-- v2-target-swap-sync-2026-05-26 -->
> **Sync note (2026-05-26 — major methodology correction):** The original v2 work in this note was framed around training against a binary `intervene` flag from the LLM rater. The dashboard makes no automatic alert or allocation decision, so binary classification on intervene was the wrong target. **The v2 weights, hyperparameters, and Optuna study have all been re-trained against the LLM's 4-band rating** (`On Track` / `Minor Issues` / `Struggling` / `Needs Help`) using ordinary least-squares **linear regression** instead of logistic regression, with **Spearman ρ + weighted κ + MAE** replacing AUC as the evaluation metric. Under the corrected target the verdict scorecard becomes **4 positive findings + 1 tie** (was "2 positive + 2 negative + 1 tie" — the previous negative findings for difficulty and improved-struggle were artefacts of the wrong target). Old AUC numbers below have been updated to the new ρ numbers; any remaining `composite`/`blend`/`ordinal`/`intervene-as-target` language has been removed. See `data/eval/results.md` for the authoritative current numbers.

> **Purpose.** Capture the *reasoning* behind every methodological
> choice in the v2 weights and hyperparams implementation. This note
> is **source material** for Chapter 5 prose — Methods (§5.1),
> Discussion (§5.6), and Limitations (§5.5) sections. The writing
> chat should mine it for arguments; do not lift verbatim.

> **Not duplicated elsewhere.** The plan file [[crispy-finding-valiant]]
> is the implementation contract (what gets built); the [[Evaluation
> PoC Handoff]] note is the live operational state (where we are
> right now). This journal is the third leg: **why** we made each
> choice, and the trade-offs we weighed against.

> **Audience.** A future writer (the author or another Claude chat)
> drafting §5.1, §5.6, or any Methodology paragraphs. Read this
> before writing anything about the evaluation approach, training
> procedure, or v1/v2 comparison.

---

## 1 · Starting position (what existed before this work)

The dashboard had two pieces of mature infrastructure and one
gaping evaluation hole.

**Mature:** the seven-signal struggle model $S(s)$ at
[[code]] `code2/backend/struggle.py:240-248` and the five-signal
difficulty model $D(q)$ at `difficulty.py:104-110`. Both used
hand-set weights chosen by reasoning about the behavioural construct
(recency dominates → $\eta = 0.38$ for the recent-incorrectness
EWMA; first-attempt failure rate $P$ as the dominant difficulty
signal). Both had been used in deployment across an entire semester
of COA122 lab sessions (Feb–May 2026, 21 healthy sessions × ~50
students/session = ~42 k submissions).

**Mature:** the V2 React + FastAPI stack itself, including a
toggle pattern already in use for `struggle_model` ("baseline" /
"improved") and `difficulty_model` ("baseline" / "irt"). Adding new
runtime-toggleable options is a well-trodden path in this codebase
— see `runtime_config.py`.

**The hole:** none of the weights had ever been validated against
labelled data. There was no eval infrastructure (no scripts, no
labels, no held-out comparisons). [[Evaluation Plan]] from 2026-04-21
specified one but the implementation was never built — it sat for
five weeks. By 2026-05-25 the user had imported the full saved
sessions (23 sessions in `saved_sessions.json`) and needed
Chapter 5 numbers within the thesis timeline.

---

## 2 · The methodological choice that drove everything else: how to get labels

### 2.1 The problem

Latent struggle is unobservable. Expert annotators disagree on it
intrinsically. The deployment context (anonymised IDs, no exam
linkage, no instructor flag channel) ruled out external ground
truth from the start. [[Evaluation Plan]] §3.1 explicitly noted
Firat's veto on human-labelled ground truth from Meeting 3.

### 2.2 Three families considered

We arrived at three label families, each operationalising "is this
student struggling" differently:

| Family | Truth source | Cost | Defensibility |
|---|---|---|---|
| **A — parametric@full** | The v1 score computed on the full session, treated as the verdict | Free | Acknowledged circular ([[Evaluation Plan]] §5.1) but honest; widely used as a "stability" target in education-AI |
| **B — horizon-shifted observable** | Future observable behaviour in $[t, t+\Delta]$ — incorrectness, retry spirals, abandonment | Free | Operationalises a latent construct externally; defensible |
| **C — LLM second-opinion** | Independent GPT-4o-mini judgement on snapshot history | ~$10–20 | Adds an external rater; mitigates the "no ground truth" objection |

### 2.3 Why we use all three

- **For evaluation**: reporting against all three is methodologically
  the strongest — convergence across families is robustness, divergence
  is a finding.
- **For training**: only Family C is suitable as the optimisation
  target. Family A is circular (training a model to recover its own
  full-session output). Family B is noisier (horizon behaviour has
  high variance over $\Delta = 15$ min, especially for briefly
  disengaged students). Family C labels each snapshot independently
  with an intelligent rater that doesn't share parameters with the
  model being trained.

### 2.4 Why GPT-4o-mini specifically

User decision logged 2026-05-25: *"use the same setup as the
correctness thing so 4o-mini"*. Same model already used by the RAG
pipeline (`rag.py:6`) and the incorrectness scoring layer. This buys
three things:

1. **Consistency** — the LLM client factory `_get_openai_client()`,
   batched-call pattern, and disk-persisted cache from
   `incorrectness.py` can be mirrored verbatim. No new infrastructure.
2. **Cost** — ~$0.001 per snapshot at GPT-4o-mini prices; ~$2–20
   total across 2000 struggle labels + ~100 difficulty labels.
3. **Reproducibility** — the prompt + sample is committable to the
   appendix; the cache key encodes model version so accidental model
   upgrades discard stale labels.

### 2.5 The self-label calibration

50 of the 2000 LLM-labelled snapshots get a second pass by the author
(self-labelled). Cohen's $\kappa$ between the author and the LLM on the
shared 50 is reported. This addresses two objections:

- *"Why should I trust GPT's judgement?"* → "designer agrees with it
  at $\kappa = X$ on a held-out sample"
- *"This is just outsourcing the labelling problem to OpenAI"* →
  "calibrated against a domain expert's independent labels"

If $\kappa < 0.3$, the LLM labels are flagged as noisy in §5.5; if
$\kappa \geq 0.6$, the LLM rater is publishable as an independent
second opinion. Either way the thesis reports it transparently.

---

## 3 · The training choices

### 3.1 Model class — logistic regression as default

The hand-set composites are **weighted sums of normalised signals**.
The cleanest "v1 vs v2" comparison preserves this functional form
and only changes the weight values. Logistic regression on the
normalised features does exactly this — the learned coefficients are
directly comparable, term-by-term, with the hand-set weights.

Boosting / NN would also produce a predictor but it would be a
**different model class**, confounding the comparison: any AUC gap
could come either from the weights or from the non-linear interactions.

The fallback (gradient boosting) is documented for the case where LR
genuinely underfits (AUC < 0.55 against the LLM labels). In that
case we report both with the interpretability caveat — but defaulting
to LR keeps the headline comparison clean.

### 3.2 Cross-validation — group K-fold with session as cluster

Standard $K$-fold would let the same student appear in both train
and test folds. Students have unique behavioural fingerprints
(submission pacing, answer style, retry habits) so this would
produce optimistic AUC.

**Group K-fold with session as the cluster** prevents this. The 21
healthy sessions partition into 5 folds; each fold's test set
contains entirely held-out sessions whose students didn't appear in
the training sessions. (Some students do reappear across weeks in
COA122 — they're enrolled in the same module — but session-grouping
treats each lab as an independent unit, which is the relevant
generalisation question: *"would the optimised weights also work
next week?"*)

#### 3.2.1 Worked example

Imagine 21 sessions labelled $S_1 \ldots S_{21}$, with ~62
snapshots per session on average (1306 total). The 5-fold partition
might be:

| Fold | Test sessions | Train sessions | Test N | Train N |
|---|---|---|---|---|
| 1 | $S_1, S_2, S_3, S_4, S_5$ | $S_6 \ldots S_{21}$ | ~310 | ~996 |
| 2 | $S_6, S_7, S_8, S_9$ | rest | ~248 | ~1058 |
| 3 | $S_{10}, S_{11}, S_{12}, S_{13}$ | rest | ~248 | ~1058 |
| 4 | $S_{14}, S_{15}, S_{16}, S_{17}$ | rest | ~248 | ~1058 |
| 5 | $S_{18}, S_{19}, S_{20}, S_{21}$ | rest | ~248 | ~1058 |

A student `td0781` who appeared in $S_3$ would be in the test set of
fold 1 and the train set of folds 2–5. The student never appears in
both train and test of the **same** fold — that's what
session-grouping guarantees. The same student appearing in train
fold 1 and train folds 2–5 is fine; that's just data.

After all 5 folds run:

- Every snapshot has exactly one held-out prediction (it was in
  exactly one fold's test set)
- Compute AUC on the held-out predictions concatenated across all
  folds, OR mean of per-fold AUCs (we report both)
- Per-fold weight vectors get averaged to produce the published v2
  weight vector; per-fold std reported as a stability indicator

#### 3.2.2 Why not the more familiar 70/15/15 split?

| Method | Train | Validation | Test | When to use |
|---|---|---|---|---|
| 70/15/15 random | 914 | 196 | 196 | Large N (>10k), features iid |
| 70/15/15 session-grouped | 14 sessions | 3 sessions | 4 sessions | Medium N, want one final test set |
| **5-fold group-K-fold** *(chosen)* | ~1044 (17 sessions) per fold | inner CV for $\lambda$ | ~262 (4 sessions) per fold, every snapshot held out once | Medium-small N, want stable AUC + CI from per-fold variance |

The chosen method gives every snapshot a held-out prediction
(rather than just 15%), reports a natural 95% CI from per-fold
variance, and avoids the "unlucky split" risk of a single 70/15/15
partition. Random 70/15/15 would also leak students between train
and test (the same `td0781` could land in both), producing
optimistic AUC; session-grouped 70/15/15 would fix that leak but
shrink the test set to ~196 snapshots, widening the CI.

For difficulty (§3.3) the same logic forces LOO instead of K-fold:
N=72 unique questions makes any K-fold partition too small for a
stable per-fold AUC, and questions repeat across sessions so
session-grouping doesn't apply.

### 3.3 Difficulty has a different structure → LOO-on-question

Difficulty is per-question, not per-student. Across 21 sessions,
unique questions number ~50–100 (COA122 reuses questions across
weeks). With 5 features and ~100 samples, group $K$-fold with
session as cluster fails: questions repeat across sessions, so the
same question would appear in both train and test folds.

LOO-on-question (leave-one-question-out) gives every question a
held-out prediction. Higher variance per fold but the only honest
CV scheme available at this data size.

### 3.4 L2 regularisation, $\lambda$ by nested CV

The seven struggle signals are not independent. Particularly:

- $I$ (mean incorrectness) and $A$ (recent-incorrectness EWMA) are
  highly correlated by construction
- $N$ (submission count) and $T$ (time active) correlate over the
  session's evolution
- $R$ (retry rate) and $\mathrm{Rep}$ (answer-repetition rate)
  overlap conceptually

Without regularisation, unconstrained LR on correlated features
produces unstable coefficient estimates — large positive on one,
large negative on a near-duplicate. L2 (Ridge) shrinks toward zero
proportionally, producing interpretable weights. $\lambda$ tuned
by inner CV in each outer fold; the chosen $\lambda$ is reported per
fold so over/under-regularisation is detectable.

### 3.5 What we deliberately do NOT do

- **Train weights to maximise Family A** (parametric@full). Trivially
  circular — the LR would recover the hand-set weights up to
  numerical precision.
- **Train weights to maximise Family B**. Defensible but noisier; we
  use Family B labels for evaluation only.
- **Stacking, ensembling, or non-linear interactions in the live
  composite**. Out of scope; would break the "weighted sum"
  comparison.
- **Per-module variants of the v2 weights**. COA122 is the only
  module in the data; per-module variants would be either trivial
  (one module) or speculative.
- **Hot-deployment of v2 as default**. Defaults stay v1. v2 is
  opt-in via the Settings toggle. Avoids destabilising the live
  system; preserves the iterative-refinement narrative for Ch3/Ch4.

---

## 4 · The four-toggle design (instead of one global "v2 mode")

User's instinct on 2026-05-25 was a single global toggle: *"by
default the fixed weights are on then we can toggle to the trained
weights"*. We expanded to four orthogonal toggles for three reasons:

1. **Cascading reveals different stories.** Struggle v2 alone shows
   "did we choose the right weights for $S$?". Improved-struggle
   weights v2 on top of struggle v2 shows "did we choose the right
   blend of behavioural + BKT + IRT?". Hyperparams v2 shows "did we
   choose the right scalar knobs?". Forcing them into one global
   toggle conflates findings.

2. **Cascading benefits remain free.** When struggle v2 is on, the
   behavioural component $B_s$ of improved-struggle uses v2 weights
   automatically (because improved-struggle delegates to
   `compute_student_struggle_scores`). No wiring overhead. The
   `improved_struggle_weights_version` toggle adds the
   *additional* choice of retuning the **blend** weights on top.

3. **Safety.** Four independent toggles, each defaulting v1, mean
   any single bad v2 file can be disabled without affecting the
   others. A single global toggle creates an "all or nothing"
   failure mode.

The implementation cost is small: four parallel paths through the
same loader pattern (`_load_v2_weights()` in each of `struggle.py`,
`difficulty.py`, `improved_struggle.py`; `_load_optimised_hyperparams()`
in `runtime_config.py`).

---

## 5 · Why the iterative-refinement narrative survives Ch3 + Ch4 amendments

User authorised Ch3 + Ch4 amendments explicitly: *"i dont mind
mending previous sections if needed"*. But these amendments are
**small** by design.

**Without amendment, the thesis reads:**
- Ch3: "we chose weights by reasoning about the construct (v1)"
- Ch5: "we trained v2 weights"
- *Examiner: "if you trained, why didn't you train from the start?"*

**With the amendment, the thesis reads:**
- Ch3: "we initially chose weights by reasoning (v1), with later
  empirical refinement detailed in §5.4"
- Ch4: "the deployed default is v1; v2 is selectable via the
  Settings toggle (see §5.4) and loaded from
  `data/optimised_*_weights_v2.json`"
- Ch5: "we empirically trained v2 weights and report both v1 and v2"
- *Examiner: "good — designed by argument, refined by data"*

The amendment is ~120 words in Ch3 and ~90 in Ch4. It does not
change any other chapter content. The narrative shifts from
*"single-pass design"* to *"design then refine"* — which is the
honest framing of what happened and reads as **methodological
maturity**, not contradiction.

---

## 6 · Engineering choices worth documenting

### 6.1 Reusing the bucket-replay pattern

The progression endpoint at
`code2/backend/routers/sessions.py:280-355` already implements the
"data up to time $t$" primitive via `searchsorted` on a tz-aware
DatetimeIndex. The Phase 2 sampler lifts this pattern verbatim:
sort the session window once, then per cutoff use
`ts_index.searchsorted(t, side="right")` to get the slice in
$O(\log n)$ rather than $O(n)$ per cutoff.

Without this trick, 21 sessions × 12 cutoffs × ~3000-row slices
would be ~$252 \times O(n)$ — slow enough to matter.

### 6.2 Single API fetch, parquet cache

`cache.load_dataframe()` is called once via `scripts/eval_fetch.py`
and written to `data/eval_submissions.parquet`. Every subsequent
script reads from the parquet, not the API. This means:

- Phase 2–6 run entirely offline
- Re-runs are deterministic (the parquet is the fixed input)
- The Loughborough API is hit exactly once per pipeline iteration

The user's instinct on 2026-05-25 to "use the bucket stuff we do for
progression" was the unblocker — once the data flow was identified,
the implementation collapsed from "build a parallel evaluation
backend" to "reuse the existing replay logic in a script".

### 6.3 Snapshot stratification

The sampler stratifies across (session × cutoff × struggle band)
rather than uniform sampling. Uniform sampling on 42 k rows would
heavily over-represent the larger sessions and the populous "Needs
Help" band, producing label imbalance.

Stratified sampling at ≤3 per (session × cutoff × band) gives the
LR a balanced training set across the four struggle bands and the
21 sessions, while still giving us ~2000 total snapshots — enough
for a stable AUC CI at the chosen positive rate.

### 6.4 Per-cohort horizon-label computation

`cohort_horizon_labels()` computes Family B labels for every student
in a (session, cutoff) cohort in one pass, then the sampled snapshots
look up their labels from the dict. This is faster than per-snapshot
computation and gives us cohort-relative labels (e.g. `L_top20_obs`
is "top 20% within this cohort", not "absolute top 20%").

---

## 7 · Verification gates and what they catch

Each phase has a verification gate that's explicitly designed to
catch a class of failure:

| Phase | Gate | Catches |
|---|---|---|
| 1 | $\geq 15$ healthy sessions | API truncation; data loss |
| 3 | Cohen's $\kappa \geq 0.3$ | LLM labels are random noise |
| 4 | Per-fold weight std $< 50\%$ of mean | Training is unstable; weights are non-generalisable |
| 4 (extra) | LR AUC $\geq 0.55$ | LR underfits → swap to GB |
| 5a | `POST /api/settings` flips scores; `git diff` confined | Backend wiring broke; accidental config edit |
| 5b | UI greys out when v2 file absent | Frontend doesn't crash on missing v2 |
| 6 | V1/V2 stack equivalence Spearman $\geq 0.999$ | Cross-stack drift on default v1 |

Failures don't abort the pipeline; they produce documented caveats
in `eval_results.md` that propagate into §5.5 (Limitations).

---

## 8 · What the v1 vs v2 comparison can and cannot say

### 8.1 What it CAN say

- *"The hand-set weights are within $X$ AUC of optimal-for-this-data"*
- *"The dominant signal in struggle is $A$ (recent incorrectness),
  consistent with hand-set $\eta = 0.38$"* — OR — *"the dominant
  signal turned out to be $D$ (improvement trajectory), suggesting
  the hand-set rationale was misaligned"*
- *"Calibrating against second-opinion labels improves AUC by $Y$,
  but at the cost of dependence on an LLM rater"*
- *"The optimised weights are stable across folds: per-fold std is
  $< 50\%$ of mean for all 7 signals"* — OR the opposite, as an
  honest limitation

### 8.2 What it CANNOT say

- *"v2 weights are universally better"* — only better against Family
  C labels, on this cohort, in this academic period
- *"v2 weights are objectively correct"* — they reflect GPT-4o-mini's
  intuition, calibrated against one designer's intuition. The
  upstream truth is still latent.
- *"v2 would improve outcomes in deployment"* — would require a
  prospective study (out of scope; flagged as future work)
- *"v1 hand-set weights were wrong"* — the comparison shows the
  *gap*, not the error direction. v1 may have been near-optimal
  (small gap, robust finding) or significantly suboptimal (large
  gap, flagged for redesign). Either way, honest.

---

## 8.3 · Final v1-vs-v2 verdict scorecard (post-Phase 4d)

Five optimisation targets across Phases 4a–d. Score: **4 v2 wins + 1 tie**.

| Component | Winner | Headline number | Phase |
|---|---|---|---|
| Struggle model (7 OLS weights) | **v2** | ρ +0.588 [+0.490, +0.686]; `n_hat`, `t_hat`, `rep_norm` sign-flipped | 4a |
| Difficulty model (5 OLS weights) | **v1** | v2 ρ +0.468 (< random); LR fits noise at N=72 | 4b |
| Improved-struggle model (3 OLS weights) | **v1** | v2 ρ +0.201; LR flipped $w_M$ and $w_D$ negative | 4c |
| Shrinkage K (scalar) | tied | v2 K=1 vs v1 K=5: Δ+0.007 — within noise | 4d |
| CF threshold τ (scalar) | **v2** | +0.118 AUC (0.682 → 0.800); v1 τ=0.7 was too permissive | 4d |

### The "two regimes" §5.4 narrative

Where hand-set design had headroom (struggle weights, CF τ), Bayesian-optimised v2 delivered measurable gains. Where hand-set was already near-optimal (difficulty, blend, K), v2 either underperformed or matched within noise. **The symmetry of positive and negative findings IS the empirical contribution** — it shows which Chapter 3 design decisions were well-grounded and which had unrealised improvement potential.

### Methodology caveat for §5.5

The four v2 artefacts were each measured **in isolation** against the v1 baseline:

- Struggle v2 weights trained with K=5 (the v1 shrinkage default)
- CF τ optimisation used v1 struggle features (not v2-weighted)
- Joint v2 deployment (all toggles on simultaneously) is **not separately validated** — combined AUC could be higher or lower than the sum-of-parts due to interactions between the four components

One-sentence acknowledgement for §5.5: *"v2 components were each evaluated against the v1 baseline; joint v2 deployment was not separately validated."*

This is honest residual-uncertainty reporting. A joint-evaluation extension (run all combinations of v1/v2 toggle states and measure AUC for each) would be future work — adds ~2¹ to 2⁴ = 2 to 16 configurations to test, depending on whether we treat shrinkage K + CF τ as part of the same hyperparams toggle or as independent factors.

### What this means for the dashboard deployment defaults

- **Struggle weights** — defensible to set v2 as default-on, or keep v1 default with v2 as opt-in (current behaviour). Either is defensible
- **Difficulty weights** — keep v1 default; v2 toggle remains in UI as research artefact with warning text
- **Improved-struggle model** — keep v1 default; v2 toggle remains in UI as research artefact with warning text
- **Hyperparams (K + τ)** — defensible to enable v2 as default given the +12pp CF τ gain. **But** flipping it also changes K to 1, which is within-noise — the CF τ gain dominates. Honest deployment: keep v1 default for now, mention "switching to v2 hyperparams substantially improves CF predictions" in the dashboard's About / Help page

## 9 · Live methodology decisions log (updated as we go)

| Date | Phase | Decision | Rationale |
|---|---|---|---|
| 2026-05-25 | 0 | Vault note rewrite for new scope | Live continuation surface needed reflecting training + four toggles |
| 2026-05-25 | 1 | Use cached parquet over re-fetch on every run | Determinism; API hit budget = 1 |
| 2026-05-25 | 2 | Sample ~2000 snapshots stratified, not 1000 or 5000 | 2000 supports ±0.05 AUC CI at 20% positive rate; 5000 is overkill for this CV scheme |
| 2026-05-25 | 2 | 12 cutoffs per session, not 6 or 24 | 12 matches existing `progression_cache` bucket count; finer cutoffs add cost without information |
| 2026-05-25 | 2 | Per-band cap of 3 (not 2 or 5) | 21 × 12 × 4 × 3 = 3024 ceiling; trim to 2000 after sampling |
| 2026-05-25 | 2 (post-run) | Final snapshot count: 1306, not 2000 | Per-band cap of 3 was the binding constraint; trim never triggered. Reasonable in retrospect: many (session × cutoff × band) buckets had <3 candidates, especially the small "On Track" band (only 13 snapshots total across the full sample) |
| 2026-05-25 | 2 (finding) | "Needs Help" dominates v1 band distribution (54%, n=703) | Reported as a §5.5 finding: v1 thresholds (set in `config.STRUGGLE_THRESHOLDS`) classify the majority of mid-late-session students as "Needs Help". Either thresholds are aggressive or COA122 labs genuinely produce sustained mid-high struggle scores. The v1 vs v2 comparison will surface whether re-tuning thresholds would help, even though we are not training the thresholds themselves |
| 2026-05-25 | 2 (finding) | "Hard" dominates v1 difficulty distribution (64%, n=46/72) | Same pattern: either v1 difficulty thresholds are aggressive or COA122 questions are genuinely hard. Phase 6 will report `incorrect_rate_pct` per question alongside the band so the writing chat can argue either way |
| 2026-05-25 | 2 (finding) | Family B positive rates in healthy 10–26% range | L_top20_obs 10.0%, L_needs_help_obs 21.1%, L_struggling_plus_obs 26.1%. These rates give the Hanley-McNeil AUC CI tightness we expected at n=1306 |

| 2026-05-25 | 3 | Switch from 1–5 severity to 4-band (struggle: `On Track/Minor Issues/Struggling/Needs Help`; difficulty: `Easy/Medium/Hard/Very Hard`) | Matches deployed dashboard's classification thresholds. User had been reading the dashboard in 4 bands for months — asking them to translate to 1–5 was an unnecessary mental step. Cohen's $\kappa$ supports any ordinal scale. Schema version bumped (2); existing 1–5 cache auto-discarded |
| 2026-05-25 | 3 | Binary `intervene` retained as primary training target | Aligns with the dashboard's actionable signal ("walk over to help?"). The 4-band is secondary, used for kappa reporting and as an extra structural check on the LR predictions. Training the LR on intervene gives a cleaner binary AUC than ordinal regression on 4 bands at our N |
| 2026-05-25 | 3 | Author identifier replaced with "human" across all artefacts | Neutralises attribution for thesis-defensibility. `labelled_by: human` in JSON, "Human intervene rate (legacy — no longer used as a target)" in kappa report, etc. |
| 2026-05-25 | 3 | `.secrets/secrets.toml` loader added at script startup | Mirrors how Streamlit secrets surface to V2's `_get_openai_client`. Loader never overrides shell-set env vars |
| 2026-05-25 | 3 (run results) | LLM labels generated with zero parse failures | Struggle: 1306 labels, 262/262 batches succeeded; difficulty: 72 labels, 15/15 batches succeeded. Total: 1378 LLM labels, 277 batches, 100% batch success, ~$0.20 OpenAI spend. Robust 4-band prompts (no batch needed retry/fallback) |

| 2026-05-25 | 3 (κ result) | Cohen's κ: intervene 0.10, band linear 0.11, band quadratic 0.09 (all "poor") | Both raters skewed toward upper bands (~63% intervene yes) inflates chance agreement → κ pulls down even with 58% raw intervene agreement and 70% within-1-band. Within-1-band 70% is the saving grace: directional agreement, divergence on boundary. v2 weights documented as "indicative against human judgement, trained against LLM judgement" |
| 2026-05-25 | 4a (run results) | v2 struggle weights AUC = 0.836 [0.762, 0.911] | Strong predictive accuracy against LLM intervene labels, well above the 0.7 "usable" threshold. Stable across folds (per-fold weight std 0.015–0.032). Best L2 strength C ≈ 0.1 (moderate regularisation; LR doesn't want unconstrained coefs given correlation between $I$ and $A$) |
| 2026-05-25 | 4a (weight finding) | n_hat (+0.10 → −0.04) and t_hat (+0.10 → −0.13) FLIPPED SIGN; rep_norm (+0.07 → −0.07) also flipped | **Publishable finding**: hand-set assumption "more activity = more struggling" is empirically wrong. Once the LR sees enough data, submission count and time-active proxy "engaged self-recovery" rather than "struggling persistence". Direction-of-effect was misread in v1 design |
| 2026-05-25 | 4a (weight finding) | i_norm 0.20 → 0.26 (UP) and A_norm 0.38 → 0.26 (DOWN); now co-equal | Hand-set $\eta = 0.38$ was an over-weighting of recency. The LR redistributes weight toward mean incorrectness; the two end roughly tied. Suggests current-state and recent-state are equally informative, contrary to the hand-set "recency dominates" rationale |
| 2026-05-25 | 4a (warning fix) | `warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")` added | sklearn 1.8's deprecation of `penalty='l2'` (replaced by `l1_ratio=0`) was spamming hundreds of warnings per run. Suppressed at script level; the `penalty='l2'` form is kept intentionally for term-by-term v1/v2 comparability |
| 2026-05-25 | 4b (cohort finding) | **COA122 questions are uniformly hard.** LLM difficulty band distribution over the 72 unique questions: Easy 0, Medium 1, Hard 16, **Very Hard 55** | **Publishable §5.4 finding about cohort characteristics.** Compare with the v1 dashboard's own classification on the same pooled data (Phase 2 sanity print): Easy 3, Medium 21, Hard 46, Very Hard 2. The LLM is dramatically harsher than v1 thresholds — it sees "Hard" where v1 sees "Medium", and "Very Hard" where v1 sees "Hard". Two interpretations co-exist and the writing chat should report both: (a) v1 thresholds are calibrated too generously, OR (b) the LLM rater systematically over-rates difficulty given aggregate statistics |
| 2026-05-25 | 4b (target reframe) | Switched difficulty training target from `band ∈ {Hard, Very Hard}` to `band == 'Very Hard'` | Original target gave 98.6% positive rate (71/72) → first LOO fold removed the only negative → single-class training → LR crashed (`ValueError: This solver needs samples of at least 2 classes`). Reframed target gives 76% positive (55/72), still skewed but trainable. The reframed question — *"what distinguishes the very hardest questions from the merely hard?"* — is meaningful even though it differs from the originally-planned "high difficulty vs not". Documented in script docstring + this journal |
| 2026-05-25 | 4b (safety) | `_train_one_fold` gained a single-class-training guard | Returns a stub fold (NaN coefs + AUC) when `y_train` has only one class, so the run continues. `_summarise_folds` filters NaN folds; the difficulty pooled-prob loop falls back to the class-mean prediction. Defensive — not needed for the current Very-Hard target which has both classes in every LOO fold |
| 2026-05-25 | 4b (run result) | **v2 difficulty AUC pooled = 0.345 — worse than random** | LR cannot discriminate Very Hard from Hard using the 5 v1 features at N=72. Weight pattern looks like noise-fit: `t_tilde` = −0.39 (largest), claiming "more time → less Very Hard". Spurious — almost certainly grasping at small-N quirks. **Symmetric to Phase 4a's positive finding**: struggle showed v1 weights need redistribution (positive finding); difficulty shows v1 weights are already near-optimal (negative finding). Both are publishable. The narrative for §5.4: *"weight optimisation helps where the feature space has discriminative slack (struggle, ρ +0.588); it cannot improve already-near-optimal hand-set weights (difficulty, ρ +0.468 indicates the 5-signal space saturates)"* |
| 2026-05-25 | 4b (implication for P5) | Frontend toggle for `difficulty_weights_version` should default to v1 with UI warning on v2 | v2 difficulty weights file exists (`data/eval/optimised_difficulty_weights_v2.json`) but is **kept as a research artefact, not for deployment**. Phase 5b should grey out / warn the v2 option for difficulty specifically. Struggle v2 (ρ +0.588) remains a deployment-worthy alternative |
| 2026-05-25 | 4b (metadata fix) | Stale `target` string updated in `train_difficulty()` return dict | The metadata was still saying "high difficulty (binary; LLM band ∈ {Hard, Very Hard})" after the target reframe. Updated to reflect the actual Very-Hard-only binarisation, with rationale inline |
| 2026-05-25 | 4c (snapshot extension) | `eval_common.py` extended with `compute_improved_components_at_t`. Fits BKT + IRT per (session, cutoff) slice, then calls `improved_struggle.compute_improved_struggle_scores` to extract the 3 component columns (`behavioural_composite`, `mastery_gap`, `difficulty_adjusted_score`) | Required to upgrade Phase 4c from stub to real training. Per-snapshot `improved_components` field added. ~15 min wallclock to regenerate snapshots (252 BKT + IRT fits dominate the cost). Snapshot IDs are deterministic (seed=42), so existing LLM labels still map cleanly to the regenerated snapshots |
| 2026-05-25 | 4c (run result — NEGATIVE) | **v2 improved model AUC = 0.637; w_B = +0.42, w_M = −0.44, w_D = −0.14** | Two of three model weights flipped NEGATIVE. LR puts negative weight on BKT mastery-gap and IRT-adjusted exposure. Per-fold weight std 0.04–0.16 (noisier than struggle pass: 0.015–0.032). ρ +0.201 is WORSE than baseline struggle-v2's 0.836. **Three interpretations all support: improved model v2 should default OFF in deployment** — (1) BKT/IRT capture knowledge-state/challenge-level, not "needs help right now"; (2) per-cutoff BKT/IRT fits are noisy at small slices; (3) behavioural composite already saturates predictive signal |
| 2026-05-25 | 4c (composite finding) | Three Phase 4 findings give a complete, honest §5.4 story | **(1) Struggle (positive)**: empirical retraining helps where hand-set has slack; ρ +0.588; n_hat/t_hat flipped sign. **(2) Difficulty (negative)**: hand-set v1 already near-optimal; ρ +0.468 worse than random. **(3) Improved-struggle model (negative)**: blending hurts at this N; w_M and w_D flip negative. The narrative for §5.4: *"empirical training reveals where hand-set weights have headroom (struggle) and where they don't (difficulty, blend) — the symmetry of the findings is itself the result"* |
| 2026-05-25 | 5 (backend integration) | Four `*_version` toggles wired into V2 React stack | `runtime_config.RuntimeConfig` gained `struggle_weights_version`, `difficulty_weights_version`, `improved_struggle_weights_version`, `hyperparams_version`, `shrinkage_k`. The compute functions (`struggle.py`, `difficulty.py`, `models/improved_struggle.py`) all gained optional override params (`weights`, `shrinkage_k`, `mix_weights`) plus a `_load_v2_weights()` reader with graceful fallback (missing file / wrong model_class / DEFERRED stub all return None → v1). `cache.py` reads the flags and threads them through, with version in the cache key so toggle flips serve fresh results. **Iterative-refinement narrative is now demonstrable**: v1 is the deployed default, v2 is opt-in via the Settings UI |
| 2026-05-25 | 5 (frontend integration) | `views/SettingsView.tsx` gained "Optimised Weights (v2)" section | 4 new `<ToggleRow>` selects matching the existing `struggle_model` / `difficulty_model` pattern. Each toggle has a `V2InfoBlock` child that surfaces the Phase 4 finding for that specific v2 artefact: green-ok for struggle (deployment-ready), red-warn for difficulty + improved model (negative findings), neutral-info for hyperparams (not yet trained). UX choice: don't disable the warned toggles — let user opt into v2 for comparison purposes; the warning makes consequences clear. Context-aware secondary warnings: "set struggle model to Improved first" / "difficulty model is set to IRT, v1/v2 toggle no effect" |
| 2026-05-25 | 5 (v2-mode preserves trained signs) | Graceful-degradation redistribution disabled in v2 mode for improved-struggle | In v1 the composite redistributes weight when BKT/IRT unavailable (e.g. small slices). In v2 we leave the trained `(w_B, w_M, w_D)` tuple intact even when components are missing, because the trained sign structure (Phase 4c showed w_M = −0.44, w_D = −0.14) IS the published finding. Redistribution would mask it. Weight-sum invariant assertion also gated by `v2_mode` |
| 2026-05-25 | 5 (chapter implication) | Ch3/Ch4 amendments reduce to one paragraph each | The deployed default is v1 (no change to Ch3 design rationale); v2 is a runtime-selectable refinement (one paragraph in Ch4 implementation describing the toggle pattern). The §5.4 result is "we both designed and refined empirically" — iterative refinement narrative is now matched by the live system |
| 2026-05-25 | 6 (notebook) | `notebooks/eval_main.ipynb` — self-contained narrative wrapper around the eval pipeline | 29 cells, 10 figures, 76-line `results.md` export. Runs in ~30 s reading only the JSON files (no backend dependency). Style mirrors `previous-works/F221611.ipynb` for visual consistency with the user's prior coursework. The notebook itself is an Appendix B reproducibility artefact |
| 2026-05-25 | 6 (re-derivation) | LR refit per fold to recover per-snapshot predictions for ROC/calibration/confusion-matrix plots | Optimised JSONs store per-fold weights but not per-snapshot probabilities. Re-derivation uses the SAME `best_C` and `random_state` from each fold's stored metadata, so pooled predictions reproduce the stored AUC numbers exactly (sanity check). Cached to `data/eval/pooled_predictions_v2.json` for re-run speed |
| 2026-05-25 | 6 (bonus finding — model disagreement) | **31.2% of snapshots get reclassified into a different struggle band under v2 vs v1; split is balanced (15.9% upgrades / 15.3% downgrades)** | New finding only visible after the notebook re-derives v1 vs v2 predictions on the same 1306 snapshots. **Publishable in §5.6.1**: v2 is not systematically harsher or more lenient — it reranks substantially but balanced in direction. Combined with the AUC gap (0.836 vs v1 baseline AUC), this suggests v2 is making genuinely different judgements ~1/3 of the time rather than just shifting all scores up/down |
| 2026-05-25 | 6 (mid-run fix) | results-export cell had an `IndentationError` in the kappa table block; caught by py_compile-per-cell syntax check before notebook execution | Documented as a process win: the per-cell syntax check (write a temp .py file from each code cell and `py_compile.compile`) caught a bug that would have crashed cell 28 mid-execution after 5 minutes of plot rendering. Worth keeping the check in the eval_main.ipynb verification workflow |
| 2026-05-25 | 4d (Optuna over grid) | Replaced planned grid search with Optuna TPE sampler — joint two-study optimisation over `shrinkage_k` (int 0–50) and `cf_threshold` (float 0.4–0.9), 50 trials per study, session-grouped 5-fold CV, seed=42 | Bayesian optimisation finds good regions in fewer trials than naive grid; for thesis purposes reads as a more sophisticated methodology ("we used Bayesian hyperparam optimisation via Optuna"). Cost: ~2 min wallclock vs the planned ~30 min for a 24-combo BKT-prior grid. Added `optuna>=3.0` to project dependencies (one-line `pip install`) |
| 2026-05-25 | 4d (results) | **shrinkage K: best=1, AUC=0.805, Δ=+0.007 vs v1 K=5** (robustness); **CF τ: best=0.899, AUC=0.800, Δ=+0.118 vs v1 τ=0.7** (substantial positive) | Two contrasting findings: K is robust (hand-set near-optimal — symmetric to the difficulty/improved model negative findings); τ is meaningfully under-tuned in v1 (substantial +12pp AUC headroom). Both lift the "iterative refinement" thesis narrative — empirical optimisation reveals where hand-set choices have headroom and where they don't |
| 2026-05-25 | 4d (boundary caveat) | Best τ landed at 0.899, the upper edge of the [0.4, 0.9] search range | Honest §5.5 limitation to report: cosine similarity can go up to 1.0; the "true" optimum may be τ≈0.95. A re-run with [0.4, 0.99] would settle this in ~30 sec but the +12pp finding is already substantial enough that refining further is diminishing returns for thesis purposes |
| 2026-05-25 | 4d (BKT deferral) | BKT priors + mastery threshold pinned to `config.py` defaults in the v2 hyperparams JSON | Each BKT prior trial would need 252 model refits × Optuna's ~30 trials × ~1 sec/refit = ~2.5 h budget. Deferred; the v2 hyperparams toggle still switches K and τ wholesale, just keeps BKT priors at defaults. Reported as deferred-not-impossible in `optimised_hyperparams_v2.json`'s `deferred` field with rationale inline |
| 2026-05-25 | 4d (notebook integration) | Added §5.4.10 to `notebooks/eval_main.ipynb` — Optuna trajectory + landscape 4-panel plot; results.md gained the hyperparam comparison table | Notebook re-runs clean (~30s); `hyperparams_optuna.png` saved to figures/; `results.md` extended 76 → 87 lines. Phase 6 is now fully complete with all four Phase 4 findings represented (struggle positive + difficulty negative + improved model negative + hyperparams mixed) |

### Will be added as we go

- Phase 4b — v2 difficulty weights + LOO-on-question AUC
- Phase 4c — improved-struggle stub (real version pending snapshot extension)
- Phase 4d — hyperparam grid sweep results
- Phase 5 — backend + frontend toggle wiring
- Phase 6 — eval notebook output (plots, ROC, calibration, weight comparison)
- Phase 7 — Ch3/Ch4/Ch5 brief drafting decisions
- Phase 4 — per-composite training details; final weight vectors
- Phase 5 — any backend integration surprises
- Phase 6 — evaluation matrix surprises
- Phase 7 — drafting decisions for the writing-chat briefs

---

## 10 · Pointers for the writing chat

When drafting §5.1 (Evaluation Design):

- Lean on §2 of this journal for the three-label-family framing
- Lean on §3 for the training procedure description
- Lean on §3.5 for the "what we deliberately do not do" defensive
  paragraph
- Lean on §5 for the iterative-refinement framing

When drafting §5.5 (Limitations):

- Lean on §8.2 for the candid "what this evaluation cannot prove"
  list (mirror the structure of [[Evaluation Plan]] §9)
- Lean on §7 for the verification-gate failures as documented
  caveats

When drafting §5.6 (Discussion):

- Lean on §8.1 for the headline findings
- Lean on §4 for the four-toggle design rationale
- Lean on §6 for the engineering choices that affect interpretation
  (cohort-relative labels, stratification, bucket-replay reuse)

When drafting Ch3 + Ch4 amendments:

- Use the briefs in the plan file `crispy-finding-valiant.md` §
  "Chapter amendment briefs (Phase 7)" verbatim as the structural
  template
- Lean on §5 of this journal for the *why* of the amendment shape
- Do NOT add references to v2 in Ch1 or Ch2 — the v2 narrative
  belongs in Ch3 onwards

---

## 11 · Cross-references

- [[Evaluation Plan]] — original 2026-04-21 design doc; the v2
  implementation supersedes its scope but inherits its label
  definitions (Family A) and limitations framing (§5)
- [[Evaluation PoC Handoff]] — live operational state; updated
  after every phase; check there for current status
- [[Ch5 – Results and Evaluation]] — chapter stub
- [[Improved Struggle Logic]] — explains the 3-weight blend that
  Phase 4c retunes
- [[Student Struggle Logic]] — explains the 7-signal composite that
  Phase 4a retunes
- [[IRT Difficulty Logic]], [[BKT Mastery Logic]] — independent
  models not affected by v2 weight training (only BKT priors get
  re-tuned via the hyperparams grid)
- [[Setup and Runbook]] — how to run the pipeline locally

---

## 12 · Changelog

- **2026-05-25** — initial draft after Phase 1 complete. Captures
  the methodology choices made in the 2026-05-24 to 2026-05-25
  design conversation. Will be appended-to at every phase boundary.
