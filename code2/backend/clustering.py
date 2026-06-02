# clustering.py — TF-IDF + KMeans mistake clustering for incorrect submissions.

import hashlib
import json
import logging

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score

from . import config
from .analytics import _get_openai_client

logger = logging.getLogger(__name__)


_cluster_cache: dict[tuple[str, int, str], list[dict] | None] = {}


def _label_clusters_with_openai(clusters: list[dict], question_id: str) -> list[dict]:
    """
    Send all cluster representative answers to OpenAI in one call and fill in 'label'.
    Falls back to 'Mistake Group N' on any error.
    """
    cluster_blocks = []
    for i, c in enumerate(clusters):
        examples = "; ".join(f'"{e}"' for e in c["example_answers"])
        cluster_blocks.append(f"Cluster {i + 1}: {examples}")

    numbered = "\n".join(cluster_blocks)
    prompt = (
        f"You are analysing wrong student answers to a computing/programming question "
        f"(question ID: {question_id}).\n"
        f"Below are {len(clusters)} clusters of incorrect answers, each shown with up to 3 "
        f"representative examples.\n"
        f"For each cluster, provide a concise label (3-6 words) describing the TYPE of mistake "
        f"students are making — focus on the conceptual error, not just what they wrote.\n\n"
        f"Return ONLY a JSON array of strings, one label per cluster, in the same order.\n"
        f"Example output for 3 clusters: "
        f'["Off-by-one indexing error", "Wrong loop condition", "Incorrect variable scope"]\n\n'
        f"Clusters:\n{numbered}"
    )

    try:
        client = _get_openai_client()
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            timeout=15.0,
        )
        labels = json.loads(response.choices[0].message.content.strip())
        if isinstance(labels, list) and len(labels) == len(clusters):
            for i, lbl in enumerate(labels):
                clusters[i]["label"] = str(lbl).strip()
            return clusters
    except Exception:
        pass

    for i, c in enumerate(clusters):
        if c["label"] is None:
            c["label"] = f"Mistake Group {i + 1}"
    return clusters


def cluster_question_mistakes(
    question_df: pd.DataFrame,
    question_id: str,
) -> list[dict] | None:
    """
    Cluster incorrect student answers for a question using TF-IDF + K-means.

    Returns a list of cluster dicts sorted by count descending:
        label            (str)   — short AI-generated description of the mistake type
        count            (int)   — number of incorrect submissions in this cluster
        percent_of_wrong (float) — percentage of all wrong submissions
        example_answers  (list[str]) — up to CLUSTER_MAX_EXAMPLES representative answers

    Returns None if there are fewer than CLUSTER_MIN_WRONG incorrect submissions
    or if vectorisation fails.
    """
    wrong_df = question_df[question_df["incorrectness"] >= config.CORRECT_THRESHOLD].copy()
    wrong_df = wrong_df[wrong_df["student_answer"].notna()]
    wrong_df["student_answer"] = wrong_df["student_answer"].astype(str).str.strip()
    wrong_df = wrong_df[wrong_df["student_answer"] != ""]

    total_wrong = len(wrong_df)
    if total_wrong < config.CLUSTER_MIN_WRONG:
        return None

    _answer_payload = "\0".join(sorted(wrong_df["student_answer"].tolist()))
    _answer_hash = hashlib.sha1(_answer_payload.encode("utf-8")).hexdigest()
    cache_key = (question_id, total_wrong, _answer_hash)
    if cache_key in _cluster_cache:
        return _cluster_cache[cache_key]

    unique_answers = wrong_df["student_answer"].unique().tolist()

    if len(unique_answers) == 1:
        result = [{
            "label": "Common Wrong Answer",
            "count": total_wrong,
            "percent_of_wrong": 100.0,
            "example_answers": unique_answers[:config.CLUSTER_MAX_EXAMPLES],
        }]
        _cluster_cache[cache_key] = result
        return result

    vectorizer = TfidfVectorizer(
        max_features=500,
        sublinear_tf=True,
        strip_accents="unicode",
        analyzer="word",
        min_df=1,
    )
    try:
        X = vectorizer.fit_transform(unique_answers)
    except ValueError:
        _cluster_cache[cache_key] = None
        return None

    n_unique = len(unique_answers)
    max_k = min(config.CLUSTER_MAX_K, n_unique - 1)

    if max_k < 2:
        result = [{
            "label": "Mixed Wrong Answers",
            "count": total_wrong,
            "percent_of_wrong": 100.0,
            "example_answers": unique_answers[:config.CLUSTER_MAX_EXAMPLES],
        }]
        _cluster_cache[cache_key] = result
        return result

    best_k = 2
    best_score = -1.0
    for k in range(2, max_k + 1):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X)
        if len(set(labels)) < 2:
            continue
        try:
            score = silhouette_score(X, labels, metric="cosine")
        except ValueError:
            continue
        if score > best_score:
            best_score = score
            best_k = k

    km_final = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    dedup_labels = km_final.fit_predict(X)

    answer_to_cluster: dict[str, int] = dict(zip(unique_answers, dedup_labels.tolist()))
    wrong_df["_cluster"] = wrong_df["student_answer"].map(answer_to_cluster)

    clusters: list[dict] = []
    centroids = km_final.cluster_centers_

    for cluster_id in range(best_k):
        cluster_rows = wrong_df[wrong_df["_cluster"] == cluster_id]
        count = len(cluster_rows)
        if count == 0:
            continue

        dedup_indices = [i for i, lbl in enumerate(dedup_labels) if lbl == cluster_id]

        centroid = centroids[cluster_id]
        centroid_norm = centroid / (np.linalg.norm(centroid) + 1e-9)
        cluster_dense = X[dedup_indices].toarray()
        norms = np.linalg.norm(cluster_dense, axis=1, keepdims=True) + 1e-9
        similarities = (cluster_dense / norms).dot(centroid_norm)
        sorted_idx = np.argsort(-similarities)
        example_answers = [
            unique_answers[dedup_indices[i]]
            for i in sorted_idx[:config.CLUSTER_MAX_EXAMPLES]
        ]

        clusters.append({
            "label": None,
            "count": count,
            "percent_of_wrong": round(count / total_wrong * 100, 1),
            "example_answers": example_answers,
        })

    clusters.sort(key=lambda c: c["count"], reverse=True)
    clusters = _label_clusters_with_openai(clusters, question_id)

    _cluster_cache[cache_key] = clusters
    return clusters
