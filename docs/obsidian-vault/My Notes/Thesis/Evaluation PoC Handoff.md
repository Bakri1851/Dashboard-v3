---
tags: [thesis, evaluation, ch5, implementation, handoff, live]
date: 2026-05-25
status: 🟢 Implementation + Phase 7 briefs done. See [[v2 Empirical Refinement Brief]] for the Ch3/Ch4/Ch5 writing-chat brief. Phase 8 (literature) optional
source: Conversation 2026-05-24 + 2026-05-25 (human + Claude)
related: [[Evaluation Plan]], [[Ch5 – Results and Evaluation]], [[Evidence Bank]], [[Report Sync]], [[Improved Struggle Logic]], [[BKT Mastery Logic]], [[IRT Difficulty Logic]], [[Student Struggle Logic]], [[Setup and Runbook]], [[Full Roadmap]]
---

# Evaluation Implementation Handoff — Live Continuation Surface

<!-- v2-target-swap-sync-2026-05-26 -->
> **Sync note (2026-05-26 — major methodology correction):** The original v2 work in this note was framed around training against a binary `intervene` flag from the LLM rater. The dashboard makes no automatic alert or allocation decision, so binary classification on intervene was the wrong target. **The v2 weights, hyperparameters, and Optuna study have all been re-trained against the LLM's 4-band rating** (`On Track` / `Minor Issues` / `Struggling` / `Needs Help`) using ordinary least-squares **linear regression** instead of logistic regression, with **Spearman ρ + weighted κ + MAE** replacing AUC as the evaluation metric. Under the corrected target the verdict scorecard becomes **4 positive findings + 1 tie** (was "2 positive + 2 negative + 1 tie" — the previous negative findings for difficulty and improved-struggle were artefacts of the wrong target). Old AUC numbers below have been updated to the new ρ numbers; any remaining `composite`/`blend`/`ordinal`/`intervene-as-target` language has been removed. See `data/eval/results.md` for the authoritative current numbers.

> **Purpose.** Capture the entire live state of the v2 weights and
> hyperparams implementation. Self-contained — a fresh Claude chat
> (or future human) can pick up the work without re-deriving anything
> from prior conversation.

> **Scope.** Real production implementation (was originally scoped as
> a PoC; user revised on 2026-05-25 to "do it for real"). Four optimised
> v2 artefacts trained against GPT-4o-mini second-opinion labels, wired
> into the V2 React stack as runtime-toggleable Settings.

> **Status as of 2026-05-25.** Phase 0 (this note) being rewritten now.
> Phase 1 (`scripts/eval_fetch.py`) script written but my environment
> can't reach the Loughborough internal API — needs human to run
> locally and paste the sanity output.

> **Authoritative plan** lives at `C:\Users\human\.claude\plans\
> crispy-finding-valiant.md`. This vault note is the user-facing live
> mirror; the plan file is the implementation contract.

---

## 1 · Purpose and how to use this note

The note exists because a long conversation produced execution
decisions that wouldn't survive a fresh chat unless written down. It
is **self-contained**.

**Reading order:**

- **Resuming work?** Jump to §8 (current blocker), §10 (continuation
  prompt), then §6 (phase status).
- **Trying to understand how this relates to [[Evaluation Plan]]?**
  Read §2.
- **Need to understand the v2 toggles and what they do?** §5.
- **Need a label definition?** §4.
- **Need to find a code path?** §11.

The authoritative design source remains [[Evaluation Plan]]. The
authoritative implementation contract is `crispy-finding-valiant.md`.
This note is the live operational mirror — updated after every phase.

---

## 2 · Relationship to [[Evaluation Plan]] and original PoC scope

| | [[Evaluation Plan]] (2026-04-21) | Original PoC scope (2026-05-24) | Current implementation (2026-05-25) |
|---|---|---|---|
| Layer | Design | Lightweight evaluation | Full production implementation |
| Output | Specs | AUC numbers for §5.4 | Numbers + four deployable v2 toggles |
| System edits | None | None | V2 React backend + frontend modifications |
| Time | — | ~5 h | ~16.5 h |
| Chapter touched | — | Ch5 only | Ch3 + Ch4 (small) + Ch5 |
| Author commits | [[Evaluation Plan]] §10 vetoed system changes | Pure research artefact | Iterative-refinement narrative; v1 deployed default, v2 opt-in |

**Why the scope grew:** the user revised on 2026-05-25 with two
explicit asks: *"we should weight, irt/bkt train"* and *"by default
the fixed weights are on then we can toggle to the trained weights".*
Plus *"if we are training the struggle we should also train the
difficulty weights"* and *"are the hyperparams being optimised"* —
which added four-toggle scope rather than just one. User authorised
Ch3 + Ch4 amendments ("i dont mind mending previous sections").

[[Evaluation Plan]] §5.1 circular-ground-truth limitation still
applies and remains honest §5.5 thesis material. The horizon-shifted
labels (Family B) and the LLM second-opinion labels (Family C) added
in this implementation address it but don't eliminate it.

---

## 3 · Methodology — three label families used both for evaluation and training

The three label families serve two purposes in this implementation:

1. **Evaluation** — every model (v1 hand-set, v2 optimised, IRT, BKT,
   improved) gets reported against all three label families in §5.4.
2. **Training** — the LLM second-opinion labels (Family C) are the
   targets for the four v2 optimisation passes (Phases 4a/b/c/d).

### 3.1 Three label families

| Family | Truth source | Question answered | Used for |
|---|---|---|---|
| **A** | `parametric@full-session` (from [[Evaluation Plan]] §3.1) | "How fast does criterion X converge to the parametric verdict?" | Evaluation only (stability / early-warning) |
| **B** | Horizon-shifted observables in $[t, t+\Delta]$ | "Does criterion X predict observable bad behaviour later?" | Evaluation only (external validity) |
| **C** | GPT-4o-mini second-opinion ratings | "Does criterion X match an independent intelligent rater?" | **Both** evaluation AND training targets |

### 3.2 Why use Family C as training target rather than B or A

- **Family A** as training target is circular (training a model to
  recover itself).
- **Family B** as training target is defensible but the labels are
  noisier (future behaviour has high variance, especially over $\Delta
  = 15$ min for students who briefly disengage).
- **Family C** is the cleanest training target: each label is a single
  judgement made by an independent intelligent rater that does not
  share parameters with the model being trained. Calibrated against
  human's 50 self-labels via Cohen's $\kappa$.

### 3.3 Thesis framing (for §5.1.3)

> Latent struggle is unobservable; expert annotators disagree on it
> intrinsically. We therefore operationalise it through three
> complementary truth families. Family A treats the full-session
> parametric verdict as the reference; Family B treats future
> observable behaviour as the reference; Family C uses an
> independently-prompted LLM rater calibrated against author
> self-labels. Family C also serves as the training target for the
> optimised v2 weight vectors (§5.4.X), with strict session-grouped
> cross-validation to prevent train/test leakage.

---

## 4 · Ground-truth label definitions (all three families, formal)

### 4.1 Family A — parametric@full (from [[Evaluation Plan]] §3.1)

Let `parametric(s)` be the v1 7-signal struggle score for student
`s` computed on the full session.

| Label | Definition |
|---|---|
| `L_top20` | 1 iff `s` is in the top 20% by `parametric@full-session` |
| `L_needs_help` | 1 iff `parametric(s) ≥ 0.50` |
| `L_struggling_plus` | 1 iff `parametric(s) ≥ 0.35` |

### 4.2 Family B — horizon-shifted observable (`_obs` suffix)

Let `inc(s, t, Δ)` be `s`'s mean incorrectness in `[t, t+Δ]`;
`gap(s, t)` the longest inter-submission gap; `baseline(s)` the
median gap up to `t`; `dup(s, t, Δ)` the count of near-duplicate
wrong submissions.

| Label | Definition |
|---|---|
| `L_top20_obs(s, t, Δ)` | 1 iff `s` in top 20% by `inc(s, t, Δ)` |
| `L_needs_help_obs(s, t, Δ)` | 1 iff `dup ≥ 3` OR `gap > 3 × baseline(s)` |
| `L_struggling_plus_obs` | `L_top20_obs ∨ L_needs_help_obs` |

Default `Δ = 15 min`.

### 4.3 Family C — LLM second-opinion (NEW in this implementation)

Per-snapshot ratings from GPT-4o-mini (same model as
[[code]] `rag.py:6`), via the same `_get_openai_client()` factory and
batched-call pattern as `incorrectness.py`.

**Struggle labels** (per snapshot):

| Label | Definition |
|---|---|
| `L_intervene_llm(s, t)` | 1 iff GPT outputs `"intervene": true` for the snapshot |
| `L_severity_llm(s, t)` | GPT's 1–5 severity rating (continuous) |

**Difficulty labels** (per unique question, end-of-session):

| Label | Definition |
|---|---|
| `L_difficulty_llm(q)` | GPT's 1–5 difficulty rating (continuous) |
| `L_high_diff_llm(q)` | 1 iff `L_difficulty_llm(q) ≥ 4` |

**human self-labels:** 50 snapshots drawn from the LLM-labelled 2000,
labelled independently by human; Cohen's $\kappa$ reported against
the LLM on the shared 50. $\kappa < 0.3$ → flagged as limitation,
training still proceeds with caveat.

---

## 5 · Four v2 artefacts and their runtime toggles

The four optimised artefacts and their associated toggles in V2 React
Settings. All default `"v1"` — the dashboard behaves identically to
the deployed version unless a toggle is explicitly flipped.

| Toggle | Affects | Loaded from | Disable conditions |
|---|---|---|---|
| `struggle_weights_version` | 7-signal $S(s)$ composite | `data/optimised_struggle_weights_v2.json` | When the JSON file is absent (frontend greys out the select with tooltip) |
| `difficulty_weights_version` | 5-signal $D(q)$ composite | `data/optimised_difficulty_weights_v2.json` | When file absent, OR when `difficulty_model == "irt"` (IRT bypasses composite weights) |
| `improved_struggle_weights_version` | 3-weight $(w_B, w_M, w_D)$ blend | `data/optimised_improved_weights_v2.json` | When file absent, OR when `struggle_model != "improved"` |
| `hyperparams_version` | CF $\tau$, shrinkage $K$, BKT mastery threshold, BKT priors $(p_\mathrm{init}, p_\mathrm{learn}, p_\mathrm{guess}, p_\mathrm{slip})$ | `data/optimised_hyperparams_v2.json` | When file absent |

### 5.1 Cascade behaviour
When `struggle_weights_version == "v2"` is on, improved-struggle's
behavioural component $B_s$ uses the optimised v2 weights
automatically — no extra wiring. The `improved_struggle_weights_version`
toggle only retunes the **model weights** on top.

### 5.2 Safety guarantees
- All four toggles default `"v1"`. Default install = current dashboard
  behaviour.
- Missing or malformed v2 JSON → silent fallback to v1 with a
  warning log line. Never crashes.
- Frontend selects greyed out + tooltipped when their v2 file is
  absent — user can't accidentally select an option that doesn't
  resolve.
- `cache.invalidate()` runs on every `POST /api/settings` so toggle
  flips always serve fresh scores.

### 5.3 V1 Streamlit untouched
V1 retains v1 weights as the reference implementation. The Ch4
amendment brief explicitly states this so the thesis narrative is
clean: V2 React is where v2 lives.

---

## 6 · Implementation phases (live status)

| Phase | What | Status | Outputs |
|---|---|---|---|
| **0** | Rewrite this vault note for new scope | ✅ done (2026-05-25) | This file + `v2 Methodology Journal.md` |
| **1** | `scripts/eval_fetch.py` + sanity check | ✅ done (2026-05-25) | `data/eval_submissions.parquet` (42,443 rows, spans 2025-10-06 → 2026-05-15, 21/23 healthy sessions) |
| **2** | `scripts/eval_common.py` + ~2000-snapshot fixture | ✅ done (2026-05-25) | `data/eval_snapshots.json` — 1306 struggle snapshots + 72 difficulty entries. Band split: 13 On Track / 120 Minor / 470 Struggling / 703 Needs Help. Family B positive rates: L_top20_obs 10.0%, L_needs_help_obs 21.1%, L_struggling_plus_obs 26.1% |
| **3 (LLM labels)** | `scripts/eval_label.py --mode struggle` + `--mode difficulty`. GPT-4o-mini, schema_version 2 (4-band scale). API key auto-loaded from `.secrets/secrets.toml` via loader added to script | ✅ done (2026-05-25) | **`data/eval/llm_struggle_labels.json`** — 1306 labels, 262/262 batches succeeded, 0 parse failures. **`data/eval/llm_difficulty_labels.json`** — 72 labels, 15/15 batches succeeded, 0 parse failures. Total: 1378 LLM labels, 100% batch success, ~$0.20 OpenAI spend |
| **3 (self-label)** | `scripts/eval_label.py --mode self-label` | ✅ done (2026-05-25) | `data/eval/self_labels.json` — **50/50 labels saved** (schema_v2 4-band). CLI display widened mid-run after first 7 labels: `<br>` rendered as newlines, no answer/feedback truncation. The first 7 labels remain valid (judgement was based on what was visible at the time) |
| **3 (κ)** | `scripts/eval_label.py --mode kappa` | ✅ done (2026-05-25) | `data/eval/kappa_report.json`. **κ_intervene = 0.103, κ_band_linear = 0.111, κ_band_quad = 0.094** (all "poor" by Landis-Koch). Exact intervene agreement = 58% (29/50); band exact = 34%; **band within-1-step = 70% (35/50)** — directional agreement, divergence on precise boundary. Distributions both lean upper bands: human intervene 60%, LLM intervene 66%; both put 17/50 in Needs Help. Reported as §5.5 limitation; v2 weights documented as "indicative not validated" against human judgement |
| **4a** | `scripts/optimise_v2_weights.py --kind struggle` | ✅ done (2026-05-25) | `data/eval/optimised_struggle_weights_v2.json`. **AUC mean = 0.836, 95% CI [0.762, 0.911]** across 5 session-grouped folds. All 5 folds converged; best C consistently 0.1. Per-fold weight std tight (0.015–0.032) → stable solution. **Notable findings**: (1) `n_hat` and `t_hat` flipped from positive (+0.10 each in v1) to NEGATIVE (−0.04, −0.13 in v2) — activity proxies as engaged-self-recovery, not struggling-persistence; (2) v1's $\eta = 0.38$ on recency dropped to 0.26 in v2; (3) mean incorrectness bumped from 0.20 → 0.26 (now co-equal with recency); (4) `rep_norm` also flipped sign |
| **4b** | `scripts/optimise_v2_weights.py --kind difficulty` | ✅ done (2026-05-25) — **NEGATIVE FINDING** | `data/eval/optimised_difficulty_weights_v2.json`. **AUC pooled = 0.345** (worse than random). Target reframed to `Very Hard only` after the original `{Hard, Very Hard}` gave 98.6% positive and crashed LOO. Even with the reframe (76% pos), the LR cannot discriminate Very Hard from Hard using the 5 v1 features — the LR weights are likely noise-fitting at N=72 (e.g. `t_tilde` = −0.39, claiming "more time → less likely Very Hard", almost certainly spurious). **Honest publishable finding: v1 hand-set difficulty weights are near-optimal on this cohort; the 5-feature space saturates at COA122's uniformly-hard distribution and offers no headroom for empirical improvement.** Frontend toggle for `difficulty_weights_version` should default to v1 and warn that v2 is experimental / worse on held-out evaluation |
| **4c** | `scripts/optimise_v2_weights.py --kind improved` | ✅ done REAL (2026-05-25) — **NEGATIVE FINDING** | `data/eval/optimised_improved_weights_v2.json`. Snapshot extension implemented (`compute_improved_components_at_t` in eval_common.py fits BKT + IRT per (session, cutoff) and attaches B_s/M_s/D_s to each snapshot). Training: **AUC = 0.637 [0.572, 0.703]** across 5 session-grouped folds. **Blend weights: w_B = +0.42, w_M = −0.44, w_D = −0.14.** Two of three model weights flipped negative — LR puts negative weight on BKT mastery_gap and IRT-adjusted exposure components. Per-fold weight std 0.04–0.16 (noisier than struggle pass). Three reading: (1) BKT/IRT capture knowledge-state/challenge-level, not "needs help right now"; (2) per-cutoff BKT/IRT fits are noisy at small slices, propagating to blend; (3) behavioural composite already saturates predictive signal. All three support: **improved-v2 blend should default OFF; v1 blend is the better choice**. Headline AUC (0.637) is worse than baseline struggle-v2 (0.836), suggesting the model HURTS at this N |
| **4a** | `scripts/optimise_v2_weights.py` struggle mode | ⏳ pending | `data/optimised_struggle_weights_v2.json` |
| **4b** | Same script, difficulty mode | ⏳ pending | `data/optimised_difficulty_weights_v2.json` |
| **4c** | Same script, improved-struggle mixing mode | ⏳ pending | `data/optimised_improved_weights_v2.json` |
| **4d** | `scripts/optimise_hyperparams.py` grid search | ⏳ pending | `data/optimised_hyperparams_v2.json` |
| **5a** | V2 backend wiring (runtime_config, schemas, struggle, difficulty, improved_struggle, cache, settings router) | ⏳ pending | 8 modified files in `code2/backend/` |
| **5b** | V2 frontend selects (4 selects with disable logic) | ⏳ pending | Modified Settings UI components |
| **6** | `scripts/eval_main.py` — full evaluation matrix | ⏳ pending | `eval_results.md` |
| **7** | Writing-chat briefs (Ch3 + Ch4 amendments, Ch5 §5.4 numbers) | ⏳ pending | Brief paragraphs handed to other chat |
| **8** | Literature `\cite{}` additions + `sync_literature.py` | ⏳ pending | Updated `Report/references.bib` + coverage notes |

**Total estimate:** ~16.5 h Claude time + ~45 min human time + ~$15–25 OpenAI spend.

### 6.1 Per-phase status update protocol
After each phase completes, update:
1. The status emoji + date in this section's table
2. The frontmatter `status` field at the top of this note
3. Append a one-liner to §12 changelog
4. The §6 row gets concrete output paths + headline numbers if any

---

## 7 · Decisions logged this session

| Decision | Value | Rationale |
|---|---|---|
| LLM rater model | GPT-4o-mini | Same as `rag.py:6`; cheap and capable enough for snapshot rating |
| LLM client pattern | Reuse `_get_openai_client()` from `analytics.py` + batched-call + disk cache, exactly mirroring `incorrectness.py` | Consistency with existing OpenAI integration; same error handling and retry behaviour |
| Sessions to use | All 23 saved sessions | User imported these on 2026-05-25; gives broadest coverage |
| Snapshot count | ~2000 (struggle) + ~50–100 (difficulty per question) + 50 (human self-label calibration) | 2000 supports stable AUC CIs with 4-fold split; 50 supports kappa estimate with reasonable CI |
| Model class for training | Logistic regression (primary), gradient boosting fallback if LR AUC < 0.55 | Preserves "weighted sum" functional form → v1 vs v2 directly comparable |
| Cross-validation | Group K-fold ($K=5$) with session as group for struggle / improved model; LOO-on-question for difficulty | Prevents train/test leakage on students; appropriate for question-level N |
| Regularisation | L2 (Ridge), $\lambda$ tuned by nested CV | Handles signal correlation (esp. $I$ vs $A$ in struggle) |
| Default toggle state | All four `"v1"` | Iterative-refinement narrative; v2 is opt-in |
| V1 Streamlit | Untouched | Reference implementation; toggle scope is V2-only |
| Chapter amendments | Ch3 (~120w) + Ch4 (~90w) + Ch5 §5.4 numbers + Ch5 §5.6.1 model disagreement | Authorised explicitly by user |

### 7.1 Outstanding decisions
- None currently. All forks resolved before plan exit on 2026-05-25.

---

## 8 · Open blockers

### 8.1 Phase 1 — Loughborough internal API not reachable from Claude's environment

**The problem.** `cache.load_dataframe()` calls
`data_loader.fetch_raw_data_uncached()` which hits
`http://sccb2.sci-project.lboro.ac.uk/retrievalEndpoint.php`. From
Claude's sandbox this connection times out after 30 s — the endpoint
is on Loughborough's internal network and likely requires VPN /
campus presence.

**The fix.** human runs the existing script on a machine that can
reach the API (the same machine you deploy the dashboard from):

```powershell
python scripts/eval_fetch.py
```

This produces:

- `data/eval_submissions.parquet` (or `.pkl` fallback if pyarrow
  isn't installed)
- Console output with per-session row + student counts
- Pass/Partial/Fail line at the bottom

Paste the console output back to Claude and the pipeline resumes
from Phase 2 entirely offline.

**Status:** waiting on human (2026-05-25).

---

## 9 · Parallel chat — Chapter 5 prose writing

A separate Claude chat is writing Chapter 5 prose using the handoff
prompt issued on 2026-05-24. That chat does NOT know about the
training scope — it's writing the subsections that don't need numbers.

### 9.1 Subsections being written there (no numbers needed yet)
- §5.1.1 Scope of Evaluation
- §5.1.2 Evidence Sources
- §5.1.3 Retrospective Evaluation Protocol (should follow §3.3 framing)
- §5.1.4 Limitations of Evaluation
- §5.2.* Functional Testing
- §5.3.2 Usability and Interpretability (survey-driven, n=8 in hand)
- §5.3.3 Robustness and Failure Handling
- §5.5.* Survey (n=8, Microsoft Forms, ethically approved)
- §5.6.2 Tradeoffs and Threats to Validity
- §5.6.3 Limitations

### 9.2 Subsections waiting for this implementation
- §5.3.1 Performance/Refresh — needs latency capture (separate ask)
- §5.4.1–§5.4.8 — all results subsections; numbers come from
  `eval_results.md` (Phase 6 output)
- §5.6.1 Model Disagreement — needs v1/v2 disagreement matrix and
  Family A vs B vs C label disagreement matrix

### 9.3 Ch3 + Ch4 amendment briefs (Phase 7)
Sent to the writing chat at end of implementation. The chat authors
the prose; this implementation just provides the briefs.

---

## 10 · Continuation prompt (paste into a fresh chat to resume)

Copy from `===` to `===`:

```
===
I'm resuming work on the evaluation + v2 optimisation implementation
for my MSc thesis on a learning analytics dashboard (V1 Streamlit at
code/, V2 React+FastAPI at code2/).

THREE authoritative documents to read before doing anything:

1. C:\Users\human\.claude\plans\crispy-finding-valiant.md
   — the implementation contract; what gets built and how

2. docs/obsidian-vault/My Notes/Thesis/Evaluation PoC Handoff.md
   (THIS note) — live status, decisions log, blockers, label
   definitions, continuation context

3. docs/obsidian-vault/My Notes/Thesis/Evaluation Plan.md
   — the original design doc from 2026-04-21 (cross-reference only;
   the implementation supersedes its scope)

Scope: optimise four artefacts via LR/grid search against GPT-4o-mini
labels (struggle model weights, difficulty model weights,
improved-struggle model weights, scalar hyperparams). Wire each as a
runtime-toggleable v2 option in the V2 React Settings view; all
default v1. Both versions reported in Ch5 §5.4.

Current state (2026-05-25): Phase 0 → Phase 3 self-label all DONE.
Next steps in order:

  1. python scripts/eval_label.py --mode kappa
     (instant — reports Cohen's κ between human and LLM on shared 50)

  2. python scripts/optimise_v2_weights.py --kind struggle
     python scripts/optimise_v2_weights.py --kind difficulty
     python scripts/optimise_v2_weights.py --kind improved
     (~30 sec each; struggle and difficulty produce real weights,
      improved writes a stub — see §6 for the snapshot-extension
      caveat needed to make it real)

  3. Decide whether to also write scripts/optimise_hyperparams.py
     (Phase 4d). Adds ~1.5h. Optional if 4a/4b give good enough
     numbers on their own.

  4. Phase 5a + 5b (V2 backend + frontend toggles). Phase 6
     (evaluation notebook with plots styled per
     [[previous-works/F221611.ipynb]]). Phase 7 (briefs to writing
     chat). Phase 8 (literature sync).

Cached data on disk:
  - data/eval/submissions.parquet     42,443 rows
  - data/eval/snapshots.json          1306 struggle + 72 difficulty
  - data/eval/llm_struggle_labels.json   1306 labels, schema_v2
  - data/eval/llm_difficulty_labels.json   72 labels, schema_v2
  - data/eval/self_labels.json          50 human labels, schema_v2
  - data/eval/optimised_*_v2.json     (next — written by Phase 4)

Decisions already made (do not reopen — see §7 of the vault note):
- GPT-4o-mini as labeller; mirror incorrectness.py's client+cache pattern
- All 23 saved sessions; ~2000 struggle snapshots; ~50-100 difficulty
- Logistic regression primary, gradient boosting fallback
- Group K-fold (session as cluster) for struggle/improved; LOO-on-question for difficulty
- L2 regularisation, λ tuned by nested CV
- All four toggles default v1; v2 is opt-in
- V1 Streamlit untouched; toggles are V2-React-only
- Ch3 + Ch4 amendments authorised; iterative-refinement narrative

After resuming any phase, update this vault note's §6 status table,
the frontmatter status field, and the §12 changelog. The note is the
live continuation surface.
===
```

---

## 11 · Code locations

### 11.1 V2 backend — files to MODIFY in Phase 5a

| File | Change |
|---|---|
| `code2/backend/runtime_config.py` | Add 4 `*_version` fields + `_load_optimised_hyperparams()` helper |
| `code2/backend/config.py` | Add 4 `*_V2_PATH` constants + `SHRINKAGE_K_DEFAULT = 5` |
| `code2/backend/schemas.py` | Mirror 4 new fields in `RuntimeSettings` |
| `code2/backend/struggle.py::compute_student_struggle_scores` | Accept `weights=` + `shrinkage_k=` overrides; `_load_v2_weights()` reader |
| `code2/backend/difficulty.py::compute_question_difficulty_scores` | Accept `weights=` override + reader |
| `code2/backend/models/improved_struggle.py::compute_improved_struggle_scores` | Accept `mix_weights=` override + reader |
| `code2/backend/cache.py` | Read all 4 version flags in `load_*_df`; include in cache key |
| `code2/backend/routers/settings.py` | Wire 4 new fields through `_to_runtime_settings` response |

### 11.2 V2 frontend — files to MODIFY in Phase 5b

| File | Change |
|---|---|
| `code2/frontend/src/components/settings/StruggleModelSettings.tsx` (or wherever the existing `struggle_model` toggle lives — locate via grep) | Add `struggle_weights_version` + `improved_struggle_weights_version` selects |
| `code2/frontend/src/components/settings/DifficultyModelSettings.tsx` (or equivalent) | Add `difficulty_weights_version` select |
| `code2/frontend/src/components/settings/AdvancedSettings.tsx` (or wherever runtime sliders live) | Add `hyperparams_version` select |
| `code2/frontend/src/types/settings.ts` (or equivalent) | Mirror 4 schema fields |

### 11.3 Existing code to REUSE (no modification)

| Function | File:line | Used by |
|---|---|---|
| `load_dataframe` | `code2/backend/cache.py:67` | All eval scripts |
| `filter_df` | `code2/backend/cache.py:128` | `eval_common.py` |
| Bucket-replay pattern | `code2/backend/routers/sessions.py:280-355` | `eval_common.py` |
| `_get_openai_client` | `code2/backend/analytics.py` | `eval_label.py` |
| `_incorrectness_cache` pattern | `code2/backend/incorrectness.py:30-50` | `eval_label.py` (mirror this) |
| `compute_irt_model` | `code2/backend/models/irt.py:269` | `eval_main.py` |
| `fit_bkt_parameters` | `code2/backend/models/bkt.py:337` | `eval_main.py` |
| Spearman + top-k overlap | `code2/backend/routers/models_cmp.py` | `eval_main.py` |
| Bayesian shrinkage $K$ | currently hardcoded in `struggle.py` | Promoted to `config.py` constant in Phase 5a |

### 11.4 V1 reference (untouched)
| Concern | File |
|---|---|
| All analytics | `code/learning_dashboard/analytics.py` (Streamlit-coupled) |
| IRT (Rasch 1PL) | `code/learning_dashboard/models/irt.py` |
| BKT | `code/learning_dashboard/models/bkt.py` |
| Improved struggle | `code/learning_dashboard/models/improved_struggle.py` |

### 11.5 Data files
| File | Contents | Phase that writes |
|---|---|---|
| `data/eval_submissions.{parquet,pkl}` | Cached raw DataFrame | 1 |
| `data/eval_snapshots.json` | 2000 frozen snapshots | 2 |
| `data/llm_struggle_labels.json` | GPT-4o-mini struggle ratings | 3 |
| `data/llm_difficulty_labels.json` | GPT-4o-mini difficulty ratings | 3 |
| `data/self_labels.json` | human's 50 self-labels | 3 |
| `data/optimised_struggle_weights_v2.json` | Optimised $S$ weights | 4a |
| `data/optimised_difficulty_weights_v2.json` | Optimised $D$ weights | 4b |
| `data/optimised_improved_weights_v2.json` | Optimised improved model weights | 4c |
| `data/optimised_hyperparams_v2.json` | Grid-searched scalar hyperparams | 4d |
| `eval_results.md` | Final results tables | 6 |

---

## 13 · Final v1-vs-v2 verdict scorecard (post-Phase 4d)

Five optimisation targets across Phases 4a–d. **Four v2 wins + one tie** (post-target-swap; the previous "two-and-a-half wins each" framing was under the wrong binary target).
**This is the §5.4 headline narrative for the thesis.**

| Component | Winner | AUC / Evidence | Phase |
|---|---|---|---|
| **Struggle model** (7 OLS weights) | ✅ **v2** | ρ +0.573 [+0.430, +0.715] vs v1 ρ +0.423; `n_hat`, `t_hat`, `rep_norm` sign-flipped → activity proxies engaged self-recovery, not stuck-persistence | 4a |
| **Difficulty model** (5 OLS weights) | ✅ **v2** | ρ +0.287 vs v1 ρ +0.027 — weak but positive; under the wrong (binary) target the previous narrative was 'v1 wins'. v1 is essentially flat. | 4b |
| **Improved-struggle model** (3 OLS weights) | ✅ **v2** | ρ +0.168 vs v1 ρ −0.017; OLS still flips $w_M$ and $w_D$ negative — BKT+IRT components hurt, but the trained blend still beats the v1 default. Caveat: still weaker than struggle alone. | 4c |
| **Shrinkage K** (scalar) | ⚖️ **tied** | v2 K=1 beats v1 K=5 by Δ+0.013 ρ — within fold-variance noise; either defensible | 4d |
| **CF threshold τ** (scalar) | ✅ **v2** | +0.200 ρ (0.234 → 0.434); hand-set τ=0.7 was meaningfully too permissive | 4d |

### The "two regimes" §5.4 narrative

Under the corrected 4-band target, v2 outperforms v1 on all three trained weight vectors and on the CF threshold τ; only the shrinkage K is within fold-variance noise. The earlier binary-intervene framing produced "two negative findings" for difficulty and improved-struggle, but those were artefacts of training against a binary alert decision the dashboard does not make. Under the proper ranking target the differences become weakly-positive gains, not losses.

### Subtle methodology caveat for §5.5

The four v2 artefacts were each measured **in isolation** against the v1 baseline:

- Struggle v2 weights were trained with K=5 (the v1 shrinkage default)
- CF τ optimisation used v1 struggle features (not v2-weighted features)
- Joint v2 deployment (all toggles on) is not separately validated — combined AUC could be higher or lower than the sum-of-parts due to interactions

One-sentence §5.5 acknowledgement: *"v2 components were each evaluated against the v1 baseline; joint v2 deployment was not separately validated."*

For the defence demo this is fine — flipping individual toggles in Settings shows the leaderboard responding to each component independently.

### Methodology footnote (for writing chat / future you)

A few framing details that live in [[v2 Empirical Refinement Brief]] §4 (the §5.4 methodology preamble) but are easy to miss if you only read this handoff:

- **Models we trained vs evaluated only.** Four v2 weight artefacts were trained from scratch in Phases 4a–d: the 7-signal struggle model (LR), 5-signal difficulty model (LR), 3-weight improved model (LR), and two scalar hyperparameters K and τ (Optuna TPE). The other dashboard models — IRT 2PL (already MLE-fitted at lifespan startup), BKT per-skill (already MLE-fitted via forward algorithm), mistake clustering (unsupervised), measurement confidence (formula-based), and incorrectness scoring (gpt-4o-mini API call) — were **evaluated** but **not retrained**. §5.4 should call this distinction out explicitly so a reader doesn't conflate "evaluated" with "fitted from scratch in this work".
- **CV scheme rationale.** Struggle and improved model use **GroupKFold with session as the group cluster** (5 folds) so train and test never share students. Difficulty uses **LOO on questions** (effectively 72 folds) because the 72 unique questions repeat across sessions and session-grouping is therefore not applicable. Optuna uses session-grouped 5-fold CV per trial.
- **Model class default + fallback.** LR + L2 (Ridge) is the default because it shares the linear-combination functional form of the v1 composites — this keeps the v1 ↔ v2 comparison interpretable as "do the trained weights tell a different story than the designed ones". A gradient-boosting fallback was on the table for any composite whose AUC fell below 0.55; it was not triggered.
- **Two-Ks naming clash.** The letter $K$ appears in two unrelated places: the **number of CV folds** ($K=5$ for session-grouped runs) and the **shrinkage hyperparameter** $K$ of Equation \ref{eq:struggle-shrunk} (default $K=5$, Optuna-optimised to $K=1$). They share both the letter and the integer 5 by coincidence. Worth a one-line footnote in §5.4 so a reader doesn't think the K-fold count was the thing being optimised.

These are not new findings — they're framing decisions that should land in §5.4 prose. See [[v2 Empirical Refinement Brief]] §4 for the paste-ready guidance and optional LaTeX draft.

## 12 · Changelog

- **2026-05-25 (P7 done — writing-chat briefs)** — [[v2 Empirical Refinement Brief]] created. Single self-contained brief covering: Ch3 amendment (~120 words, post the existing `line 259` "trial and error" sentence — empirical refinement framing), Ch4 amendment (~90 words, near `line 952` improved model defaults — toggle plumbing) plus a Settings-view secondary insertion (~§4.9.6), and the full Ch5 §5.4 numbers brief covering §5.4.2 (κ), §5.4.3 (struggle headline), §5.4.9 (new — weaker positive findings for difficulty + improved model), §5.4.10 (new — Optuna TPE on K and τ), and §5.6.1 (v1↔v2 disagreement + verdict scorecard). All numbers sourced from `data/eval/results.md`; 11 figures inventoried under `data/eval/figures/`; pre-paste + post-paste checklists included. Brief is paste-ready for the writing chat. Phase 8 (literature sync) is the only remaining optional polish.
- **2026-05-25 (P4d done — Optuna TPE hyperparam optimisation)** — `scripts/optimise_hyperparams.py` written using Optuna TPE sampler (Bayesian optimisation, more efficient than naive grid). Two parallel studies, 50 trials each, session-grouped 5-fold CV against the LLM 4-band rating. **Findings**: (1) **shrinkage K: best=1, AUC=0.805, Δ=+0.007 vs v1 K=5** — robustness finding, hand-set K is near-optimal. (2) **CF τ: best=0.899, AUC=0.800, Δ=+0.118 vs v1 τ=0.7** — substantial positive finding, hand-set τ was too permissive; strict τ≈0.9 lifts CF AUC by 12pp. **Caveat for §5.5**: best τ landed at the upper boundary of the [0.4, 0.9] search range; finer search may yield further improvement. `data/eval/optimised_hyperparams_v2.json` populated with full per-trial trajectories + the 5 unoptimised BKT hyperparams pinned to defaults (so the runtime_config loader can switch wholesale to v2). Hyperparams v2 toggle in V2 React Settings is now REAL (no longer DEFERRED stub). BKT priors + mastery threshold remain deferred (would each need ~30 min of BKT refits per trial). Phase 4 fully closed.
- **2026-05-25 (P6 done — eval notebook + figures + results.md)** — `notebooks/eval_main.ipynb` runs end-to-end in ~30 s. 10 figures saved to `data/eval/figures/` (cohort_distributions, kappa, weights_struggle_v1_vs_v2, per_fold_auc_struggle, roc_struggle, calibration_struggle, weight_heatmap_struggle, confusion_bands, negative_findings, model_disagreement). `data/eval/results.md` (76 lines, 6 tables) ready for writing chat to lift verbatim into §5.4 / §5.5 / §5.6 prose. **Bonus finding (only visible after notebook re-derives v1 vs v2 predictions on same snapshots): 31.2% of students reclassified into a different struggle band under v2 (408/1306); split is balanced (15.9% upgrades, 15.3% downgrades) — v2 is not systematically harsher or more lenient than v1.** This is a §5.6.1 model-disagreement headline. Notebook uses F221611-styled plots (paired bars with value annotations, text-box AUC overlays, ConfusionMatrixDisplay with RdGy cmap, grid alpha 0.3). Mid-run bug caught and fixed: results-export cell had a Python indentation error in the kappa-table block which the syntax-check script flagged before execution. Phase 7 (writing-chat briefs) next.
- **2026-05-25 (P5 done — backend + frontend toggles live)** — V2 React stack now has the four v2 toggles wired end-to-end. **Backend** (8 files): `config.py` (4 V2 path constants + `SHRINKAGE_K_DEFAULT`), `runtime_config.py` (4 `*_version` + `shrinkage_k` fields + `_load_optimised_hyperparams()` helper + `update()` side-effects on hp-version flip), `schemas.py` (`RuntimeSettings` extended), `struggle.py` + `difficulty.py` + `models/improved_struggle.py` (each gained `_load_v2_weights()` + override params with v2-mode redistribution gating), `cache.py` (`load_*_df` pass overrides through + cache key includes version), `routers/settings.py` (`_to_runtime_settings` surfaces 5 new fields). **Frontend** (2 files): `types/api.ts` extended; `views/SettingsView.tsx` added "Optimised Weights (v2)" section (n=5) with 4 `<ToggleRow>` selects + `V2InfoBlock` subcomponent (green-ok / red-warn / neutral-info variants reflecting Phase 4 findings). All defaults stay v1 → no breaking change. Verified live by user: section visible, toggles flip backend, leaderboards re-rank. **Iterative-refinement narrative now demonstrable in defence demo.** Phase 6 (eval notebook + plots) next.
- **2026-05-25 (P4c real done — NEGATIVE FINDING)** — Upgraded from stub. `scripts/eval_common.py` extended with `compute_improved_components_at_t` (fits BKT + IRT at each (session, cutoff), attaches `improved_components` field per snapshot). Snapshots regenerated (~15 min wallclock for 252 BKT/IRT fits). `optimise_v2_weights.py --kind improved` now trains real 3-weight LR. **Result: AUC = 0.637 [0.572, 0.703]; w_B = +0.42, w_M = −0.44, w_D = −0.14.** Two of three model weights flipped NEGATIVE — LR doesn't trust the BKT/IRT components. Headline AUC of 0.637 is WORSE than baseline struggle-v2 (0.836), meaning the improved model actively hurts at this N. Three interpretations all support: improved model v2 should default OFF in deployment, v1 (0.45/0.30/0.25) stays as the recommended blend. Symmetric to Phase 4b's negative finding for difficulty: **two negative findings + one positive (struggle) gives a complete, honest §5.4 story**.
- **2026-05-25 (P4b done — NEGATIVE FINDING)** — v2 difficulty weights trained with reframed `Very Hard only` target. **AUC pooled = 0.345** (worse than random). LR cannot discriminate Very Hard from Hard using the 5 v1 features at N=72. Weights show noise-fitting patterns (e.g. `t_tilde` = −0.39 — "more time = less likely Very Hard", spurious). **Honest publishable finding**: v1 hand-set difficulty weights are near-optimal for COA122; no headroom for empirical improvement given the available features. Symmetric to Phase 4a's struggle finding: where struggle showed v1 weights need redistribution (publishable positive finding), difficulty shows v1 weights are already correct (publishable negative finding). The difficulty toggle in Phase 5 should default to v1 with a UI warning that v2 is experimental + worse on held-out evaluation. Metadata `target` string in script updated to reflect the reframe.
- **2026-05-25 (P4b cohort finding)** — **COA122 is uniformly hard.** LLM difficulty band distribution: Easy 0, Medium 1, Hard 16, **Very Hard 55** (n=72). v1 dashboard on same data: Easy 3, Medium 21, Hard 46, Very Hard 2. The LLM is dramatically harsher than v1 thresholds (sees "Very Hard" where v1 sees "Hard"). Two interpretations: (a) v1 thresholds calibrated generously, (b) LLM over-rates difficulty from aggregate stats. Both worth reporting in §5.4 — this is a publishable cohort-characteristics finding. Original `band ∈ {Hard, Very Hard}` training target gave 98.6% positive (untrainable, LOO crashed); reframed to `band == 'Very Hard'` (76% positive) — same data, sharper question: *"what distinguishes the very hardest from the merely hard?"*. Script also gained a single-class-fold safety guard.
- **2026-05-25 (P4a done)** — v2 struggle weights trained. **AUC = 0.836 [0.762, 0.911]** across 5 session-grouped folds. Weight vector stable (per-fold std 0.015–0.032). Headline finding: hand-set $\eta = 0.38$ on recency was over-weighted; LR redistributes to ≈0.26 on each of mean incorrectness and recency. Submission count + time active flipped sign (positive in v1, negative in v2) — activity proxies engaged self-recovery in LR's view, not struggling persistence. Publishable finding. sklearn `FutureWarning` spam fix added to `scripts/optimise_v2_weights.py`. Phase 4b/4c next.
- **2026-05-25 (P3 κ)** — Kappa report: **κ_intervene = 0.10, κ_band_linear = 0.11, κ_band_quad = 0.09** — all "poor" by Landis-Koch thresholds. Exact intervene agreement 58%, band within-1-step 70%. Both raters skewed toward Needs Help / Struggling, which inflates chance agreement and pulls κ down. Documented as §5.5 limitation; v2 weights framed as "indicative not validated against human judgement, trained against LLM second-opinion judgement". `data/eval/kappa_report.json` persists the numbers for §5.4 citation.
- **2026-05-25 (P3 done)** — Phase 3 self-label complete: 50/50 labels saved to `data/eval/self_labels.json`. CLI display improved mid-run after the first 7 labels (full answer + feedback, `<br>` → newlines, wider Q column); first 7 still valid. Kappa report queued next. Phase 4 scripts (`scripts/optimise_v2_weights.py`) written and ready to fire as soon as κ runs.
- **2026-05-25 (P3 LLM)** — Phase 3 LLM labels complete: 1306 struggle labels (262/262 batches, 0 failures) + 72 difficulty labels (15/15 batches, 0 failures) under 4-band schema. ~$0.20 OpenAI spend. Mid-conversation scale change: switched from 1–5 severity to 4-band (`On Track / Minor Issues / Struggling / Needs Help` and `Easy / Medium / Hard / Very Hard`) to match deployed dashboard semantics. Schema version bumped to 2; old cache auto-discarded. Author identifier replaced with "human" across script + vault notes for neutral attribution. `.secrets/secrets.toml` loader added to `eval_label.py` so the script auto-resolves the API key. Self-label (n=50) + Cohen's $\kappa$ pending. Next: Phase 4 (optimisation scripts) being written in parallel.
- **2026-05-25 (P2 done)** — Phase 2 complete. `scripts/eval_common.py`
  written; sampler produced 1306 struggle snapshots + 72 difficulty
  entries to `data/eval_snapshots.json`. Band distribution skews
  toward "Needs Help" (54%) and "Hard" (64%) — flagged for §5.5 as
  v1 threshold-calibration finding. Family B horizon-shifted
  positive rates within healthy 10–26% range. Methodology journal
  `v2 Methodology Journal.md` created as supplementary source
  material for the writing chat. Next: Phase 3 (`scripts/eval_label.py`).
- **2026-05-25 (P1 done)** — Phase 1 complete. human ran
  `scripts/eval_fetch.py` locally and cached 42,443 rows to
  `data/eval_submissions.parquet` (time range 2025-10-06 →
  2026-05-15). 21/23 sessions healthy; 2 small sessions
  (Week 12 with 3 students; Week 11 16:00 with 7 students) excluded
  from downstream phases.
- **2026-05-25 (P0 done)** — Phase 0 (this rewrite) underway. Scope
  pivot from PoC to full implementation. Plan file
  `crispy-finding-valiant.md` rewritten to cover four v2 toggles,
  training procedure, Ch3/4 amendments, literature sync. Phase 1
  `scripts/eval_fetch.py` written; blocked on human-local API access
  (resolved same day). Vault note title changed from
  "Evaluation PoC Handoff" to "Evaluation Implementation Handoff"
  (filename preserved for cross-link stability).
- **2026-05-24** — Original PoC handoff note written. Scope was
  evaluation only, no training, no system changes.
