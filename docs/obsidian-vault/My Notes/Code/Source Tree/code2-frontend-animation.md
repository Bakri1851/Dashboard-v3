# code2/frontend/src/animation/

Framer-motion-based animation primitives for the React SPA. Introduced during post-Phase-11 polish (commit `5ea4d21`) and reused across views to keep the dashboard legible during live data refreshes rather than flashing content in and out.

Related: [[code2-frontend-views-session-progression]] · [[Session Progression]] · [[Streamlit vs React Parity Audit]]

## Files

| File | Role |
|------|------|
| `motion.ts` | Named variants and transitions consumed by every animated view: `viewTransition` (page enter/exit), `fadeUp` (card mount), `stagger` (child reveal), `scoreBarSpring` (ScoreBar tween), `rowLayoutSpring` (leaderboard reorder). Re-exports `useReducedMotion` from framer-motion so callers can honour the user's accessibility preference. |
| `AnimatedCard.tsx` | Thin `motion.div` wrapper that applies a `Variants` object and the shared card styling. Used by SessionProgression, StudentDetail, QuestionDetail, and ComparisonView to animate card mounts. |
| `ViewTransition.tsx` | Wraps a full page and applies `viewTransition` on mount/unmount. Used at the route boundary so navigating between the 9 sidebar views produces a consistent fade-up-and-stagger instead of a jump-cut. |

## Design intent

Animation is a presentation-layer concern and deliberately never touches analytics. All views still function with `useReducedMotion` honoured — transitions collapse to zero-duration and no layout shifts. This matches NFR2 (interpretability) by keeping the instructor's attention anchored on the data that is actually changing, rather than being distracted by abrupt leaderboard reorders.

## Code references

- `code2/frontend/src/animation/motion.ts` — variants + transitions
- `code2/frontend/src/animation/AnimatedCard.tsx` — card wrapper
- `code2/frontend/src/animation/ViewTransition.tsx` — page wrapper
- Consumers: `code2/frontend/src/views/SessionProgression.tsx`, `StudentDetail.tsx`, `QuestionDetail.tsx`, `ComparisonView.tsx`, `InClassView.tsx`
