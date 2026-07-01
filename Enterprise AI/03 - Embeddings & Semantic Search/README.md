# Embeddings & Semantic Search

Dense vector representations of text and their use in similarity search.

## Directory Structure

```
01-theory/                   # Deep dives into embedding concepts
├── 01-what-are-embeddings.md
├── 02-embedding-models.md
├── 03-contrastive-learning.md
├── 04-similarity-metrics.md
├── 05-bi-encoders-vs-cross-encoders.md
├── 06-sparse-embeddings.md
├── 07-hybrid-search.md
├── 08-evaluation-metrics.md
├── 09-embedding-quantization.md
└── 10-multi-modal-embeddings.md

02-code/                     # Runnable scripts
├── 01-generate-embeddings.py           — Compare model quality, dims, speed
├── 02-semantic-search.py               — End-to-end search pipeline
├── 03-bi-encoder-vs-cross-encoder.py   — Retrieve vs re-rank comparison
├── 04-hybrid-search-implementation.py  — BM25 + dense + RRF
├── 05-train-embedding-model.py         — Fine-tune with contrastive loss
├── 06-evaluate-retrieval.py            — Recall@k, MRR, NDCG harness
├── 07-embedding-quantization.py        — FP32 vs INT8 vs binary
├── 08-multi-modal-search.py            — Text-to-image with CLIP
├── 09-visualize-embeddings.py          — PCA/UMAP projections
└── 10-benchmark-embedding-models.py    — Speed/recall decision table

03-best-practices/           # Production guidance
├── 01-model-selection.md
├── 02-normalization-and-metrics.md
├── 03-domain-adaptation.md
├── 04-embedding-caching-and-cost.md
└── 05-embedding-drift-monitoring.md

04-resources/                # Papers, tools, courses
└── links.md
```

## Prerequisites

- Python 3.10+
- `pip install sentence-transformers numpy rank-bm25 scikit-learn matplotlib`
- Optional: `pip install umap-learn torch transformers Pillow` (for UMAP, CLIP)

## Suggested Learning Path

1. **Theory:** what-are-embeddings → similarity-metrics → embedding-models → bi-encoders-vs-cross-encoders
2. **Code:** generate-embeddings → semantic-search → hybrid-search → bi-encoder-vs-cross-encoder
3. **Evaluate:** evaluate-retrieval → benchmark-embedding-models → embedding-quantization
4. **Advanced:** train-embedding-model → domain-adaptation → embedding-drift-monitoring
5. **Production:** model-selection → normalization-and-metrics → caching-and-cost
