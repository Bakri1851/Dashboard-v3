# Writing Roadmap

> [!info] **Self-contained handoff doc.** This file is designed to let any future chat pick up the thesis-writing work without losing context. Last updated 2026-05-04 after Ch2 restructure + Stage 1c + Stage 1b §2.2.2 + Stage 1b §2.3.2.
>
> Companions: [[Rewrite Queue]] (granular edits), [[Report Sync]] (code↔thesis mismatch table), [[Evidence Bank]] (eval evidence checklist), [[Figures and Tables]] (figure inventory), and `docs/obsidian-vault/My Notes/Literature/_import_checklist.md` (live import progress).

---

## Order of operations

| #   | Task                                | Status  | Notes                                                                                                                                                                                                                               |
| --- | ----------------------------------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Ch2 restructure                     | ✅       | Promoted thematic groups to subsections; old file preserved as `requirements-specification-old.tex`                                                                                                                                 |
| 2   | Stage 1c §2.2.1 struggle paragraphs | ✅       | Composite indicators, time-decay, Bayesian shrinkage                                                                                                                                                                                |
| 3   | Stage 1c cite-only adds             | ✅       | §2.1.1 LA in HE, §2.2.3 Difficulty (IRT), §2.3.1 CF, §2.5.2 Instructor Dashboards                                                                                                                                                   |
| 4   | Stage 1b §2.2.2 Knowledge Tracing   | ✅       | Relocation move + Corbett (with Eq. 2) + Yudelson + Piech/Khajah; grounded in 4 source PDFs                                                                                                                                         |
| 5   | Stage 1b §2.3.2 Text Mining         | ✅       | TF-IDF + K-means + silhouette + LLM labelling. Manning 2006 added at TF-IDF formula; k-means objective re-attributed to Arthur & Vassilvitskii potential function; Wang/Shang/Zhong 2023 grounds the closing LLM-labelling sentence |
| 6   | Stage 1b §2.4 RAG                   | 🔄 NEXT | Dense embeddings + HNSW; ~400 w                                                                                                                                                                                                     |
| 7   | Stage 1b §2.6 Research Gaps         | ⏳       | Uncomment commented draft + refresh against V2 features                                                                                                                                                                             |
| 8   | Stage 2 Ch3 stubs                   | ⏳       | 7 stub subsections; start with §3.4 advanced models                                                                                                                                                                                 |
| 9   | Phase 2 imports (34 refs)           | ⏳       | Interleave; required before Ch4 §4.7/§4.8 prose                                                                                                                                                                                     |
| 10  | Stage 3 Ch4 implementation rewrite  | ⏳       | **Largest single task** — full V1→V2 rewrite                                                                                                                                                                                        |
| 11  | Stage 4 Ch5 evaluation              | ⏳       | Empty chapter; needs smoke tests + screenshots first                                                                                                                                                                                |
| 12  | Stage 5 Ch1 cite adds + tense fixes | ⏳       | Lightweight; mostly drop-in cites                                                                                                                                                                                                   |
| 13  | Ch6 Conclusion                      | ⏳       | Summary + contributions + future work                                                                                                                                                                                               |
| 14  | Appendices A–F                      | ⏳       | Code, screenshots, tests, formulae, derivations                                                                                                                                                                                     |
| 15  | Final polish pass                   | ⏳       | Terminology, figure numbering, LaTeX compile                                                                                                                                                                                        |

Cosmetic backlog (do at any point, ~2 min each): Ch6 §6.2 heading missing "and"; Ch3 §3.3.4 wordy heading; Ch4 §4.12/§4.13 likely overlapping subsections (resolve at Ch4 rewrite time).

---

## TL;DR — current state (2026-05-04)

- **Submission deadline: 20 May 2026** (~16 days out).
- **Phase 1 reference imports: 46/46 ✅ COMPLETE.**
- **Phase 2 reference imports: 0/34 pending.** Non-blocking until Ch4 §4.7/§4.8 prose; Section M lists this as the most droppable item.
- **Ch2 restructured 2026-05-04.** Promoted thematic groups from subsubsections to subsections. New numbering: §2.1 LA & Dashboards, §2.2 Modelling Student Behaviour, §2.3 Data-Driven Personalisation, §2.4 RAG, §2.5 Existing Systems, §2.6 Research Gaps, §2.7 Requirements. Old `requirements-specification.tex` preserved as `requirements-specification-old.tex`.
- **Stage 1c ✅ COMPLETE.** Three method paragraphs (composite indicators, time-decay, Bayesian shrinkage) landed in §2.2.1. All cite-only adds done in §2.1.1, §2.2.3, §2.3.1, §2.5.2.
- **Stage 1b §2.2.2 Knowledge Tracing ✅ COMPLETE.** Relocation move done; 3 new paragraphs (Corbett BKT formal definition + Eq. 2 prediction equation, Yudelson individualisation, Piech DKT + Khajah rebuttal) grounded in the four uploaded source PDFs.
- **Stage 1b §2.3.2 Text Mining ✅ COMPLETE.** TF-IDF + k-means + k-means++ + silhouette grounded; closing LLM-labelling sentence cites Wang/Shang/Zhong 2023 (PAS / GoalEx). TF-IDF formula attributed to Manning 2006 not Salton 1975 (factual fix). k-means objective uses Arthur & Vassilvitskii's potential-function form. Rewritten in literature voice (no "submission"/"mistake patterns" dashboard-vocab).
- **Thesis chapter state:** Ch1 written, Ch2 partial (§2.4/§2.6 still pending), Ch3 partial, Ch4 outdated (V1), Ch5 empty, Ch6 empty.

The next concrete writing task is **Stage 1b §2.4 RAG for Instructor Feedback** — RAG framing + dense embeddings + HNSW + LLMs-in-education. Lewis/Reimers/Malkov/Kasneci already in the bib; gao2023retrieval, karpukhin2020dense, izacard2021leveraging, wang2020minilm pending Phase 2 import.

---

## Section A — Two-phase reference import system

The reference work is split into two batches because they serve different purposes.

### Phase 1 (DONE) — 46 academic refs to fill the literature-review gaps

Originally 50 planned; finalised at 46 after dropping 4 along the way (see "Removed / superseded" below).

**State:** all 46 ticked off, all in `references.bib`, all matched to vault notes via Better BibTeX CamelCase citekeys.

### Phase 2 (TODO) — 34 software + foundational citations

Triggered by user-supplied list 2026-05-03. Closes three remaining gaps:

1. **Software citations** (sklearn, NumPy, pandas, SciPy, Streamlit, ChromaDB, OpenAI ×2, MiniLM) — currently zero in the bib. Reproducible-research norms require these.
2. **HMM/EM machinery underlying BKT** — Baum-Welch and Rabiner missing; Corbett & Anderson 1995 alone doesn't ground the inference algorithm.
3. **Dashboard-design + ethics literature** — Few 2006, Schwendimann 2017, Bodily & Verbert 2017, Matcha 2020, Jivet 2018, Slade & Prinsloo 2013, Pardo & Siemens 2014.

Plus IRT theory expansion (Bock & Aitkin, Birnbaum), James & Stein 1961 peer-reviewed shrinkage, Pardos & Heffernan + Reye for BKT, Gao/Karpukhin/Izacard for RAG, CF eval (Herlocker 2004, Shani 2011, Gama 2013, Wilcoxon 1945, Demšar 2006), VanLehn 2011 ITS effect-size, Robins/Rountree 2003 CSEd, Kazemitabaar 2024 CodeAid (closest direct system analogue).

**Full list with target chapter sections + per-item rationale:** `_import_checklist.md` "Phase 2" section.

**Decisions encoded** (made during Phase 2 planning):

- **Drop** Robertson 2009 (BM25), Bruch 2023 (hybrid fusion), Cormack 2009 (RRF) — the RAG implementation is pure dense (ChromaDB + SBERT, no sparse retrieval). Importing these would misrepresent the architecture.
- **Drop** Bodily & Verbert 2017 LAK '17 conference paper — the journal review covers the same ground at greater depth.
- **Keep** Wilcoxon + Demšar despite Ch5 not being written yet — Dr. Batmaz has flagged paired statistical tests as a Ch5 requirement.

### Workflow for Phase 2 imports

Same as Phase 1:

1. User imports each ref into Zotero (Better BibTeX gives CamelCase keys).
2. User re-exports `Report/references.bib`.
3. User pings the assistant; assistant verifies in bib, ticks the box, annotates the citekey in the checklist.
4. Once all 34 are in, run `python scripts/sync_literature.py` to refresh `coverage.md`.
5. Then resume writing — Phase 2 unlocks **no new writing tasks**, just enriches existing Stages 1–5.

---

## Section B — Workflow conventions established in this push

These rules emerged through iteration; preserve them in future chats.

### Refs first, then prose

Before the assistant gives any prose example for a section, the relevant refs must already be in `references.bib`. Workflow per writing batch:

1. Assistant lists the refs needed for the upcoming section + DOIs/arXiv IDs where useful.
2. User imports them into Zotero, re-exports the bib.
3. User confirms.
4. Assistant gives the where/what/how/example walkthrough using the actual citekeys from the bib.
5. User writes the prose into the `.tex` file themselves.
6. After a batch, run `python scripts/sync_literature.py` to update coverage.

### Tell-then-write, never write-the-tex

The assistant tells the user what to write with example prose; **the user pastes/adapts and writes it into the `.tex` files themselves**. The assistant should never edit `Report/main-sections/*.tex` directly. This was confirmed multiple times.

### Reference list edits stay in `_import_checklist.md`

Any structural changes to the reference plan (additions, drops, reorderings) get recorded in `_import_checklist.md` only. Don't touch `references.bib` or vault notes proactively unless executing a sync step.

### Better BibTeX naming convention

Better BibTeX generates CamelCase keys like `corbettKnowledgeTracingModeling1995`. The vault literature notes are kept synchronised by filename (the note for that key is `corbettKnowledgeTracingModeling1995.md`). The earlier underscore-style stubs were renamed via PowerShell on 2026-05-03 — do not regress.

If a Better BibTeX key comes back malformed (year missing, author missing, mixed case oddity), the fix is in Zotero: edit the entry's metadata, then right-click → Better BibTeX → Refresh BibTeX key, then re-export.

### Code-check before importing speculative refs

Speculative refs (e.g. "if the architecture has hybrid retrieval, cite BM25") get verified against the actual codebase before being imported. The Phase 2 BM25/RRF/Bruch drop was the result of this check.

---

## Section C — Writing Stages (the actual work)

Each stage targets specific subsections of the thesis. Stages can be done in any order, but the suggested sitting order is below the per-stage detail.

### Stage 1a — Replace low-quality web citations ✅ DONE

Three "anonymous" placeholders (`a2020_atrisk` edInsight vendor page, `a2022_early` Wikipedia EWS article, `a2023_real` Databricks glossary) were swapped for proper academic refs in Ch2 §2.2 EWS subsection.

**Outcome:**

- Wikipedia ref → replaced by `macfadyenMiningLMSData2010` (canonical EWS-in-LA paper) at line 189.
- Databricks ref → dropped entirely (Marr 2021 was already covering the role).
- edInsight ref → kept as a *product example* and supplemented with `arnoldCourseSignalsPurdue2012a` and `jayaprakashEarlyAlertAcademically2014` as academic backing in a new sentence at line 218–219.
- Appendix table at `Report/appendix-sections/themes-and-references.tex` lines 15 and 28 updated.

### Stage 1c — Ch2 §2.1.4 struggle extensions + cite-only adds (in progress, prose pending)

**File:** `Report/main-sections/requirements-specification.tex`. Existing §2.1.4 sits at lines 75–101.

#### 1c-i. Three method paragraphs to add

Insert short paragraphs (~50–70 words each) **after** the existing line 87 paragraph (Piech-modeling) and before line 89's KT bridge. Each paragraph grounds one of the four formula moves the dashboard makes beyond the basic Dong/Or/Estey signals.

| Theme | Position | Cites | Suggested length |
|---|---|---|---|
| Composite indicators (why a weighted sum is justifiable) | First of three | `oecdHandbookConstructingComposite2008`, `saisanaUncertaintySensitivityAnalysis2005` | ~50 w |
| Time-decay weighting (why recent observations weigh more) | Second | `hunterExponentiallyWeightedMoving1986`, `korenCollaborativeFilteringTemporal2010` | ~60 w |
| Bayesian shrinkage (why pull toward class mean for sparse data) | Third | `efronSteinsParadoxStatistics1977` (motivation), `gelmanBayesianDataAnalysis2013` (n/(n+K) formula) | ~70 w |

> **Editorial rule (Rewrite Queue):** Ch2 gets one core equation per technique + citation; full notation lives in Ch3 and Appendix E. Don't write the formulas in §2.1.4 — just describe what the technique does and cite.

> **Note:** Draper & Smith (1998) regression-slope was originally a 4th paragraph; it was dropped on 2026-05-03 to keep the section tight. Improvement trajectory will be discussed in Ch3 §3.3.1 instead.

#### 1c-ii. Optional clusters that can extend §2.1.4 further

If §2.1.4 needs more depth, three additional clusters are available:

- **Gaming / wheel-spinning**: `bakerDevelopingGeneralizableDetector2008`, `beckWheelSpinningStudentsWho2013` — grounds the `r_hat` retry-rate and `rep_hat` answer-repetition signals.
- **Formative-assessment frame**: `blackAssessmentClassroomLearning1998`, `hattiePowerFeedback2007` — rationale for monitor-and-intervene loop. Could go at the start of §2.1.4 or in §2.1.9 RAG instead.
- **LLM-as-judge**: `zhengJudgingLLMasaJudgeMTBench2023`, `chiangCanLargeLanguage2023`, `liuGEvalNLGEvaluation2023`, `gilardiChatGPTOutperformsCrowd2023` — grounds the gpt-4o-mini incorrectness-scoring entry point.

#### 1c-iii. Cite-only adds to existing Ch2 subsections

These are pure `\cite{}` insertions into already-written sentences — no new prose required.

| Subsection | Lines | Cites to add |
|---|---|---|
| §2.1.1 LA Foundations | 5–32 | `siemensLearningAnalyticsEmergence2013`, `clowOverviewLearningAnalytics2013`, `romeroEducationalDataMining2020` |
| §2.1.6 Modelling Task Difficulty | 105–122 | `rasch1960probabilistic`, `lord1968statistical` (note: Wright & Stone dropped) |
| §2.1.7 Collaborative Filtering | 123–133 | `herlockerAlgorithmicFrameworkPerforming1999`, `resnickGroupLensOpenArchitecture1994` |
| §2.2.2 Instructor Facing Dashboards | 160–186 | `holsteinStudentLearningBenefits2018`, `holsteinIntelligentTutorsTeachers2017a` |

Voice cues (from existing §2.1.4 prose):

- Author surname + `et al.\ ` (trailing backslash-space is correct LaTeX) at start of attribution sentence.
- Single `\cite{key}` at end of sentence, before the period.
- Use connectors: "Beyond ...", "Another approach ...", "A complementary line ...".
- Close subsection with a synthesis sentence in the spirit of "Together, these works demonstrate ..." or "Overall, the literature suggests ...".

### Stage 1b — Write four empty §2.1 stubs (Ch2 NEW subsections)

**File:** `Report/main-sections/requirements-specification.tex`.

#### 1b-i. §2.1.5 Knowledge Tracing & Bayesian Student Models (line 103)

**Pre-step — relocation move:** Lines 89–93 of §2.1.4 currently sit in the *struggle* subsection but talk about knowledge tracing (Khajah BKT-IRT hybrid + Kim KT-with-questions). They belong in §2.1.5, not §2.1.4.

1. **Cut** lines 89–93 from §2.1.4 and **paste** as the opening paragraph of §2.1.5.
2. **Replace** in §2.1.4 with a one-line bridge: *"A complementary approach is knowledge tracing, which models latent skill mastery directly; see §2.1.5."*
3. **Build on** the relocated paragraph by adding new cites: `corbettKnowledgeTracingModeling1995` (seminal definition), `yudelsonIndividualizedBayesianKnowledge2013` (per-student fitting), `piechDeepKnowledgeTracing2015` (DKT modern baseline), `khajahHowDeepKnowledge2016` (extended BKT matches DKT).

This eliminates the BKT/IRT duplication risk between §2.1.4 (struggle) and §2.1.5 (KT). Ch3 §3.4.2/§3.4.3 and Ch4 §4.8.2/§4.8.3 are *not* duplication — they serve different roles (system design / implementation), not literature review.

**Length:** ~350–450 words across 4 paragraphs:

| Para | Purpose | Cites |
|---|---|---|
| 1 (relocated) | Existing KT teaser | `khajah_supercharging`, `kim_knowledge` (already cited) |
| 2 | Frame BKT formally as latent-skill mastery; introduce 4 parameters by name (no equation — that goes in Ch3) | `corbettKnowledgeTracingModeling1995` |
| 3 | Per-student parameter individualisation as a refinement | `yudelsonIndividualizedBayesianKnowledge2013` |
| 4 | Modern neural baseline (DKT) and the 2016 BKT-matches-DKT result; close by justifying why BKT is the right choice for this dashboard | `piechDeepKnowledgeTracing2015`, `khajahHowDeepKnowledge2016` |

After Phase 2 imports land, also weave in `pardoModelingIndividualization2010` (per-student precedent) and `reye2004student` (DBN/HMM formulation) to deepen paras 3 and 2 respectively.

#### 1b-ii. §2.3.2 Text Mining and Mistake Pattern Recovery ✅ COMPLETE

Subsection lives at lines 152–182 of `requirements-specification.tex`. Grounds the TF-IDF + K-means + silhouette + LLM-labelling pipeline used in mistake clustering, written in literature voice (no dashboard-specific vocabulary).

**Final cites used:** `saltonVectorSpaceModel1975` (vector space model framing only), `manningIntroductionInformationRetrieval2006` (TF-IDF formula — *not* Salton, per fact-check), `MacQueen1967SomeMF` (k-means origin, objective-only attribution), `arthurKmeansAdvantagesCareful` (k-means++ + the potential-function form $\phi = \sum_x \min_c \|x-c\|^2$ used in the equation), `rousseeuwSilhouettesGraphicalAid1987` (silhouette), `wangGoalDrivenExplainableClustering2023` (LLM cluster-explanation labelling — newly imported).

**Key decisions made during writing:**

- **TF-IDF formula attribution corrected.** Salton 1975 introduces VSM but does *not* contain the `tf · log(N/df)` formula in this form (that's later — Salton & Buckley 1988 / Manning 2008 are the textbook attributions). Cite Manning at the formula; cite Salton 1975 at the VSM framing only.
- **K-means objective re-attributed to Arthur & Vassilvitskii.** The form $\phi = \sum_x \min_c \|x-c\|^2$ is their potential-function notation, not MacQueen's. Cite Arthur at the equation, MacQueen at the prose ("MacQueen's $k$-means... minimise within-cluster variance") for objective-only attribution. This neutralises the MacQueen-vs-Lloyd algorithmic blur.
- **Closing LLM-labelling sentence reframed as literature claim.** Originally read as a forward-link to dashboard implementation ("a Large Language Model can label each centroid... to produce interpretable mistake categories"). Rewritten as a literature claim — "Once clusters are formed, a large language model can produce natural-language cluster explanations" — with `wangGoalDrivenExplainableClustering2023` (PAS / GoalEx). Kept Ch2 voice clean.
- **Three display equations retained** (TF-IDF, k-means, silhouette). Editorial rule (one core equation per technique) is being relaxed across Ch2 — §2.2.2 already has the BKT prediction equation. Three equations in §2.3.2 is the cap.

**Future-use papers (Phase 2 candidates):** `viswanathanLargeLanguageModelsEnable2023` (NOT yet in bib) — three-stage LLM-clustering taxonomy (before/during/after); fits Ch3 §3.3.5 / Ch4 §4.6 as system-design precedent. Wang/Shang/Zhong already imported, so it's available for Ch3 §3.3.5 too. Both pair Lloyd 1982 + Arthur 2007 in their k-means baselines, which is the modern citation norm — flag for Ch3/Ch4 when writing Stage 2/3.

#### 1b-iii. §2.1.9 RAG for Instructor Feedback (line 136)

NEW subsection grounding the RAG pipeline used in suggested-feedback generation.

**Cites:** `lewisRetrievalAugmentedGenerationKnowledgeIntensive2020` (RAG seminal), `reimersSentenceBERTSentenceEmbeddings2019` (sentence embeddings), `malkovEfficientRobustApproximate2016` (HNSW / ChromaDB underpinning), `kasneciChatGPTGoodOpportunities2023` (LLMs in education context).

**After Phase 2 imports:** add `gao2023retrieval` (modern RAG survey, taxonomy framing), `karpukhin2020dense` (dense passage retrieval), `izacard2021leveraging` (Fusion-in-Decoder generative pattern). Also `wang2020minilm` for the specific `all-MiniLM-L6-v2` model.

**Structure** (~300–400 words):

| Para | Purpose | Cites |
|---|---|---|
| 1 | RAG framing — why retrieve+generate beats pure LLM for instructor feedback | `lewisRetrievalAugmentedGenerationKnowledgeIntensive2020`, `gao2023retrieval` (Phase 2) |
| 2 | Dense embeddings as the retrieval mechanism | `reimersSentenceBERTSentenceEmbeddings2019`, `wang2020minilm` (Phase 2), `karpukhin2020dense` (Phase 2) |
| 3 | HNSW for efficient approximate nearest-neighbour search at scale | `malkovEfficientRobustApproximate2016` |
| 4 | LLMs in education frame; close by linking to the dashboard's instructor-facing use | `kasneciChatGPTGoodOpportunities2023` |

> **Heads-up:** the RAG implementation is **pure dense** (ChromaDB + SBERT, with metadata pre-filter, no sparse retrieval). Don't position the architecture as hybrid — if you do, you'll need to justify with BM25/Bruch/RRF citations that we deliberately dropped. Stick with "dense retrieval over student-scoped documents."

#### 1b-iv. §2.1.10 Summary of Identified Research Gaps (line 138)

Existing commented-out draft sits at lines 142–151. Action:

1. Uncomment.
2. Refresh against the V2 codebase — the original draft predates many V2 features (BKT, IRT, mistake clustering, RAG).
3. Frame the gap as: real-time, lab-session-scale, instructor-facing analytics with interpretable models and LLM-mediated feedback. Cross-reference §2.1.5 (KT), §2.1.8 (text mining), §2.1.9 (RAG).
4. **No new cites required** — synthesis paragraph.

### Stage 2 — Ch3 stubs (Design and Modelling)

**File:** `Report/main-sections/design-and-architecture.tex`. **No `\cite{}` calls in this chapter yet.**

| Stub | Line | Cites |
|---|---|---|
| §3.3.1 Student Struggle Model (already written, just add cites) | 49 | `oecdHandbookConstructingComposite2008`, `efronSteinsParadoxStatistics1977`, `gelmanBayesianDataAnalysis2013` (n/(n+K) formula), `little2014statistical`, `macfadyenMiningLMSData2010`, `bakerDevelopingGeneralizableDetector2008`, `beckWheelSpinningStudentsWho2013`, `zhengJudgingLLMasaJudgeMTBench2023` |
| §3.3.2 Temporal Smoothing | 140 | `hunterExponentiallyWeightedMoving1986`, plus cross-ref to Ebbinghaus / Wixted at the conceptual level (they're Ch2 cites). Write the EWMA recurrence; cross-ref Appendix E. |
| §3.3.3 Question Difficulty (already written) | 142 | `manningIntroductionInformationRetrieval2008` for TF-IDF framing |
| §3.3.4 CF (already written) | 199 | covered in Ch2 §2.1.7 — no new cites |
| §3.3.5 Mistake Clustering | 308 | `saltonVectorSpaceModel1975`, `MacQueen1967SomeMF`, `arthurKmeansAdvantagesCareful`, `rousseeuwSilhouettesGraphicalAid1987` |
| §3.4.1 Measurement Confidence | 312 | `lord1968statistical` (CTT). Note: Crocker & Algina was dropped (Lord & Novick covers CTT adequately). |
| §3.4.2 IRT | 314 | `rasch1960probabilistic`, `fisherMathematicalFoundationsTheoretical1922` (footnote on MLE), `LimitedMemoryAlgorithm` (Byrd, footnote on L-BFGS-B). After Phase 2: add `bock1981marginal` and `birnbaum1968some` for theory expansion. |
| §3.4.3 BKT | 316 | `corbettKnowledgeTracingModeling1995`, `yudelsonIndividualizedBayesianKnowledge2013`. Cite default `BKT_P_INIT=0.3, _LEARN=0.1, _GUESS=0.2, _SLIP=0.1` from `config.py`. After Phase 2: add `baum1970maximization` (EM origin) and `rabiner1989tutorial` (forward-backward) for the inference algorithm. |
| §3.4.4 Improved Struggle | 318 | `little2014statistical` for mean-imputation. Document the graceful-degradation rules (0.75/0.00/0.25 fallback when mastery_summary coverage < 50%; 0.70/0.30/0.00 when IRT has < 2 distinct values; 1.00/0.00/0.00 when both collapse) per `improved_struggle.py:168-171`. **This is a dashboard-original design contribution, not a citation gap.** |
| §3.5 RAG Feedback Design | 320 | `lewisRetrievalAugmentedGenerationKnowledgeIntensive2020`, `hattiePowerFeedback2007`, `kasneciChatGPTGoodOpportunities2023`. After Phase 2: `gao2023retrieval`, `karpukhin2020dense`, `izacard2021leveraging`. |

**Important — Ch3 vs Ch2 separation:** Ch2 = "what the literature says about this technique"; Ch3 = "how this system uses it (with our parameter values from `config.py`)". Same papers cited in both with different framing — that's correct, not duplication.

### Stage 3 — Ch4 implementation cites

**File:** `Report/main-sections/implementation.tex`. Most subsections still stub; Ch4 is the **largest writing task** in the whole thesis and the highest priority overall. The cite-inserting subset (once prose is written):

| Stub | Cites |
|---|---|
| §4.6 Analytics § Incorrectness Scoring | `zhengJudgingLLMasaJudgeMTBench2023` for LLM-as-judge framing; after Phase 2 add `openai2023gpt4` and `openai2024gpt4o` for the gpt-4o-mini call |
| §4.7 RAG Suggested Feedback | `lewisRetrievalAugmentedGenerationKnowledgeIntensive2020`, `reimersSentenceBERTSentenceEmbeddings2019`, `malkovEfficientRobustApproximate2016`, `liuGEvalNLGEvaluation2023`. Phase 2: `wang2020minilm`, `chroma_software` |
| §4.8 Advanced Models § IRT | `LimitedMemoryAlgorithm` (Byrd) one-line cite at L-BFGS-B call-site narration |
| §4.8 Advanced Models § BKT | `corbettKnowledgeTracingModeling1995`, `yudelsonIndividualizedBayesianKnowledge2013`. Phase 2: `baum1970maximization`, `rabiner1989tutorial` |
| New "Implementation Stack" subsection (Phase 2) | `pedregosa2011scikit`, `harris2020array`, `mckinney2010data`, `virtanen2020scipy`, `streamlit_software`, `chroma_software`, `openai2023gpt4`, `openai2024gpt4o`, `wang2020minilm` |

### Stage 4 — Ch5 evaluation cites

**File:** `Report/main-sections/results-and-evaluation.tex`. Entire chapter is empty stubs. **Substantial writing required, not just cite insertion.**

| Subsection | Cites |
|---|---|
| §5.1 Evaluation Design | `fawcettIntroductionROCAnalysis2006`, `hanleyMeaningUseArea1982` (ROC-AUC framing); Phase 2: `jivet2018license` (LAD evaluation criteria), `gama2013evaluating` (prequential / time-aware eval) |
| §5.4 Model Comparison | `CoefficientAgreementNominal` (Cohen's κ for chance-corrected agreement); `spearmanProofMeasurementAssociation1904` for rank correlation. Phase 2: `wilcoxon1945individual`, `demsar2006statistical` for paired comparisons |
| §5.x CF Evaluation (Dr. Batmaz request) | Phase 2: `herlocker2004evaluating`, `shani2011evaluating` |
| §5.x LLM evaluation | `chiangCanLargeLanguage2023`, `gilardiChatGPTOutperformsCrowd2023`, `kasneciChatGPTGoodOpportunities2023` |

> **Dr. Batmaz's specific Ch5 ask:** use held-out historical sessions as proxy ground truth; report MAE/RMSE, precision@k, coverage. This is what the Phase 2 CF-eval cites support.

### Stage 5 — Ch1 optional context cites

**File:** `Report/main-sections/introduction.tex`. Ch1 is **fully written** but currently uncited. Three cites can be inserted into existing prose if context fits:

- `clowOverviewLearningAnalytics2013` — LA cycle framing (§1.1)
- `holsteinStudentLearningBenefits2018` — teacher-facing analytics motivation (§1.2)
- `blackAssessmentClassroomLearning1998` — formative-assessment grounding (§1.1 or §1.2)

After Phase 2: add `slade2013ethical` and `pardoSiemens2014ethical` to the Ch1 risk/ethics framing (closes the ethics gap noted in §6 too); `vanlehn2011relative` for ITS effect-size benchmark in §1.2 motivation.

Skip if it disrupts the existing flow.

---

## Section D — Suggested sitting order

Pick whichever order fits the day, but this minimises rework:

1. **Stage 1c §2.1.4 struggle extensions** (3 short paragraphs, ~200 words). Highest leverage per page written; closes 3 supervisor backlog items in one sitting.
2. **Stage 1c cite-only adds** (§2.1.1, §2.1.6, §2.1.7, §2.2.2). Low effort, high checkbox count.
3. **Stage 1b §2.1.5 Knowledge Tracing** (~400 words including the relocation move). Most cohesive single new subsection.
4. **Stage 1b §2.1.8 Text Mining** (~300 words).
5. **Stage 1b §2.1.9 RAG** (~400 words).
6. **Stage 1b §2.1.10 Summary** (uncomment + refresh, ~150 words).
7. **Stage 2 Ch3 stubs.** Start with §3.4 Advanced Models (IRT + BKT + Improved Struggle — mathematically self-contained). Then §3.3.2 Temporal Smoothing, §3.3.5 Mistake Clustering, §3.5 RAG.
8. **Phase 2 imports interleave here** — start importing software citations once you have time. Best to do them BEFORE writing Ch4 implementation prose, since Ch4 §4.7/§4.8 specifically need them.
9. **Stage 3 Ch4 implementation rewrite.** This is the biggest single writing task in the thesis. The full V2 system needs to be described from scratch (current Ch4 describes V1 prototype only). See "Chapter status" below for scope.
10. **Stage 4 Ch5 evaluation chapter.** Needs running smoke tests + screenshot capture first (Appendices B and C). Then write the evaluation chapter referring to those.
11. **Stage 5 Ch1 cite-only adds + risk/mitigation table refresh.**
12. **Ch6 Conclusion** — summary, contributions, future work. After Ch5 is settled.
13. **Appendices E (formulae) and F (derivations).** Can be written alongside Ch3.
14. **Final polish pass** — terminology consistency, figure numbering, LaTeX compile check.

---

## Section E — Chapter status (from previous roadmap, still current)

| Section | Status | Work needed | Effort |
|---|---|---|---|
| Ch1 — Introduction | ✅ Written | Convert future tense to past/present; update Table 1 risk mitigations with actual decisions; optional new cites (Stage 5) | Small |
| Ch2 — Background & Requirements | Mostly written, gaps | Stage 1a ✅ done; Stage 1c (3 method paragraphs + cite adds) pending; Stage 1b (4 new subsections) pending | Medium |
| Ch3 — Design & Modelling | Partial | Stage 2 — 7 stub subsections to write + cite-only adds to existing §3.3.1 / §3.3.3 | Medium |
| Ch4 — Implementation | **Outdated** | Full rewrite — currently describes V1 prototype only; V2 has ~10 new features (OpenAI scoring, 7-signal struggle, CF, mistake clustering, IRT, BKT, improved struggle, lab assistants, saved sessions, RAG suggested feedback, settings). **Largest single writing task.** | Large |
| Ch5 — Results & Evaluation | Empty | Write from scratch — eval design, FR/NFR functional testing, results, discussion. Needs Appendices B + C as input. | Large |
| Ch6 — Conclusion | Empty | Write from scratch — summary, contributions, future work | Medium |
| Appendix A — Code Snippets | Empty | Add key implementation excerpts to support Ch4 | Small |
| Appendix B — UI Screenshots | Empty | Screenshot every dashboard view; needed for Ch4 figures and Ch5 evaluation | Small |
| Appendix C — Test Results | Empty | Document smoke test outcomes; populates Ch5 §5.2/§5.3 | Medium |
| Appendix D — References | Done | — | — |
| Appendix E — Formulae | Empty | Collect struggle, difficulty, IRT, BKT, EWMA, n/(n+K), TF-IDF, cosine, silhouette formulas | Small |
| Appendix F — Formula Derivations | Empty | Derive BKT update, Rasch MLE gradient, Bayesian shrinkage posterior, Bernoulli log-likelihood | Medium |

---

## Section F — Decisions / non-obvious choices made in this push

Anything that took deliberation and shouldn't be relitigated:

1. **edInsight ref kept as a product example.** Vendor pages are defensible when citing a product, not when citing a definition. Wrapped with academic backing (Arnold 2012, Jayaprakash 2014).
2. **Morris 1983 → Gelman BDA 2013** for Bayesian shrinkage. The dashboard uses a fixed pseudo-count K=5 (conjugate Bayes with known hyperparameter), not empirical Bayes. Gelman BDA Ch. 5 is the textbook reference for the n/(n+K) formula actually used; Morris addresses estimating the prior from data, which is a different problem.
3. **Khajah 2014 dropped, Khajah 2016 retained.** The 2016 "How Deep is Knowledge Tracing?" result (extended BKT matches DKT empirically) is the more defensible angle for keeping interpretable BKT.
4. **Wright & Stone 1979 dropped.** Rasch + Lord & Novick cover the IRT/CTT foundations adequately.
5. **Salton & McGill 1983, Lloyd 1982, Han Kamber Pei 2011 dropped from §2.1.8.** Salton/Wong/Yang 1975 + Manning 2008 + MacQueen + Arthur cover the same ground.
6. **Crocker & Algina 1986 dropped** from Ch3 §3.4.1 Measurement Confidence. Lord & Novick 1968 covers CTT foundations.
7. **Shute 2008 dropped from §2.1.9 RAG.** Black & Hattie cover the formative-feedback angle.
8. **Draper & Smith 1998 dropped from §2.1.4.** Improvement-trajectory description belongs in Ch3 not Ch2.
9. **Hallucinated "Agnihotri, Ott & Pazzani 2015" stub deleted.** Created speculatively in a prior chat session; no such paper exists. Replaced with Arnold 2012 + Jayaprakash 2014.
10. **`liu_open` dropped** by user choice; not used.
11. **Phase 2 hybrid-retrieval cluster (BM25 + Bruch + Cormack) dropped.** RAG implementation in `code2/learning_dashboard/rag.py` is pure dense (ChromaDB + SBERT, metadata pre-filter only). Importing these would misrepresent the architecture.
12. **Phase 2 Bodily & Verbert 2017 LAK paper dropped.** The journal review variant covers the same ground at greater depth; one is enough.
13. **Verbert 2020 → Verbert 2013** rename. Better BibTeX assigned the wrong year initially; user corrected.
14. **§2.1.4 → §2.1.5 KT paragraph relocation** is the standard fix for the BKT/IRT duplication risk between subsections. Cut lines 89–93 from §2.1.4, paste into §2.1.5, replace with a one-line bridge.
15. **TF-IDF formula attributed to Manning 2006, not Salton 1975** in §2.3.2. Salton 1975 introduces VSM but not the `tf · log(N/df)` form. Cite Salton at the VSM framing, Manning at the formula. This is a factual correction, not just a citation-style preference.
16. **K-means equation cites Arthur & Vassilvitskii, not MacQueen** in §2.3.2. The form $\phi = \sum_x \min_c \|x-c\|^2$ is Arthur's potential-function notation. MacQueen retains an objective-only prose citation. Avoids the MacQueen-vs-Lloyd algorithmic blur (MacQueen's original procedure is online/sequential, not the batch assign-update of Lloyd 1957/1982).
17. **Closing LLM-labelling sentence in §2.3.2 framed as literature claim, not implementation forward-link.** Cites `wangGoalDrivenExplainableClustering2023` (PAS / GoalEx) — newly imported. Kept Ch2 in literature voice; dashboard-specific framing of the same step ("OpenAI labels each centroid...") belongs in Ch3 §3.3.5 / Ch4.
18. **`viswanathanLargeLanguageModelsEnable2023` (Few-Shot Clustering) flagged for Ch3 §3.3.5 / Ch4 §4.6, not §2.3.2.** Three-stage LLM-clustering taxonomy (before/during/after) fits system-design framing better than literature review. Add to Phase 2 import checklist if not already there.

---

## Section G — Citekey hygiene followups

Three Better BibTeX citekeys are functional but malformed. They will compile and won't break anything; cosmetic fix only.

| Current key | Problem | Fix in Zotero | Expected new key |
|---|---|---|---|
| `arthurKmeansAdvantagesCareful` | year missing | Add `2007` to Date field | `arthurKmeansAdvantagesCareful2007` |
| `LimitedMemoryAlgorithm` | author was missing during initial export; now added but key not regenerated | Right-click entry → Better BibTeX → Refresh BibTeX key | `byrdLimitedMemoryAlgorithm1995` |
| `CoefficientAgreementNominal` | author was missing during initial export; now added but key not regenerated | Same — refresh key | `cohenCoefficientAgreementNominal1960` |
| `MacQueen1967SomeMF` | unusual mixed-case key with title-truncation; functional but inconsistent with the rest of the bib | Refresh key | likely `macqueenMethodsClassificationAnalysis1967` |
| `little2014statistical` | year is 2014 in Zotero entry but checklist labels it 2002 | Verify whether this is the 2nd ed (2002) or 3rd ed (2019); update Date field | depends on edition |
| `malkovEfficientRobustApproximate2016` | citekey says 2016 (arXiv) but checklist labels it 2020 (TPAMI). Same paper, different year choice. | Pick one — TPAMI 2020 is the more citable version | `malkovEfficientRobustApproximate2020` if you change to TPAMI |

After fixing in Zotero, re-export `references.bib` and run `python scripts/sync_literature.py`. The vault notes need to be renamed too — see the "After each chapter chunk" instructions in `_import_checklist.md`.

---

## Section H — Voice and style cues (for future writing)

From the existing §2.1.4 prose and the Stage 1a sentence rewrites, the established style:

- **Author surname + `\ ` (backslash-space)** — `Dong et al.\ highlighted ...`, `Estey et al.\ proposed ...`. The `\ ` after `et al.` prevents LaTeX from collapsing inter-word spacing.
- **Single `\cite{key}` at end of sentence**, before the period.
- **Short paragraphs** (1–3 sentences typical, occasional longer).
- **Connectors that shape the argument**: "Beyond threshold-based approaches ...", "Another approach uses ...", "A related but distinct line of work ...", "More recent work has ...", "For the present project ...".
- **Mix quantitative and qualitative**: "over 77% accuracy", "514 students", "11% false-positive rate" alongside "the difficulty of distinguishing slight from serious struggle".
- **Closing synthesis sentence per subsection**: "Together, these works demonstrate ...", "Overall, the literature suggests ...".
- **No equations in Ch2** — that's an editorial rule. One core equation per technique, in Ch3 + Appendix E.

---

## Section I — Critical files reference

### LaTeX source

- `Report/main.tex` — root document (verify on each build)
- `Report/main-sections/introduction.tex` — Ch1 (written; needs cite adds + tense fixes)
- `Report/main-sections/requirements-specification.tex` — Ch2 (most active editing area)
- `Report/main-sections/design-and-architecture.tex` — Ch3 (7 stub subsections to fill)
- `Report/main-sections/implementation.tex` — Ch4 (full rewrite needed)
- `Report/main-sections/results-and-evaluation.tex` — Ch5 (empty; write from scratch)
- `Report/main-sections/conclusion.tex` — Ch6 (empty; write from scratch)
- `Report/appendix-sections/themes-and-references.tex` — appendix table mapping themes → citation lists; updated whenever a citekey changes
- `Report/appendix-sections/{code-snippets,ui-screenshots,detailed-test-results,formulae,formulae-derivation}.tex` — appendices A–F (mostly empty)
- `Report/references.bib` — Better BibTeX export. **Do not hand-edit.** Modify Zotero entries and re-export instead.

### Vault notes (Obsidian)

- `docs/obsidian-vault/My Notes/Literature/_import_checklist.md` — **live tracking of import progress**. Phase 1 (46/46 ✅), Phase 2 (0/34 pending). Includes Removed/superseded log.
- `docs/obsidian-vault/My Notes/Literature/coverage.md` — **auto-generated** by `sync_literature.py`. Gives Active / Planned / Stale / Issues counts. Don't hand-edit.
- `docs/obsidian-vault/My Notes/Literature/index.md` — thematic grouping of citations by §-subsection. Hand-edited when groups change.
- `docs/obsidian-vault/My Notes/Literature/<citekey>.md` — one literature note per Better BibTeX citekey. Frontmatter `citekey:` field must match filename. Zotero Integration plugin enriches notes with abstract + metadata on import.
- `docs/obsidian-vault/My Notes/Thesis/Writing Roadmap.md` — **this file**.
- `docs/obsidian-vault/My Notes/Thesis/Rewrite Queue.md` — granular checklist of every specific edit.
- `docs/obsidian-vault/My Notes/Thesis/Report Sync.md` — code↔thesis mismatch table.
- `docs/obsidian-vault/My Notes/Thesis/Evidence Bank.md` — what evaluation evidence exists or needs to be collected.
- `docs/obsidian-vault/My Notes/Thesis/Figures and Tables.md` — figure inventory.

### Scripts

- `scripts/sync_literature.py` — keeps vault notes in sync with `references.bib` and `\cite{}` calls. Excludes `index.md`, `coverage.md`, and any file starting with `_` (so `_import_checklist.md` is safe). Run after every batch.

---

## Section J — Verification commands

After every batch of edits:

```bash
# from repo root
python scripts/sync_literature.py
```

Open `docs/obsidian-vault/My Notes/Literature/coverage.md` and confirm:

1. **Cited but missing bib entry — broken `\cite{}`: 0** (every cite resolves to a bib entry)
2. **Stale: 0** (every note has a plan or a cite)
3. **Active count climbs** as new cites land; **Planned** drops.
4. **In Zotero but not cited** is OK as a positive number — that's the intermediate state during writing.
5. **In Zotero but no literature note: 0** (every bib entry has a vault note)

Then build the report:

```bash
cd Report
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Look for `?` warnings — they indicate undefined citations.

End-state target after all writing: **Active ≥ 79, Planned = 0, Broken = 0, Stale = 0, In-Zotero-but-not-cited = 0, In-Zotero-but-no-note = 0.**

---

## Section K — Open questions / followups

Surfaced during this push, not yet resolved:

1. **Ch4 RAG section needs to credit Dr. Batmaz** for the hybrid SQL + ChromaDB design. He proposed the architecture in Meeting 3.
2. **Ch5 CF evaluation methodology** — Dr. Batmaz specifically asked for held-out-historical-sessions as proxy ground truth, with MAE/RMSE/precision@k/coverage. Phase 2 imports (Herlocker 2004, Shani 2011) support this.
3. **Ch6 future work — ML-based weight optimisation.** Once labelled ground-truth data exists, the parametric weights (α, β, γ, δ, η) could be optimised via supervised ML rather than set manually. Currently they are trial-and-error per the maths-fix commit `8c4c13c`.
4. **§3.4 Advanced Models disagreement (~0% agreement with baseline).** IRT collapses under sparse per-question data; BKT mastery-threshold sensitivity with default parameters. Frame as known limitation in Ch5 §5.5 with possible causes — not as a failure.
5. **Smart device integration (FR6)** — explicitly scoped out, but discuss honestly as future work in Ch6.
6. **Measurement Confidence formula and graceful-degradation weight redistribution** — both are dashboard-original design contributions, not citation gaps. Frame as such in Ch3 §3.4.1 and §3.4.4.
7. **Streamlit-only V1 vs React+FastAPI V2 framing.** The thesis Ch4 currently describes V1; V2 has feature-parity (per `code2/CHECKLIST.md` Phase 9). Decide whether to write Ch4 about V2 (recommended) or both stacks.
8. **Recap toolkit (`docs/recap_toolkit/dashboard_v3_toolkit.html`)** — keep in sync after major thesis edits, especially the Roadmap, Section Plan, Status, and Literature panels.

---

## Section L — How to resume in a future chat

If picking up in a fresh chat:

1. **Read this file in full** — gives complete context.
2. **Read `_import_checklist.md`** — gives current Phase 1 / Phase 2 import state.
3. **Read `coverage.md`** — gives current Active / Planned / Broken counts.
4. **Optionally read** `Rewrite Queue.md` for granular edits and `Report Sync.md` for code↔thesis divergence.
5. **State to the assistant:** "I'm continuing the thesis writing work; Writing Roadmap.md has the full plan. Current task is [stage X]." The assistant should resume the refs-first → tell-then-write workflow.

Do not attempt to edit `Report/` files via assistant. The assistant's job is to research, plan, give example prose, and verify references — the user does the actual `.tex` writing.

---

## Section M — Deadline and realistic scope

**Submission: 20 May 2026** (~17 days from 2026-05-03).

The biggest risk items in priority order:

1. **Ch4 Implementation rewrite.** Largest single task; current text describes V1 only.
2. **Ch5 Evaluation chapter (entire).** Needs smoke tests run + screenshots first.
3. **Phase 2 imports (34 refs).** ~2 hours of Zotero work; non-blocking but should land before Ch4 RAG/§4.8 prose.
4. **Stage 1b new Ch2 subsections.** ~3 sessions of writing.
5. **Stage 1c §2.1.4 method paragraphs + cite-only adds.** ~1 session.
6. **Ch6 Conclusion.** ~1–2 sessions; depends on Ch5 settling.
7. **Appendices A/B/C.** Mechanical; can interleave with anything.
8. **Appendices E/F formulae and derivations.** Can be written alongside Ch3.

If time runs short, the prioritisation is: **Ch4 → Ch5 → Stage 1b/1c → Stage 2 → Ch6 → Stage 5/Ch1 polish → Phase 2 polish imports**. Stage 5 Ch1 cite-only adds and the citekey-hygiene cleanup are the most droppable.
