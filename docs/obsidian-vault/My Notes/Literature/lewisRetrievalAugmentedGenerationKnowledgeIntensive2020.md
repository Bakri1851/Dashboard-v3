---
category: literaturenote
citekey: lewisRetrievalAugmentedGenerationKnowledgeIntensive2020
year: 2020
in_zotero: true
status: active
last_imported: 2026-05-05
tags: [Computation and Language (cs.CL), FOS: Computer and information sciences, Machine Learning (cs.LG)]
cited_in_tex:
  - Report/main-sections/requirements-specification.tex:188
  - Report/main-sections/requirements-specification.tex:189
  - Report/main-sections/requirements-specification.tex:190
  - Report/main-sections/requirements-specification.tex:195
cited_in_planned: []
last_synced: 2026-05-05
---
# Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks

%% Begin annotations %%
## Summary

> [!Cite]
> [1]

P. Lewis _et al._, ‘Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks’, 2020, _arXiv_. doi: [10.48550/ARXIV.2005.11401](https://doi.org/10.48550/ARXIV.2005.11401).

> [!Synth]
> **Contribution**::
>
> **Related**:: 

> [!md]
> **FirstAuthor**:: Lewis, Patrick
> **Author**:: Perez, Ethan
> **Author**:: Piktus, Aleksandra
> **Author**:: Petroni, Fabio
> **Author**:: Karpukhin, Vladimir
> **Author**:: Goyal, Naman
> **Author**:: Küttler, Heinrich
> **Author**:: Lewis, Mike
> **Author**:: Yih, Wen-tau
> **Author**:: Rocktäschel, Tim
> **Author**:: Riedel, Sebastian
> **Author**:: Kiela, Douwe
~
> **Title**:: Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
> **Year**:: 2020
> **Citekey**:: lewisRetrievalAugmentedGenerationKnowledgeIntensive2020
> **itemType**:: preprint
> **DOI**:: 10.48550/ARXIV.2005.11401

> [!LINK]
>

> [!Abstract]
>
> Large pre-trained language models have been shown to store factual knowledge in their parameters, and achieve state-of-the-art results when fine-tuned on downstream NLP tasks. However, their ability to access and precisely manipulate knowledge is still limited, and hence on knowledge-intensive tasks, their performance lags behind task-specific architectures. Additionally, providing provenance for their decisions and updating their world knowledge remain open research problems. Pre-trained models with a differentiable access mechanism to explicit non-parametric memory can overcome this issue, but have so far been only investigated for extractive downstream tasks. We explore a general-purpose fine-tuning recipe for retrieval-augmented generation (RAG) -- models which combine pre-trained parametric and non-parametric memory for language generation. We introduce RAG models where the parametric memory is a pre-trained seq2seq model and the non-parametric memory is a dense vector index of Wikipedia, accessed with a pre-trained neural retriever. We compare two RAG formulations, one which conditions on the same retrieved passages across the whole generated sequence, the other can use different passages per token. We fine-tune and evaluate our models on a wide range of knowledge-intensive NLP tasks and set the state-of-the-art on three open domain QA tasks, outperforming parametric seq2seq models and task-specific retrieve-and-extract architectures. For language generation tasks, we find that RAG models generate more specific, diverse and factual language than a state-of-the-art parametric-only seq2seq baseline.
>

# Notes%% begin annotations %%
## Summary

_Hand-written summary lives here. Survives re-imports. PDF annotations append below._



## Summary

_Hand-written summary lives here. Survives re-imports. PDF annotations append below._



%% end annotations %%


%% Import Date: 2026-05-05T18:39:58.562+01:00 %%
%% End annotations %%
