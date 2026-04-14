---
tags: [testing, assistant-app, rag, phase9]
status: ✅ Implemented
date: 2026-04-14
---

# Phase 9 Testing Guide — RAG Suggested Feedback

Step-by-step instructions for manually verifying the Phase 9 RAG pipeline end-to-end. See [[Suggested Focus Areas Panel]] for what the feature looks like, and [[RAG Pipeline - Two-Layer Retrieval]] for the architecture.

---

## Prerequisites

```bash
# From repo root (Dashboard v3/)
pip install -r code/requirements.txt   # installs chromadb + sentence-transformers
```

Confirm both new packages installed:

```bash
python -c "import chromadb; from sentence_transformers import SentenceTransformer; print('OK')"
```

You also need `OPENAI_API_KEY` in `.streamlit/secrets.toml` for the generation step.

---

## Start both apps

```bash
# Terminal 1 — instructor dashboard
python -m streamlit run code/app.py

# Terminal 2 — lab assistant portal
streamlit run code/lab_app.py --server.port 8502
```

---

## Test 1 — Suggestions appear on assignment

1. In the instructor app, start a lab session (sidebar → "Start Lab Session").
2. In the assistant app (port 8502), join with the session code and your name.
3. In the instructor app, assign a **struggling student** who has ≥ 2 submissions.
4. In the assistant app, the assigned-student card should show:
   - A **"Generating suggestions…"** spinner briefly (first call only — model download ~30 s on a fresh machine)
   - Then a **"Suggested Focus Areas"** heading with 2–3 bullet points beneath it
   - The bullets should relate to the student's actual wrong answers, not generic tips

**Expected:** bullets appear above the `---` separator and the "Top Struggling Questions" panel.

---

## Test 2 — No re-call on auto-refresh

Add a temporary debug print to confirm caching works.

In `code/learning_dashboard/rag.py`, find `generate_assistant_suggestions` and add after the cache-hit check:

```python
if student_id in _suggestion_cache:
    print(f"[rag] cache hit for {student_id}")
    return _suggestion_cache[student_id]
```

Then watch the assistant app terminal over 6 auto-refresh cycles (5 s each, ~30 s total).

**Expected:** `[rag] cache hit for <student_id>` printed 5 times; no OpenAI call logged after the first.

Remove the print when done.

---

## Test 3 — "Not enough data yet" for low-data students

1. Find (or simulate) a student with exactly 1 submission.
2. Have the instructor assign that student to the assistant.
3. In the assistant app, look at the student card.

**Expected:** "Suggested Focus Areas" heading appears with `"Not enough data yet"` caption below it. No spinner, no OpenAI call.

---

## Test 4 — Different suggestions per student

1. Assign student A (note their bullets).
2. Release student A from the instructor sidebar.
3. Assign student B (different question history).

**Expected:** student B's bullets are distinct from A's — grounded in B's own submission history, not A's.

---

## Test 5 — Graceful degradation (missing deps)

In a throwaway terminal, uninstall the RAG deps:

```bash
pip uninstall chromadb sentence-transformers -y
```

Restart the assistant app and assign a student.

**Expected:**
- No traceback in the console (one-time warning log only)
- The assistant card renders normally — student card, top-3 questions, mark-helped button all present
- "Suggested Focus Areas" block is simply absent — no error message shown

Reinstall afterwards:

```bash
pip install chromadb>=0.4.0 sentence-transformers>=2.2.0
```

---

## Test 6 — Cache clears on session change

1. Start a session, assign a student, confirm bullets appear.
2. End the session from the instructor app.
3. Start a new session with a different session code.
4. Join as assistant, get assigned the same student ID.

**Expected:** suggestions regenerate (new OpenAI call + spinner) — stale bullets from the old session are not shown.

> **Fix note (2026-04-14):** before this date the cache was keyed on the non-existent `lab_data["session_id"]`, so it always resolved to `""` and this test silently no-op'd (cache hit, no regeneration). The fix switched the key to `session_code` in `assistant_app.py` and `session_code` / `loaded_session_id` in `views.py`. If you are running the test on an older commit the "Expected" above will not hold.

---

## Test 7 — ChromaDB directory created

After test 1 completes, confirm the on-disk store exists:

```bash
ls data/rag_chroma/
```

**Expected:** directory exists and contains ChromaDB's internal files (SQLite `.db` and/or parquet files).

---

## Test 8 — Privacy check (NFR5)

Add a temporary print inside `generate_assistant_suggestions` just before the OpenAI call:

```python
print(f"[rag] prompt user context:\n{user_msg}")
```

Assign student A and inspect the printed prompt.

**Expected:** only student A's submissions appear in the prompt. No other student IDs, answers, or feedback visible. This is enforced by:
- Layer 1: `df[df["user"] == student_id]` (only A's rows enter the pipeline)
- Layer 2: `where={"student_id": student_id}` (ChromaDB only returns A's chunks)

Remove the print when done.

---

## Test 9 — Syntax check

```bash
python -m py_compile \
  code/app.py \
  code/lab_app.py \
  code/learning_dashboard/rag.py \
  code/learning_dashboard/assistant_app.py \
  code/learning_dashboard/ui/views.py \
  code/learning_dashboard/config.py \
  code/learning_dashboard/paths.py
```

**Expected:** no output (zero errors).

---

## Instructor-side RAG (question clusters)

See [[Phase 9 RAG Suggested Feedback for Question Clusters]] for the feature overview. The tests below cover the parallel pipeline wired into `question_detail_view`.

### Test 10 — Teaching feedback appears below clusters

1. Start a lab session and load data with at least one question whose `wrong_count >= CLUSTER_MIN_WRONG`.
2. In the instructor app, open **Question Drill-Down** and click into that question.
3. Confirm the sequence below the header:
   - Mistake-cluster cards (existing `render_mistake_clusters`).
   - A short spinner: **"Generating teaching feedback…"**.
   - A purple uppercase heading **"SUGGESTED TEACHING FEEDBACK"**.
   - 2–3 bullets describing misconceptions + recommended follow-up.

**Expected:** bullets sit between the cluster cards and the `---` separator before the Students table. They should reference the clustered mistake patterns, not individual students.

---

### Test 11 — Cache per question

1. Open question A → bullets appear (spinner visible first call).
2. Back → open question B → new spinner, different bullets.
3. Back → re-open question A → **bullets appear instantly, no spinner** (cache hit).

**Expected:** each `question_id` triggers at most one OpenAI call per session.

---

### Test 12 — Low-wrong-count question skips RAG

1. Open a question with fewer than `CLUSTER_MIN_WRONG` wrong submissions.

**Expected:** the existing "Not enough incorrect answers to cluster…" info message shows. **No** "Suggested Teaching Feedback" heading, **no** spinner — the RAG block is gated behind the cluster branch and never fires.

---

### Test 13 — Cluster cache clears on session change

1. With a session active and question A's bullets cached, end the session.
2. Start a new session, load data, re-open question A.

**Expected:** spinner re-fires and bullets regenerate — the `_rag_cluster_session_id` guard invalidates both the module-level `_cluster_suggestion_cache` and `st.session_state["cached_cluster_suggestions"]`.

> **Fix note (2026-04-14):** shares the same key-mismatch bug as Test 6 prior to this date — see Test 6's fix note. The instructor path also gained `loaded_session_id` precedence, so switching between two **saved** sessions in "Previous Sessions" now also invalidates the cache.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| "Suggested Focus Areas" never appears, no spinner | `chromadb` or `sentence-transformers` not installed | `pip install chromadb sentence-transformers` |
| Spinner shows indefinitely | First-run model download (~90 MB, ~30 s) | Wait; subsequent runs are instant |
| Bullets look generic / wrong student | Old ChromaDB collection from a different session | End + restart session; cache clears automatically |
| OpenAI error in console | `OPENAI_API_KEY` missing or quota exceeded | Check `.streamlit/secrets.toml` |
| `data/rag_chroma/` permission error | Windows path with spaces | Run from repo root; `paths.rag_chroma_dir()` uses `pathlib.Path` which handles spaces |

---

## Related notes

- [[RAG Pipeline - Two-Layer Retrieval]] — pipeline architecture (Dr. Batmaz)
- [[rag.py — RAG Engine and ChromaDB Interface]] — implementation detail
- [[Suggested Focus Areas Panel]] — UI states and cache behaviour
- [[Phase 9 RAG Suggested Feedback for Question Clusters]] — instructor-side parallel feature
- [[Setup and Runbook]] — general app setup
