# measurement.py

**Path:** `code/learning_dashboard/models/measurement.py`
**Folder:** [[models]]

> Adds a measurement-confidence column alongside the AI incorrectness score.

## Responsibilities

- For each row with an `ai_feedback` string, compute a confidence in `[0, 1]`:
  - Short / empty feedback → low confidence.
  - Extreme scores (near `0` or `1`) → high confidence; mid-range scores → penalised.
- Leave `incorrectness` itself unchanged; return the DataFrame with a new `measurement_confidence` column.

## Key functions / classes

- `compute_incorrectness_with_confidence(df)` → DataFrame with `incorrectness` (unchanged) and `measurement_confidence` added.

## Dependencies

- `pandas`, `numpy`.
- Reads [[config]]: `MEASUREMENT_CONFIDENCE_MIN_LENGTH`, `MEASUREMENT_CONFIDENCE_BASE`.

## Related notes

- [[Analytics Engine]]
- [[Improved Struggle Logic]] — consumes confidence-aware scores when available
- [[Formulae and Equations]]
