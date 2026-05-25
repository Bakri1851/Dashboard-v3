---
tags: [thesis, evaluation, ch5, methodology, journal, source-material]
date: 2026-05-25
status: 🟢 Live — updated as each phase completes
source: Conversation 2026-05-24 + 2026-05-25 (Bakri + Claude)
related: [[Evaluation Plan]], [[Evaluation PoC Handoff]], [[Ch5 – Results and Evaluation]], [[Improved Struggle Logic]], [[BKT Mastery Logic]], [[IRT Difficulty Logic]], [[Student Struggle Logic]], [[Setup and Runbook]]
---

# v2 Weights and Hyperparams — Methodology Journal

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

> **Audience.** A future writer (Bakri or another Claude chat)
> drafting §5.1, §5.6, or any Methodology paragraphs. Read this
> before writing anything about the evaluation approach, training
> procedure, or v1/v2 comparison.

---

## 1 · Starting position (what existed before this work)

The dashboard had two pieces of mature infrastructure and one
gaping evaluation hole.

**Mature:** the seven-signal struggle composite $S(s)$ at
[[code]] `code2/backend/struggle.py:240-248` and the five-signal
difficulty composite $D(q)$ at `difficulty.py:104-110`. Both used
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

50 of the 2000 LLM-labelled snapshots get a second pass by Bakri
(self-labelled). Cohen's $\kappa$ between Bakri and the LLM on the
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

### Will be added as we go

- Phase 3 — LLM prompt design choices; κ result
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
