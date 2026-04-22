---
type: community
cohesion: 0.50
members: 4
---

# Measurement Confidence

**Cohesion:** 0.50 - moderately connected
**Members:** 4 nodes

## Members
- [[Phase 1 — Measurement confidence for AI-derived incorrectness scores.]] - rationale - code\learning_dashboard\models\measurement.py
- [[Wrap analytics.compute_incorrectness_column() and add confidence metadata.]] - rationale - code\learning_dashboard\models\measurement.py
- [[compute_incorrectness_with_confidence()]] - code - code\learning_dashboard\models\measurement.py
- [[measurement.py]] - code - code\learning_dashboard\models\measurement.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Measurement_Confidence
SORT file.name ASC
```
