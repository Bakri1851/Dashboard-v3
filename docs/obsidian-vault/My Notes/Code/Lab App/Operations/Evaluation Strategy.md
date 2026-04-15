---
tags: [lab-app, evaluation, meeting3, meeting4]
date: 2026-04-16
status: 🔶 Planned — not yet implemented
source: FYP Meeting 3 (2026-04-08) + Meeting 4 (2026-04-16)
---

# Evaluation Strategy

> ⚠️ **Implementation required before Wed 23 Apr** — Dr. Batmaz set this as the top priority for the coming week.

## Dr. Batmaz's Requirement

The struggle detection model needs a mathematically justifiable evaluation before submission. No human subjects required — fully retrospective using existing session data.

## Approved Method — Retrospective Temporal Evaluation

Dr. Batmaz described this in detail in Meeting 4 and confirmed it is the correct approach:

1. **Take a full recorded session** — 28,000 records available from Dr. Batmaz's module (Weeks 1–12, ~57–62 students). Filter by module + date range from the database.
2. **Label students retrospectively** — using the existing parametric struggle criteria applied to the *full* session, label each student as struggling/not-struggling based on their end-of-session outcome. This is the ground truth.
3. **Feed partial data to the model** — truncate the session at minute 20 (or 30) and run the ranking model on only that prefix. See which students it flags as struggling.
4. **Measure early prediction accuracy** — check whether the model correctly identifies the retrospectively-labelled struggling students *before the session ends*. Earlier correct prediction = better model.
5. **Sweep the time cutoff** — repeat at minute 20, 30, 40, etc. Plot when each ranking criterion first correctly identifies all (or most) struggling students. Earlier = better.
6. **Compare ranking criteria** — the three criteria to compare:
   - **Parametric model** — the existing weighted 7-signal struggle score
   - **CF-based ranking** — cosine similarity elevation above threshold
   - **Hypothesis-based ranking** — students who ask similar questions to known-struggling students are themselves likely to struggle

Whichever criterion correctly identifies struggling students earliest wins. This gives a mathematical, label-free comparison that justifies the model choices.

## Dataset

- Source: Dr. Batmaz's module, all labs, Weeks 1–12
- Size: ~28,000 interaction records
- Students: ~57–62
- Filter: by module code + date range in the database
- Status: data is live in the dashboard database; verified present in the Data Analysis view

## Planned Actions

- [ ] Implement retrospective labelling function — apply parametric criteria to full session, output per-student label
- [ ] Implement temporal truncation — filter session data to rows with timestamp ≤ T minutes
- [ ] Run parametric model on truncated data — extract ranked struggle scores
- [ ] Run CF model on truncated data — extract students above similarity threshold
- [ ] Run hypothesis-based ranking on truncated data — identify students sharing question clusters with labelled strugglers
- [ ] Compare predictions against ground truth labels — precision/recall or simple hit rate
- [ ] Sweep T (minute cutoff) and record accuracy at each step
- [ ] Plot results — accuracy vs time for each ranking criterion
- [ ] Draft Ch5 §5.4 results section from these results

## Future Work — Weight Optimisation

> 💡 Currently α, β, γ, δ, η are set by trial and error due to absence of labeled ground truth.
> Once labeled data is available (even from this retrospective labelling), weights could be trained:
> - Logistic regression over validated struggle labels
> - Gradient boosting (XGBoost / sklearn)
> - Optuna hyperparameter search over the weight space
> The absence of labeled data must be stated explicitly as a limitation in Ch5.
