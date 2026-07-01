# Resources

## Foundational Papers

| Paper | Year | Contribution |
|---|---|---|
| [SimCSE: Simple Contrastive Learning of Sentence Embeddings](https://arxiv.org/abs/2104.08821) | 2021 | Contrastive learning without labeled pairs |
| [E5: Text Embeddings by Weakly-Supervised Contrastive Pre-training](https://arxiv.org/abs/2212.03533) | 2022 | Strong open-source embedding model |
| [BGE: C-Pack: Packaged Resources For Advanced Chinese Embeddings](https://arxiv.org/abs/2309.07597) | 2023 | BGE model family |
| [SPLADE: Sparse Lexical and Expansion Model for First Stage Ranking](https://arxiv.org/abs/2107.05720) | 2021 | Learned sparse embeddings |
| [ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction](https://arxiv.org/abs/2004.12832) | 2020 | Late interaction (retrieve + score jointly) |
| [Contriever: Unsupervised Dense Information Retrieval](https://arxiv.org/abs/2112.09118) | 2021 | Unsupervised dense retrieval |
| [DPR: Dense Passage Retrieval for Open-Domain Question Answering](https://arxiv.org/abs/2004.04906) | 2020 | Bi-encoder retrieval |
| [Matryoshka Representation Learning](https://arxiv.org/abs/2205.13147) | 2022 | Flexible-dimension embeddings |
| [CLIP: Learning Transferable Visual Models From Natural Language Supervision](https://arxiv.org/abs/2103.00020) | 2021 | Multi-modal embeddings |
| [Reciprocal Rank Fusion](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) | 2009 | Hybrid search fusion method |

## Retrieval Benchmarks

| Benchmark | Description |
|---|---|
| [MTEB (Massive Text Embedding Benchmark)](https://huggingface.co/spaces/mteb/leaderboard) | 58 datasets across 8 tasks — the standard leaderboard |
| [BEIR (Benchmarking IR)](https://github.com/beir-cellar/beir) | 18 retrieval datasets, zero-shot evaluation |
| [MS MARCO Passage Ranking](https://microsoft.github.io/msmarco/) | 1M queries, passage ranking — the most common IR benchmark |
| [LoTTE (Long-Tail Topic-stratified)](https://github.com/nickilotte/LoTTE) | Long-tail retrieval eval (good for RAG testing) |

## Tools & Libraries

| Tool | Description |
|---|---|
| [Sentence-Transformers](https://sbert.net) | Primary library for embedding models |
| [FlagEmbedding (BGE)](https://github.com/FlagOpen/FlagEmbedding) | BGE model training and inference |
| [FAISS](https://github.com/facebookresearch/faiss) | Vector similarity search library |
| [USearch](https://github.com/unum-cloud/usearch) | Smaller, faster alternative to FAISS |
| [Milvus](https://milvus.io) | Distributed vector database |
| [Qdrant](https://qdrant.tech) | Rust-based vector database |
| [Rank-BM25](https://github.com/dorianbrown/rank_bm25) | BM25 implementation for sparse retrieval |
| [Pinecone](https://pinecone.io) | Managed vector database |

## Courses & Guides

- [Cohere Embedding Course](https://cohere.com/llmu) — LLM University, embedding module
- [Sentence-Transformers Training Guide](https://www.sbert.net/docs/training/overview.html) — official fine-tuning guide
- [FAISS The Missing Manual](https://github.com/facebookresearch/faiss/wiki) — FAISS documentation and tutorials
