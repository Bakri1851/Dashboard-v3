# sound.py

**Path:** `code/learning_dashboard/sound.py`
**Folder:** [[learning_dashboard]]

> Sci-fi sound effects generated in the browser via the Web Audio API, injected through zero-height `st.components.v1.html()` iframes. No audio files, no libraries beyond the stdlib.

## Responsibilities

- Expose one `play_*()` function per event so any part of the app can fire a sound.
- Gate every playback on the `sounds_enabled` Streamlit session-state toggle (see [[config]] for the default).
- Inject a short JavaScript snippet per call that synthesises tones with `OscillatorNode` / `GainNode`, so nothing plays on page refresh alone.

## Key functions / classes

- `_sounds_enabled()` — reads `st.session_state.sounds_enabled`.
- `_play(js_body)` — private core that wraps a JS body in a hidden iframe.
- Event helpers: `play_session_start`, `play_session_end`, `play_selection`, `play_navigation`, `play_refresh`, `play_assistant_join`, `play_assignment_received`, `play_high_struggle`.

## Dependencies

- `streamlit.components.v1` only — no audio libraries, no external assets.
- Consumed by [[instructor_app]] (session start/end, refresh, assignment) and [[assistant_app]] (join, assignment received, high struggle).

## Related notes

- [[Setup and Runbook]] — browser autoplay caveat
