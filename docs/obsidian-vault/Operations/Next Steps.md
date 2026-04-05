# Next Steps

The next round of work should prioritise stabilising the current system before adding major new features. The highest-value improvements now come from making behavioural signals more reliable, ensuring assistant allocation works correctly, improving cache and refresh consistency, and tightening the distinction between student-level struggle and question-level difficulty.

Related: [[Known Issues]], [[Instructor Dashboard]], [[Lab Assistant System]], [[Analytics Engine]]

## Priority backlog

1. Fix and fully validate **send assistant help** logic
   - ensure assistant assignment is sent correctly
   - ensure the correct student/question/context is passed through
   - confirm assistant-side receipt and display
   - handle duplicate sends / failed sends cleanly
   - add visible status feedback in UI

2. Tighten **student struggle** analytics
   - verify current behavioural features are computed correctly
   - review retry rate, recent incorrectness, repetition rate, and trajectory logic
   - make sure struggle reflects short-term lab difficulty rather than long-run ability
   - activate or properly integrate temporal smoothing if it improves stability

3. Tighten **task difficulty** analytics
   - ensure question-level metrics are clearly separate from student-level struggle
   - review failure rate, average attempts, average time, and first-attempt failure logic
   - make sure difficult questions are identified at class level rather than from isolated student behaviour

4. Improve **cache / refresh correctness**
   - verify analytics refreshes are consistent across reloads
   - ensure stale cached results do not survive when source data changes
   - check whether clustering / scoring / assistant state is recomputed when needed
   - make refresh behaviour predictable in live lab use

5. Improve **UI semantics**
   - make labels clearer: struggling student vs difficult question
   - ensure rankings, colours, and badges mean exactly what users think they mean
   - reduce ambiguity around “needs help”, “difficult”, “assigned”, and “resolved”
   - improve confidence in what instructors are seeing without clutter

6. Add **model version / analytics mode switch**
   - preserve current scoring as baseline
   - allow later comparison against improved models without replacing baseline immediately
   - keep this lightweight for now

7. Build **evaluation / diagnostics support**
   - compare stability of current struggle and difficulty scores over time
   - inspect false positives / false negatives manually
   - create a simple diagnostics page or hidden developer view if needed

## Modelling backlog

### Near-term
- calibrate AI-derived incorrectness / correctness signal
- formalise post-parse feature tables for student-session and question-session analytics
- make temporal smoothing a deliberate modelling choice rather than a stub

### Mid-term
- add a more principled **difficulty model** (likely IRT-based)
- add a stronger **struggle model** using behavioural and temporal signals
- keep collaborative filtering as an alternative / secondary signal rather than the main one

### Later
- add skill tagging / concept mapping if knowledge tracing is introduced
- explore BKT / KT as an additional mastery signal
- improve misconception clustering if it gives useful instructor-facing value

## Documentation follow-up

- update docs to reflect the distinction between:
  - student struggle
  - task difficulty
  - assistant allocation
  - alternative recommendation / similarity methods
- document exactly how each behavioural feature is computed
- document refresh / cache behaviour
- document expected assistant assignment flow end-to-end
- keep literature review and modelling documentation aligned with the implemented analytics
- add a short “baseline vs improved models” note once alternative models are introduced

## Code references

- analytics engine / scoring logic
- refresh + cache flow
- assistant assignment / send-help logic
- instructor dashboard views
- question and student ranking components
- clustering / alternative recommendation logic