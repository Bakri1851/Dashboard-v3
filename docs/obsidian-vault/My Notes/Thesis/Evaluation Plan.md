---
tags: [thesis, evaluation, meeting4, design-doc, ch5]
date: 2026-04-21
status: 🟡 Draft — awaiting Bakri review, then Firat sign-off Wed 23 Apr
source: Task prompt 2026-04-21 + FYP Meeting 3 (2026-04-08) + Meeting 4 (2026-04-16)
related: [[Evaluation Strategy]], [[Ch5 – Results and Evaluation]], [[Evidence Bank]], [[Report Sync]], [[Meeting Log]], [[Figures and Tables]], [[Full Roadmap]]
---

# Evaluation Plan — Struggle-Detection Model Comparison

> **Purpose.** Operationalise the retrospective temporal evaluation Dr. Batmaz
> approved in Meeting 4 so Ch5 §5.4 Results can be written. This is a
> **design document**, not an implementation. Implementation begins after
> review.

> **Scope.** Compare three ranking criteria — parametric, CF, hypothesis-based —
> against a full-session parametric ground-truth label, at a sweep of time
> cutoffs, over the ~28k-record Weeks 1–12 dataset.

---

## 1 · Open questions (resolve before Wed 23 Apr)

These are genuinely ambiguous after reading the code. I've taken a view on each
but need either Firat or Bakri to confirm.

1. **Where do the 28k records physically live?**
   The data-pipeline audit found no disk dump. `data/saved_sessions.json` has
   only 8 retroactive *session records* (time-window pointers), not interactions.
   All raw data still comes from the live API (`sccb2.sci-project.lboro.ac.uk/retrievalEndpoint.php`)
   at view time. If the API only retains recent weeks we've silently lost
   earlier-week data.
   → **Preferred resolution:** capture all Weeks 1–12 from the API into a frozen
   local parquet and pin it as the evaluation set. A reproducible evaluation
   cannot run against a changing live source. Action: request a CSV/JSON export
   from Firat as belt-and-braces.

2. **Evaluation unit — one timeline or twelve weekly sessions?**
   Firat's Meeting 4 sketch treats "session" singular. I'll interpret it as:
   - **(a)** one 2-hour lab per week × 12 weeks = 12 evaluation sessions, each
     ~4-5k records. Gives 12 paired curves and cross-session statistics.
   This is what the plan below assumes. Alternative (b) — one aggregate
   28k timeline — loses the natural session boundaries the academic calendar
   already gives us and hides inter-week variability.

3. **Incorrectness cache coverage?**
   `data/incorrectness_cache.json` is 108 KB as of 2026-04-16. Probably covers
   the demo sessions only. Warming all 28k records will hit OpenAI for ~1,400
   batch calls, costing roughly USD 2 and 10–15 minutes wall-clock. We pre-warm
   once, commit `data/incorrectness_cache_v1.json` as the frozen artefact, and
   use it read-only from the evaluator. This must happen **before** the Wed
   meeting if we want live numbers at that meeting.

4. **Canonical implementation — `code/` or `code2/`?**
   [[CLAUDE.md]] names `code/` as the canonical reference, but `code/learning_dashboard/analytics.py:25`
   reads `st.secrets`, blocking headless runs. `code2/learning_dashboard/analytics.py`
   is Streamlit-free and otherwise mirrors `code/`. Resolution: the evaluator
   imports from `code2/`, and we run one cross-validation pass where both
   stacks score the same cohort and we assert numerical equality to ±1e-9.
   Anything else is a bug in one of the two stacks that has to be fixed.

---

## 2 · Repo audit

### 2.1 Models that already exist

| Criterion | Function | File:lines | Status |
|---|---|---|---|
| **Parametric** | `compute_student_struggle_scores` | `code/learning_dashboard/analytics.py:251-366` | ✅ built |
| **CF** | `compute_cf_struggle_scores` | `code/learning_dashboard/analytics.py:378-471` | ✅ built |
| **Hypothesis-based** | — | — | ❌ not built; designed in §3.3 below |
| Improved struggle (opt.) | `models/improved_struggle.compute_improved_struggle` | `code/learning_dashboard/models/improved_struggle.py` | ✅ built, toggleable |
| IRT (Rasch) | `models/irt.fit_irt_difficulty` | `code/learning_dashboard/models/irt.py` | ✅ built |
| BKT mastery | `models/bkt.compute_all_mastery` | `code/learning_dashboard/models/bkt.py` | ✅ built |
| Measurement wrapper | `models/measurement.compute_measurement_columns` | `code/learning_dashboard/models/measurement.py` | ✅ built |

Parametric is a 7-component weighted composite:
`0.10·N + 0.10·T + 0.20·I + 0.10·R + 0.38·A + 0.05·D + 0.07·REP`
(`config.py:18-25`, sum = 1.0 asserted at import) with Bayesian shrinkage
`K=5` pulling low-*n* students toward the class mean.

CF is cosine k-NN (`k=3`, default threshold 0.6) over five normalised features
`[n_hat, t_hat, i_norm, A_norm, d_hat]`. Its output is a weighted-neighbour
mean of **parametric-derived** binary help-need labels.

> ⚠️ **Key framing consequence.** CF is a *post-processor* of parametric,
> not an independent signal. Evaluating CF against parametric-as-truth will
> look rosy by construction. The honest framing of the CF-vs-parametric
> comparison is "does CF add early-warning or stability value over raw
> parametric?", **not** "is CF a better model than parametric?". Called out
> again in §5 Limitations.

### 2.2 Data path

- **Historical load:** user picks saved session → `apply_saved_session_to_state` →
  `load_data()` → `filter_by_datetime_window(df, start, end)`
  (`code/learning_dashboard/data_loader.py:552-567`).
- Timestamps parsed naïve via `pd.to_datetime`. Primary key implicit
  `(user, question, timestamp)` — not explicit but stable in practice.
- Student IDs stable across weeks and across saved-vs-live.
- **"State at time T" primitive:** trivial — `df[df.timestamp <= cutoff]`.
  No new data infrastructure required.

### 2.3 Coupling and obstacles

| Obstacle | Location | Workaround |
|---|---|---|
| `st.secrets` read on OpenAI client init | `code/learning_dashboard/analytics.py:25` | Import from `code2/learning_dashboard/analytics.py:23-27` (uses `os.environ`). |
| Temporal smoothing `α=0.3` is ON (per [[Full Roadmap]] Step 1, 2026-04-10) | analytics / config | Runs are reported with smoothing both ON and OFF — ablation, not footnote. |
| Bayesian shrinkage `K=5` dominates at low *n* | `config.py` `SHRINKAGE_K` | Ablation with `K=0`. At T=10% most students have <5 submissions → shrinkage flattens the ranking. |
| Threshold labels at low *n* are noise-dominated | `config.py` struggle thresholds | Don't evaluate only the default 0.50 "Needs Help" threshold. See §3.1. |

### 2.4 Existing evaluation code

**None** in `code/`, `code2/`, `scripts/`, or top-level. The closest thing is
`code2/backend/routers/models_cmp.py`, which computes Spearman ρ and top-k
overlap for parametric-vs-improved in the live comparison view. **Reuse or
mirror those implementations** — don't re-derive from scratch.

---

## 3 · Proposed evaluation design

### 3.1 Ground-truth labels

Run `compute_student_struggle_scores` on the full session. Derive **three**
label definitions in parallel:

| Label | Definition | Rationale |
|---|---|---|
| `L_top20` | Top 20% of students by parametric score are `struggling=1` | Top-*k* framing matches instructor need ("who should I prioritise?") and is robust to threshold drift |
| `L_needs_help` | `struggle_score ≥ 0.50` | Uses the codebase's semantic class; may produce a very small positive class |
| `L_struggling_plus` | `struggle_score ≥ 0.35` | Broader inclusion; more positives |

Report all three. If results disagree by label definition that's an honest
sensitivity finding; if they agree that's robustness. Either way it's
defensible.

### 3.2 Ranking criteria at cutoff T

Uniform interface: every criterion is a function
`(df_up_to_T, seed_labels=None) → Series[score, indexed by student]`.

1. **Parametric@T** — `compute_student_struggle_scores(df_up_to_T)`. Pure as-is.
2. **CF@T** — `compute_cf_struggle_scores(parametric_df_at_T)`. Pure as-is.
3. **Hypothesis-based@T** — new, spec in §3.3.
4. *(optional baseline)* **Random@T** — reproducibly-shuffled ranking. Included
   to anchor the floor of any precision@k plot.
5. *(optional baseline)* **Most-submissions@T** and **Most-incorrect@T** —
   trivial single-signal rankings. If the 7-component parametric doesn't
   meaningfully beat them, that's an important honest finding.

### 3.3 Hypothesis-based model — design

> Firat's phrasing (Meeting 4): *"Students asking similar questions to
> retrospectively-labelled strugglers are themselves likely struggling."*

At cutoff T:

1. **Seed step.** Run parametric on `df_up_to_T`. Flag the top
   `s = max(3, ceil(0.15 · n_students))` as provisional strugglers.
   Rationale: needs ≥3 seeds for any neighbourhood signal, and 15% is a
   deliberately tighter quantile than the 20% in `L_top20` so we aren't
   trivially recovering ourselves.
2. **Question-profile vectors.** For each student *u*, build
   `v_u ∈ {0,1}^Q` where `v_u[q] = 1` iff *u* attempted *q* and their mean
   incorrectness on *q* exceeded 0.5. This is their **"bad question set"**.
3. **Similarity.** Jaccard on bad-question-sets between every pair of students.
   Jaccard is interpretable, handles sparse sets gracefully, and is exactly
   what Firat described verbally.
4. **Score.**
   `hypothesis_score[u] = α · parametric[u] + (1 − α) · mean_{s ∈ seeds} Jaccard(v_u, v_s)`
   with `α = 0.5` as default. `α = 1` recovers parametric; `α = 0` is pure
   propagation. Report `α ∈ {0, 0.3, 0.5, 0.7}` as sensitivity.

**Why this shape.**
- Feature source (question-overlap) is **different from CF's** (behavioural
  composites) → genuine 3rd axis, not repackaged CF.
- Fully deterministic, fits in ~50 lines, no embeddings, no training.
- Degrades gracefully: at very early T when bad-question-sets are empty,
  Jaccard ≈ 0 and the score reverts to scaled parametric.

### 3.4 Metrics at each cutoff T

For every `(session, T, label L, criterion C)`:

| Metric | Why |
|---|---|
| **Precision@k, Recall@k, F1@k** (k = #positives in L) | Headline. Directly answers "of the students I flag, how many are real strugglers?" and vice versa |
| **Spearman ρ** vs full-session parametric | Rank agreement without binarisation — independent of threshold choice |
| **NDCG@k** | Ranking quality that rewards getting the *most* struggling to the top |
| **Time-to-stable-recall** (derived) | Earliest T at which recall@k reaches ≥0.8 × recall@k(T=full). This is the scalar that most directly answers Firat's "earliest correct identification wins" |
| **Jaccard(top-k@T, top-k@full)** | Symmetric-cut sanity check; very easy to explain in a viva |

Bootstrap 95% CIs over students (resample within each session). Paired
Wilcoxon signed-rank across the 12 sessions to compare criteria.

### 3.5 Time cutoffs

Sweep two families, same computations, different x-axis:

- **Relative:** T ∈ {10%, 20%, …, 90%, 100%} of session wall-clock duration.
  Comparable across sessions of different lengths.
- **Absolute:** T ∈ {15, 30, 45, 60, 75, 90, 105, 120} minutes. Directly
  answers the instructor-actionable question.

Both are cheap; present whichever is more interpretable per finding.

### 3.6 Code structure (implementation, *not this doc*)

> 🚫 **Do not implement yet** — this section is part of the design only.
> Implementation opens as a separate task after review.

```
code/evaluation/                      # new package
    __init__.py
    harness.py           # load_session(week), truncate_at(T), pre-warmed cache loader
    criteria.py          # parametric_rank, cf_rank, hypothesis_rank  (uniform API)
    labels.py            # top_k_labels, threshold_labels, struggling_plus_labels
    metrics.py           # precision_at_k, recall_at_k, ndcg_at_k, spearman, time_to_stable
    temporal_sweep.py    # main loop: sessions × cutoffs × criteria × labels
    report.py            # matplotlib figure generation + CSV/MD table emitters
    run_evaluation.py    # CLI entry point
```

- **Entry point:** `python -m evaluation.run_evaluation --out data/evaluation_runs/2026-04-21`
- **Imports from `code2/learning_dashboard/`** for headlessness.
- **Outputs** under `data/evaluation_runs/{iso-date}/`: `results.parquet`,
  `figures/*.png`, `tables/*.csv`, `summary.md`.
- **Frozen cache:** `data/incorrectness_cache_v1.json`, read-only to the harness.
- **No new dependencies.** pandas, numpy, scikit-learn, scipy, matplotlib are
  already in `requirements.txt`. `tqdm` is a nice-to-have, not essential.

### 3.7 Validation sanity checks

Before trusting any headline number:

1. **Self-recovery.** At T = 100%, parametric criterion must recover its own
   labels with precision = recall = 1.0. If this fails, the harness plumbing
   is wrong — stop and fix.
2. **Trivial floor.** The Random criterion should hit precision@k ≈ k/n.
   Included as a baseline line on every plot.
3. **Cross-stack equivalence.** One session scored by both `code/` Streamlit
   path and `code2/` headless path should be identical to ±1e-9 in struggle
   scores. If not, there's a bug in one stack.

---

## 4 · Alternatives considered and rejected

### 4.1 Label generation

- **Tertiles** — rejected. Loses continuous info, awkward to explain, and the
  boundary between middle and top tertile is semantically fuzzy.
- **Fixed-score threshold only** — rejected as sole label. Retained as one of
  three. At low *n*, tiny score differences flip labels.
- **Human-labelled ground truth** (TA notes, surveys, exam-score proxy) —
  Firat explicitly vetoed the first two (Meeting 3); exam scores aren't
  available in-session and carry too many confounds.

### 4.2 Metrics

- **AUROC** — rejected as headline. Our target is rank agreement with a
  *continuous* score, which Spearman handles more naturally. Keep AUROC as a
  tertiary metric for `L_top20` only.
- **RMSE on scores** — rejected. Scale-dependent; criteria have different
  output scales; would conflate "wrong ranking" with "right ranking on a
  different scale".
- **Kendall τ** — considered. Spearman is reported more often in education
  literature. Keep Spearman as headline, τ in appendix if they diverge.

### 4.3 Time cutoffs

- **Per-student submission count** (T = "after each student submitted 5
  items") — rejected for headline. Heterogeneous across students, instructor
  intervention is wall-clock driven. Possible appendix robustness check.
- **Absolute only** — rejected. Different weekly labs have different durations.
- **Percentage only** — rejected. Hides the practitioner question "after how
  many minutes can I act?".

### 4.4 Hypothesis-based model

- **Personalised PageRank on a student-question bipartite graph** — rejected.
  Overkill for a ~60-student cohort, harder to explain, no obvious improvement
  over Jaccard-kNN.
- **Sentence-transformer embeddings over question text** — rejected. Fragile,
  slow, and most of the question text is identifiers, not prose.
- **Propagate parametric scores over the CF similarity matrix** — rejected.
  That is literally CF, just iterated. Would make the "3rd criterion"
  indistinguishable from the 2nd.
- **Seed purely from `L_top20` at full session** — rejected as target leakage.
  Seeds must come from `parametric@T`, not `parametric@full`.

### 4.5 Evaluation harness location

- **Jupyter notebook as source of truth** — rejected. Hard to re-run
  programmatically, harder to diff. Notebook is fine as a narrative *wrapper*
  around the CLI.
- **Inside the Streamlit comparison view** — rejected. That view is for live
  demo; batch evaluation doesn't belong there.
- **Inside `code2/` backend** — rejected. Evaluator is a research artefact,
  not part of the serving stack.

---

## 5 · Limitations (honest §5.5 material)

These are the concessions Ch5 §5.5 must make explicitly.

1. **Circular ground truth.** Truth = parametric@full-session. Parametric@T
   converges to that as T → full by construction. The evaluation measures
   *how quickly each criterion recovers the parametric verdict*, not
   *whether that verdict is correct*. First paragraph of §5.5.
2. **CF is a post-processor of parametric.** Not an independent signal.
   Honest framing: "does CF add stability or early-warning value?", not "is
   CF better".
3. **Shared upstream dependency on OpenAI-derived incorrectness.** All three
   criteria consume the same `incorrectness` column. Any bias there is
   inherited by every downstream model. Cannot be disentangled without a
   second independent incorrectness source.
4. **Low statistical power.** 12 weekly sessions × ~60 students is small.
   Paired tests won't show between-criterion precision@k differences under
   ~0.1 as significant.
5. **Single cohort, single instructor.** External validity is nil — Firat's
   module, 2025–26 students. The dashboard may behave differently elsewhere.
6. **Retrospective only.** Says nothing about whether an instructor acting on
   the early-T signal would actually help students.
7. **Hand-tuned weights.** The 7-component parametric mix was set by trial and
   error. The evaluation shows the system as configured, not that it's
   optimally configured. Calibrating weights to maximise early recall would
   be circular.
8. **Smoothing and shrinkage hyperparameters** fixed at current defaults in
   headline results. Ablations (§6 item 2) narrow but don't eliminate this.

---

## 6 · Strengthening ideas (beyond what Firat asked)

Strongest-first. Bakri decides which to take on given the ~2 days before the
Wed meeting and ~4 weeks to submission.

1. **Mini prospective study using the 2 remaining lab sessions.**
   Freeze all models. Before session *N*, predict top-5 strugglers using only
   Weeks 1 to *N-1* as prior. After session *N*, compare against actual
   end-of-session ground truth. Even one prospective session is qualitatively
   stronger than any amount of retrospective evaluation and directly answers
   "does this work live?". **High defensive value in a viva.** Cost: ~4h setup
   + session time. *Decision pending.*
2. **Stability ablations as first-class results, not appendix footnotes.**
   Run the full sweep with (a) smoothing off, (b) shrinkage off, (c)
   parametric weights perturbed ±20% on the heaviest (`A=0.38`, `I=0.20`).
   Compute is cheap; a "robust across ablations" column is very hard for an
   examiner to attack. *Decision pending — recommend yes.*
3. **Qualitative case studies (3 students).** Pick 3 students where the three
   criteria most disagree at end-of-session. Walk through their actual
   submissions and ask: which criterion "got them right" by human reading?
   Low-risk because framed as illustrative, not evaluative. 1–2h.
   *Decision pending — recommend yes.*
4. **Report CF's diagnostics panel directly.** CF already tracks which
   students it "elevated" beyond parametric. Count how many of those turn out
   to be true-positive strugglers at full session. Directly measures CF's
   value-add. Low cost.
5. **Trivial single-signal baselines** (most-submissions, most-incorrect) as
   additional lines on every plot. If the 7-component parametric doesn't
   meaningfully beat them, that's important to report honestly. 30 min.
   *Decision pending — recommend yes.*
6. **Per-student time-to-first-correct-identification.** For every
   ground-truth struggler individually, at what T does each criterion first
   flag them? Plot as a Gantt-style chart. Gives an instructor-friendly
   visualisation of the same data. *Decision pending.*

---

## 7 · Risks and time estimate

### 7.1 Risks

| Risk | Mitigation |
|---|---|
| Incorrectness cache under-warmed for Weeks 1–12 | Pre-warm script run this evening; commit frozen cache |
| API has truncated earlier weeks — data simply gone | Dump everything reachable immediately; ask Firat for CSV backup |
| Hypothesis ranking fails to beat random | Report as negative finding and stop — don't spend days trying to "fix" it |
| Temporal smoothing makes early-T signal look artificially weak | Smoothing-off ablation is headline, not appendix |
| Scope creep: writing this doc turns into building the evaluator | Explicit non-goals list (§9). Separate task for implementation. |
| `code/` vs `code2/` numerical drift | §3.7 cross-stack equivalence check catches this early |

### 7.2 Time from current state

**Doc writing (this task, no code):**
- Draft `Evaluation Plan.md` in vault voice — 3–4h
- Incorporate Bakri pushback — 1–2h
- **Total:** ~1 working day

**Follow-on implementation (separate task, NOT this task):**
- Harness + parametric + CF + metrics — ~1 day
- Hypothesis model + sweep runner — ~0.5 day
- Figure generation + ablations — ~0.5 day
- Buffer + incorrectness pre-warm — ~0.5 day
- **Total implementation:** ~2.5 working days. Within budget for Wed 23 Apr
  if work starts immediately after doc sign-off.

---

## 8 · Implementation checklist (to hand to the next task)

> 🚫 **Do not implement yet.** Listed here so the handover to the
> implementation task is mechanical.

**Pre-flight:**
- [ ] Confirm §1 open questions with Bakri / Firat
- [ ] Pre-warm `data/incorrectness_cache_v1.json` over all 28k records
- [ ] Freeze the Week 1–12 dataset locally (parquet)

**Build order (files to create under `code/evaluation/`):**
1. [ ] `harness.py` — `load_session(week)`, `truncate_at(T)`, `load_frozen_cache()`
2. [ ] `labels.py` — `top_k_labels`, `threshold_labels`, `struggling_plus_labels`
3. [ ] `criteria.py` — uniform API:
   ```python
   def rank(df_up_to_T: pd.DataFrame, seed_labels: pd.Series | None = None) -> pd.Series:
       """Return score per student, index=user, sorted desc."""
   ```
   Implementations: `parametric_rank`, `cf_rank`, `hypothesis_rank`,
   `random_rank`, `most_submissions_rank`, `most_incorrect_rank`.
4. [ ] `metrics.py` — `precision_at_k`, `recall_at_k`, `f1_at_k`,
       `ndcg_at_k`, `spearman_rho`, `jaccard_topk`, `time_to_stable_recall`.
       Mirror or import Spearman + top-k overlap from
       `code2/backend/routers/models_cmp.py`.
5. [ ] `temporal_sweep.py` — loop
       `sessions × cutoffs × criteria × labels → rows`.
6. [ ] `report.py` — CSV/parquet writers + matplotlib plotters.
7. [ ] `run_evaluation.py` — CLI.

**Sanity gates before reporting results:**
- [ ] Self-recovery: parametric@100% gives precision = recall = 1.0
- [ ] Random floor: random@any-T gives precision@k ≈ k/n
- [ ] Cross-stack equivalence: `code/` = `code2/` to ±1e-9 on one session

---

## 9 · What this evaluation does NOT prove

Plain-language version for the conclusion of Ch5 §5.5:

> This evaluation does not demonstrate that the system correctly identifies
> struggling students in an absolute sense. It demonstrates how quickly, and
> how robustly, three candidate ranking criteria converge on the ranking that
> the parametric model itself reaches by the end of a session. Because the
> ground truth is itself a model output, the evaluation is best read as a
> *stability and early-warning study*, not a validation against an external
> truth. External validation would require either independent labels (TA
> observations, post-hoc exam scores) or a prospective classroom study —
> both of which are out of scope for this thesis and are listed as future
> work in [[Future Work Inventory]].

---

## 10 · Non-goals of this design task

- Writing *any* evaluation code.
- Modifying any file other than this one (and one pointer row in the toolkit
  HTML, optionally, once this doc is reviewed).
- Running the evaluator.
- Generating Ch5 figures or tables.
- Editing [[Ch5 – Results and Evaluation]] yet — it will cross-link to this
  doc once sign-off is complete.

---

## 11 · Mapping to Ch5 subsections

| This doc | [[Ch5 – Results and Evaluation]] subsection | Notes |
|---|---|---|
| §2 Repo audit | §5.1 Evaluation Design — "what's implemented" paragraph | |
| §3 Evaluation design | §5.1 Evaluation Design — methodology prose | Primary source |
| §3.4 Metrics + §3.5 cutoffs | §5.4 Results — tables + figures | One figure per metric family |
| §4 Alternatives rejected | §5.1 Evaluation Design — "why this design" | Brief footnotes only |
| §5 Limitations | §5.5 Discussion — limitations paragraph | Verbatim-ish |
| §6 Strengthening ideas | §5.4 Results (ablations) + §5.5 Discussion (future work) | |
| §9 "Does not prove" paragraph | §5.5 Discussion — closing paragraph | Plain-language copy |

---

## 12 · Changelog

- **2026-04-21** — initial draft (Bakri + Claude). Awaiting review.
