# Resources — RAG Systems

## Foundational Papers

| Paper | Year | Contribution |
|---|---|---|
| [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) | 2020 | The original RAG paper (Lewis et al., Meta) |
| [REALM: Retrieval-Augmented Language Model Pre-Training](https://arxiv.org/abs/2002.08909) | 2020 | Early retrieval-augmented LM pre-training |
| [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172) | 2023 | U-shaped recall curve for long contexts |
| [Self-RAG: Learning to Retrieve, Generate, and Critique](https://arxiv.org/abs/2310.11511) | 2023 | Self-reflection + retrieval tokens |
| [Corrective RAG (CRAG)](https://arxiv.org/abs/2401.15884) | 2024 | Retrieval quality self-correction |
| [GraphRAG: Unlocking LLM Discovery on Narrative Private Data](https://arxiv.org/abs/2404.16130) | 2024 | Microsoft's hierarchical graph-based RAG |
| [RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval](https://arxiv.org/abs/2401.18059) | 2024 | Hierarchical document summarization for retrieval |
| [RAGAS: Automated Evaluation of Retrieval Augmented Generation](https://arxiv.org/abs/2309.15217) | 2023 | Reference-free RAG evaluation metrics |
| [REPLUG: Retrieval-Augmented Black-Box Language Models](https://arxiv.org/abs/2301.12652) | 2023 | RAG without fine-tuning the LLM |
| [HyDE: Precise Zero-Shot Dense Retrieval without Relevance Labels](https://arxiv.org/abs/2212.10496) | 2022 | Hypothetical Document Embeddings |
| [FRMT: RAG with Multi-Hop Reasoning](https://arxiv.org/abs/2310.06478) | 2023 | Multi-hop retrieval with reasoning |
| [Dense Passage Retrieval for Open-Domain QA](https://arxiv.org/abs/2004.04906) | 2020 | DPR — foundational dense retrieval system |

## Evaluation Frameworks

| Tool | Description |
|---|---|
| [RAGAS](https://docs.ragas.io/) | Reference-free RAG evaluation with LLM-as-judge |
| [TruLens](https://trulens.org/) | RAG quality tracking with groundedness, relevance, context metrics |
| [ARES](https://github.com/stanford-futuredata/ARES) | Fine-tuned evaluation classifiers for RAG |
| [DeepEval](https://docs.confident-ai.com/) | LLM evaluation framework with RAG-specific metrics |
| [LangSmith](https://smith.langchain.com/) | Tracing and evaluation platform for LangChain apps |
| [Phoenix (Arize)](https://github.com/Arize-AI/phoenix) | LLM observability with RAG evaluation |
| [MLflow Evaluate](https://mlflow.org/docs/latest/llms/llm-evaluate/) | MLflow's LLM evaluation capabilities |

## Production RAG Frameworks

| Framework | Description |
|---|---|
| [LangChain](https://www.langchain.com/) | Most popular RAG framework (Python + JS) |
| [LlamaIndex](https://www.llamaindex.ai/) | Data-centric RAG framework, strong indexing |
| [Haystack](https://haystack.deepset.ai/) | Production RAG framework by deepset |
| [Canopy](https://www.pinecone.io/blog/canopy/) | Pinecone's RAG framework |
| [R2R](https://github.com/SciPhi-AI/R2R) | Production-ready RAG API (Python) |
| [Vectara](https://vectara.com/) | Managed RAG API |
| [Cohere RAG](https://cohere.com/rag) | Cohere's managed RAG API |

## Chunking Libraries

| Library | Description |
|---|---|
| [LangChain Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/) | Recursive, semantic, document-aware, code |
| [Unstructured](https://unstructured.io/) | Enterprise document parsing + chunking |
| [Semantic Chunker](https://github.com/brandonstarxel/semantic_chunkers) | Embedding-based semantic chunking |
| [Jina Segmenter](https://jina.ai/segmenter/) | AI-powered text segmentation |
| [spaCy Sentencizer](https://spacy.io/api/sentencizer) | Rule-based sentence segmentation |

## Tutorials & Guides

- [Pinecone RAG Tutorial](https://www.pinecone.io/learn/rag/) — Comprehensive RAG guide
- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/) — Official LangChain guide
- [LlamaIndex RAG Starter](https://docs.llamaindex.ai/en/stable/getting_started/starter_example.html) — LlamaIndex RAG tutorial
- [RAG from Scratch (YouTube)](https://www.youtube.com/playlist?list=PLfaIDFEXuae2LXbO1_PKyALiERRU5Qf9i) — Video series by LangChain
- [Building RAG with Mistral and Qdrant](https://qdrant.tech/articles/rag-with-mistral/) — Qdrant's RAG guide
- [Advanced RAG Techniques](https://www.llamaindex.ai/blog/advanced-rag-techniques) — LlamaIndex blog post

## RAG Datasets

| Dataset | Description |
|---|---|
| [KILT](https://github.com/facebookresearch/KILT) | Knowledge-intensive language tasks benchmark |
| [Natural Questions](https://github.com/google-research-datasets/natural-questions) | Real Google queries with annotated passages |
| [MS MARCO](https://microsoft.github.io/msmarco/) | Bing queries with human-generated answers |
| [HotPotQA](https://hotpotqa.github.io/) | Multi-hop QA dataset |
| [TriviaQA](https://nlp.cs.washington.edu/triviaqa/) | Trivia questions with web evidence |
| [FiQA](https://sites.google.com/view/fiqa/) | Financial domain QA |

## Tools & Libraries

| Tool | Description |
|---|---|
| [Sentence-Transformers](https://sbert.net) | Embedding models for retrieval |
| [Cross-Encoder](https://www.sbert.net/examples/applications/cross-encoder/README.html) | Re-ranking (ms-marco-MiniLM) |
| [Rank-BM25](https://github.com/dorianbrown/rank_bm25) | Sparse retrieval |
| [FAISS](https://github.com/facebookresearch/faiss) | Vector search library |
| [Qdrant](https://qdrant.tech) | Vector database |
| [Milvus](https://milvus.io) | Distributed vector database |
| [Pinecone](https://pinecone.io) | Managed vector database |
