"""Throwaway: compare embedding + chat model combos on one real student.

Runs 4 configs and prints bullets side-by-side:
  - MiniLM (local)          + gpt-4o-mini
  - MiniLM (local)          + gpt-4o
  - text-embedding-3-small  + gpt-4o-mini
  - text-embedding-3-small  + gpt-4o

Delete when done — not part of the app.
"""
from __future__ import annotations

import json
import os
import sys
import time
import tomllib
from pathlib import Path

import requests

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "code"))

# Load OPENAI_API_KEY from .streamlit/secrets.toml so _get_openai_client works
secrets_path = ROOT / ".streamlit" / "secrets.toml"
if secrets_path.exists():
    with open(secrets_path, "rb") as f:
        os.environ["OPENAI_API_KEY"] = tomllib.load(f).get("OPENAI_API_KEY", "")

import chromadb
from openai import OpenAI
from sentence_transformers import SentenceTransformer

from learning_dashboard import config
from learning_dashboard.data_loader import (
    detect_format,
    normalize_and_clean,
    parse_json_response,
    parse_xml_response,
)

CLIENT = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def fetch_and_parse():
    raw = requests.get(config.API_URL, timeout=config.API_TIMEOUT).text
    fmt = detect_format(raw)
    records = parse_json_response(raw) if fmt == "json" else parse_xml_response(raw)
    df = normalize_and_clean(records)
    return df


def cheap_incorrectness(df):
    """Compute incorrectness only for the target student (single batched call).
    Fill rest with 0.5 since we only query one student anyway."""
    from learning_dashboard.analytics import _call_openai_batch
    unique = [t for t in df["ai_feedback"].astype(str).str.strip().unique() if t]
    # Batch all of them once (might be pricier if corpus is huge — cap it)
    unique = unique[:200]
    scores = {}
    BATCH = 20
    for i in range(0, len(unique), BATCH):
        chunk = unique[i:i+BATCH]
        vals = _call_openai_batch(chunk)
        scores.update(zip(chunk, vals))
    df = df.copy()
    df["incorrectness"] = df["ai_feedback"].astype(str).str.strip().map(
        lambda t: scores.get(t, 0.5)
    )
    return df


def pick_target_student(df):
    """Pick a student with >=5 submissions and >=1 non-empty ai_feedback."""
    counts = (
        df[df["ai_feedback"].astype(str).str.strip() != ""]
        .groupby("user")
        .size()
        .sort_values(ascending=False)
    )
    for uid, n in counts.items():
        if n >= 5:
            return uid, n
    return counts.index[0], counts.iloc[0]


def embed_minilm(docs):
    model = SentenceTransformer(config.RAG_EMBEDDING_MODEL)
    return model.encode(docs, show_progress_bar=False).tolist()


def embed_openai(docs):
    resp = CLIENT.embeddings.create(model="text-embedding-3-small", input=docs)
    return [d.embedding for d in resp.data]


def build_collection(df, session_id, embed_fn, suffix):
    client = chromadb.EphemeralClient()
    name = f"cmp_{session_id[:8]}_{suffix}"
    try:
        client.delete_collection(name=name)
    except Exception:
        pass
    coll = client.create_collection(name=name)

    ids, docs, metas = [], [], []
    for i, row in enumerate(df.itertuples(index=False)):
        q = getattr(row, "question", "") or ""
        a = getattr(row, "student_answer", "") or ""
        fb = getattr(row, "ai_feedback", "") or ""
        sid = getattr(row, "user", "") or ""
        inc = float(getattr(row, "incorrectness", 0.0) or 0.0)
        ids.append(f"{i}")
        docs.append(f"{q} | {a} | {fb}")
        metas.append({"student_id": str(sid), "question": str(q), "incorrectness": inc})

    if not docs:
        return None

    embeddings = embed_fn(docs)
    coll.upsert(ids=ids, embeddings=embeddings, documents=docs, metadatas=metas)
    return coll


def run_rag(df, student_id, coll, embed_fn, chat_model):
    sdf = df[df["user"] == student_id]
    top_q_series = (
        sdf.groupby("question")["incorrectness"].mean().sort_values(ascending=False)
    )
    top_q = top_q_series.index[0]
    top_rows = sdf[sdf["question"] == top_q].sort_values("timestamp", ascending=False)
    query_text = str(top_rows.iloc[0].get("ai_feedback", "") or "") or str(top_q)

    query_emb = embed_fn([query_text])[0]
    results = coll.query(
        query_embeddings=[query_emb],
        n_results=config.RAG_SUGGESTION_MAX_RESULTS,
        where={"student_id": str(student_id)},
    )
    retrieved_docs = results.get("documents", [[]])[0] or []
    retrieved_metas = results.get("metadatas", [[]])[0] or []
    paired = sorted(
        zip(retrieved_docs, retrieved_metas),
        key=lambda x: x[1].get("incorrectness", 0.0),
        reverse=True,
    )
    sorted_docs = [d for d, _ in paired]

    top3 = (
        sdf.groupby("question")["incorrectness"]
        .mean()
        .sort_values(ascending=False)
        .head(3)
    )
    top3_lines = "\n".join(f"  - {q}: {v:.0%} incorrect" for q, v in top3.items())
    snippets = "\n".join(f"  [{i+1}] {d}" for i, d in enumerate(sorted_docs))

    system_msg = (
        "You are advising a lab assistant on how to help a student. "
        "Be concise and practical."
    )
    user_msg = (
        f"Student struggle score: 0.70 (High)\n"
        f"Top questions by incorrectness:\n{top3_lines}\n\n"
        f"Retrieved Q&A snippets (worst first):\n{snippets}\n\n"
        "Return a JSON array of 2 or 3 short bullet strings (max 15 words each) "
        "on what to check or discuss with this student. No prose outside the array."
    )

    t0 = time.time()
    response = CLIENT.chat.completions.create(
        model=chat_model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    latency = time.time() - t0
    usage = response.usage
    raw = response.choices[0].message.content.strip()
    try:
        parsed = json.loads(raw)
    except Exception:
        return {"bullets": [raw], "latency": latency, "usage": usage}

    bullets = []
    if isinstance(parsed, dict):
        for v in parsed.values():
            if isinstance(v, list) and v:
                bullets = [str(x).strip() for x in v if str(x).strip()]
                break
        if not bullets:
            bullets = [str(v).strip() for v in parsed.values() if isinstance(v, str)]
    elif isinstance(parsed, list):
        bullets = [str(x).strip() for x in parsed]

    return {"bullets": bullets[:3], "latency": latency, "usage": usage}


def main():
    print(">> Fetching API data ...")
    df = fetch_and_parse()
    print(f"   {len(df)} rows, {df['user'].nunique()} students")

    print(">> Picking target student ...")
    student_id, n = pick_target_student(df)
    print(f"   student={student_id}  submissions={n}")

    print(">> Scoring incorrectness (OpenAI batch) ...")
    df = cheap_incorrectness(df)

    session_id = "cmp"

    print(">> Building MiniLM collection ...")
    coll_minilm = build_collection(df, session_id, embed_minilm, "minilm")
    print(">> Building OpenAI-embed collection ...")
    coll_openai = build_collection(df, session_id, embed_openai, "oai")

    configs = [
        ("MiniLM        + gpt-4o-mini", coll_minilm, embed_minilm, "gpt-4o-mini"),
        ("MiniLM        + gpt-4o     ", coll_minilm, embed_minilm, "gpt-4o"),
        ("OpenAI-embed  + gpt-4o-mini", coll_openai, embed_openai, "gpt-4o-mini"),
        ("OpenAI-embed  + gpt-4o     ", coll_openai, embed_openai, "gpt-4o"),
    ]

    print("\n" + "=" * 80)
    print(f"STUDENT: {student_id}  ({n} submissions)")
    print("=" * 80)
    for label, coll, emb, chat in configs:
        print(f"\n--- {label} ---")
        out = run_rag(df, student_id, coll, emb, chat)
        for b in out["bullets"]:
            print(f"  • {b}")
        print(f"  [latency {out['latency']:.2f}s  tokens in={out['usage'].prompt_tokens} out={out['usage'].completion_tokens}]")


if __name__ == "__main__":
    main()
