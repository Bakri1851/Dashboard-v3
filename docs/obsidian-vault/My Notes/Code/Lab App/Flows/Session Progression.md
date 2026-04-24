# Session Progression

Retrospective view showing how the class's struggle distribution evolved across a session. Complements the live In-Class view by answering "when did this start?" rather than "who is struggling now?".

Related: [[Pages and UI Flow]] · [[Saved Session History]] · [[code2-frontend-views-session-progression]] · [[Student Struggle Logic]]

## Entry points

- Sidebar entry within the instructor React SPA (9th view after Phase 11).
- Link from Saved Sessions: selecting a historical session and clicking "Replay progression" takes the user here with the session ID pre-loaded.

## Flow

1. View mounts with a `sessionId`.
2. Request sent to `GET /api/sessions/{sessionId}/progression?buckets=20`.
3. Backend replays that session's submissions in time buckets, classifying each student's struggle level at the end of each bucket.
4. Frontend draws a stacked-area chart of `On Track / Minor Issues / Struggling / Needs Help` counts across time.
5. Scrubber picks a bucket; the "at this point" card shows struggle mean + top strugglers at that moment.
6. Clicking a student name navigates to their Student Detail view (preserving session context).

## Why this view exists

Real-time dashboards excel at "now" but elide temporal structure. For debrief and lesson-adjustment purposes the instructor needs to know whether a concept was understood early and lost, or never clicked in the first place. Session Progression surfaces that without requiring the instructor to scrub through raw submission logs.

## Related endpoints

- `GET /api/sessions/{id}/progression?buckets=N` — primary data source
- `GET /api/sessions` — list saved sessions, feeds the entry-point picker

## Code references

- View: `code2/frontend/src/views/SessionProgression.tsx`
- Endpoint: `code2/backend/routers/sessions.py:get_session_progression`
- Types: `code2/frontend/src/types/api.ts:SessionProgression`
