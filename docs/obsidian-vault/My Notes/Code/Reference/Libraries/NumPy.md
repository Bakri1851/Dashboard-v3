---
name: NumPy
description: Numerical computing library used in the scoring formulas
type: reference
---

# NumPy

Python library for fast array and numerical operations.

## Version

`numpy >= 1.26.0`

## Why this library

The scoring models require element-wise operations, min-max normalisation, and linear regression over submission sequences. NumPy provides these primitives efficiently and is a transitive dependency of both Pandas and scikit-learn, so it is always present.

## Where used

- `code/learning_dashboard/analytics.py` — all scoring computations
- `code/learning_dashboard/models/irt.py` — IRT MLE optimisation
- `code/learning_dashboard/models/bkt.py` — BKT forward-pass probability updates
- `code/learning_dashboard/models/improved_struggle.py` — combined model outputs

## Key operations used

- `np.array` / `np.zeros` / `np.ones` — constructing score vectors
- `np.clip(value, 0, 1)` — ensuring scores stay in `[0, 1]` after weighting
- `np.mean` — computing mean incorrectness across submissions
- `np.exp` — exponential time-decay weights for `A_raw` (recent incorrectness component)
- `np.polyfit` / manual slope calculation — computing `d_hat`, the incorrectness trajectory slope over submission order
- `np.maximum`, `np.minimum` — min-max normalisation: `(x - min) / (max - min)`, returning `0` when `min == max`
- `np.nan_to_num` — replacing NaN values with `0` after normalisation edge cases

## Normalisation convention

Min-max normalisation returns `0` (not `NaN`) when `min == max` (i.e., all students have the same value for a feature). This is a deliberate choice so students with no distinguishing signal score neutrally rather than erroring.

## Related

- [[Analytics Engine]]
- [[Student Struggle Logic]]
- [[Question Difficulty Logic]]
- [[IRT Difficulty Logic]]
- [[BKT Mastery Logic]]
