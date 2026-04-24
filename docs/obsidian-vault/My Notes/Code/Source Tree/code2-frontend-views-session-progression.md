# code2/frontend/src/views/SessionProgression.tsx

The 9th instructor view, added post-Phase-11. Replays a completed (or in-progress) session as a time-bucketed stacked-area chart of struggle levels, with a scrubber that moves through historical points. Lets an instructor see *when* the class tipped from "On Track" into "Struggling" rather than only the current snapshot.

Related: [[Session Progression]] · [[code2-frontend-animation]] · [[Student Struggle Logic]]

## Data source

Consumes `GET /api/sessions/{sessionId}/progression?buckets=20` (served by `code2/backend/routers/sessions.py:get_session_progression`). The endpoint replays the session in time buckets and returns, for each bucket:

- ISO timestamp at the end of the bucket
- `struggle_buckets`: counts per struggle level (`On Track`, `Minor Issues`, `Struggling`, `Needs Help`)
- Aggregate struggle mean / median at that point
- Per-student snapshot of top N most-struggling students

## Rendering

- `StackedArea` chart (`components/charts/StackedArea.tsx`) plots the four struggle levels across time with colours from `LEVEL_STYLES` in `theme/tokens.ts`.
- A scrubber / timeline slider selects a bucket; state `scrubIdx` drives a `LevelChips` summary and the students-list card.
- Animation variants from `animation/motion.ts` (`stagger`, `fadeUp`) fade cards in on mount.
- Clicking a student row in the "top N at this point" card routes to Student Detail via `viewStore.pickStudent()`.

## Design intent

The live In-Class view shows the current snapshot; Session Progression is the retrospective companion. The two together let an instructor answer "who is struggling *now*?" and "when did the struggle start?" — the latter being essential for post-session debrief and for identifying teaching moments to revisit.

## Code references

- `code2/frontend/src/views/SessionProgression.tsx` — view component
- `code2/backend/routers/sessions.py:124` — `get_session_progression` endpoint
- `code2/frontend/src/types/api.ts:SessionProgression` — response type
- `code2/frontend/src/components/charts/StackedArea.tsx` — chart primitive
