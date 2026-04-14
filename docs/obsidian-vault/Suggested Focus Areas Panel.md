---
tags: [assistant-app, ui, rag, phase9]
status: ✅ Implemented
date: 2026-04-14
---

# Suggested Focus Areas Panel

UI block in the assistant app's assigned-student card that surfaces 2–3 LLM-generated coaching bullets grounded in the student's submission history.

---

## Location

`code/learning_dashboard/assistant_app.py` — `render_assigned_view()`, inserted between the student card block and the "Top Struggling Questions" separator.

---

## Rendered states

| Condition | Display |
|---|---|
| ≥2 submissions + bullets generated | **Suggested Focus Areas** heading + `• bullet` lines |
| < 2 submissions (`RAG_MIN_SUBMISSIONS`) | **Suggested Focus Areas** heading + `"Not enough data yet"` caption |
| deps missing or LLM failed | Nothing (silent no-op — no error shown) |

---

## Cache behaviour

Suggestions are generated once per student assignment per session:

1. First render: calls `rag.generate_assistant_suggestions(...)` with a spinner
2. Result stored in `st.session_state["cached_suggestions"][student_id]`
3. All subsequent auto-refresh reruns hit the session state cache
4. On session change (`session_id` differs): `rag.clear_suggestion_cache()` + clear session state dict — next assignment regenerates fresh

---

## Privacy

The RAG pipeline enforces student-scoped retrieval at two layers:
- Layer 1: `df[df["user"] == student_id]` pandas filter
- Layer 2: `where={"student_id": student_id}` ChromaDB metadata filter

No other students' data appears in the OpenAI prompt. Satisfies NFR5.

---

## Related notes

- [[rag.py — RAG Engine and ChromaDB Interface]] — generation logic
- [[RAG Pipeline - Two-Layer Retrieval]] — pipeline detail
- [[Assistant App]] — parent app
