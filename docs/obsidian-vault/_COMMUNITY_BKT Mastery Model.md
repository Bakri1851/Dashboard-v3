---
type: community
cohesion: 0.24
members: 10
---

# BKT Mastery Model

**Cohesion:** 0.24 - loosely connected
**Members:** 10 nodes

## Members
- [[Per-student aggregate mastery statistics.      Accepts the output of ``compute_a]] - rationale - code\learning_dashboard\models\bkt.py
- [[Per-student, per-question mastery for the entire dataset.      Returns DataFrame]] - rationale - code\learning_dashboard\models\bkt.py
- [[Phase 3 — Bayesian Knowledge Tracing (BKT) mastery estimation.  Standard BKT wit]] - rationale - code\learning_dashboard\models\bkt.py
- [[Replay one student's chronological submissions and return final mastery per ques]] - rationale - code\learning_dashboard\models\bkt.py
- [[Single BKT HMM update step.  Returns P(L_{t+1}).]] - rationale - code\learning_dashboard\models\bkt.py
- [[bkt.py]] - code - code\learning_dashboard\models\bkt.py
- [[bkt_update()]] - code - code\learning_dashboard\models\bkt.py
- [[compute_all_mastery()]] - code - code\learning_dashboard\models\bkt.py
- [[compute_student_mastery()]] - code - code\learning_dashboard\models\bkt.py
- [[compute_student_mastery_summary()]] - code - code\learning_dashboard\models\bkt.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/BKT_Mastery_Model
SORT file.name ASC
```
