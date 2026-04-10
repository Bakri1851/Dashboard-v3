Part of [[Assistant App]] · [[UI Flow]]

# Assistant App — Join Session View

Shown when there is an active session but the assistant has no identity in the URL (the `?aid=` query param is absent or stale). This is the entry point for a new assistant or anyone whose session identity was lost.

Related: [[Lab Assistant System]], [[No Active Session]], [[Unassigned View]]

## What is displayed

- Heading: **"Lab Assistant"** with subtitle **"JOIN SESSION"**
- Optional info banner (populated by `_pop_join_notice()` — carries errors or messages from a previous join attempt)
- **Name** text input (max 40 characters)
- **Session Code** text input (max 6 characters, auto-uppercased client-side)
- **Join Session** button

## Behaviour on join

1. Validates name is non-empty and code is exactly `LAB_CODE_LENGTH` (6) characters.
2. Calls `lab_state.join_session(code, name)` which writes the assistant record to `lab_session.json`.
3. On success: sets `st.query_params["aid"] = <new_id>` and calls `st.rerun()` — transitions to [[Unassigned View]].
4. On failure: the error message is stored for the next render cycle via `_pop_join_notice()` and shown as a red banner.

## URL persistence

After joining, the `?aid=` param is set in the browser URL. Subsequent page refreshes (including auto-refresh) restore identity from this param without requiring the assistant to re-enter their name or code.

## Render function

`render_join_screen(lab_data)` in `code/learning_dashboard/assistant_app.py`

## Trigger condition

```python
assistant_id = st.query_params.get("aid")
if not assistant_id or assistant_id not in lab_data.get("lab_assistants", {}):
    render_join_screen(lab_data)
    st.stop()
```
