---
type: community
cohesion: 0.07
members: 31
---

# Lab Assistant App Flows

**Cohesion:** 0.07 - loosely connected
**Members:** 31 nodes

## Members
- [[aid= URL Query Param for Assistant Identity]] - document - CLAUDE.md
- [[Assistant App — Join Session Flow]] - document - docs/obsidian-vault/Code/Assistant App/Flows/Join Session.md
- [[Assistant App — No Active Session View]] - document - docs/obsidian-vault/Code/Assistant App/Flows/No Active Session.md
- [[Assistant App — UI Flow Overview]] - document - docs/obsidian-vault/Code/Assistant App/Flows/UI Flow.md
- [[Assistant App — Unassigned View Flow]] - document - docs/obsidian-vault/Code/Assistant App/Flows/Unassigned View.md
- [[Deferred Actions Pattern (pending_ flags)]] - document - CLAUDE.md
- [[Instructor Dashboard (app.py  instructor_app.py)]] - document - CLAUDE.md
- [[Known Issue Assistant data scope mismatch (no session window filter)]] - document - docs/obsidian-vault/Code/Assistant App/Operations/Known Issues.md
- [[Known Issue Name collision on assistant rejoin (stale assigned_student)]] - document - docs/obsidian-vault/Code/Assistant App/Operations/Next Steps.md
- [[Lab App — Live Assistant Assignment Flow]] - document - docs/obsidian-vault/Code/Lab App/Flows/Live Assistant Assignment.md
- [[Lab App — Saved Session History Flow]] - document - docs/obsidian-vault/Code/Lab App/Flows/Saved Session History.md
- [[Lab Assistant App (lab_app.py  assistant_app.py)]] - document - CLAUDE.md
- [[Lab Assistant System Module]] - document - docs/obsidian-vault/Code/Assistant App/Modules/Lab Assistant System.md
- [[Phase 11 In-app Help System (Assistant App)]] - document - docs/obsidian-vault/Code/Assistant App/Operations/Next Steps.md
- [[Plotly Dependency]] - document - code/requirements.txt
- [[Rationale aid= URL param for assistant identity persistence across phone refreshes]] - document - docs/obsidian-vault/Code/Assistant App/Flows/Join Session.md
- [[Rationale Deferred actions pattern due to Streamlit widget-state constraints]] - document - CLAUDE.md
- [[Rationale File-lock JSON as IPC between two Streamlit processes]] - document - CLAUDE.md
- [[Rationale Thin wrapper entry points for stable launch commands]] - document - docs/obsidian-vault/Code/Assistant App/Modules/App Entrypoint.md
- [[Retroactive Session Save Feature]] - document - docs/obsidian-vault/Code/Lab App/Flows/Saved Session History.md
- [[Saved Sessions (datasaved_sessions.json)]] - document - CLAUDE.md
- [[Self-allocation Feature (allow_self_allocation toggle)]] - document - docs/obsidian-vault/Code/Lab App/Flows/Live Assistant Assignment.md
- [[Session Code (6-char alphanumeric)]] - document - CLAUDE.md
- [[Shared State File (datalab_session.json)]] - document - CLAUDE.md
- [[Streamlit Framework Dependency]] - document - code/requirements.txt
- [[_normalize_state() — Consistency Repair on Every Read]] - document - docs/obsidian-vault/Code/Assistant App/Modules/Lab Assistant System.md
- [[data_loader.py — API Fetch and Persistence]] - document - CLAUDE.md
- [[filelock Dependency]] - document - code/requirements.txt
- [[lab_state.py — File-locked State Manager]] - document - CLAUDE.md
- [[paths.py — Runtime Paths and Migration]] - document - CLAUDE.md
- [[uiviews.py — Page-Level Views]] - document - CLAUDE.md

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Lab_Assistant_App_Flows
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Advanced Features & RAG Design]]

## Top bridge nodes
- [[Instructor Dashboard (app.py  instructor_app.py)]] - degree 6, connects to 1 community
- [[Assistant App — UI Flow Overview]] - degree 4, connects to 1 community