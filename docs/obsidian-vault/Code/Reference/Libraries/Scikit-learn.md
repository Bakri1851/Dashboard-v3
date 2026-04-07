---
name: Scikit-learn
description: Machine learning library used for mistake clustering (TF-IDF + K-means) and collaborative filtering (cosine similarity)
type: reference
---

# Scikit-learn

Python machine learning library providing standard algorithms for classification, clustering, and similarity.

## Version

`scikit-learn >= 1.4.0`

## Why this library

Two analytics features require ML algorithms not available in NumPy/Pandas alone:

1. **Mistake clustering** — groups wrong answers by semantic similarity using TF-IDF text features and K-means. Scikit-learn provides the full pipeline (vectoriser → clustering → evaluation) in one dependency.
2. **Collaborative filtering** — computes pairwise student similarity from behavioural features using cosine similarity. Scikit-learn's `cosine_similarity` operates on NumPy arrays directly.

No separate NLP or recommendation library is needed — everything is available within scikit-learn.

## Where used

- `code/learning_dashboard/analytics.py` — both clustering and collaborative filtering

## Key classes and functions used

### Mistake clustering (`cluster_question_mistakes`)

- `TfidfVectorizer` — converts wrong answer strings into TF-IDF feature vectors. Sparse representation handles short answer text efficiently.
- `KMeans(n_clusters=k)` — groups answer vectors into `k` clusters. `k` is auto-selected (see below).
- `silhouette_score(X, labels)` — measures cluster quality for each candidate `k`; the `k` with the highest silhouette score is chosen (range: `2` to `config.CLUSTER_MAX_K`).
- `cosine_similarity(centroids, vectors)` — finds the answer closest to each cluster centroid to use as the representative example shown in the UI.

### Collaborative filtering (`compute_cf_struggle_scores`, `get_similar_students`)

- `cosine_similarity(student_feature_matrix)` — computes pairwise similarity between all students based on normalised behavioural features (submission count, time active, incorrectness, retry rate). Students similar to confirmed strugglers are flagged even if their own parametric struggle score is below the threshold.

## Config values controlling clustering

- `config.CLUSTER_MIN_WRONG` — minimum number of wrong answers needed before clustering is attempted
- `config.CLUSTER_MAX_K` — upper bound on number of clusters to evaluate
- `config.CLUSTER_MAX_EXAMPLES` — number of representative examples shown per cluster in the UI
- `config.CLUSTER_EXAMPLE_MAX_CHARS` — character limit per example answer

## Related

- [[Analytics Engine]]
- [[Student Struggle Logic]]
- [[Question Difficulty Logic]]
- [[Dashboard Pages and UI Flow]]
