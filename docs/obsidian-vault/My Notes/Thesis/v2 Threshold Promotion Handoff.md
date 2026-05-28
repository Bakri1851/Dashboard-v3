---
phase: implementation-handoff
status: completed
completed: 2026-05-27
covers: promotion of constrained CV-trained band-thresholds to production
sibling-of: "[[v2 Relabel Handoff]]"
sibling-of-2: "[[v2 Target-Swap Handoff]]"
sibling-of-3: "[[v2 Threshold Training Handoff]]"
inputs:
  - data/eval/experiments/threshold_search_cv.json
  - scripts/experiments/threshold_search_constrained.py
created: 2026-05-27
---

# Handoff — Ship constrained CV-trained thresholds

> This handoff covers the **implementation pass**: code + notebook + config changes to promote the trained thresholds to production. Writing-chat work (§5.4.11 prose, §5.6 anti-result, cross-chapter touches) is covered by the sibling `[[v2 Threshold Training Handoff]]` doc.

## §0 Goal + scope

User has approved promoting the **constrained CV-trained band-thresholds** to production for 4 of 6 (model × score-space) combinations. Same shape as the earlier v2-weights and Optuna-hyperparams promotions. Test-folder analysis is complete; this handoff covers only the **promotion + propagation**, not re-analysis.

**Decision: default-only, no Settings UI toggle.** Reason: we removed the Model Comparison view this same session for being "evaluation, not production"; adding a threshold-comparison toggle would repeat that anti-pattern in miniature. Thresholds are a downstream label-display calibration (ranking is unchanged; only classification labels move), not a modelling choice in the way weights and CF τ are. Rollback path is `git revert` on the config commit plus a notebook rerun — same friction as any other backend default change.

**Ship for these 4 model sets** (the κ winners):

- Struggle baseline composite (v1 weights applied to features → [0,1] composite)
- Struggle v2 OLS (v2 weights → [0,3] band-index)
- Difficulty baseline composite ([0,1])
- Difficulty v2 OLS ([0,3])

**Do NOT ship for these 2 sets** (κ gain insufficient / negative):

- Struggle improved (BKT+IRT) — constrained Δκ = −0.002, indistinguishable from noise
- Difficulty IRT (Rasch scaled) — constrained κ remains negative (model–rater mismatch; gets a §5.6 anti-result write-up, no config change)

## §1 Authoritative values to ship

All values are mean across CV folds, per-fold std ≤ 0.03 throughout. Source: `data/eval/experiments/threshold_search_cv.json` (keys `*_constrained`).

**`[0, 1]` composite-score thresholds** (the values shown in Settings → Read-only config reference):

```python
# In code2/backend/config.py
STRUGGLE_THRESHOLDS = [
    (0.000, 0.315, 'On Track',     '#10a15d'),
    (0.315, 0.505, 'Minor Issues', '#ffcc00'),
    (0.505, 0.605, 'Struggling',   '#ff6600'),
    (0.605, 1.000, 'Needs Help',   '#ff2d55'),
]
# Prior hand-set: (0.0, 0.2, 0.35, 0.5, 1.0)

DIFFICULTY_THRESHOLDS = [
    (0.000, 0.363, 'Easy',      '#00ff88'),
    (0.363, 0.463, 'Medium',    '#ffcc00'),
    (0.463, 0.588, 'Hard',      '#ff6600'),
    (0.588, 1.000, 'Very Hard', '#ff2d55'),
]
# Prior hand-set: (0.0, 0.35, 0.5, 0.75, 1.0)
```

**`[0, 3]` band-index rounding cutpoints (for v2 OLS prediction → band)**:

```
Struggle v2 OLS:   c1=1.22, c2=1.78, c3=2.09   (replaces natural-round 0.5, 1.5, 2.5)
Difficulty v2 OLS: c1=1.88, c2=2.19, c3=2.69
```

The v2 OLS cutpoints are used **only in the evaluation notebook** for the confusion-matrix cell (helper `ols_pred_to_band()` in `notebooks/eval_main.ipynb` cell 24). They are not — currently — used by the deployed backend; see §2 pre-flight check.

## §2 Pre-flight checks (5 min before touching anything)

**Check A — v2-weights output scale**: when a user has `struggle_weights_version = "v2"` in Settings, what space does the backend's composite score live in? Inspect `code2/backend/cache.py` `load_struggle_df()` around lines 186–205. The v2 OLS weights were trained against `[0, 3]` band-index targets, so applying them to features `[0, 1]` could yield outputs in `[0, 3]` band-index space, NOT `[0, 1]`. If the dashboard then applies `STRUGGLE_THRESHOLDS` (defined for `[0, 1]`) to a `[0, 3]` score, every entity classifies as the top band — that would be a latent bug.

- If v2-weights output is already rescaled to `[0, 1]` before threshold application: no extra work — the single STRUGGLE_THRESHOLDS set serves both v1 and v2 weights.
- If v2-weights output is in `[0, 3]`: need to ALSO add a `STRUGGLE_V2_THRESHOLDS` set + a dispatch in `load_struggle_df` (or wherever the score-to-band mapping happens) keyed on `runtime_config.struggle_weights_version`. Same pattern for difficulty.

Same check for `difficulty_weights_version`. Report findings before proceeding; do not assume.

**Check B — `score_to_band()` / `ols_pred_to_band()` mirrors**: grep for `score_to_band` and `ols_pred_to_band` across `code2/`, `notebooks/`, and `scripts/` to find every consumer of the threshold values. All consumers must be updated together; don't leave one stale.

**Check C — current notebook state**: confirm `notebooks/eval_main.ipynb` and `notebooks/model_comparison.ipynb` execute cleanly against the current (pre-promotion) state. Run `jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=600 <nb>` on each and confirm exit 0. Establishes a known-good baseline before the change.

**Check D — git working tree**: `git status` should show only the in-flight session changes; nothing should be committed mid-promotion.

## §3 Implementation phases

Each phase ends in a runnable, self-consistent state. Stop and check before advancing.

### Phase 1 — Backend config (`code2/backend/config.py`)

Replace `STRUGGLE_THRESHOLDS` and `DIFFICULTY_THRESHOLDS` with the values in §1. Add a comment block above each citing the source:

```python
# Thresholds trained 2026-05-27 via constrained CV (κ-max grid search with
# c1 >= train-fold P5 and every band >= 10% of score range). See
# scripts/experiments/threshold_search_constrained.py and
# data/eval/experiments/threshold_search_cv.json. CV-validated linear-weighted
# Cohen's kappa improvement over the prior hand-set values:
#   struggle:   +0.303 -> +0.390  (delta +0.087, GroupKFold(5), n=1306)
#   difficulty: +0.065 -> +0.239  (delta +0.175, LeaveOneOut, n=72)
# Prior hand-set values retained in comments for rollback reference.
```

Verify: `python -m py_compile code2/backend/config.py` passes. `python -c "import sys; sys.path.insert(0, 'code2'); from backend import config; print(config.STRUGGLE_THRESHOLDS)"` shows the new values.

### Phase 2 — Backend score-to-band path (conditional on §2 Check A)

If check A revealed v2-weights output lives in `[0, 3]` band-index space, add:

```python
# In code2/backend/config.py — only if dispatch is needed
STRUGGLE_V2_OLS_BAND_CUTPOINTS   = (1.22, 1.78, 2.09)  # for [0,3] OLS predictions
DIFFICULTY_V2_OLS_BAND_CUTPOINTS = (1.88, 2.19, 2.69)
```

Plus a small helper in `code2/backend/cache.py` (or wherever the band mapping happens) that dispatches on `runtime_config.struggle_weights_version` and picks the right cutpoint set. Match the existing weight-version dispatch pattern in `load_struggle_df` for consistency.

If check A showed v2 outputs are rescaled to `[0, 1]`: skip this phase entirely; the single `STRUGGLE_THRESHOLDS` set serves both.

### Phase 3 — Eval notebook (`notebooks/eval_main.ipynb`)

Locate cell 24 (the `ols_pred_to_band()` helper). The current implementation uses `np.round` (natural cutpoints at 0.5, 1.5, 2.5). Replace with explicit cutpoint-based mapping that takes a tuple param so the helper can serve both struggle and difficulty:

```python
def ols_pred_to_band(pred: float, cutpoints: tuple = (0.5, 1.5, 2.5)) -> str:
    """Map continuous OLS prediction in [0, 3] band-index space to band label."""
    c1, c2, c3 = cutpoints
    if pred < c1: return STRUGGLE_BANDS[0]
    if pred < c2: return STRUGGLE_BANDS[1]
    if pred < c3: return STRUGGLE_BANDS[2]
    return STRUGGLE_BANDS[3]
```

Update the cell's call site to pass `(1.22, 1.78, 2.09)` for struggle confusion-matrix construction. Add a parallel call site for difficulty if cell 24 (or its sibling) handles difficulty v2 OLS.

Find every other call to `ols_pred_to_band` in the notebook and pass the appropriate cutpoint set. If a difficulty-v2 mapping doesn't exist yet, this might be a good moment to add one (consistency with the struggle path).

### Phase 4 — Model comparison notebook (`notebooks/model_comparison.ipynb`)

The notebook uses `score_to_band()` (defined in cell 4) which reads `STRUGGLE_THRESHOLDS` / `DIFFICULTY_THRESHOLDS` from `backend.config`. Since Phase 1 updated `config.py`, this notebook will pick up the new thresholds automatically on re-run. No code edits needed.

### Phase 5 — Re-run both notebooks

```bash
PYTHONIOENCODING=utf-8 python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=900 notebooks/eval_main.ipynb
PYTHONIOENCODING=utf-8 python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=600 notebooks/model_comparison.ipynb
```

Expected: both exit 0. `eval_main.ipynb` regenerates 15+ figures plus `data/eval/results.md`. `model_comparison.ipynb` regenerates 4 figures plus 2 pairs CSVs.

If MemoryError on import (Windows paging-file issue hit several times this session): retry, or run the notebooks individually with a 30 s pause between, or close other processes first.

### Phase 6 — Frontend (no source changes; verify auto-update)

The Settings → Advanced → Read-only config reference card in `code2/frontend/src/views/SettingsView.tsx` reads thresholds via `useSettings()` from the backend. No frontend source change needed — restart the backend and the card auto-displays the new values.

Manual verification: start the backend (`uvicorn backend.main:app --app-dir code2 --port 8000`), open `http://localhost:5173/settings`, switch to Advanced tab, confirm the Read-only config reference shows the new cutpoint values.

### Phase 7 — Vault sync (light touch)

Add a sync note to the top of any vault file that cites threshold values verbatim:

```
> 2026-05-27 evening — band thresholds promoted from hand-set to constrained CV-trained values.
> Struggle (0.0, 0.315, 0.505, 0.605, 1.0); difficulty (0.0, 0.363, 0.463, 0.588, 1.0).
> See `data/eval/experiments/threshold_search_cv.json` for full derivation.
```

Files most likely to need this:

- `docs/obsidian-vault/My Notes/Thesis/v2 Methodology Journal.md`
- `docs/obsidian-vault/My Notes/Thesis/Evaluation PoC Handoff.md`
- `docs/obsidian-vault/My Notes/Thesis/Evidence Bank.md`
- `docs/obsidian-vault/My Notes/Thesis/Figures and Tables.md`

`grep -rln "0\.2.*0\.35.*0\.5\|0\.35.*0\.5.*0\.75" docs/obsidian-vault/` will find them. Don't sweep prose-heavy notes that cite the values incidentally — only the source-of-truth ones.

Do NOT touch `Report/main-sections/*.tex` — that's the writing chat's job per `[[v2 Threshold Training Handoff]]`.

## §4 Verification (post-promotion)

1. **`config.py` py_compile**: passes (catches malformed tuples).
2. **Backend smoke**: `python -c "import sys; sys.path.insert(0, 'code2'); from backend.runtime_config import RuntimeConfig; rc = RuntimeConfig.defaults(); print(rc.struggle_weights_version, rc.difficulty_weights_version, rc.hyperparams_version)"` shows `v2 v2 v2` (sanity that the morning's v2-defaults promotion is intact).
3. **Frontend `tsc`**: `cd code2/frontend && npx tsc --noEmit` passes.
4. **Notebook re-run exit codes**: both 0.
5. **Figure spot-check** (visual): open `data/eval/figures/confusion_bands.png` — exact-band agreement % should be higher under the new thresholds. `data/eval/figures/model_disagreement.png` should look qualitatively different from the pre-promotion version.
6. **`results.md` numerical spot-check**: open `data/eval/results.md`, locate the exact-band agreement % and model-disagreement counts. Confirm they shifted (these are the numbers the writing chat will lift into §5.4.8 + §5.6.1 prose).
7. **Live dashboard**: start backend + Vite, open `/settings` → Advanced, confirm Read-only config reference shows new cutpoint values. Open `/inclass` and confirm leaderboard still renders (band label colours next to scores should match the new thresholds — qualitative check).

## §5 Rollback

Single-commit promotion makes rollback clean:

```bash
git revert <promotion-commit-sha>
PYTHONIOENCODING=utf-8 python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=900 notebooks/eval_main.ipynb
PYTHONIOENCODING=utf-8 python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=600 notebooks/model_comparison.ipynb
```

Notebooks regenerate against the reverted config; backend boot picks up reverted thresholds automatically.

## §6 Out of scope (do NOT do)

- **Report prose changes** in `Report/main-sections/*.tex` — separate writing chat owns §5.4.11 + §5.6 + cross-chapter touches. See `[[v2 Threshold Training Handoff]]` for that scope.
- **New Settings UI toggle** for v1-thresholds vs trained-thresholds — explicitly not wanted; one-way promotion only (rollback via git, not via UI). Decision rationale in §0.
- **3-band scheme collapse** — `On Track` and `Easy` band labels stay defined in the 4-band palette even though they'll appear empty on this cohort. Future-cohort generality.
- **Touching the test-folder analysis scripts** in `scripts/experiments/threshold_search*.py` — they stay put as reproducibility artefacts. Delete-safe via `rm -rf scripts/experiments/ data/eval/experiments/`.
- **Re-analysing or re-running the threshold search** — the values in §1 are final per user approval. Just propagate them.
- **Re-shooting the Appendix B Settings screenshot** — that's a writing-chat task too. Just confirm the UI displays the new values; the screenshot capture is end-of-thesis-prep work.

## §7 Order of operations (single-session execution)

1. Pre-flight checks A–D
2. Phase 1 — `config.py`
3. Phase 2 — backend dispatch (only if §2 Check A required it)
4. Phase 3 — `eval_main.ipynb` cell 24
5. Phase 4 — `model_comparison.ipynb` (no edits)
6. Phase 5 — re-run both notebooks
7. Phase 6 — frontend boot smoke
8. Phase 7 — vault sync notes
9. Verification §4

Expected wall-clock: 30–45 min including pre-flight + verification, assuming no surprises in §2 Check A. If A surfaces a v2-output-scale bug, add 15–30 min for the dispatch logic.

## §8 If anything breaks

- **Notebook MemoryError on import**: Windows paging-file issue hit ≥4× during the analysis session. Retry. If persistent, close all other processes / VS Code / browser tabs and retry.
- **κ doesn't improve in regenerated `results.md`**: most likely cause = backend v2-weights-output scale issue uncaught in §2 Check A. The notebook's confusion-matrix cell may be applying [0,1] thresholds to a [0,3] score. Re-verify Check A.
- **Frontend `tsc` fails after Phase 1**: unexpected — `config.py` is backend-only. Investigate; do not skip.
- **Live dashboard shows everyone in the same band**: same root cause as the κ-doesn't-improve case. Roll back, fix dispatch, retry.

## §9 Source-of-truth files

| File | Purpose |
|---|---|
| `data/eval/experiments/threshold_search_cv.json` | All trained cutpoints + per-fold detail |
| `scripts/experiments/threshold_search_constrained.py` | The script that generated the shipped values |
| `code2/backend/config.py` | Where the values land after promotion |
| `notebooks/eval_main.ipynb` cell 24 | Where `ols_pred_to_band` lives (Phase 3 target) |

## §10 What's been done already this session (for context)

The session that produced this handoff also delivered two unrelated-but-concurrent changes:

1. **v2 defaults promotion** — `struggle_weights_version`, `difficulty_weights_version`, `improved_struggle_weights_version`, `hyperparams_version` all default to `"v2"` on a fresh backend boot. V2InfoBlock evaluation prose stripped from `SettingsView.tsx`. Toggles retained.
2. **Model Comparison view removal** — `code2/frontend/src/views/ComparisonView.tsx`, `code2/backend/routers/models_cmp.py`, and 5 Pydantic / TypeScript schema types deleted. Analytics preserved in the new `notebooks/model_comparison.ipynb` (generated by `scripts/experiments/_nb_create_model_comparison.py`).

Neither affects this handoff's scope; both are listed only so the implementation chat knows the codebase state when it picks up.

End of handoff.
