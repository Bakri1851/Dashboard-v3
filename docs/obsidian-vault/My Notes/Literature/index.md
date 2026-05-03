# Literature Index

All academic references cited in the thesis and implementation notes, grouped by **the tex subsection they belong to** (Ch2 §2.1 Literature + Ch2 §2.2 Existing Systems, plus a tail for Ch3/Ch4/Ch5-only refs). Status: ✅ cited in some `.tex` · 🟡 planned (note + intent, no `\cite{}` yet).

Related: [[Ch2 – Background and Requirements]], [[Ch3 – Design and Modelling]], [[Thesis Overview]]

---

## §2.1.1 Learning Analytics in Higher Education

Foundational definitions, surveys of the LA field, ethics framing.

- ✅ [[nguyen_2020_data|Nguyen et al. (2020)]] — data-driven approaches in education; 2012 evidence of real-time-feedback gains
- ✅ [[wikipediacontributors_2019_learning|Wikipedia (2019)]] — working definition of learning analytics
- ✅ [[vieira_2018_visual|Vieira et al. (2018)]] — visual analytics in education; data-source survey (also cited in §2.1.2)
- ✅ [[gelan_2018_affordances|Gelan et al. (2018)]] — affordances of analytics tools; the VITAL flipped-classroom result
- ✅ [[wilson_2017_learning|Wilson et al. (2017)]] — LA in higher education; privacy and observable-vs-cognitive limitation
- ✅ [[tzimas_2021_ethical|Tzimas et al. (2021)]] — ethical considerations (privacy, consent, fairness)
- ✅ [[dasilva_2022_a|Da Silva et al. (2022)]] — learning analytics system architecture
- ✅ [[li_2020_course|Li et al. (2020)]] — course-level analytics and temporal granularity
- 🟡 [[romero_2020_educational|Romero & Ventura (2020)]] — updated survey of EDM and LA; modern framing paper
- 🟡 [[siemens_2013_learning|Siemens (2013)]] — emergence of learning analytics as a discipline
- 🟡 [[clow_2013_an|Clow (2013)]] — overview of LA; learning analytics cycle

---

## §2.1.2 Dashboards for Learning Analytics

Prior LA dashboards and visual-analytics approaches; teacher-facing orchestration analytics.

- ✅ [[klerkx_2017_learning|Klerkx et al. (2017)]] — dashboard taxonomy; course-level vs session-level gap
- ✅ [[verbert_2013_learning|Verbert et al. (2013)]] — dashboard design principles; interpretability as key requirement
- ✅ [[govaerts_the|Govaerts et al.]] — SAM dashboard; separates at-risk from on-track students
- ✅ [[ahn_2019_the|Ahn (2019)]] — Edsight responsive web dashboard
- 🟡 [[holstein_2018_student|Holstein, McLaren & Aleven (2018)]] — mixed-reality teacher awareness tool
- 🟡 [[holstein_2017_intelligent|Holstein, McLaren & Aleven (2017)]] — intelligent tutors as teachers' aides

---

## §2.1.3 Real-Time Data Analytics and Visualisation

Motivation for live over post-session monitoring.

- ✅ [[marr_2021_what|Marr (2021)]] — cross-industry case for real-time analytics
- ✅ [[mustafaayobamiraji_2024_realtime|Mustafa, Ayobami & Raji (2024)]] — real-time analytics in retail/education
- ✅ [[montebello_assisting|Montebello]] — AI-assisted real-time attention/participation detection

---

## §2.1.4 Modelling Student Struggle

Papers grounding the 7-signal struggle model and its weighting.

### Core struggle papers (currently cited)

- ✅ [[dong_using|Dong et al.]] — session-level struggle detection (77% accuracy); 4-failure threshold
- ✅ [[or_2024_exploring|Or (2024)]] — novice-programmer testing; 4+ consecutive incorrect submissions
- ✅ [[estey_2017_automatically|Estey et al. (2017)]] — trajectory metric; 11% false-positive rate
- ✅ [[piech_modeling|Piech et al.]] — graphical model of student progression paths (also §2.1.6)
- ✅ [[kim_knowledge|Kim et al.]] — knowledge tracing with student questions and skill extraction
- ✅ [[koutcheme_using|Koutcheme et al.]] — LLM repair quality correlates with explanation quality
- ✅ [[pitts_a|Pitts et al.]] — LLM-based programming education works best with human oversight

### Formative assessment grounding

- 🟡 [[black_1998_assessment|Black & Wiliam (1998)]] — seminal formative-assessment paper; grounds the monitor-and-intervene loop
- 🟡 [[shute_2008_focus|Shute (2008)]] — focus on formative feedback; types/timing/effectiveness
- 🟡 [[hattie_2007_the|Hattie & Timperley (2007)]] — power of feedback (task / process / self-regulation / self)

### Composite indicators and Bayesian shrinkage

- 🟡 [[oecd_2008_handbook|OECD/JRC (2008)]] — handbook on constructing composite indicators
- 🟡 [[saisana_2005_uncertainty|Saisana, Saltelli & Tarantola (2005)]] — uncertainty/sensitivity analysis as quality-assessment for composite indicators (JRSS A)
- 🟡 [[efron_1977_stein|Efron & Morris (1977)]] — Stein's paradox; James-Stein shrinkage intuition
- 🟡 [[gelman_2013_bayesian|Gelman et al. (2013)]] — Bayesian Data Analysis 3rd ed.; conjugate normal-normal derivation of n/(n+K)
- 🟡 [[little_2002_statistical|Little & Rubin (2002)]] — statistical analysis with missing data; mean-imputation basis
- 🟡 [[draper_1998_applied|Draper & Smith (1998)]] — applied regression; linear slope as trajectory signal

### Time-decay weighting (EWMA + temporal CF)

- 🟡 [[hunter_1986_the|Hunter (1986)]] — the exponentially weighted moving average; canonical EWMA recursion (J. Quality Technology)
- 🟡 [[koren_2009_collaborative|Koren (2009)]] — collaborative filtering with temporal dynamics; explicit time-decay weighting in CF (KDD 2009 / CACM 2010)

### Gaming detection and unproductive persistence

- 🟡 [[baker_2008_why|Baker et al. (2008)]] — generalizable detector of when students game the system (UMUAI)
- 🟡 [[beck_2013_wheelspinning|Beck & Gong (2013)]] — wheel-spinning; failing to master a skill

### LLM-as-judge and LLMs in education

- 🟡 [[zheng_2023_judging|Zheng et al. (2023)]] — judging LLM-as-a-judge with MT-Bench and Chatbot Arena
- 🟡 [[kasneci_2023_chatgpt|Kasneci et al. (2023)]] — ChatGPT for good? opportunities and challenges of LLMs for education
- 🟡 [[chiang_2023_can|Chiang & Lee (2023)]] — can LLMs be an alternative to human evaluations?
- 🟡 [[liu_2023_geval|Liu et al. (2023)]] — G-Eval: NLG evaluation using GPT-4 with better human alignment
- 🟡 [[gilardi_2023_chatgpt|Gilardi, Alizadeh & Kubli (2023)]] — ChatGPT outperforms crowd-workers for text-annotation

---

## §2.1.5 Knowledge Tracing and Bayesian Student Models

Foundation for the BKT mastery module and improved struggle model.

- ✅ [[khajah_supercharging|Khajah]] — Supercharging BKT with multidimensional generalizable IRT and skill discovery (single-author summary; ERIC EJ1430505)
- 🟡 [[khajah_2014_incorporating|Khajah, Wing, Lindsey & Mozer (2014)]] — incorporating latent factors into KT; constructive BKT-with-IRT extension (EDM 2014); motivates 4-param BKT as the baseline to extend
- 🟡 [[khajah_2016_how|Khajah, Lindsey & Mozer (2016)]] — How deep is knowledge tracing? extended BKT matches DKT empirically (EDM 2016); justifies *not* jumping to DKT (interpretability)
- 🟡 [[corbett_1995_knowledge|Corbett & Anderson (1995)]] — knowledge tracing seminal paper (BKT origin)
- 🟡 [[yudelson_2013_individualized|Yudelson, Koedinger & Gordon (2013)]] — individualized Bayesian knowledge tracing
- 🟡 [[piech_2015_deep|Piech et al. (2015)]] — deep knowledge tracing; modern neural baseline

---

## §2.1.6 Modelling Task Difficulty

Difficulty model and IRT module.

### Core difficulty papers (currently cited)

- ✅ [[dannath_evaluating|Dannath et al.]] — task-level struggle in ITS; separate difficulty from ability
- ✅ [[frederikbaucks_2024_gaining|Baucks et al. (2024)]] — IRT reveals hidden course-difficulty patterns
- ✅ [[pankiewicz_measuring|Pankiewicz]] — multi-attempt environments complicate difficulty measurement
- ✅ [[baeres_2020_an|Baeres et al. (2020)]] — IRT-based course-difficulty analysis (also §2.2.3 EWS context)

### Classical Test Theory and Item Response Theory

- 🟡 [[rasch_1960_probabilistic|Rasch (1960)]] — origin of Rasch / 1PL model
- 🟡 [[lord_1968_statistical|Lord & Novick (1968)]] — classical test theory foundation
- 🟡 [[wright_1979_best|Wright & Stone (1979)]] — best test design; Rasch measurement practice
- 🟡 [[crocker_1986_introduction|Crocker & Algina (1986)]] — introduction to classical and modern test theory
- 🟡 [[fisher_1922_on|Fisher (1922)]] — mathematical foundations of theoretical statistics; MLE foundation

---

## §2.1.7 Collaborative Filtering

CF as alternative to scoring; foundational and educational refs.

- ✅ [[schafer_2007_collaborative|Schafer et al. (2007)]] — k-NN CF with cosine similarity
- ✅ [[deschnes_2020_recommender|Deschênes (2020)]] — recommender systems for education
- 🟡 [[herlocker_1999_an|Herlocker et al. (1999)]] — algorithmic framework for performing CF
- 🟡 [[resnick_1994_grouplens|Resnick et al. (1994)]] — GroupLens; open architecture for CF of netnews

---

## §2.1.8 Text Mining and Mistake Pattern Recovery

Grounds TF-IDF + K-means + silhouette in the mistake-clustering pipeline.

- 🟡 [[salton_1983_introduction|Salton & McGill (1983)]] — introduction to modern information retrieval
- 🟡 [[salton_1975_a|Salton, Wong & Yang (1975)]] — a vector space model for automatic indexing; canonical TF-IDF formulation
- 🟡 [[manning_2008_introduction|Manning, Raghavan & Schütze (2008)]] — modern TF-IDF + clustering textbook
- 🟡 [[macqueen_1967_some|MacQueen (1967)]] — K-means origin
- 🟡 [[lloyd_1982_least|Lloyd (1982)]] — Lloyd's algorithm; least-squares quantization
- 🟡 [[arthur_2007_kmeanspp|Arthur & Vassilvitskii (2007)]] — k-means++; advantages of careful seeding (sklearn default)
- 🟡 [[rousseeuw_1987_silhouettes|Rousseeuw (1987)]] — silhouettes; cluster-quality validation
- 🟡 [[han_2011_data|Han, Kamber & Pei (2011)]] — Data Mining: Concepts and Techniques

---

## §2.1.9 Retrieval-Augmented Generation for Instructor and Assistant Feedback

Phase 9 RAG pipeline (ChromaDB + sentence-transformers).

- 🟡 [[lewis_2020_retrievalaugmented|Lewis et al. (2020)]] — retrieval-augmented generation for knowledge-intensive NLP
- 🟡 [[reimers_2019_sentencebert|Reimers & Gurevych (2019)]] — Sentence-BERT; sentence embeddings via Siamese BERT
- 🟡 [[malkov_2020_efficient|Malkov & Yashunin (2020)]] — HNSW; efficient ANN search (TPAMI 42(4))

---

## §2.2.1 Learning Management Systems

- ✅ [[wikipediacontributors_2019_learning|Wikipedia (2019, LMS)]] — definition of learning management systems and Moodle

---

## §2.2.2 Instructor Facing Dashboards

- ✅ [[kiatxin_development|Kiat Xin et al.]] — Blocks: Progress Bar; ed-tech development
- ✅ [[leecultura_2023_multimodal|Lee & Cultura (2023)]] — EMODA / MM dashboard; multimodal sensors

---

## §2.2.3 Early Warning and At-Risk Student Systems

- ✅ [[a2020_atrisk|Anon. (2020)]] — edInsight at-risk scoring example
- ✅ [[macfadyenMiningLMSData2010|Macfadyen & Dawson (2010)]] — canonical EWS paper; mining LMS data
- ✅ [[arnoldCourseSignalsPurdue2012a|Arnold & Pistilli (2012)]] — Course Signals at Purdue; institutional EWS deployment
- ✅ [[jayaprakashEarlyAlertAcademically2014|Jayaprakash et al. (2014)]] — early-alert OAAI; multi-institution deployment

---

## Ch3 / Ch4 / Ch5 — refs not used in §2.1 / §2.2

### §3.4.2 IRT optimisation

- 🟡 [[byrd_1995_a|Byrd, Lu, Nocedal & Zhu (1995)]] — L-BFGS-B; bound-constrained optimisation

### §5 Evaluation Metrics (Ch5)

- 🟡 [[spearman_1904_the|Spearman (1904)]] — proof and measurement of association between two things
- 🟡 [[cohen_1960_a|Cohen (1960)]] — coefficient of agreement for nominal scales (kappa)
- 🟡 [[fawcett_2006_an|Fawcett (2006)]] — introduction to ROC analysis
- 🟡 [[hanley_1982_the|Hanley & McNeil (1982)]] — meaning and use of the area under an ROC curve
