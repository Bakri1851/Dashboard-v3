---
tags: [thesis, evaluation, ch5, implementation, handoff, live]
date: 2026-05-25
status: 🟢 Phase 2 complete (1306 snapshots + 72 difficulty entries) · Phase 3 next
source: Conversation 2026-05-24 + 2026-05-25 (Bakri + Claude)
related: [[Evaluation Plan]], [[Ch5 – Results and Evaluation]], [[Evidence Bank]], [[Report Sync]], [[Improved Struggle Logic]], [[BKT Mastery Logic]], [[IRT Difficulty Logic]], [[Student Struggle Logic]], [[Setup and Runbook]], [[Full Roadmap]]
---

# Evaluation Implementation Handoff — Live Continuation Surface

> **Purpose.** Capture the entire live state of the v2 weights and
> hyperparams implementation. Self-contained — a fresh Claude chat
> (or future Bakri) can pick up the work without re-deriving anything
> from prior conversation.

> **Scope.** Real production implementation (was originally scoped as
> a PoC; user revised on 2026-05-25 to "do it for real"). Four optimised
> v2 artefacts trained against GPT-4o-mini second-opinion labels, wired
> into the V2 React stack as runtime-toggleable Settings.

> **Status as of 2026-05-25.** Phase 0 (this note) being rewritten now.
> Phase 1 (`scripts/eval_fetch.py`) script written but my environment
> can't reach the Loughborough internal API — needs Bakri to run
> locally and paste the sanity output.

> **Authoritative plan** lives at `C:\Users\Bakri\.claude\plans\
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
  Bakri's 50 self-labels via Cohen's $\kappa$.

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

**Bakri self-labels:** 50 snapshots drawn from the LLM-labelled 2000,
labelled independently by Bakri; Cohen's $\kappa$ reported against
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
toggle only retunes the **blend weights** on top.

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
| **3** | `scripts/eval_label.py` (GPT-4o-mini, mirrors `incorrectness.py` pattern) + Bakri self-labels 50 + Cohen's $\kappa$ | 🟡 NEXT | `data/llm_struggle_labels.json`, `data/llm_difficulty_labels.json`, `data/self_labels.json` |
| **4a** | `scripts/optimise_v2_weights.py` struggle mode | ⏳ pending | `data/optimised_struggle_weights_v2.json` |
| **4b** | Same script, difficulty mode | ⏳ pending | `data/optimised_difficulty_weights_v2.json` |
| **4c** | Same script, improved-struggle mixing mode | ⏳ pending | `data/optimised_improved_weights_v2.json` |
| **4d** | `scripts/optimise_hyperparams.py` grid search | ⏳ pending | `data/optimised_hyperparams_v2.json` |
| **5a** | V2 backend wiring (runtime_config, schemas, struggle, difficulty, improved_struggle, cache, settings router) | ⏳ pending | 8 modified files in `code2/backend/` |
| **5b** | V2 frontend selects (4 selects with disable logic) | ⏳ pending | Modified Settings UI components |
| **6** | `scripts/eval_main.py` — full evaluation matrix | ⏳ pending | `eval_results.md` |
| **7** | Writing-chat briefs (Ch3 + Ch4 amendments, Ch5 §5.4 numbers) | ⏳ pending | Brief paragraphs handed to other chat |
| **8** | Literature `\cite{}` additions + `sync_literature.py` | ⏳ pending | Updated `Report/references.bib` + coverage notes |

**Total estimate:** ~16.5 h Claude time + ~45 min Bakri time + ~$15–25 OpenAI spend.

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
| Snapshot count | ~2000 (struggle) + ~50–100 (difficulty per question) + 50 (Bakri self-label calibration) | 2000 supports stable AUC CIs with 4-fold split; 50 supports kappa estimate with reasonable CI |
| Model class for training | Logistic regression (primary), gradient boosting fallback if LR AUC < 0.55 | Preserves "weighted sum" functional form → v1 vs v2 directly comparable |
| Cross-validation | Group K-fold ($K=5$) with session as group for struggle / improved-blend; LOO-on-question for difficulty | Prevents train/test leakage on students; appropriate for question-level N |
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

**The fix.** Bakri runs the existing script on a machine that can
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

**Status:** waiting on Bakri (2026-05-25).

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

1. C:\Users\Bakri\.claude\plans\crispy-finding-valiant.md
   — the implementation contract; what gets built and how

2. docs/obsidian-vault/My Notes/Thesis/Evaluation PoC Handoff.md
   (THIS note) — live status, decisions log, blockers, label
   definitions, continuation context

3. docs/obsidian-vault/My Notes/Thesis/Evaluation Plan.md
   — the original design doc from 2026-04-21 (cross-reference only;
   the implementation supersedes its scope)

Scope: optimise four artefacts via LR/grid search against GPT-4o-mini
labels (struggle composite weights, difficulty composite weights,
improved-struggle blend weights, scalar hyperparams). Wire each as a
runtime-toggleable v2 option in the V2 React Settings view; all
default v1. Both versions reported in Ch5 §5.4.

Current state: read §6 and §8 of the vault handoff note. If §8 still
shows the API-reachability blocker, the next step is for Bakri to run
`python scripts/eval_fetch.py` locally and paste the sanity output.

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
| `data/self_labels.json` | Bakri's 50 self-labels | 3 |
| `data/optimised_struggle_weights_v2.json` | Optimised $S$ weights | 4a |
| `data/optimised_difficulty_weights_v2.json` | Optimised $D$ weights | 4b |
| `data/optimised_improved_weights_v2.json` | Optimised improved-blend weights | 4c |
| `data/optimised_hyperparams_v2.json` | Grid-searched scalar hyperparams | 4d |
| `eval_results.md` | Final results tables | 6 |

---

## 12 · Changelog

- **2026-05-25 (P2 done)** — Phase 2 complete. `scripts/eval_common.py`
  written; sampler produced 1306 struggle snapshots + 72 difficulty
  entries to `data/eval_snapshots.json`. Band distribution skews
  toward "Needs Help" (54%) and "Hard" (64%) — flagged for §5.5 as
  v1 threshold-calibration finding. Family B horizon-shifted
  positive rates within healthy 10–26% range. Methodology journal
  `v2 Methodology Journal.md` created as supplementary source
  material for the writing chat. Next: Phase 3 (`scripts/eval_label.py`).
- **2026-05-25 (P1 done)** — Phase 1 complete. Bakri ran
  `scripts/eval_fetch.py` locally and cached 42,443 rows to
  `data/eval_submissions.parquet` (time range 2025-10-06 →
  2026-05-15). 21/23 sessions healthy; 2 small sessions
  (Week 12 with 3 students; Week 11 16:00 with 7 students) excluded
  from downstream phases.
- **2026-05-25 (P0 done)** — Phase 0 (this rewrite) underway. Scope
  pivot from PoC to full implementation. Plan file
  `crispy-finding-valiant.md` rewritten to cover four v2 toggles,
  training procedure, Ch3/4 amendments, literature sync. Phase 1
  `scripts/eval_fetch.py` written; blocked on Bakri-local API access
  (resolved same day). Vault note title changed from
  "Evaluation PoC Handoff" to "Evaluation Implementation Handoff"
  (filename preserved for cross-link stability).
- **2026-05-24** — Original PoC handoff note written. Scope was
  evaluation only, no training, no system changes.
