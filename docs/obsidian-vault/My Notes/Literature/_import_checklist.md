# Zotero Import Checklist

> [!success] Progress — COMPLETE
> **46 / 46 imported (100%)** ✅
> `████████████████████`
>
> Ch2: 36/36 ✅ · Ch3: 2/2 ✅ · Ch5: 3/3 ✅ · Already imported (Stage 1a + bonuses): 5/5 ✅

> [!info] Reordered by **chapter of first use** so you can import → write → import next chapter.
> Most refs are used in multiple chapters; each appears here under its **earliest** appearance, with later chapters annotated. After each chapter's batch is in, run `python scripts/sync_literature.py`, write that chapter, then move on.

**Reordered:** 2026-05-02 · **Source:** `coverage.md` (planned column) + writing plan stage order

---

## Ch2 — Background and Requirements (37 imports)

The bulk of the work. Once these are in, you can write Stage 1c (extensions to existing §2.1) and Stage 1b (the four new §2.1 subsections). Sub-grouped by section so you can also batch sub-batches.

### §2.1.1 LA Foundations (3)

- [x] **Siemens (2013)** — Learning Analytics: The Emergence of a Discipline · *American Behavioral Scientist* → `siemensLearningAnalyticsEmergence2013`
- [x] **Clow (2013)** — An Overview of Learning Analytics · *Teaching in Higher Education* — *(also Ch1)* → `clowOverviewLearningAnalytics2013`
- [x] **Romero & Ventura (2020)** — Educational Data Mining and Learning Analytics: An Updated Survey · *WIREs Data Mining & KD* → `romeroEducationalDataMining2020`

### §2.1.4 Modelling Student Struggle — extensions (12)

Composite indicators:
- [x] **OECD / JRC (2008)** — Handbook on Constructing Composite Indicators — *(also Ch3, Question Difficulty Logic)* → `oecdHandbookConstructingComposite2008`
- [x] **Saisana, Saltelli & Tarantola (2005)** — Uncertainty and Sensitivity Analysis Techniques as Tools for the Quality Assessment of Composite Indicators · *JRSS A* — *(also Student Struggle Logic)* — sensitivity-analysis defence for the weight choices → `saisanaUncertaintySensitivityAnalysis2005`

Time-decay:
- [x] **Hunter (1986)** — The Exponentially Weighted Moving Average · *J. Quality Technology* — *(also Student Struggle Logic)* — canonical EWMA recursion → `hunterExponentiallyWeightedMoving1986`
- [x] **Koren (2009)** — Collaborative Filtering with Temporal Dynamics · *KDD 2009* (also CACM 53(4) 2010) — *(also Student Struggle Logic)* — explicit time-decay weighting in CF → `korenCollaborativeFilteringTemporal2010`

Bayesian shrinkage:
- [x] **Efron & Morris (1977)** — Stein's Paradox in Statistics · *Scientific American* — *(also Ch3)* — motivation/intuition
- [x] **Gelman, Carlin, Stern, Dunson, Vehtari & Rubin (2013)** — Bayesian Data Analysis, 3rd ed. · *CRC Press* — book — *(also Ch3)* — conjugate normal-normal derivation that gives n/(n+K), the formula actually used. Replaces Morris 1983.

Gaming / wheel-spinning behaviour:
- [x] **Baker et al. (2008)** — Developing a Generalizable Detector of When Students Game the System · *UMUAI 2008* — *(also Ch3)* → `bakerDevelopingGeneralizableDetector2008`
- [x] **Beck & Gong (2013)** — Wheel-Spinning · *AIED 2013* — *(also Ch3)* → `beckWheelSpinningStudentsWho2013`

LLM-as-judge:
- [x] **Zheng et al. (2023)** — Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena · *NeurIPS 2023* — *(also Ch3, Ch4)* · arXiv `2306.05685` → `zhengJudgingLLMasaJudgeMTBench2023`
- [x] **Chiang & Lee (2023)** — Can LLMs Be an Alternative to Human Evaluations? · *ACL 2023* — *(also Ch5)* · arXiv `2305.01937` → `chiangCanLargeLanguage2023`
- [x] **Liu et al. (2023)** — G-Eval: NLG Evaluation using GPT-4 · *EMNLP 2023* — *(also Ch4)* · arXiv `2303.16634` → `liuGEvalNLGEvaluation2023`
- [x] **Gilardi, Alizadeh, Kubli (2023)** — ChatGPT Outperforms Crowd Workers · *PNAS 2023* — *(also Ch5)* → `gilardiChatGPTOutperformsCrowd2023`

### §2.1.5 Knowledge Tracing (4) — NEW subsection

- [x] **Corbett & Anderson (1995)** — Knowledge Tracing · *UMUAI* — *(also Ch3, BKT, Improved Struggle)* → `corbettKnowledgeTracingModeling1995`
- [x] **Yudelson, Koedinger, Gordon (2013)** — Individualized Bayesian Knowledge Tracing · *AIED 2013* — *(also Ch3, BKT)* → `yudelsonIndividualizedBayesianKnowledge2013`
- [x] **Piech et al. (2015)** — Deep Knowledge Tracing · *NeurIPS 2015* — *(also Ch3, BKT)* · arXiv `1506.05908` → `piechDeepKnowledgeTracing2015`
- [x] **Khajah, Lindsey & Mozer (2016)** — How Deep is Knowledge Tracing? · *EDM 2016* — *(also Ch3, BKT)* — extended BKT matches DKT empirically; justifies interpretable BKT over DKT → `khajahHowDeepKnowledge2016`

### §2.1.6 Modelling Task Difficulty — extensions (2)

- [x] **Rasch (1960)** — Probabilistic Models for Some Intelligence and Attainment Tests · book — *(also Ch3, IRT)* — primary source for the 1PL model implemented in `models/irt.py` → `rasch1960probabilistic`
- [x] **Lord & Novick (1968)** — Statistical Theories of Mental Test Scores · book — *(also Ch3, IRT, Measurement Confidence)* — CTT foundations for §3.4.1 + statistical bridge from CTT to latent-trait models → `lord1968statistical`

### §2.1.7 Collaborative Filtering — extensions (2)

- [x] **Herlocker, Konstan, Borchers, Riedl (1999)** — An Algorithmic Framework for CF · *SIGIR 1999* → `herlockerAlgorithmicFrameworkPerforming1999`
- [x] **Resnick et al. (1994)** — GroupLens · *CSCW 1994* → `resnickGroupLensOpenArchitecture1994`

### §2.1.8 Text Mining and Mistake Pattern Recovery (5) — NEW subsection

- [x] **Salton, Wong & Yang (1975)** — A Vector Space Model for Automatic Indexing · *CACM* — canonical TF-IDF / vector-space formulation (replaces Salton & Lesk 1968) → `saltonVectorSpaceModel1975`
- [x] **Manning, Raghavan, Schütze (2008)** — Introduction to Information Retrieval · *Cambridge UP* — book — *(also Ch3)* → `manningIntroductionInformationRetrieval2008`
- [x] **MacQueen (1967)** — Some Methods for Classification and Analysis of Multivariate Observations · *Berkeley Symp. Math. Stat.* → `MacQueen1967SomeMF` ⚠ unusual citekey style (mixed case) — refresh in Better BibTeX if you want it lowercased
- [x] **Arthur & Vassilvitskii (2007)** — k-means++: The Advantages of Careful Seeding · *SODA 2007* — justifies sklearn default `k-means++` initialiser → `arthurKmeansAdvantagesCareful` ⚠ year missing — add `2007` to Zotero Date field and refresh key
- [x] **Rousseeuw (1987)** — Silhouettes · *J. Computational & Applied Math* → `rousseeuwSilhouettesGraphicalAid1987`

### §2.1.9 RAG for Instructor Feedback (4) — NEW subsection

- [x] **Lewis et al. (2020)** — Retrieval-Augmented Generation · *NeurIPS 2020* — *(also Ch3, Ch4, RAG)* · arXiv `2005.11401` → `lewisRetrievalAugmentedGenerationKnowledgeIntensive2020`
- [x] **Reimers & Gurevych (2019)** — Sentence-BERT · *EMNLP 2019* — *(also Ch4, RAG)* · arXiv `1908.10084` → `reimersSentenceBERTSentenceEmbeddings2019`
- [x] **Malkov & Yashunin (2020)** — HNSW · *IEEE TPAMI 42(4)* — *(also Ch4, RAG)* · arXiv `1603.09320` → `malkovEfficientRobustApproximate2016` ⚠ Zotero entry uses arXiv 2016 — citekey says 2016 but you're citing 2020. If you want the 2020 TPAMI year in the citekey, edit the Zotero entry's Date field to `2020-04` (TPAMI vol 42 iss 4) and refresh the key.
- [x] **Kasneci et al. (2023)** — ChatGPT for Good? · *Learning and Individual Differences* — *(also Ch3, Ch5, RAG)* → `kasneciChatGPTGoodOpportunities2023`


### §2.2.2 Instructor Facing Dashboards (2)

- [x] **Holstein, McLaren, Aleven (2018)** — Mixed-Reality Teacher Awareness Tool · *AIED 2018* — *(also Ch1)* → `holsteinStudentLearningBenefits2018`
- [x] **Holstein, McLaren, Aleven (2017)** — Intelligent Tutors as Teachers' Aides · *LAK 2017* — *(also Lab Assistant System)* → `holsteinIntelligentTutorsTeachers2017a`

### §2.1 formative-frame (2 — could go in §2.1.4 or §2.1.9)

- [x] **Black & Wiliam (1998)** — Assessment and Classroom Learning · *Assessment in Education* — *(also Ch1, Student Struggle Logic)* → `blackAssessmentClassroomLearning1998`
- [x] **Hattie & Timperley (2007)** — The Power of Feedback · *Review of Educational Research* — *(also Ch3, RAG)* → `hattiePowerFeedback2007`

> **After this chunk:** ~38 of 50 imports done. Run sync, write Stage 1c + Stage 1b. Most Ch3 / Ch4 / Ch5 cites also unlock here as a side effect.

---

## Ch3 — Design and Modelling (2 net-new imports)

Most Ch3 cites are already covered by Ch2 imports. These two are unique to Ch3. (§3.4.1 Measurement Confidence is covered by Lord & Novick 1968, already imported under §2.1.6 — Crocker & Algina dropped, see Removed / superseded.)

### §3.4.2 IRT (1)

- [x] **Fisher (1922)** — On the Mathematical Foundations of Theoretical Statistics · *Phil. Trans. Royal Society A* → `fisherMathematicalFoundationsTheoretical1922`

### §3.4.4 Improved Struggle Model (1)

- [x] **Little & Rubin (2002)** — Statistical Analysis with Missing Data, 2nd ed. · *Wiley* — book → `little2014statistical` ⚠ Zotero entry dated 2014 (likely a reprint or 3rd ed) — verify whether this is the 2nd ed (2002) or 3rd ed (2019); update Zotero metadata if needed

> **After this chunk:** all Ch3 cites importable. Write Stage 2.

---

## Ch4 — Implementation (0 net-new imports)

All Ch4 cites are already covered by Ch2 + Ch3 batches above. Just write Stage 3 when ready.

---

## Ch5 — Results and Evaluation (3 net-new imports)

### §5.1 Evaluation Design (2)

- [x] **Fawcett (2006)** — An Introduction to ROC Analysis · *Pattern Recognition Letters* → `fawcettIntroductionROCAnalysis2006`
- [x] **Hanley & McNeil (1982)** — Meaning and Use of the Area Under a ROC Curve · *Radiology* → `hanleyMeaningUseArea1982`

### §5.4 Model Comparison (1)

- [x] **Spearman (1904)** — The Proof and Measurement of Association Between Two Things · *American J. Psychology* → `spearmanProofMeasurementAssociation1904`

> **After this chunk:** all Ch5 cites importable. Write Stage 4.

---

## Ch1 — Introduction (0 net-new imports)

All three optional Ch1 cites (`clow_2013_an`, `holstein_2018_student`, `black_1998_assessment`) are already in the Ch2 batch above. Stage 5 is just inserting them into existing Ch1 prose if context fits.

---

## Already imported (Stage 1a + first 3 of Ch2)

- ✅ Macfadyen & Dawson (2010) — `macfadyenMiningLMSData2010`
- ✅ Arnold & Pistilli (2012) — `arnoldCourseSignalsPurdue2012a`
- ✅ Jayaprakash et al. (2014) — `jayaprakashEarlyAlertAcademically2014`
- ✅ **Byrd, Lu, Nocedal, Zhu (1995)** — L-BFGS-B — *Ch3 §3.4.2* → `LimitedMemoryAlgorithm` ⚠ citekey needs regen in Better BibTeX (authors now added)
- ✅ **Cohen (1960)** — κ coefficient — *Ch5 §5.4* → `CoefficientAgreementNominal` ⚠ citekey needs regen in Better BibTeX (author now added)

> Arthur & Vassilvitskii (2007) was previously listed here but isn't in the bib — moved back to §2.1.8 main list as pending.

## Removed / superseded

- ❌ Agnihotri, Ott & Pazzani (2015) — *hallucinated, not a real paper*
- ❌ `liu_open` — author chose to drop
- ❌ `a2022_early` (Wikipedia EWS article) — replaced by Macfadyen 2010
- ❌ `a2023_real` (Databricks glossary) — dropped, redundant with Marr 2021
- ❌ Morris (1983) — *Parametric Empirical Bayes Inference* · JASA — replaced by Gelman BDA 2013 because the dashboard uses a fixed pseudo-count K (conjugate Bayes with known hyperparameter), not empirical Bayes (estimating the prior from data)
- ❌ Draper & Smith (1998) — *Applied Regression Analysis* — dropped from §2.1.4
- ❌ Shute (2008) — *Focus on Formative Feedback* — dropped from §2.1.9 (formative-frame Black & Hattie cover the angle)
- ❌ Khajah, Wing, Lindsey & Mozer (2014) — *Incorporating Latent Factors Into Knowledge Tracing* · EDM 2014 — dropped from §2.1.5 (Khajah 2016 covers the BKT-extension angle adequately)
- ❌ Wright & Stone (1979) — *Best Test Design* · Mesa Press — dropped from §2.1.6 (Rasch + Lord & Novick cover IRT/CTT foundations)
- ❌ Salton & McGill (1983) — *Introduction to Modern Information Retrieval* · McGraw-Hill — dropped from §2.1.8 (Salton/Wong/Yang 1975 + Manning 2008 cover TF-IDF)
- ❌ Lloyd (1982) — *Least Squares Quantization in PCM* · IEEE TIT — dropped from §2.1.8 (MacQueen 1967 + Arthur & Vassilvitskii 2007 cover k-means)
- ❌ Han, Kamber, Pei (2011) — *Data Mining: Concepts and Techniques* · Morgan Kaufmann — dropped from §2.1.8 (Manning 2008 covers the textbook angle)
- ❌ Crocker & Algina (1986) — *Introduction to Classical and Modern Test Theory* — dropped from §3.4.1 (Lord & Novick 1968 covers CTT foundations adequately)
- ❌ Wright & Stone (1979) — *Best Test Design* · Mesa Press — dropped from §2.1.6 (practical Rasch test-construction guide; the dashboard uses Rasch as a difficulty estimator over fixed lab questions, not as a test-design instrument — no item selection, no fit statistics in §5, so the book's load-bearing content doesn't apply. Rasch 1960 + Lord & Novick 1968 cover the model class and its statistical foundations.)
- ❌ Crocker & Algina (1986) — *Introduction to Classical and Modern Test Theory* — dropped from §3.4.1 (the measurement confidence formula in `models/measurement.py` is a bespoke heuristic — `base × length_factor × (0.5 + 0.5 × extremity_factor)` — not classical CTT; no true-score decomposition, no reliability coefficient, no Cronbach's α. Lord & Novick 1968, already imported under §2.1.6, covers any CTT framing §3.4.1 needs.)

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

---

## Phase 2 — Software & foundational citations (34 additions)

> [!note] Phase 2 Progress
> **0 / 34 imported (0%)** · 34 to go
> `░░░░░░░░░░░░░░░░░░░░`
>
> Software: 0/9 · IRT: 0/2 · Shrinkage: 0/1 · BKT/HMM: 0/4 · RAG: 0/3 · Eval: 0/5 · Dashboard: 0/5 · Ethics: 0/2 · ITS: 0/1 · CSEd: 0/1 · Analogue: 0/1

Triggered by 2026-05-03 audit + user-supplied research list. Closes three real gaps in the existing pool: software citations (currently zero), HMM/EM machinery underlying BKT (Baum-Welch and Rabiner missing), and dashboard-design + ethics literature (currently sparse).

**Dropped from the original 38-item list:**

- Robertson & Zaragoza 2009 (BM25), Bruch et al. 2023 (hybrid fusion), Cormack et al. 2009 (RRF) — RAG implementation is pure dense (ChromaDB + SBERT), no sparse retrieval. Importing these would misrepresent the architecture.
- Bodily & Verbert 2017 (LAK '17 conference paper) — the journal review version covers the same ground at greater depth.

## Software stack — Ch4 Implementation (9)

- [ ] **Pedregosa et al. (2011)** — Scikit-learn: Machine Learning in Python · *JMLR* — used in `code/learning_dashboard/analytics.py:14-17` (KMeans, TfidfVectorizer, silhouette, cosine kNN CF)
- [ ] **Harris et al. (2020)** — Array Programming with NumPy · *Nature* — underpins all numerical routines (`analytics.py:10`, `models/irt.py:5`)
- [ ] **McKinney (2010)** — Data Structures for Statistical Computing in Python · *SciPy proceedings* — student-interaction dataframes and temporal slicing
- [ ] **Virtanen et al. (2020)** — SciPy 1.0: Fundamental Algorithms for Scientific Computing in Python · *Nature Methods* — `scipy.optimize.minimize(method='L-BFGS-B')` for IRT MLE (`models/irt.py:145-151`); `scipy.stats.wilcoxon` for Ch5 paired tests
- [ ] **Streamlit** — software citation, GitHub/website — Ch4 frontend; both `app.py` and `lab_app.py` are Streamlit apps
- [ ] **Chroma / ChromaDB** — software citation, GitHub repo — Ch4 RAG vector store (`code2/learning_dashboard/rag.py:68,160`)
- [ ] **OpenAI (2023)** — GPT-4 Technical Report · arXiv `2303.08774` — Ch3/Ch4 RAG generation; canonical GPT-4-family reference
- [ ] **OpenAI (2024)** — GPT-4o System Card — Ch4 RAG implementation; pairs with GPT-4 TR for the `gpt-4o-mini` model used (`code2/learning_dashboard/config.py:14`)
- [ ] **Wang et al. (2020)** — MiniLM: Deep Self-Attention Distillation for Task-Agnostic Compression of Pre-Trained Transformers · *NeurIPS 2020* · arXiv `2002.10957` — distillation method behind `all-MiniLM-L6-v2` (`config.py:173`); pairs with Reimers & Gurevych 2019

## IRT / measurement theory — Ch3 §3.3.5 (2)

- [ ] **Bock & Aitkin (1981)** — Marginal Maximum Likelihood Estimation of Item Parameters: Application of an EM Algorithm · *Psychometrika* — methodological grounding for L-BFGS-B Rasch fit beyond Rasch 1960 and Lord & Novick 1968
- [ ] **Birnbaum (1968)** — Some Latent Trait Models and Their Use in Inferring an Examinee's Ability — book chapter in Lord & Novick 1968 — original 2PL/3PL formulation; "why Rasch among the IRT family" reference

## Bayesian shrinkage — Ch3 §3.3 / Ch2 §2.1.4 (1)

- [ ] **James & Stein (1961)** — Estimation with Quadratic Loss · *Berkeley Symp. Math. Stat.* — original Stein/James-Stein shrinkage paper; peer-reviewed counterpart to Efron & Morris 1977 (already cited)

## BKT / Knowledge Tracing — HMM/EM machinery — Ch3 §3.3.6 (4)

- [ ] **Pardos & Heffernan (2010)** — Modeling Individualization in a Bayesian Networks Implementation of Knowledge Tracing · *UMAP 2010* — canonical extension of BKT with per-student parameters; direct precedent for individualised 4-parameter HMM BKT
- [ ] **Reye (2004)** — Student Modelling Based on Belief Networks · *Int. J. AIED* — DBN/HMM formulation justifying BKT as a special case
- [ ] **Baum, Petrie, Soules & Weiss (1970)** — A Maximization Technique Occurring in the Statistical Analysis of Probabilistic Functions of Markov Chains · *Annals of Mathematical Statistics* — original Baum-Welch / EM-for-HMM paper; primary HMM citation currently missing in §3.3.6
- [ ] **Rabiner (1989)** — A Tutorial on Hidden Markov Models and Selected Applications in Speech Recognition · *Proc. IEEE* — universal HMM tutorial; pairs with Baum 1970 to ground forward-backward / Viterbi machinery underlying BKT inference

## RAG architecture — Ch2 §2.1.9 / Ch3 §3.5 (3)

- [ ] **Gao et al. (2023)** — Retrieval-Augmented Generation for Large Language Models: A Survey · arXiv `2312.10997` — standard modern RAG survey; provides Naive/Advanced/Modular taxonomy
- [ ] **Karpukhin et al. (2020)** — Dense Passage Retrieval for Open-Domain Question Answering · *EMNLP 2020* · arXiv `2004.04906` — foundational dense-retrieval paper; justifies embedding-based retrieval layer
- [ ] **Izacard & Grave (2021)** — Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering · *EACL 2021* · arXiv `2007.01282` — Fusion-in-Decoder; justifies retrieve-then-generate two-stage pattern

## CF + statistical evaluation — Ch5 (5)

- [ ] **Herlocker, Konstan, Terveen & Riedl (2004)** — Evaluating Collaborative Filtering Recommender Systems · *ACM TOIS* — canonical CF evaluation paper (MAE/RMSE, precision@k, coverage); Dr. Batmaz request
- [ ] **Shani & Gunawardana (2011)** — Evaluating Recommendation Systems — chapter in *Recommender Systems Handbook* — comprehensive evaluation-properties framework
- [ ] **Gama, Sebastião & Rodrigues (2013)** — On Evaluating Stream Learning Algorithms · *Machine Learning* — canonical reference for prequential / time-aware evaluation
- [ ] **Wilcoxon (1945)** — Individual Comparisons by Ranking Methods · *Biometrics Bulletin* — original signed-rank test; Ch5 paired comparison anchor
- [ ] **Demšar (2006)** — Statistical Comparisons of Classifiers over Multiple Data Sets · *JMLR* — methodological justification for Wilcoxon (and Friedman/Nemenyi) for paired ML/IR system comparison

## Dashboard design — Ch2 §2.1.2 / §2.2.2 / Ch3 UI (5)

- [ ] **Few (2006)** — Information Dashboard Design: The Effective Visual Communication of Data · O'Reilly — book — visual rationale for Streamlit layout choices
- [ ] **Schwendimann et al. (2017)** — Perceiving Learning at a Glance: A Systematic Literature Review of Learning Dashboard Research · *IEEE TLT* — defining SLR of learning dashboards
- [ ] **Bodily & Verbert (2017)** — Review of Research on Student-Facing Learning Analytics Dashboards and Educational Recommender Systems · *IEEE TLT* (journal review only — LAK '17 variant dropped) — pairs LADs and educational recsys
- [ ] **Matcha, Uzir, Gašević & Pardo (2020)** — A Systematic Review of Empirical Studies on Learning Analytics Dashboards: A Self-Regulated Learning Perspective · *IEEE TLT* — most recent SLR with empirical baselines; replaces `kiatxin_development` if removed
- [ ] **Jivet, Scheffel, Specht & Drachsler (2018)** — License to Evaluate: Preparing Learning Analytics Dashboards for Educational Practice · *LAK '18* — theory-grounded LAD evaluation criteria for Ch5

## Ethics — Ch1 / Ch6 (2)

- [ ] **Slade & Prinsloo (2013)** — Learning Analytics: Ethical Issues and Dilemmas · *American Behavioral Scientist* — seminal LA-ethics paper on consent, classification, student agency; closes a gap currently only Tzimas 2021 covers
- [ ] **Pardo & Siemens (2014)** — Ethical and Privacy Principles for Learning Analytics · *Br. J. Educational Technology* — cornerstone principles paper (transparency, student-as-agent, accountability); pairs with Slade & Prinsloo

## ITS framing — Ch1 / Ch6 (1)

- [ ] **VanLehn (2011)** — The Relative Effectiveness of Human Tutoring, Intelligent Tutoring Systems, and Other Tutoring Systems · *Educational Psychologist* — standard effect-size benchmark (~0.76σ for ITS) for positioning Dashboard-v3's lab-assistant intervention

## CS education context — Ch2 (1)

- [ ] **Robins, Rountree & Rountree (2003)** — Learning and Teaching Programming: A Review and Discussion · *Computer Science Education* — canonical novice-programmer review; standard background citation in CSEd theses on lab support

## Direct system analogue — Ch2 / Ch6 (1)

- [ ] **Kazemitabaar et al. (2024)** — CodeAid: Evaluating a Classroom Deployment of an LLM-based Programming Assistant that Balances Student and Educator Needs · *CHI 2024* — most rigorous in-the-wild evaluation (700 students, 12 weeks) of an LLM coding assistant with RAG over instructor-verified content; closest direct system analogue to Dashboard-v3
