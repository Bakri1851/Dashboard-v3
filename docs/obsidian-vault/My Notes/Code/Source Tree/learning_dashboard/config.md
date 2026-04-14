# config.py

**Path:** `code/learning_dashboard/config.py`
**Folder:** [[learning_dashboard]]

> Single source of truth for every tunable constant in the project. Start here for parameter changes.

## Responsibilities

- Hold all scoring weights, thresholds, API settings, UI limits, feature-flag defaults, and the project colour palette.
- Define the `list[tuple[float, float, str, str]]` threshold tables used for dynamic classification (struggle and difficulty bands).
- Expose feature-flag defaults for the improved models (IRT, BKT, improved struggle) and the RAG pipeline.

## Key constants

- **API:** `API_URL`, `API_TIMEOUT`, `CACHE_TTL`
- **Data cleaning:** `EXCLUDED_MODULES`, `MODULE_RENAME_MAP`
- **Baseline struggle weights:** `STRUGGLE_WEIGHT_N/T/I/R/A/D/REP` — sum to 1.00
- **Baseline difficulty weights:** `DIFFICULTY_WEIGHT_C/T/A/F/P`
- **Recent-incorrectness decay:** `DECAY_HALFLIFE_SECONDS = 1800`
- **Bayesian shrinkage:** `SHRINKAGE_K = 5`
- **Thresholds:** `STRUGGLE_THRESHOLDS`, `DIFFICULTY_THRESHOLDS`, `IRT_DIFFICULTY_THRESHOLDS`
- **BKT params:** `BKT_P_INIT`, `BKT_P_LEARN`, `BKT_P_GUESS`, `BKT_P_SLIP`, `BKT_MASTERY_THRESHOLD = 0.95`
- **Improved-struggle weights:** `BEHAVIORAL = 0.45`, `MASTERY_GAP = 0.30`, `DIFFICULTY_ADJ = 0.25`
- **RAG:** `RAG_EMBEDDING_MODEL = "all-MiniLM-L6-v2"`, `RAG_SUGGESTION_MAX_RESULTS = 5`
- **Feature flags:** `IMPROVED_MODELS_ENABLED_DEFAULT`, `IRT_ENABLED_DEFAULT`, `BKT_ENABLED_DEFAULT`, `IMPROVED_STRUGGLE_ENABLED_DEFAULT`, `RAG_ENABLED_DEFAULT`
- **Theme:** `COLORS`, `FONT_HEADING = "Orbitron"`, `FONT_BODY = "Share Tech Mono"`

## Dependencies

- No imports — pure data module.
- Imported by nearly every other module.

## Related notes

- [[Formulae and Equations]]
- [[Student Struggle Logic]] · [[Question Difficulty Logic]] · [[Improved Struggle Logic]]
- [[BKT Mastery Logic]] · [[IRT Difficulty Logic]]
