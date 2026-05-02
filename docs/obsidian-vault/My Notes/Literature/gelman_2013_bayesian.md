---
citekey: gelman_2013_bayesian
status: planned
in_zotero: false
cited_in_tex: []
cited_in_planned:
  - Ch2 – Background and Requirements
  - Ch3 – Design and Modelling
  - Student Struggle Logic
last_synced: 2026-05-03
---
# Gelman, Carlin, Stern, Dunson, Vehtari & Rubin — Bayesian Data Analysis, 3rd Edition

Canonical textbook reference for Bayesian methods. Chapter 5 derives the conjugate normal–normal posterior, which produces the shrinkage formula `n/(n+K)` used directly in `analytics.py` (with `SHRINKAGE_K = 5` from `config.py`). This is the actual formula used in the dashboard, distinct from the Stein/Efron empirical-Bayes intuition (`efron_1977_stein`, kept as motivation).

Replaces `morris_1983_parametric` because Morris addresses *empirical* Bayes (estimating the prior from data), whereas the dashboard uses a fixed pseudo-count K — i.e. conjugate Bayes with a known hyperparameter, which is the textbook case in Gelman BDA.

Cited in: [[Ch2 – Background and Requirements]] · [[Ch3 – Design and Modelling]] · [[Student Struggle Logic]]
