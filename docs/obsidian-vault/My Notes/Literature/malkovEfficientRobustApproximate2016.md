---
category: literaturenote
citekey: malkovEfficientRobustApproximate2016
year: 2016
in_zotero: true
status: active
last_imported: 2026-05-04
tags: [Computer Vision and Pattern Recognition (cs.CV), Data Structures and Algorithms (cs.DS), FOS: Computer and information sciences, Information Retrieval (cs.IR), Social and Information Networks (cs.SI)]
---

# Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs

> [!Cite]
> [1]

Yu. A. Malkov and D. A. Yashunin, ‘Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs’, 2016, _arXiv_. doi: [10.48550/ARXIV.1603.09320](https://doi.org/10.48550/ARXIV.1603.09320).

> [!Synth]
> **Contribution**::
>
> **Related**:: 

> [!md]
> **FirstAuthor**:: Malkov, Yu. A.
> **Author**:: Yashunin, D. A.
~
> **Title**:: Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs
> **Year**:: 2016
> **Citekey**:: malkovEfficientRobustApproximate2016
> **itemType**:: preprint
> **DOI**:: 10.48550/ARXIV.1603.09320

> [!LINK]
>

> [!Abstract]
>
> We present a new approach for the approximate K-nearest neighbor search based on navigable small world graphs with controllable hierarchy (Hierarchical NSW, HNSW). The proposed solution is fully graph-based, without any need for additional search structures, which are typically used at the coarse search stage of the most proximity graph techniques. Hierarchical NSW incrementally builds a multi-layer structure consisting from hierarchical set of proximity graphs (layers) for nested subsets of the stored elements. The maximum layer in which an element is present is selected randomly with an exponentially decaying probability distribution. This allows producing graphs similar to the previously studied Navigable Small World (NSW) structures while additionally having the links separated by their characteristic distance scales. Starting search from the upper layer together with utilizing the scale separation boosts the performance compared to NSW and allows a logarithmic complexity scaling. Additional employment of a heuristic for selecting proximity graph neighbors significantly increases performance at high recall and in case of highly clustered data. Performance evaluation has demonstrated that the proposed general metric space search index is able to strongly outperform previous opensource state-of-the-art vector-only approaches. Similarity of the algorithm to the skip list structure allows straightforward balanced distributed implementation.
>

# Notes%% begin annotations %%
## Summary

_Hand-written summary lives here. Survives re-imports. PDF annotations append below._



%% end annotations %%


%% Import Date: 2026-05-04T22:59:12.648+01:00 %%
