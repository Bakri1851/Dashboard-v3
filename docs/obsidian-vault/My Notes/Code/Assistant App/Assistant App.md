# Assistant App

Mobile lab assistant portal running on port 8502 (`code/lab_app.py` → `assistant_app.main()`). Lets lab assistants join a session, receive student assignments, self-claim from a waiting list, and mark students as helped.

---

## Notes index

| Note | Folder | Summary |
| --- | --- | --- |
| [[UI Flow]] | Flows | Overview of all 4 views, `?aid=` URL persistence, sound cues |
| [[No Active Session]] | Flows | No-session screen; auto-refreshes until instructor starts a session |
| [[Join Session]] | Flows | Name + code entry; `?aid=` param set on success |
| [[Unassigned View]] | Flows | Waiting state; available struggling students; optional self-allocation |
| [[Assigned View]] | Flows | Student card, top struggling questions, **Suggested Focus Areas** RAG panel, mark-helped and release actions |
| [[App Entrypoint]] | Modules | `lab_app.py` → `assistant_app.main()`; join-flow routing (join → waiting → assigned) |
| [[Lab Assistant System]] | Modules | Join/assign/self-claim/mark-helped flows; file-locked `lab_session.json` schema |
| [[UI System]] | Modules | Mobile CSS (`get_mobile_css()`), 4 `render_*` functions, collapsed sidebar layout |
| [[Known Issues]] | Operations | Assistant data scope mismatch (loads data without instructor's session window) |
| [[Next Steps]] | Operations | Phase 0d–0e (assistant bug fixes), Phase 6 mobile refinement |
| [[RAG Architecture]] | Operations | Dr. Batmaz's hybrid SQL + ChromaDB RAG design — **✅ Implemented** (Phase 9) |
| [[rag.py — RAG Engine and ChromaDB Interface]] | — | New module: ChromaDB collection build + GPT-4o-mini suggestion generation |
| [[Suggested Focus Areas Panel]] | — | UI block in assigned view; cache behaviour; privacy (NFR5) |

---

Part of [[Code Index]] · see also [[Lab App]]
