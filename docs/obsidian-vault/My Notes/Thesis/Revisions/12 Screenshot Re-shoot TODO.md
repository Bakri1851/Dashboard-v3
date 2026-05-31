# 12 — Screenshot Re-shoot TODO (before submission)

Several deployed V2 views were changed *after* the current screenshots were captured, so the PNGs in `Report/figures/implementation/` — now displayed in Appendix B ([[02 Proposed Report Edits — structural]] / `appendix-sections/ui-screenshots.tex`) — are **stale and must be re-captured before submission**. ← [[00 Index]]

**How to update (no `.tex` change needed):** re-capture each view from the current deployed V2 UI and overwrite the PNG **keeping the same filename** in `Report/figures/implementation/`. Because Appendix B references the figures by filename + `\label`, dropping in the new image and recompiling updates everything automatically. Capture at a consistent resolution and theme, ideally from the 25COA122 cohort so the captions still hold.

## Known stale
- **Settings (`ui-settings.png`)** — ⚠️ confirmed stale. The deployed Settings card no longer matches this screenshot (e.g. the removed weight-version selector; layout changed). **Re-shoot.** *(This was already flagged in the original Appendix B stub TODO.)*

## Re-shoot / verify checklist
Tick once the screenshot matches the current deployed UI. Instructor views (Appendix B → *Instructor Dashboard (V2)*):
- [ ] `ui-inclass-basic.png` — In-Class, Basic layout
- [ ] `ui-inclass.png` — In-Class, Advanced layout
- [ ] `v2-inclass.png` — In-Class, scifi theme
- [ ] `ui-studentdetail.png` — Student Detail (Improved Models on)
- [ ] `ui-questiondetail.png` — Question Detail (clusters + RAG)
- [ ] `ui-dataanalysis.png` — Data Analysis (e.g. Activity-by-Week heatmap)
- [x] `ui-settings.png` — **Settings — re-shoot (stale)**
- [ ] `ui-previoussessions.png` — Previous Sessions
- [ ] `ui-progression.png` — Session Progression

Assistant views (Appendix B → *Lab Assistant (mobile)*):
- [ ] `asst-join.png` — join screen
- [ ] `asst-unassigned.png` — standby, self-allocation OFF
- [ ] `asst-unassigned2.png` — standby, self-allocation ON
- [ ] `asst-assigned.png` — assigned student card (mark-helped)
- [ ] `asst-dispatch.png` — instructor dispatch console

Kept inline (not in Appendix B) — also verify:
- [ ] `v2-live-session.png` — instructor sidebar during a live session (Implementation §4.6, `fig:session-live`)

## After re-shooting
- Confirm captions in `ui-screenshots.tex` still describe what the new image shows (e.g. if a panel was removed/renamed).
- Recompile (2 passes) and check Appendix B + the List of Figures render the updated images.
- If a view's *design rationale* also changed, reflect it in the relevant brief ([[03 Design Rationale & Missing Views]] for the Settings design statement).
