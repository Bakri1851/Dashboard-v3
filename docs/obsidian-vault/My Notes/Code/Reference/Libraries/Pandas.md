---
name: Pandas
description: Data manipulation library; the primary data structure throughout the entire pipeline
type: reference
---

# Pandas

Python library for tabular data manipulation using the `DataFrame` abstraction.

## Version

`pandas >= 2.1.0`

## Why this library

All submission data flows through the app as a single `DataFrame` — from raw API response through filtering, aggregation, and scoring to the UI renderers. Pandas provides the groupby, merge, and boolean-indexing operations the pipeline relies on, and integrates directly with Plotly for chart data.

## Where used

- `code/learning_dashboard/data_loader.py` — parses JSON/XML API responses into a `DataFrame`; applies module normalization and time filters; manages saved session persistence
- `code/learning_dashboard/analytics.py` — groupby aggregates per student and per question; produces `struggle_df` and `difficulty_df`
- `code/learning_dashboard/ui/views.py` — slices DataFrames for individual student/question drill-downs
- `code/learning_dashboard/ui/components.py` — passes DataFrames into Plotly chart builders

## Key operations used

- `pd.DataFrame` — primary data structure; one row per submission record
- `pd.json_normalize()` — flattens nested JSON from the API response into tabular columns
- `pd.to_datetime()` — parses `submission_time` strings into `datetime` objects for time filtering
- `df.groupby()` — aggregates submissions per `user_id` (struggle model) and per `question_id` (difficulty model)
- `df[boolean_mask]` — filters rows by time window, module, session start, and saved session range
- `df.merge()` — joins scored DataFrames back to the main submission table
- `df.sort_values()` — orders leaderboard output by score descending
- `df.copy()` — avoids mutating the cached master DataFrame when applying filters

## Important convention

`data_loader.load_data()` returns a `DataFrame`. This is the live, unfiltered data. The sidebar filter chain in `instructor_app.py` applies successive masks to produce the filtered `DataFrame` passed into analytics and views. The cached master is never mutated — always copy before filtering.

## Related

- [[Data Loading and Session Persistence]]
- [[Analytics Engine]]
- [[Instructor Dashboard]]
