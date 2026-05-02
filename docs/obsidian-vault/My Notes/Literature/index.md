# Literature Index

All academic references cited in the thesis and implementation notes, grouped by theme.

Related: [[Ch2 – Background and Requirements]], [[Ch3 – Design and Modelling]], [[Thesis Overview]]

---

## Learning Analytics — Foundations

Core definitions and surveys of the LA field.

- [[verbert_2020_learning|Verbert et al. (2020)]] — dashboard design principles; interpretability as key requirement
- [[wilson_2017_learning|Wilson et al. (2017)]] — LA in higher education; privacy and scalability concerns
- [[klerkx_2017_learning|Klerkx et al. (2017)]] — dashboard taxonomy; course-level vs session-level gap
- [[wikipediacontributors_2019_learning|Wikipedia (2019)]] — working definition of learning analytics

---

## Dashboards and Visualisation

Prior systems and visual analytics approaches surveyed in Ch2.

- [[govaerts_the|Govaerts et al.]] — SAM dashboard; separates at-risk from on-track students
- [[vieira_2018_visual|Vieira et al. (2018)]] — visual analytics in education
- [[leecultura_2023_multimodal|Lee & Cultura (2023)]] — EMODA multimodal dashboard (audio/video/self-reports)
- [[mustafaayobamiraji_2024_realtime|Mustafa, Ayobami & Raji (2024)]] — real-time analytics feasibility
- [[gelan_2018_affordances|Gelan et al. (2018)]] — affordances of analytics tools; what features instructors actually use

---

## Real-Time Analytics

Motivation for live over post-session monitoring.

- [[marr_2021_what|Marr (2021)]] — cross-industry case for real-time analytics
- [[nguyen_2020_data|Nguyen et al. (2020)]] — data-driven approaches in education
- [[li_2020_course|Li et al. (2020)]] — course-level analytics and temporal granularity

---

## Student Struggle Modelling

Papers directly informing the struggle model signals and design.

- [[dong_using|Dong et al.]] — session-level struggle detection (77% accuracy)
- [[or_2024_exploring|Or (2024)]] — novice programmer testing; 4+ consecutive failures threshold
- [[estey_2017_automatically|Estey et al. (2017)]] — trajectory metric; 11% false-positive rate
- [[piech_modeling|Piech et al.]] — graphical model of student progression paths
- [[ahn_2019_the|Ahn (2019)]] — learning progression framework
- [[kim_knowledge|Kim et al.]] — knowledge tracing with student questions
- [[koutcheme_using|Koutcheme et al.]] — LLM-based answer quality; repair correlates with explanation
- [[pitts_a|Pitts et al.]] — LLMs best with human oversight

---

## BKT and Knowledge Tracing

Foundation for the BKT mastery module and improved struggle model.

- [[khajah_supercharging|Khajah et al.]] — strengthening BKT with IRT-like structure

---

## Task and Question Difficulty

Papers informing the difficulty model and IRT module.

- [[dannath_evaluating|Dannath et al.]] — task-level struggle in ITS; separate difficulty from ability
- [[frederikbaucks_2024_gaining|Baucks et al. (2024)]] — IRT reveals hidden difficulty patterns
- [[pankiewicz_measuring|Pankiewicz]] — multi-attempt environments complicate difficulty measurement
- [[baeres_2020_an|Baeres et al. (2020)]] — IRT-based course difficulty analysis

---

## Collaborative Filtering

Foundation for the CF diagnostic layer in the analytics engine.

- [[schafer_2007_collaborative|Schafer et al. (2007)]] — k-NN CF with cosine similarity
- [[deschnes_2020_recommender|Deschnes (2020)]] — recommender systems for education

---

## Early Warning Systems

At-risk and early warning systems surveyed as existing solutions.

- [[a2020_atrisk|Anon. (2020)]] — at-risk identification framework
- [[a2022_early|Anon. (2022)]] — early warning system for student performance
- [[a2023_real|Anon. (2023)]] — real-time early warning framework

---

## Ethics, Design, and Context

Broader contextual references.

- [[tzimas_2021_ethical|Tzimas et al. (2021)]] — ethical considerations (privacy, consent, fairness)
- [[dasilva_2022_a|Da Silva et al. (2022)]] — learning analytics system architecture
- [[montebello_assisting|Montebello]] — AI-assisted instructor and student support
- [[kiatxin_development|Kiat Xin et al.]] — educational technology development methodology

---

## 2026-04-24 additions — new groupings

Added based on the 2026-04-24 literature-gap audit ([[Rewrite Queue#2026-04-24 additions — post-Phase-11 polish]] + direct code-vs-literature cross-check). Each entry has a matching stub in this folder.

### Formative Assessment and Feedback Theory

Educational-theory grounding for the whole "monitor-and-intervene" loop the dashboard implements.

- [[black_1998_assessment|Black & Wiliam (1998)]] — seminal paper on formative assessment; grounds the monitor-and-intervene premise
- [[shute_2008_focus|Shute (2008)]] — focus on formative feedback: types, timing, effectiveness; frames the RAG suggested-feedback layer
- [[hattie_2007_the|Hattie & Timperley (2007)]] — the power of feedback: task / process / self-regulation / self levels

### Teacher-Facing Orchestration Analytics

Instructor-side analytics as a distinct category from student-side.

- [[holstein_2018_student|Holstein, McLaren & Aleven (2018)]] — mixed-reality teacher awareness tool; validates the teacher-facing analytics category
- [[holstein_2017_intelligent|Holstein, McLaren & Aleven (2017)]] — intelligent tutors as teachers' aides; instructor needs for real-time analytics

### Learning Analytics Surveys

Canonical framing papers for Ch2 §2.1.1.

- [[romero_2020_educational|Romero & Ventura (2020)]] — updated survey of EDM and LA; modern framing paper
- [[siemens_2013_learning|Siemens (2013)]] — emergence of learning analytics as a discipline
- [[clow_2013_an|Clow (2013)]] — overview of LA; learning analytics cycle

### At-Risk Identification and Early Warning

Canonical early-warning references to replace the three anonymous citations.

- [[macfadyenMiningLMSData2010|Macfadyen & Dawson (2010)]] — mining LMS data for early warning; the canonical EWS paper
- [[arnoldCourseSignalsPurdue2012a|Arnold & Pistilli (2012)]] — Course Signals at Purdue; canonical institutional EWS deployment
- [[jayaprakashEarlyAlertAcademically2014|Jayaprakash et al. (2014)]] — early alert for academically at-risk students (open-source initiative)

### Gaming Detection and Unproductive Persistence

Grounds the `r_hat` (retry rate) and `rep_hat` (answer repetition) signals in the 7-signal struggle model.

- [[baker_2008_why|Baker et al. (2008)]] — generalizable detector of when students game the system (UMUAI)
- [[beck_2013_wheelspinning|Beck & Gong (2013)]] — wheel-spinning: students who fail to master a skill

### LLM-as-Judge and LLM-in-Education

Grounds gpt-4o-mini incorrectness scoring and the broader use of LLMs in the pipeline.

- [[zheng_2023_judging|Zheng et al. (2023)]] — judging LLM-as-a-judge with MT-Bench and Chatbot Arena
- [[kasneci_2023_chatgpt|Kasneci et al. (2023)]] — ChatGPT for good? opportunities and challenges of LLMs for education
- [[chiang_2023_can|Chiang & Lee (2023)]] — can LLMs be an alternative to human evaluations?
- [[liu_2023_geval|Liu et al. (2023)]] — G-Eval: NLG evaluation using GPT-4 with better human alignment
- [[gilardi_2023_chatgpt|Gilardi, Alizadeh & Kubli (2023)]] — ChatGPT outperforms crowd-workers for text-annotation tasks

### Classical Test Theory and Item Response Theory

Foundational IRT and measurement-theory references for Ch3 §3.4.1 and §3.4.2.

- [[rasch_1960_probabilistic|Rasch (1960)]] — probabilistic models for some intelligence and attainment tests; origin of Rasch/1PL model
- [[lord_1968_statistical|Lord & Novick (1968)]] — statistical theories of mental test scores; classical test theory foundation
- [[wright_1979_best|Wright & Stone (1979)]] — best test design; Rasch measurement practice
- [[crocker_1986_introduction|Crocker & Algina (1986)]] — introduction to classical and modern test theory
- [[fisher_1922_on|Fisher (1922)]] — on the mathematical foundations of theoretical statistics; MLE foundational paper

### Knowledge Tracing — Foundations

Extends the BKT grouping with the seminal Corbett & Anderson paper and modern baselines.

- [[corbett_1995_knowledge|Corbett & Anderson (1995)]] — knowledge tracing: modeling the acquisition of procedural knowledge; BKT seminal paper
- [[yudelson_2013_individualized|Yudelson, Koedinger & Gordon (2013)]] — individualized Bayesian knowledge tracing models
- [[piech_2015_deep|Piech et al. (2015)]] — deep knowledge tracing; modern neural baseline for KT

### Composite Indicators and Bayesian Shrinkage

Grounds the weighted-sum struggle/difficulty formulas and the `n/(n+K)` shrinkage pull toward class mean.

- [[oecd_2008_handbook|OECD/JRC (2008)]] — handbook on constructing composite indicators
- [[saisana_2005_uncertainty|Saisana, Saltelli & Tarantola (2005)]] — uncertainty and sensitivity analysis as quality-assessment tools for composite indicators (JRSS A)
- [[efron_1977_stein|Efron & Morris (1977)]] — Stein's paradox in statistics; James-Stein shrinkage
- [[gelman_2013_bayesian|Gelman et al. (2013)]] — Bayesian Data Analysis, 3rd ed.; conjugate normal-normal derivation of n/(n+K) shrinkage
- [[little_2002_statistical|Little & Rubin (2002)]] — statistical analysis with missing data; mean-imputation basis
- [[draper_1998_applied|Draper & Smith (1998)]] — applied regression analysis; linear slope as trajectory signal

### Time-Decay Weighting (EWMA + Temporal CF)

Grounds the exponential time-decay in `A_raw` (30-minute half-life) and the future EWMA smoothing layer.

- [[hunter_1986_the|Hunter (1986)]] — the exponentially weighted moving average; canonical EWMA reference (J. Quality Technology)
- [[koren_2009_collaborative|Koren (2009)]] — collaborative filtering with temporal dynamics; explicit time-decay weighting in CF (KDD 2009 / CACM 2010)

### Text Mining, Clustering, and Information Retrieval

Grounds TF-IDF + K-means + silhouette in the mistake-clustering pipeline.

- [[salton_1983_introduction|Salton & McGill (1983)]] — introduction to modern information retrieval
- [[salton_1975_a|Salton, Wong & Yang (1975)]] — a vector space model for automatic indexing; canonical TF-IDF / vector-space formulation
- [[manning_2008_introduction|Manning, Raghavan & Schütze (2008)]] — introduction to information retrieval; modern TF-IDF + clustering textbook
- [[macqueen_1967_some|MacQueen (1967)]] — some methods for classification and analysis of multivariate observations; K-means origin
- [[lloyd_1982_least|Lloyd (1982)]] — least squares quantization in PCM; Lloyd's algorithm
- [[arthur_2007_kmeanspp|Arthur & Vassilvitskii (2007)]] — k-means++: the advantages of careful seeding
- [[rousseeuw_1987_silhouettes|Rousseeuw (1987)]] — silhouettes: a graphical aid to interpretation and validation of cluster analysis
- [[han_2011_data|Han, Kamber & Pei (2011)]] — data mining: concepts and techniques

### Retrieval-Augmented Generation and Embeddings

Grounds the Phase 9 RAG pipeline (ChromaDB + sentence-transformers).

- [[lewis_2020_retrievalaugmented|Lewis et al. (2020)]] — retrieval-augmented generation for knowledge-intensive NLP tasks
- [[reimers_2019_sentencebert|Reimers & Gurevych (2019)]] — Sentence-BERT: sentence embeddings using Siamese BERT networks
- [[malkov_2020_efficient|Malkov & Yashunin (2020)]] — efficient and robust approximate nearest neighbor search (HNSW)

### Collaborative Filtering — Foundations

Extends the CF grouping with the canonical citations.

- [[herlocker_1999_an|Herlocker et al. (1999)]] — algorithmic framework for performing collaborative filtering
- [[resnick_1994_grouplens|Resnick et al. (1994)]] — GroupLens: an open architecture for collaborative filtering of netnews

### Optimisation

Reference for the L-BFGS-B solver used in IRT fitting.

- [[byrd_1995_a|Byrd et al. (1995)]] — a limited memory algorithm for bound constrained optimization (L-BFGS-B)

### Evaluation Metrics

Reference for agreement / correlation / ROC metrics reported in Ch5.

- [[spearman_1904_the|Spearman (1904)]] — the proof and measurement of association between two things
- [[cohen_1960_a|Cohen (1960)]] — a coefficient of agreement for nominal scales (kappa)
- [[fawcett_2006_an|Fawcett (2006)]] — an introduction to ROC analysis
- [[hanley_1982_the|Hanley & McNeil (1982)]] — the meaning and use of the area under an ROC curve
