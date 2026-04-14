---
tags: [rag, phase9]
status: ✅ Implemented
date: 2026-04-14
---

# Phase 9: RAG Pipeline — How Suggested Feedback Works

A plain-language walkthrough of what happens between clicking into a question (or a student) and seeing the bullet-point suggestions render. This is the conceptual companion to the two feature-specific notes:

- [[Phase 9 RAG Suggested Feedback for Question Clusters]] — instructor side
- [[Phase 9 RAG Suggested Feedback for Lab Assistants]] — assistant side
- [[Phase 9 Testing Guide — RAG Suggested Feedback]] — manual test checklist

---

## Purpose

Asking GPT "how should I teach this topic?" gives generic textbook advice. **Retrieval-Augmented Generation (RAG)** grounds the prompt in *what real students in this session actually wrote*, so the suggestions speak to the misconceptions really present in your classroom, not hypothetical ones. The pipeline is the same for both UI surfaces — only the retrieval filter and the generation audience differ.

---

## The three stages

### 1. Build the vector store

Entry point: `build_rag_collection(df, session_id)` — [rag.py:68](../../code/learning_dashboard/rag.py).

- Walks every row of the session DataFrame (every submission from every student across every question).
- Concatenates each row into one document string: `"{question} | {student_answer} | {ai_feedback}"`.
- Passes the full batch through the `sentence-transformers` model **`all-MiniLM-L6-v2`** — a small local model (≈90 MB) that turns each document into a 384-dimensional vector capturing meaning, not keywords.
- Upserts vectors + metadata (`student_id`, `question`, `incorrectness`) into a **ChromaDB** collection named `session_<session_code>`, persisted to `paths.rag_chroma_dir()`.
- A rebuild guard caches the collection against `(session_id, row_count)` so the 5-second auto-refresh doesn't re-embed everything every tick.

### 2. Retrieve semantically similar past submissions

```python
collection.query(
    query_texts=[query_text],
    n_results=RAG_SUGGESTION_MAX_RESULTS,   # 5
    where={"question": question_id},        # or {"student_id": student_id}
)
```

Instructor side — [rag.py:317](../../code/learning_dashboard/rag.py). Assistant side uses the same query shape with a different `where` filter.

- `query_text` is built from the thing currently in focus (the question + top cluster's example answer, or the student's worst AI feedback).
- Chroma re-embeds `query_text` with the same local model, then returns the **top-5 most semantically similar submissions** *within the metadata filter*.
- The retrieval pool is always the current session — no external corpus, no cross-session bleed.

### 3. Generate with GPT-4o-mini

[rag.py:334-357](../../code/learning_dashboard/rag.py).

The OpenAI call receives:

- **System prompt** — fixes the audience (instructor advising a class, or assistant coaching a single student) and the style (practical, concise).
- **User prompt** — the cluster summary or struggle context, plus the retrieved snippets, and an instruction to return 2–3 bullets of ≤15 words each.
- `temperature=0` — deterministic output.
- `response_format={"type": "json_object"}` — forces a parseable dict.

`_extract_bullets()` pulls the bullet list out of whatever key name GPT chose, caps it at 3, and the view renders them under the appropriate heading.

---

## Instructor vs student variants

| | **Question-cluster feedback** | **Student focus-area feedback** |
|---|---|---|
| Function | `generate_cluster_suggestions` | `generate_assistant_suggestions` |
| Where the bullets render | Instructor question-detail view, under Mistake Clusters | Lab assistant app, under the assigned student |
| Retrieval filter | `where={"question": question_id}` | `where={"student_id": student_id}` |
| Query text | question ID + top cluster example | that student's latest AI feedback on their worst question |
| Prompt audience | "advising an instructor" — class-wide teaching adjustments | "advising a lab assistant" — 1-on-1 checks to run |
| Cache key | `question_id` in `_cluster_suggestion_cache` | `student_id` in `_suggestion_cache` |
| Output | 2–3 bullets on misconception → corrective feedback | 2–3 bullets on what to check or discuss |

Both share the same Chroma collection, built once per session.

---

## Why this is RAG, not plain GPT

If the prompt were just "here's question 12 NOT NULL, what should I teach?", GPT would produce recycled generic advice about nullability. With RAG, the prompt actually contains sentences like *"SELECT * FROM emp WHERE dept_id IS NULL"* — the specific wrong answer five students gave today. The LLM's job shifts from guessing what students might be confused about to diagnosing what this cohort is actually confused about. That's the "augmented" in Retrieval-Augmented Generation.

---

## Connections

- [[RAG Architecture — Hybrid SQL+ChromaDB Design]] — the two-layer filter pattern (pandas pre-filter + Chroma metadata filter) both functions use.
- [[OpenAI SDK Dependency]] — the shared `_get_openai_client()` helper.
- [[Phase 9 RAG Suggested Feedback for Question Clusters]] — instructor-side reference (caching, prompt template, reconstruction checklist).
- [[Phase 9 RAG Suggested Feedback for Lab Assistants]] — assistant-side feature note.
- [[Phase 9 Testing Guide — RAG Suggested Feedback]] — manual verification steps.
