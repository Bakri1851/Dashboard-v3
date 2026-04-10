Part of [[Assistant App]] · [[UI Flow]]

# Assistant App — No Active Session View

Shown when the shared lab session is inactive (i.e. `lab_data.get("session_active")` is falsy). This is the first screen any assistant sees if they open the app before the instructor has started a session.

Related: [[Lab Assistant System]], [[Join Session]]

## What is displayed

- Centred heading: **"Lab Assistant Portal"**
- Subheading in red: **"No Active Session"**
- Instruction text: "Ask your instructor to start a lab session, then refresh this page."
- No interactive elements or buttons.

## Behaviour

- The app continues its 5-second auto-refresh cycle, so the view transitions automatically to [[Join Session]] as soon as the instructor starts a session — no manual refresh needed.
- No state is read from the URL at this point; the `?aid=` param is ignored until a session is active.

## Render function

`render_session_ended()` in `code/learning_dashboard/assistant_app.py`

## Trigger condition

```python
if not lab_data.get("session_active"):
    render_session_ended()
    st_autorefresh(...)
    st.stop()
```
