---
citekey: _import_checklist
status: stale
in_zotero: false
cited_in_tex: []
cited_in_planned: []
last_synced: 2026-05-03
---
# Zotero Import Checklist

> [!success] Progress
> **22 / 50 imported (44%)** · 28 remaining
> `█████████░░░░░░░░░░░`
>
> Ch2: 16/38 · Ch3: 0/3 · Ch5: 0/3 · Already imported (Stage 1a + bonuses): 6/6

> [!info] Reordered by **chapter of first use** so you can import → write → import next chapter.
> Most refs are used in multiple chapters; each appears here under its **earliest** appearance, with later chapters annotated. After each chapter's batch is in, run `python scripts/sync_literature.py`, write that chapter, then move on.

**Reordered:** 2026-05-02 · **Source:** `coverage.md` (planned column) + writing plan stage order

---

## Ch2 — Background and Requirements (38 imports)

The bulk of the work. Once these are in, you can write Stage 1c (extensions to existing §2.1) and Stage 1b (the four new §2.1 subsections). Sub-grouped by section so you can also batch sub-batches.

### §2.1.1 LA Foundations (3)

- [x] **Siemens (2013)** — Learning Analytics: The Emergence of a Discipline · *American Behavioral Scientist* → `siemensLearningAnalyticsEmergence2013`
- [x] **Clow (2013)** — An Overview of Learning Analytics · *Teaching in Higher Education* — *(also Ch1)* → `clowOverviewLearningAnalytics2013`
- [x] **Romero & Ventura (2020)** — Educational Data Mining and Learning Analytics: An Updated Survey · *WIREs Data Mining & KD* → `romeroEducationalDataMining2020`

### §2.1.4 Modelling Student Struggle — extensions (13)

Composite indicators:
- [x] **OECD / JRC (2008)** — Handbook on Constructing Composite Indicators — *(also Ch3, Question Difficulty Logic)* → `oecdHandbookConstructingComposite2008`
- [ ] **Saisana, Saltelli & Tarantola (2005)** — Uncertainty and Sensitivity Analysis Techniques as Tools for the Quality Assessment of Composite Indicators · *JRSS A* — *(also Student Struggle Logic)* — sensitivity-analysis defence for the weight choices

Time-decay:
- [ ] **Hunter (1986)** — The Exponentially Weighted Moving Average · *J. Quality Technology* — *(also Student Struggle Logic)* — canonical EWMA recursion
- [ ] **Koren (2009)** — Collaborative Filtering with Temporal Dynamics · *KDD 2009* (also CACM 53(4) 2010) — *(also Student Struggle Logic)* — explicit time-decay weighting in CF

Bayesian shrinkage:
- [x] **Efron & Morris (1977)** — Stein's Paradox in Statistics · *Scientific American* — *(also Ch3)* — motivation/intuition
- [x] **Gelman, Carlin, Stern, Dunson, Vehtari & Rubin (2013)** — Bayesian Data Analysis, 3rd ed. · *CRC Press* — book — *(also Ch3)* — conjugate normal-normal derivation that gives n/(n+K), the formula actually used. Replaces Morris 1983.

Regression slope:
- [ ] **Draper & Smith (1998)** — Applied Regression Analysis, 3rd ed. · *Wiley* — book

Gaming / wheel-spinning behaviour:
- [ ] **Baker et al. (2008)** — Developing a Generalizable Detector of When Students Game the System · *UMUAI 2008* — *(also Ch3)*
- [ ] **Beck & Gong (2013)** — Wheel-Spinning · *AIED 2013* — *(also Ch3)*

LLM-as-judge:
- [x] **Zheng et al. (2023)** — Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena · *NeurIPS 2023* — *(also Ch3, Ch4)* · arXiv `2306.05685` → `zhengJudgingLLMasaJudgeMTBench2023`
- [x] **Chiang & Lee (2023)** — Can LLMs Be an Alternative to Human Evaluations? · *ACL 2023* — *(also Ch5)* · arXiv `2305.01937` → `chiangCanLargeLanguage2023`
- [x] **Liu et al. (2023)** — G-Eval: NLG Evaluation using GPT-4 · *EMNLP 2023* — *(also Ch4)* · arXiv `2303.16634` → `liuGEvalNLGEvaluation2023`
- [x] **Gilardi, Alizadeh, Kubli (2023)** — ChatGPT Outperforms Crowd Workers · *PNAS 2023* — *(also Ch5)* → `gilardiChatGPTOutperformsCrowd2023`

### §2.1.5 Knowledge Tracing (3) — NEW subsection

- [x] **Corbett & Anderson (1995)** — Knowledge Tracing · *UMUAI* — *(also Ch3, BKT, Improved Struggle)* → `corbettKnowledgeTracingModeling1995`
- [x] **Yudelson, Koedinger, Gordon (2013)** — Individualized Bayesian Knowledge Tracing · *AIED 2013* — *(also Ch3, BKT)* → `yudelsonIndividualizedBayesianKnowledge2013`
- [x] **Piech et al. (2015)** — Deep Knowledge Tracing · *NeurIPS 2015* — *(also Ch3, BKT)* · arXiv `1506.05908` → `piechDeepKnowledgeTracing2015`

### §2.1.6 Modelling Task Difficulty — extensions (3)

- [ ] **Rasch (1960)** — Probabilistic Models for Some Intelligence and Attainment Tests · book — *(also Ch3, IRT)*
- [ ] **Lord & Novick (1968)** — Statistical Theories of Mental Test Scores · book — *(also Ch3, IRT, Measurement Confidence)*
- [ ] **Wright & Stone (1979)** — Best Test Design · *Mesa Press* — book — *(also Ch3, IRT)*

### §2.1.7 Collaborative Filtering — extensions (2)

- [x] **Herlocker, Konstan, Borchers, Riedl (1999)** — An Algorithmic Framework for CF · *SIGIR 1999* → `herlockerAlgorithmicFrameworkPerforming1999`
- [x] **Resnick et al. (1994)** — GroupLens · *CSCW 1994* → `resnickGroupLensOpenArchitecture1994`

### §2.1.8 Text Mining and Mistake Pattern Recovery (8) — NEW subsection

- [ ] **Salton & McGill (1983)** — Introduction to Modern Information Retrieval · *McGraw-Hill* — book
- [ ] **Salton, Wong & Yang (1975)** — A Vector Space Model for Automatic Indexing · *CACM* — canonical TF-IDF / vector-space formulation (replaces Salton & Lesk 1968)
- [ ] **Manning, Raghavan, Schütze (2008)** — Introduction to Information Retrieval · *Cambridge UP* — book — *(also Ch3)*
- [ ] **MacQueen (1967)** — Some Methods for Classification and Analysis of Multivariate Observations · *Berkeley Symp. Math. Stat.*
- [ ] **Lloyd (1982)** — Least Squares Quantization in PCM · *IEEE Trans. Information Theory*
- [ ] **Arthur & Vassilvitskii (2007)** — k-means++: The Advantages of Careful Seeding · *SODA 2007* — justifies sklearn default `k-means++` initialiser
- [ ] **Rousseeuw (1987)** — Silhouettes · *J. Computational & Applied Math*
- [ ] **Han, Kamber, Pei (2011)** — Data Mining: Concepts and Techniques, 3rd ed. · *Morgan Kaufmann* — book

### §2.1.9 RAG for Instructor Feedback (5) — NEW subsection

- [ ] **Lewis et al. (2020)** — Retrieval-Augmented Generation · *NeurIPS 2020* — *(also Ch3, Ch4, RAG)* · arXiv `2005.11401`
- [ ] **Reimers & Gurevych (2019)** — Sentence-BERT · *EMNLP 2019* — *(also Ch4, RAG)* · arXiv `1908.10084`
- [ ] **Malkov & Yashunin (2020)** — HNSW · *IEEE TPAMI 42(4)* — *(also Ch4, RAG)* · arXiv `1603.09320` — citing 2020 (TPAMI print issue), not 2018 (date-of-publication-online)
- [ ] **Kasneci et al. (2023)** — ChatGPT for Good? · *Learning and Individual Differences* — *(also Ch3, Ch5, RAG)*
- [ ] **Shute (2008)** — Focus on Formative Feedback · *Review of Educational Research* — *(also Ch3, RAG)*

### §2.2 Existing Systems → Instructor Dashboards (2)

- [ ] **Holstein, McLaren, Aleven (2018)** — Mixed-Reality Teacher Awareness Tool · *AIED 2018* — *(also Ch1)*
- [ ] **Holstein, McLaren, Aleven (2017)** — Intelligent Tutors as Teachers' Aides · *LAK 2017* — *(also Lab Assistant System)*

### §2.1 formative-frame (2 — could go in §2.1.4 or §2.1.9)

- [ ] **Black & Wiliam (1998)** — Assessment and Classroom Learning · *Assessment in Education* — *(also Ch1, Student Struggle Logic)*
- [ ] **Hattie & Timperley (2007)** — The Power of Feedback · *Review of Educational Research* — *(also Ch3, RAG)*

> **After this chunk:** ~38 of 50 imports done. Run sync, write Stage 1c + Stage 1b. Most Ch3 / Ch4 / Ch5 cites also unlock here as a side effect.

---

## Ch3 — Design and Modelling (3 net-new imports)

Most Ch3 cites are already covered by Ch2 imports. These three are unique to Ch3.

### §3.4.1 Measurement Confidence (1)

- [ ] **Crocker & Algina (1986)** — Introduction to Classical and Modern Test Theory · book

### §3.4.2 IRT (1)

- [ ] **Fisher (1922)** — On the Mathematical Foundations of Theoretical Statistics · *Phil. Trans. Royal Society A*

### §3.4.4 Improved Struggle Model (1)

- [ ] **Little & Rubin (2002)** — Statistical Analysis with Missing Data, 2nd ed. · *Wiley* — book

> **After this chunk:** all Ch3 cites importable. Write Stage 2.

---

## Ch4 — Implementation (0 net-new imports)

All Ch4 cites are already covered by Ch2 + Ch3 batches above. Just write Stage 3 when ready.

---

## Ch5 — Results and Evaluation (3 net-new imports)

### §5.1 Evaluation Design (2)

- [ ] **Fawcett (2006)** — An Introduction to ROC Analysis · *Pattern Recognition Letters*
- [ ] **Hanley & McNeil (1982)** — Meaning and Use of the Area Under a ROC Curve · *Radiology*

### §5.4 Model Comparison (1)

- [ ] **Spearman (1904)** — The Proof and Measurement of Association Between Two Things · *American J. Psychology*

> **After this chunk:** all Ch5 cites importable. Write Stage 4.

---

## Ch1 — Introduction (0 net-new imports)

All three optional Ch1 cites (`clow_2013_an`, `holstein_2018_student`, `black_1998_assessment`) are already in the Ch2 batch above. Stage 5 is just inserting them into existing Ch1 prose if context fits.

---

## Already imported (Stage 1a + first 3 of Ch2)

- ✅ Macfadyen & Dawson (2010) — `macfadyenMiningLMSData2010`
- ✅ Arnold & Pistilli (2012) — `arnoldCourseSignalsPurdue2012a`
- ✅ Jayaprakash et al. (2014) — `jayaprakashEarlyAlertAcademically2014`
- ✅ **Arthur & Vassilvitskii (2007)** — k-means++ — *Ch2 §2.1.8* — ⚠ not yet in `references.bib` (re-export Better BibTeX)
- ✅ **Byrd, Lu, Nocedal, Zhu (1995)** — L-BFGS-B — *Ch3 §3.4.2* → `LimitedMemoryAlgorithm` ⚠ author missing
- ✅ **Cohen (1960)** — κ coefficient — *Ch5 §5.4* → `CoefficientAgreementNominal` ⚠ author missing

## Removed / superseded

- ❌ Agnihotri, Ott & Pazzani (2015) — *hallucinated, not a real paper*
- ❌ `liu_open` — author chose to drop
- ❌ `a2022_early` (Wikipedia EWS article) — replaced by Macfadyen 2010
- ❌ `a2023_real` (Databricks glossary) — dropped, redundant with Marr 2021
- ❌ Morris (1983) — *Parametric Empirical Bayes Inference* · JASA — replaced by Gelman BDA 2013 because the dashboard uses a fixed pseudo-count K (conjugate Bayes with known hyperparameter), not empirical Bayes (estimating the prior from data)

---

## Tips during import

- **arXiv IDs**: 7 of the LLM/RAG papers list arXiv IDs above — paste them all at once into Zotero's magic wand ("Add Item by Identifier") for the fastest possible import.
- **Books**: Zotero "Add Item by Identifier" → ISBN works well. Scholar metadata for books is often poor.
- **Malkov 2020**: pick the IEEE TPAMI version (vol. 42 iss. 4, April 2020), not the 2016 arXiv preprint, unless the arXiv is what's in your library. Citekey will likely become `malkovEfficientRobustApproximate2020`.
- **Rasch 1960**: out of print; the MESA Press 1980 reprint is interchangeable and easier to find.
- **Better BibTeX → Auto-pin Citation Keys** (Preferences → Better BibTeX → Citation Keys) — turn this on once at the start so keys don't churn as you edit metadata.

## After each chapter chunk

1. Re-export `Report/references.bib` from Better BibTeX.
2. Rename matching vault notes in `docs/obsidian-vault/My Notes/Literature/` so each filename + frontmatter `citekey:` matches the new Better BibTeX key.
3. Run `python scripts/sync_literature.py` from the repo root.
4. Confirm `coverage.md`:
   - **In Zotero but not cited** → climbs as you import (intermediate state, fine)
   - **Cited but missing bib** → 0
   - **In Zotero but no literature note** → 0
5. Tell me which chapter is unlocked — I'll start writing that stage.
