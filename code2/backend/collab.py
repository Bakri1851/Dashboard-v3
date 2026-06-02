# collab.py — collaborative-filtering struggle detection (CF layer over the baseline).

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


CF_FEATURES = ["n_hat", "t_hat", "i_norm", "A_norm", "d_hat"]


def compute_cf_struggle_scores(
    struggle_df: pd.DataFrame,
    threshold: float = 0.7,
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

        missing = [c for c in CF_FEATURES if c not in struggle_df.columns]
        if missing:
            diagnostics["fallback"] = True
            diagnostics["reason"] = f"missing baseline feature columns: {missing}"
            return struggle_df["struggle_score"].copy(), diagnostics

        X = np.nan_to_num(struggle_df[CF_FEATURES].values, nan=0.0)

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

        X = np.nan_to_num(struggle_df[CF_FEATURES].values, nan=0.0)
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
