---
category: literaturenote
citekey: wangGoalDrivenExplainableClustering2023
year: 2023
in_zotero: true
status: active
last_imported: 2026-05-04
tags: [Computation and Language (cs.CL), FOS: Computer and information sciences]
---

# Goal-Driven Explainable Clustering via Language Descriptions

> [!Cite]
> [1]

Z. Wang, J. Shang, and R. Zhong, ‘Goal-Driven Explainable Clustering via Language Descriptions’, 2023, _arXiv_. doi: [10.48550/ARXIV.2305.13749](https://doi.org/10.48550/ARXIV.2305.13749).

> [!Synth]
> **Contribution**::
>
> **Related**:: 

> [!md]
> **FirstAuthor**:: Wang, Zihan
> **Author**:: Shang, Jingbo
> **Author**:: Zhong, Ruiqi
~
> **Title**:: Goal-Driven Explainable Clustering via Language Descriptions
> **Year**:: 2023
> **Citekey**:: wangGoalDrivenExplainableClustering2023
> **itemType**:: preprint
> **DOI**:: 10.48550/ARXIV.2305.13749

> [!LINK]
>

> [!Abstract]
>
> Unsupervised clustering is widely used to explore large corpora, but existing formulations neither consider the users' goals nor explain clusters' meanings. We propose a new task formulation, "Goal-Driven Clustering with Explanations" (GoalEx), which represents both the goal and the explanations as free-form language descriptions. For example, to categorize the errors made by a summarization system, the input to GoalEx is a corpus of annotator-written comments for system-generated summaries and a goal description "cluster the comments based on why the annotators think the summary is imperfect.''; the outputs are text clusters each with an explanation ("this cluster mentions that the summary misses important context information."), which relates to the goal and precisely explain which comments should (not) belong to a cluster. To tackle GoalEx, we prompt a language model with "[corpus subset] + [goal] + Brainstorm a list of explanations each representing a cluster."; then we classify whether each sample belongs to a cluster based on its explanation; finally, we use integer linear programming to select a subset of candidate clusters to cover most samples while minimizing overlaps. Under both automatic and human evaluation on corpora with or without labels, our method produces more accurate and goal-related explanations than prior methods. We release our data and implementation at https://github.com/ZihanWangKi/GoalEx.
>

# Notes%% begin annotations %%
## Summary

_Hand-written summary lives here. Survives re-imports. PDF annotations append below._



%% end annotations %%


%% Import Date: 2026-05-04T22:59:13.846+01:00 %%
