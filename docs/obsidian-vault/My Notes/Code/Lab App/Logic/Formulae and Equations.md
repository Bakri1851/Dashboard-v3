# Formulae and Equations

Consolidated reference for every mathematical formula used in the scoring system. For algorithm context and step-by-step pipelines see [[Algorithms]]. For per-topic design rationale see the individual Logic notes.

Related: [[Algorithms]], [[Analytics Engine]], [[Student Struggle Logic]], [[Question Difficulty Logic]], [[IRT Difficulty Logic]], [[BKT Mastery Logic]], [[Improved Struggle Logic]], [[Glossary]]

---

## Incorrectness

Every submission receives a continuous `incorrectness` value in `[0, 1]` derived from the `ai_feedback` text.

```
incorrectness ∈ [0.0, 1.0]
fallback = 0.5   (used when feedback is empty or OpenAI call fails)
correct_threshold = 0.5   (incorrectness < 0.5 → treated as correct)
```

Source: `code/learning_dashboard/config.py` — `CORRECT_THRESHOLD`

---

## Min-Max Normalisation

Used to map raw feature values into `[0, 1]` before weighting. Returns `0` when `min == max` (single-value edge case).

```
x_hat = (x - min(x)) / (max(x) - min(x))
```

Applied to: `n` (submission count), `t` (session duration), `d` (slope), `a` (attempts per student), `t_tilde` (avg time per student).

Source: `code/learning_dashboard/analytics.py` — `min_max_normalize()`

---

## Bayesian Shrinkage

Pulls low-volume student scores toward the class mean to prevent noisy estimates from dominating.

```
w_n   = n / (n + K)          where K = 5 (SHRINKAGE_K)
S_final = w_n * S_raw + (1 - w_n) * mean(S_raw)
```

Applied after computing both baseline struggle and improved struggle scores.

Source: `code/learning_dashboard/config.py` — `SHRINKAGE_K`

---

## Baseline Student Struggle

Full 7-component weighted formula:

```
S = 0.10*n_hat + 0.10*t_hat + 0.20*i_hat + 0.10*r_hat + 0.38*A_raw + 0.05*d_hat + 0.07*rep_hat
```

| Symbol | Weight | Meaning |
|--------|--------|---------|
| `n_hat`   | 0.10 | Min-max normalised submission count |
| `t_hat`   | 0.10 | Min-max normalised session duration (minutes, first → last submission) |
| `i_hat`   | 0.20 | Mean incorrectness across all submissions |
| `r_hat`   | 0.10 | Retry rate — fraction of attempts on already-seen questions |
| `A_raw`   | 0.38 | Recent incorrectness over last 5 submissions with exponential time decay |
| `d_hat`   | 0.05 | Min-max normalised trajectory slope (positive = getting worse) |
| `rep_hat` | 0.07 | Exact-answer repetition rate on same question |

### Recent incorrectness (A_raw) — exponential decay

```
A_raw = Σ w_k * incorrectness_k  /  Σ w_k
w_k   = exp(-λ * Δt_k)           where λ = decay rate, Δt_k = time since submission k
```

Source: `code/learning_dashboard/analytics.py` — `compute_recent_incorrectness()`  
Config: `code/learning_dashboard/config.py` — `STRUGGLE_WEIGHTS`, `RECENT_SUBMISSION_COUNT`

---

## Baseline Question Difficulty

Full 5-component weighted formula:

```
D = 0.28*c_tilde + 0.12*t_tilde + 0.20*a_tilde + 0.20*f_tilde + 0.20*p_tilde
```

| Symbol | Weight | Meaning |
|--------|--------|---------|
| `c_tilde`  | 0.28 | Incorrect rate across all attempts |
| `t_tilde`  | 0.12 | Min-max normalised average time per student |
| `a_tilde`  | 0.20 | Min-max normalised average attempts per student |
| `f_tilde`  | 0.20 | Average incorrectness across all attempts |
| `p_tilde`  | 0.20 | First-attempt failure rate across students |

Source: `code/learning_dashboard/analytics.py` — `compute_question_difficulty_scores()`  
Config: `code/learning_dashboard/config.py` — `DIFFICULTY_WEIGHTS`

---

## IRT — Rasch 1PL Model

Models the probability that student `j` answers question `i` correctly as a function of latent ability and latent difficulty:

```
P(correct | θ_j, b_i) = sigmoid(θ_j − b_i)
                       = 1 / (1 + exp(-(θ_j − b_i)))
```

| Symbol | Meaning |
|--------|---------|
| `θ_j` | Latent ability of student j (estimated, continuous) |
| `b_i` | Latent difficulty of question i (estimated, continuous) |

**Identifiability constraint:** `mean(θ) = 0` (mean ability pinned to zero).

Both parameters are estimated jointly via maximum likelihood (L-BFGS-B optimiser).

**Output mapping:** raw logit-scale `b_i` is mapped to `[0, 1]` via sigmoid, then min-max normalised before classification:

```
irt_difficulty_raw  = sigmoid(b_i)
irt_difficulty_norm = min_max_normalize(irt_difficulty_raw)
```

Source: `code/learning_dashboard/models/irt.py` — `fit_rasch_model()`  
Config: `code/learning_dashboard/config.py` — `IRT_MAX_ITER`, `IRT_MIN_ATTEMPTS_PER_QUESTION`, `IRT_MIN_ATTEMPTS_PER_STUDENT`

---

## BKT — Bayesian Knowledge Tracing

Each question is treated as a single skill. The hidden state is binary: learned (L) vs not learned (~L). Four fixed parameters:

```
P(L_0) = 0.3   — prior probability of knowing the skill
P(T)   = 0.1   — probability of learning on each opportunity
P(G)   = 0.2   — probability of guessing correctly without knowing
P(S)   = 0.1   — probability of slipping (wrong despite knowing)
```

### Bayes update after each observation

```
P(L | correct) = P(L) * (1 − P(S))  /  [P(L)*(1−P(S)) + (1−P(L))*P(G)]
P(L | wrong)   = P(L) * P(S)         /  [P(L)*P(S)     + (1−P(L))*(1−P(G))]
```

### Learning transition (applied after each update)

```
P(L_next) = P(L | obs) + (1 − P(L | obs)) * P(T)
```

Submissions are replayed chronologically per student per question. Result is clipped to `[0, 1]`.

Source: `code/learning_dashboard/models/bkt.py` — `bkt_update()`, `compute_all_mastery()`  
Config: `code/learning_dashboard/config.py` — `BKT_P_INIT`, `BKT_P_LEARN`, `BKT_P_GUESS`, `BKT_P_SLIP`, `BKT_MASTERY_THRESHOLD`

---

## Improved Struggle Model (Phase 4)

Three signal groups combined into a single weighted score:

```
S_improved = w_beh * behavioral + w_mg * mastery_gap + w_da * difficulty_adjusted
```

Default weights: `w_beh = 0.45`, `w_mg = 0.30`, `w_da = 0.25`

### 1. Behavioral composite

Four sub-signals, equally weighted:

```
behavioral = (A_raw + r_hat + d_hat + rep_hat) / 4
```

### 2. Mastery gap

```
recent_performance = 1 − A_raw
mastery_gap        = max(0, mean_mastery − recent_performance)
```

A large positive gap means the student is performing well below their demonstrated mastery — a strong struggle signal. Negative values (outperforming mastery) are clamped to zero.

### 3. Difficulty-adjusted incorrectness

```
difficulty_adjusted = mean( incorrectness_i × (1 − normalized_irt_difficulty_i) )
```

Computed over the student's last `RECENT_SUBMISSION_COUNT` submissions. Failing easy questions (low IRT difficulty) yields a higher score than failing hard ones. Questions without IRT data use a neutral difficulty of `0.5`.

### Graceful degradation

| Missing data | Weight redistribution |
|---|---|
| BKT unavailable | `w_mg` added to `w_beh` |
| IRT unavailable | `w_da` added to `w_beh` |
| Both unavailable | `w_beh = 1.0` (behavioral only) |

Bayesian shrinkage (`w_n = n / (n + K)`) is applied after assembly. Score clipped to `[0, 1]`.

Source: `code/learning_dashboard/models/improved_struggle.py` — `compute_improved_struggle_scores()`  
Config: `code/learning_dashboard/config.py` — `IMPROVED_STRUGGLE_WEIGHT_BEHAVIORAL`, `IMPROVED_STRUGGLE_WEIGHT_MASTERY_GAP`, `IMPROVED_STRUGGLE_WEIGHT_DIFFICULTY_ADJ`

---

## Score Classification Thresholds

### Student Struggle

| Range | Label | Meaning |
|-------|-------|---------|
| `0.00 – 0.20` | On Track | No intervention needed |
| `0.20 – 0.35` | Minor Issues | Monitor |
| `0.35 – 0.50` | Struggling | Recommend assistant visit |
| `0.50 – 1.00` | Needs Help | Urgent |

### Question Difficulty

| Range | Label |
|-------|-------|
| `0.00 – 0.35` | Easy |
| `0.35 – 0.50` | Medium |
| `0.50 – 0.75` | Hard |
| `0.75 – 1.00` | Very Hard |

Config: `code/learning_dashboard/config.py` — `STRUGGLE_THRESHOLDS`, `DIFFICULTY_THRESHOLDS`
