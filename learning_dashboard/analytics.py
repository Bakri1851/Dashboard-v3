# analytics.py — Scoring calculations (UI-independent)
import json
import math
import os
from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st
from openai import OpenAI
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity

from learning_dashboard import config


def _get_openai_client() -> OpenAI:
    key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY", "")
    return OpenAI(api_key=key)


# Incorrectness Estimation via OpenAI

_incorrectness_cache: dict[str, float] = {}
_cluster_cache: dict[tuple[str, int], list[dict] | None] = {}


def _call_openai_batch(feedbacks: list[str]) -> list[float]:
    """
    Send a batch of feedback texts to OpenAI and return incorrectness scores [0, 1].
    Returns [0.5] * len(feedbacks) on any error.
    """
    numbered = "\n".join(f"{i + 1}. {text}" for i, text in enumerate(feedbacks))
    prompt = (
        "You are scoring student answers based on AI tutor feedback.\n"
        "For each numbered feedback text below, return a JSON array of floats "
        "from 0.0 (fully correct) to 1.0 (fully incorrect).\n"
        "Return ONLY the JSON array, nothing else.\n\n"
        f"Feedbacks:\n{numbered}"
    )
    try:
        client = _get_openai_client()
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        scores = json.loads(response.choices[0].message.content.strip())
        if isinstance(scores, list) and len(scores) == len(feedbacks):
            return [float(max(0.0, min(1.0, s))) for s in scores]
    except Exception:
        pass
    return [0.5] * len(feedbacks)


def estimate_incorrectness(feedback: Optional[str]) -> float:
    """Score a single feedback string via OpenAI. Returns float in [0, 1]."""
    if not feedback or not str(feedback).strip():
        return 0.5
    key = str(feedback).strip()
    if key not in _incorrectness_cache:
        _incorrectness_cache[key] = _call_openai_batch([key])[0]
    return _incorrectness_cache[key]


def compute_incorrectness_column(df: pd.DataFrame) -> pd.Series:
    """
    Score all ai_feedback values via OpenAI, batched for efficiency.
    Results are cached in-process to avoid repeat API calls across reruns.
    Empty/null feedback → 0.5 without an API call.
    """
    feedbacks = df["ai_feedback"].astype(str).str.strip()

    # Collect unique non-empty texts not yet cached
    uncached = [t for t in feedbacks.unique() if t and t not in _incorrectness_cache]

    # Fetch in batches
    for i in range(0, len(uncached), config.OPENAI_BATCH_SIZE):
        batch = uncached[i : i + config.OPENAI_BATCH_SIZE]
        scores = _call_openai_batch(batch)
        _incorrectness_cache.update(zip(batch, scores))

    return feedbacks.map(lambda t: _incorrectness_cache.get(t, 0.5))


# Min-Max Normalization

def min_max_normalize(series: pd.Series) -> pd.Series:
    """(x - min) / (max - min), clamped to [0, 1]. Returns 0 if min == max."""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series(0.0, index=series.index)
    result = (series - min_val) / (max_val - min_val)
    return result.clip(0.0, 1.0)


# -----------------------------------------------------------------
# Recent Incorrectness (A_raw)
# -----------------------------------------------------------------

def compute_recent_incorrectness(student_submissions: pd.DataFrame) -> float:
    """
    Last N submissions (most recent first), weighted by exponential time decay.
    w_i = exp(-lambda * delta_t_i) where delta_t_i = seconds since submission i.
    Weights are normalised to sum to 1.0.
    Falls back to equal weights if all timestamps are identical.
    """
    recent = (
        student_submissions.sort_values("timestamp", ascending=False)
        .head(config.RECENT_SUBMISSION_COUNT)
    )
    scores = recent["incorrectness"].tolist()
    n_actual = len(scores)

    if n_actual == 0:
        return 0.0

    timestamps = recent["timestamp"].tolist()
    t_now = timestamps[0]  # most recent after descending sort
    lam = math.log(2) / config.DECAY_HALFLIFE_SECONDS

    raw_weights = [
        math.exp(-lam * max(0.0, (t_now - ts).total_seconds()))
        for ts in timestamps
    ]
    weight_sum = sum(raw_weights)

    # Equal-weight fallback if all timestamps are identical (e.g. bulk import)
    if weight_sum <= 0 or all(w == raw_weights[0] for w in raw_weights):
        return sum(scores) / n_actual

    weights = [w / weight_sum for w in raw_weights]
    return sum(w * s for w, s in zip(weights, scores))


# -----------------------------------------------------------------
# Improvement Trajectory Helper
# -----------------------------------------------------------------

def _compute_slope(student_submissions: pd.DataFrame) -> float:
    """
    Linear regression slope of incorrectness vs. submission order (oldest=0).
    Positive slope = getting worse; negative = improving.
    Returns 0.0 if fewer than 2 submissions.
    """
    sorted_subs = student_submissions.sort_values("timestamp", ascending=True)
    scores = sorted_subs["incorrectness"].tolist()
    n = len(scores)
    if n < 2:
        return 0.0
    slope = np.polyfit(range(n), scores, 1)[0]
    return float(slope)


# -----------------------------------------------------------------
# Classification Helpers
# -----------------------------------------------------------------

def classify_score(
    score: float,
    thresholds: list[tuple[float, float, str, str]],
) -> tuple[str, str]:
    """Return (label, color) for the matching threshold range."""
    for i, (low, high, label, color) in enumerate(thresholds):
        if i == len(thresholds) - 1:
            if low <= score <= high:
                return label, color
        else:
            if low <= score < high:
                return label, color
    return thresholds[-1][2], thresholds[-1][3]


# -----------------------------------------------------------------
# Student Struggle Score
# -----------------------------------------------------------------

def compute_student_struggle_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute struggle scores for all students in the DataFrame.
    Returns a DataFrame with one row per student.
    """
    if df.empty:
        return pd.DataFrame(columns=[
            "user", "submission_count", "time_active_min", "n_hat", "t_hat",
            "i_hat", "r_hat", "rep_hat", "A_raw", "d_hat", "struggle_score",
            "struggle_level", "struggle_color", "mean_incorrectness_pct",
            "recent_incorrectness",
        ])

    work = df.copy()
    if "incorrectness" not in work.columns:
        work["incorrectness"] = compute_incorrectness_column(work)

    rows = []
    grouped = work.groupby("user")

    for user, group in grouped:
        n = len(group)

        # Time active (minutes from first to last submission)
        if n > 1:
            t = (group["timestamp"].max() - group["timestamp"].min()).total_seconds() / 60.0
        else:
            t = 0.0

        # Mean incorrectness: continuous gradient, no binary threshold
        i_hat = group["incorrectness"].mean()

        # Retry rate: fraction of submissions that are repeats of an already-attempted question
        unique_q = group["question"].nunique()
        r_hat = 1.0 - (unique_q / n) if n > 0 else 0.0

        # Recent incorrectness (A_raw)
        a_raw = compute_recent_incorrectness(group)

        # Improvement trajectory: linear slope of incorrectness over submission order
        d_raw = _compute_slope(group)

        # Answer repetition rate: fraction of submissions that exactly repeat
        # a previously submitted answer on the same question (exact match after strip).
        total_repeat_submissions = 0
        for _q, q_group in group.groupby("question"):
            answers = q_group.sort_values("timestamp")["student_answer"].tolist()
            seen: set[str] = set()
            for ans in answers:
                cleaned = str(ans).strip()
                if cleaned in seen:
                    total_repeat_submissions += 1
                else:
                    seen.add(cleaned)
        rep_hat = total_repeat_submissions / n if n > 0 else 0.0

        rows.append({
            "user": user,
            "submission_count": n,
            "time_active_min": round(t, 2),
            "n_raw": n,
            "t_raw": t,
            "i_hat": i_hat,
            "r_hat": r_hat,
            "A_raw": a_raw,
            "d_raw": d_raw,
            "rep_hat": rep_hat,
        })

    result = pd.DataFrame(rows)

    # Min-max normalize n, t, and trajectory slope across all students
    result["n_hat"] = min_max_normalize(result["n_raw"])
    result["t_hat"] = min_max_normalize(result["t_raw"])
    result["d_hat"] = min_max_normalize(result["d_raw"])  # positive = getting worse

    # Compute S_raw
    result["struggle_score"] = (
        config.STRUGGLE_WEIGHT_N * result["n_hat"]
        + config.STRUGGLE_WEIGHT_T * result["t_hat"]
        + config.STRUGGLE_WEIGHT_I * result["i_hat"]
        + config.STRUGGLE_WEIGHT_R * result["r_hat"]
        + config.STRUGGLE_WEIGHT_A * result["A_raw"]
        + config.STRUGGLE_WEIGHT_D * result["d_hat"]
        + config.STRUGGLE_WEIGHT_REP * result["rep_hat"]
    ).clip(0.0, 1.0)

    # Bayesian shrinkage: pull low-n scores toward the class mean to reduce noise.
    # w_n = n / (n + K) → students with few submissions are shrunk more strongly.
    s_class_mean = result["struggle_score"].mean()
    w_n = result["n_raw"] / (result["n_raw"] + config.SHRINKAGE_K)
    result["struggle_score"] = (
        w_n * result["struggle_score"] + (1 - w_n) * s_class_mean
    ).clip(0.0, 1.0)

    # Classify
    levels_colors = result["struggle_score"].apply(
        lambda s: classify_score(s, config.STRUGGLE_THRESHOLDS)
    )
    result["struggle_level"] = levels_colors.apply(lambda x: x[0])
    result["struggle_color"] = levels_colors.apply(lambda x: x[1])

    # Convenience columns
    result["mean_incorrectness_pct"] = (result["i_hat"] * 100).round(1)
    result["recent_incorrectness"] = result["A_raw"].round(3)

    # Sort descending by score
    result = result.sort_values("struggle_score", ascending=False).reset_index(drop=True)

    return result


# -----------------------------------------------------------------
# Collaborative Filtering Struggle Detection
# -----------------------------------------------------------------

CF_FEATURES = ["n_hat", "t_hat", "i_hat", "A_raw", "d_hat"]


def compute_cf_struggle_scores(
    struggle_df: pd.DataFrame,
    threshold: float = 0.6,
    k: int = 3,
) -> tuple[pd.Series, dict]:
    """
    Collaborative filtering layer: identify students behaviourally similar
    to those flagged by the parametric model.

    Returns (cf_scores Series, diagnostics dict).
    """
    diagnostics: dict = {
        "threshold": threshold,
        "k": k,
        "n_flagged_parametric": 0,
        "n_elevated_cf": 0,
        "elevated_students": [],
        "fallback": False,
    }

    try:
        n_students = len(struggle_df)
        if n_students < 4:
            diagnostics["fallback"] = True
            diagnostics["reason"] = "fewer than 4 students"
            return struggle_df["struggle_score"].copy(), diagnostics

        # Interaction matrix from normalised features
        X = struggle_df[CF_FEATURES].values

        # Pairwise cosine similarity
        W = cosine_similarity(X)

        # Binary help-need labels from parametric scores
        h = (struggle_df["struggle_score"].values >= threshold).astype(float)
        diagnostics["n_flagged_parametric"] = int(h.sum())

        if diagnostics["n_flagged_parametric"] == 0:
            diagnostics["fallback"] = True
            diagnostics["reason"] = "no students above threshold"
            return struggle_df["struggle_score"].copy(), diagnostics

        cf_scores = np.copy(h)
        users = struggle_df["user"].values
        elevated = []

        for i in range(n_students):
            if h[i] == 1.0:
                continue

            sims = W[i].copy()
            sims[i] = -1.0  # exclude self

            neighbour_idx = np.argsort(sims)[-k:][::-1]

            weights = sims[neighbour_idx]
            positive_mask = weights > 0
            if positive_mask.any():
                w_pos = weights[positive_mask]
                h_pos = h[neighbour_idx[positive_mask]]
                cf_scores[i] = float(np.dot(w_pos, h_pos) / w_pos.sum())
            else:
                cf_scores[i] = 0.0

            if cf_scores[i] > 0:
                elevated.append({
                    "Student": users[i],
                    "Parametric Score": round(float(struggle_df.iloc[i]["struggle_score"]), 3),
                    "CF Score": round(cf_scores[i], 3),
                    "Nearest Neighbours": ", ".join(
                        users[neighbour_idx].tolist()
                    ),
                })

        diagnostics["n_elevated_cf"] = len(elevated)
        diagnostics["elevated_students"] = sorted(
            elevated, key=lambda x: x["CF Score"], reverse=True
        )

        return pd.Series(cf_scores, index=struggle_df.index), diagnostics

    except Exception as e:
        diagnostics["fallback"] = True
        diagnostics["error"] = str(e)
        return struggle_df["struggle_score"].copy(), diagnostics


def get_similar_students(
    student_id: str,
    struggle_df: pd.DataFrame,
    k: int = 5,
) -> pd.DataFrame | None:
    """
    Return the k most similar students to *student_id* based on cosine
    similarity over the CF feature set.

    Returns a DataFrame with columns: Student, Similarity, Struggle Score,
    Struggle Level — sorted by similarity descending.  Returns None on error
    or if the student is not found.
    """
    try:
        if len(struggle_df) < 2:
            return None

        idx_match = struggle_df.index[struggle_df["user"] == student_id]
        if len(idx_match) == 0:
            return None

        X = struggle_df[CF_FEATURES].values
        W = cosine_similarity(X)

        pos = struggle_df.index.get_loc(idx_match[0])
        sims = W[pos].copy()
        sims[pos] = -1.0  # exclude self

        top_k = min(k, len(struggle_df) - 1)
        neighbour_idx = np.argsort(sims)[-top_k:][::-1]

        rows = []
        for ni in neighbour_idx:
            row = struggle_df.iloc[ni]
            rows.append({
                "Student": row["user"],
                "Similarity": round(float(sims[ni]), 3),
                "Struggle Score": round(float(row["struggle_score"]), 3),
                "Struggle Level": row["struggle_level"],
            })

        return pd.DataFrame(rows)
    except Exception:
        return None


# -----------------------------------------------------------------
# Question Difficulty Score
# -----------------------------------------------------------------

def compute_question_difficulty_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute difficulty scores for all questions in the DataFrame.
    Returns a DataFrame with one row per question.
    """
    if df.empty:
        return pd.DataFrame(columns=[
            "question", "total_attempts", "unique_students", "avg_attempts",
            "c_tilde", "t_tilde", "a_tilde", "f_tilde", "p_tilde",
            "difficulty_score", "difficulty_level", "difficulty_color",
            "incorrect_rate_pct",
        ])

    work = df.copy()
    if "incorrectness" not in work.columns:
        work["incorrectness"] = compute_incorrectness_column(work)

    rows = []
    grouped = work.groupby("question")

    for question, group in grouped:
        total_attempts = len(group)
        unique_students = group["user"].nunique()

        # c_tilde: incorrect rate
        correct_count = (group["incorrectness"] < config.CORRECT_THRESHOLD).sum()
        c_tilde = 1.0 - (correct_count / total_attempts) if total_attempts > 0 else 0.0

        # t_raw: avg time per student (all students; 1-attempt students contribute 0)
        time_values = []
        for _user, user_group in group.groupby("user"):
            if len(user_group) >= 2:
                t_student = (
                    user_group["timestamp"].max() - user_group["timestamp"].min()
                ).total_seconds() / 60.0
            else:
                t_student = 0.0
            time_values.append(t_student)
        t_raw = np.mean(time_values) if time_values else 0.0

        # a_raw: avg attempts per student
        a_raw = total_attempts / unique_students if unique_students > 0 else 0.0

        # f_tilde: average incorrectness across all attempts
        f_tilde = group["incorrectness"].mean()

        # p_tilde: first-attempt failure rate
        first_attempts = group.sort_values("timestamp").groupby("user").first().reset_index()
        failed_first = (first_attempts["incorrectness"] >= config.CORRECT_THRESHOLD).sum()
        p_tilde = failed_first / unique_students if unique_students > 0 else 0.0

        rows.append({
            "question": question,
            "total_attempts": total_attempts,
            "unique_students": unique_students,
            "avg_attempts": round(a_raw, 2),
            "c_tilde": c_tilde,
            "t_raw": t_raw,
            "a_raw": a_raw,
            "f_tilde": f_tilde,
            "p_tilde": p_tilde,
        })

    result = pd.DataFrame(rows)

    # Min-max normalize t_raw and a_raw
    result["t_tilde"] = min_max_normalize(result["t_raw"])
    result["a_tilde"] = min_max_normalize(result["a_raw"])

    # Compute D_raw
    result["difficulty_score"] = (
        config.DIFFICULTY_WEIGHT_C * result["c_tilde"]
        + config.DIFFICULTY_WEIGHT_T * result["t_tilde"]
        + config.DIFFICULTY_WEIGHT_A * result["a_tilde"]
        + config.DIFFICULTY_WEIGHT_F * result["f_tilde"]
        + config.DIFFICULTY_WEIGHT_P * result["p_tilde"]
    ).clip(0.0, 1.0)

    # Classify
    levels_colors = result["difficulty_score"].apply(
        lambda s: classify_score(s, config.DIFFICULTY_THRESHOLDS)
    )
    result["difficulty_level"] = levels_colors.apply(lambda x: x[0])
    result["difficulty_color"] = levels_colors.apply(lambda x: x[1])

    # Convenience columns
    result["incorrect_rate_pct"] = (result["c_tilde"] * 100).round(1)

    # Sort descending by score
    result = result.sort_values("difficulty_score", ascending=False).reset_index(drop=True)

    return result


# -----------------------------------------------------------------
# Mistake Clustering
# -----------------------------------------------------------------

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

    cache_key = (question_id, total_wrong)
    if cache_key in _cluster_cache:
        return _cluster_cache[cache_key]

    unique_answers = wrong_df["student_answer"].unique().tolist()

    # Single unique answer — no point clustering
    if len(unique_answers) == 1:
        result = [{
            "label": "Common Wrong Answer",
            "count": total_wrong,
            "percent_of_wrong": 100.0,
            "example_answers": unique_answers[:config.CLUSTER_MAX_EXAMPLES],
        }]
        _cluster_cache[cache_key] = result
        return result

    # TF-IDF on deduplicated texts
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

    # Auto-select k via silhouette score
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

    # Map cluster assignment back to all (non-deduped) rows
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

        # Cosine similarity to centroid → pick most representative answers
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


# -----------------------------------------------------------------
# Temporal Smoothing (Stub — not actively used)
# -----------------------------------------------------------------

def apply_temporal_smoothing(
    s_raw: float,
    s_previous: Optional[float],
    alpha: float = config.SMOOTHING_ALPHA,
) -> float:
    """
    S_t = (1 - alpha) * S_previous + alpha * S_raw
    Returns s_raw if s_previous is None (first computation).
    """
    if s_previous is None:
        return s_raw
    return (1 - alpha) * s_previous + alpha * s_raw
