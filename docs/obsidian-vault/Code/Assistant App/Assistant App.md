# Assistant App

Mobile lab assistant portal running on port 8502 (`code/lab_app.py` → `assistant_app.main()`). Lets lab assistants join a session, receive student assignments, self-claim from a waiting list, and mark students as helped.

---

## Notes index

| Note | Folder | Summary |
|------|--------|---------|
| [[UI Flow]] | Flows | 4 assistant views (join, unassigned, assigned, session-ended), `?aid=` URL persistence, sound cues |
| [[App Entrypoint]] | Modules | `lab_app.py` → `assistant_app.main()`; join-flow routing (join → waiting → assigned) |
| [[Lab Assistant System]] | Modules | Join/assign/self-claim/mark-helped flows; file-locked `lab_session.json` schema |
| [[UI System]] | Modules | Mobile CSS (`get_mobile_css()`), 4 `render_*` functions, collapsed sidebar layout |
| [[Known Issues]] | Operations | Assistant data scope mismatch (loads data without instructor's session window) |
| [[Next Steps]] | Operations | Phase 0d–0e (assistant bug fixes), Phase 6 mobile refinement |
| [[RAG Architecture]] | Operations | Meeting 3 placeholder: SQL + ChromaDB hybrid RAG design (Dr. Batmaz) |

---

Part of [[Code Index]] · see also [[Lab App]]
