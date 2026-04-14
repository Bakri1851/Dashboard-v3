---
tags: [library, data, placeholder, unused]
status: 🔲 Not yet used
---

# Polars

> ⚠️ Not currently used. Candidate Pandas replacement for large datasets.

## What it is

Fast DataFrame library written in Rust. Significantly faster than Pandas for
group-by, join, and aggregation. Supports lazy evaluation.

## Potential use in this project

Replace or supplement Pandas in data_loader.py and analytics.py if session datasets
grow large or multiple saved sessions are loaded and compared simultaneously.

```python
# Sketch — not implemented
import polars as pl
df = pl.read_json("lab_session.json")
struggle = df.group_by("student_id").agg(pl.col("incorrectness").mean())
```

## Relevant to report

Implementation: mention as a considered performance alternative to Pandas.
Not worth switching mid-project — note as future optimisation.
