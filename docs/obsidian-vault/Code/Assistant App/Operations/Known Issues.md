# Known Issues — Assistant App

Confirmed implementation gap for the assistant app. See also [[Lab App/Operations/Known Issues]] for instructor-side issues.

Related: [[Lab Assistant System]], [[Assistant App/Flows/UI Flow]]

## Confirmed issues

- Assistant data scope mismatch: the assistant app computes `struggle_df` from whatever `data_loader.load_data()` returns, without applying the instructor's active live-session window or loaded saved-session window. This means assistants can be shown students outside the instructor's current teaching scope. See [[Lab Assistant System]] and [[Data Pipeline]].

## Why this matters

- Assistants may be directed to help students who are outside the instructor's current teaching context.
- It blurs the boundary between live teaching scope and global live data, reducing the practical accuracy of assistant-side struggle scores.

## Notes on Phase 9 RAG

- **First-run model download (~90 MB, ~30 s):** `all-MiniLM-L6-v2` is fetched from Hugging Face on first use per machine. This blocks Streamlit for ~30 s on the very first assignment after a clean install. Subsequent runs use the local sentence-transformers cache and are instant. Note this in the dissertation deployment section.
- **Silent no-op when deps missing:** if `chromadb` or `sentence-transformers` are not installed, the "Suggested Focus Areas" panel is simply absent — no error shown, rest of the app unaffected. The lazy-import guard in `rag.py` logs a one-time warning to the console.

## Code references

- `code/learning_dashboard/assistant_app.py`: `_load_student_data()`
- `code/learning_dashboard/rag.py`: `_lazy_import()`, `clear_suggestion_cache()`
