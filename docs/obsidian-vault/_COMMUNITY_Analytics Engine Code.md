---
type: community
cohesion: 0.10
members: 30
---

# Analytics Engine Code

**Cohesion:** 0.10 - loosely connected
**Members:** 30 nodes

## Members
- [[(x - min)  (max - min), clamped to 0, 1. Returns 0 if min == max.]] - rationale - code\learning_dashboard\analytics.py
- [[Cluster incorrect student answers for a question using TF-IDF + K-means.      Re]] - rationale - code\learning_dashboard\analytics.py
- [[Collaborative filtering layer identify students behaviourally similar     to th]] - rationale - code\learning_dashboard\analytics.py
- [[Compute difficulty scores for all questions in the DataFrame.     Returns a Data]] - rationale - code\learning_dashboard\analytics.py
- [[Compute struggle scores for all students in the DataFrame.     Returns a DataFra]] - rationale - code\learning_dashboard\analytics.py
- [[Last N submissions (most recent first), weighted by exponential time decay.]] - rationale - code\learning_dashboard\analytics.py
- [[Linear regression slope of incorrectness vs. submission order (oldest=0).     Po]] - rationale - code\learning_dashboard\analytics.py
- [[Return (label, color) for the matching threshold range.]] - rationale - code\learning_dashboard\analytics.py
- [[Return the k most similar students to student_id based on cosine     similarit]] - rationale - code\learning_dashboard\analytics.py
- [[S_t = (1 - alpha)  S_previous + alpha  S_raw     Returns s_raw if s_previous i]] - rationale - code\learning_dashboard\analytics.py
- [[Score a single feedback string via OpenAI. Returns float in 0, 1.]] - rationale - code\learning_dashboard\analytics.py
- [[Score all ai_feedback values via OpenAI, batched for efficiency.     Results are]] - rationale - code\learning_dashboard\analytics.py
- [[Send a batch of feedback texts to OpenAI and return incorrectness scores 0, 1.]] - rationale - code\learning_dashboard\analytics.py
- [[Send all cluster representative answers to OpenAI in one call and fill in 'label]] - rationale - code\learning_dashboard\analytics.py
- [[_call_openai_batch()]] - code - code\learning_dashboard\analytics.py
- [[_compute_slope()]] - code - code\learning_dashboard\analytics.py
- [[_get_openai_client()]] - code - code\learning_dashboard\analytics.py
- [[_label_clusters_with_openai()]] - code - code\learning_dashboard\analytics.py
- [[analytics.py]] - code - code\learning_dashboard\analytics.py
- [[apply_temporal_smoothing()]] - code - code\learning_dashboard\analytics.py
- [[classify_score()]] - code - code\learning_dashboard\analytics.py
- [[cluster_question_mistakes()]] - code - code\learning_dashboard\analytics.py
- [[compute_cf_struggle_scores()]] - code - code\learning_dashboard\analytics.py
- [[compute_incorrectness_column()]] - code - code\learning_dashboard\analytics.py
- [[compute_question_difficulty_scores()]] - code - code\learning_dashboard\analytics.py
- [[compute_recent_incorrectness()]] - code - code\learning_dashboard\analytics.py
- [[compute_student_struggle_scores()]] - code - code\learning_dashboard\analytics.py
- [[estimate_incorrectness()]] - code - code\learning_dashboard\analytics.py
- [[get_similar_students()]] - code - code\learning_dashboard\analytics.py
- [[min_max_normalize()]] - code - code\learning_dashboard\analytics.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Analytics_Engine_Code
SORT file.name ASC
```
