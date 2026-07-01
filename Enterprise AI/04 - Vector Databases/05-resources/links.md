# Resources — Vector Databases

## Foundational Papers

| Paper | Year | Contribution |
|---|---|---|
| [HNSW: Efficient and robust approximate nearest neighbor search](https://arxiv.org/abs/1603.09320) | 2016 | Hierarchical Navigable Small World graphs — the dominant ANN algorithm |
| [IVF: Product quantization for nearest neighbor search](https://hal.inria.fr/inria-00514462/document) | 2011 | IVF + PQ compression for large-scale ANN |
| [DiskANN: Fast accurate billion-point nearest neighbor search on a single node](https://papers.nips.cc/paper/2019/hash/09853c3157aeb9c33e8f50c3e5f8e9b0-Abstract.html) | 2019 | SSD-based ANN for billion-scale search |
| [SPTAG: Space Partition Tree And Graph](https://github.com/microsoft/SPTAG) | 2020 | Microsoft's distributed ANN (Bing search) |
| [Searching in billion-scale vector spaces](https://dl.acm.org/doi/10.1145/3340531.3411876) | 2020 | Distributed ANN design patterns |
| [ANN-Benchmarks: A benchmarking tool for approximate nearest neighbor algorithms](https://github.com/erikbern/ann-benchmarks) | 2017 | Standard ANN benchmarking framework |
| [Efficient Estimation of Word Representations in Vector Space](https://arxiv.org/abs/1301.3781) | 2013 | Word2Vec — origins of modern vector representations |
| [Reciprocal Rank Fusion](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) | 2009 | Fusion method for hybrid search |
| [Scalable Nearest Neighbor Algorithms for High Dimensional Data](https://ieeexplore.ieee.org/document/6809191) | 2014 | Comparative analysis of ANN algorithms |
| [Approximate Nearest Neighbor Search on High-Dimensional Data — Experiments, Analyses, and Improvement](https://arxiv.org/abs/1610.02455) | 2016 | Comprehensive ANN survey and benchmarking |

## Official Documentation

| Database | Docs | Key Page |
|---|---|---|
| **FAISS** | [faiss.ai](https://faiss.ai) | [Index factory](https://github.com/facebookresearch/faiss/wiki/The-index-factory) |
| **pgvector** | [github.com/pgvector/pgvector](https://github.com/pgvector/pgvector) | [README with examples](https://github.com/pgvector/pgvector#usage) |
| **Qdrant** | [qdrant.tech/documentation](https://qdrant.tech/documentation) | [Filtering](https://qdrant.tech/documentation/filtering/) |
| **Milvus** | [milvus.io/docs](https://milvus.io/docs) | [Index types](https://milvus.io/docs/index.md) |
| **Pinecone** | [docs.pinecone.io](https://docs.pinecone.io) | [Indexes and pods](https://docs.pinecone.io/docs/indexes) |
| **Weaviate** | [weaviate.io/developers/weaviate](https://weaviate.io/developers/weaviate) | [Vector index properties](https://weaviate.io/developers/weaviate/config-refs/vector-index) |

## Tutorials & Guides

- [FAISS The Missing Manual](https://github.com/facebookresearch/faiss/wiki) — official FAISS wiki
- [Qdrant Vector Search Tutorial](https://qdrant.tech/articles/) — practical guides and benchmarks
- [Milvus Bootcamp](https://github.com/milvus-io/bootcamp) — end-to-end examples (RAG, recommendation, image search)
- [Pinecone Learn](https://www.pinecone.io/learn/) — vector database concepts and tutorials
- [pgvector Recipes](https://github.com/pgvector/pgvector?tab=readme-ov-file#recipes) — community examples
- [ANN-Benchmarks](https://ann-benchmarks.com/) — public leaderboard of algorithms and configurations

## Benchmarks

| Source | Scope |
|---|---|
| [ANN-Benchmarks](https://ann-benchmarks.com/) | Algorithm-level comparison (FAISS, HNSWlib, etc.) |
| [VectorDBBench](https://github.com/zilliztech/VectorDBBench) | Database-level comparison (Qdrant, Milvus, Pinecone, Weaviate) |
| [DB-Engines Vector DBMS Ranking](https://db-engines.com/en/ranking/vector+dbms) | Popularity/ecosystem ranking |
| [Milvus Benchmark](https://milvus.io/docs/benchmark.md) | Milvus vs. Qdrant vs. Pinecone (vendor-published) |
| [Qdrant Benchmark](https://qdrant.tech/benchmarks/) | Qdrant internal benchmarks |
| [Erik Bernhardsson's ANN benchmarks](https://github.com/erikbern/ann-benchmarks) | The original ANN algorithm benchmark |

## Tools & Libraries

| Tool | Description |
|---|---|
| [FAISS](https://github.com/facebookresearch/faiss) | Core ANN library from Meta |
| [HNSWlib](https://github.com/nmslib/hnswlib) | Standalone HNSW implementation |
| [USearch](https://github.com/unum-cloud/usearch) | Faster, smaller FAISS alternative in C |
| [Voyager](https://github.com/spotify/voyager) | Spotify's ANN library (Rust, HNSW-based) |
| [Vald](https://github.com/vdaas/vald) | Cloud-native, Kubernetes-native vector DB |
| [Chroma](https://github.com/chroma-core/chroma) | Developer-friendly embedded vector DB (Python) |
| [Weaviate](https://github.com/weaviate/weaviate) | Graph + vector DB |
| [LanceDB](https://github.com/lancedb/lancedb) | Serverless vector DB built on Lance columnar format |
| [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/dense-vector.html) | Dense vector support in ES 8.x+ |
| [Redis Stack](https://redis.io/docs/latest/develop/interact/search-and-query/) | Vector similarity search in Redis |

## Books

- [Milvus in Action](https://www.manning.com/books/milvus-in-action) — Manning, practical Milvus guide
- [Deep Learning for Search](https://www.manning.com/books/deep-learning-for-search) — Manning, semantic search and vector embeddings
- [AI-Powered Search](https://www.manning.com/books/ai-powered-search) — Manning, modern search with vectors

## Courses

- [Vector Database Course (Pinecone)](https://www.pinecone.io/learn/) — free, comprehensive
- [CS 410: Text Information Systems (UIUC)](https://wiki.illinois.edu/wiki/display/cs410) — Information retrieval fundamentals
- [Stanford CS 224N: NLP with Deep Learning](https://web.stanford.edu/class/cs224n/) — Word vectors and embeddings origins
