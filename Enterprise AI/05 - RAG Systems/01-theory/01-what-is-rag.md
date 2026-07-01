# What is RAG?

Retrieval-Augmented Generation (RAG) is an architectural pattern that grounds LLM outputs in external, verifiable knowledge sources retrieved at inference time.

## The Problem RAG Solves

LLMs have two fundamental limitations:

| Limitation | Consequence | RAG Solution |
|---|---|---|
| **Knowledge cutoff** | Model can't know events after training | Retrieve from live/updated documents |
| **Parametric memory** | Facts are compressed into weights, lossy | Retrieve exact text passages |
| **Hallucination** | Model generates plausible but false content | Provide factual context to constrain generation |
| **No source attribution** | Can't verify where info came from | Retrieved passages serve as citations |
| **Static knowledge** | Can't update without retraining | Swap the document store instead |

## RAG Architecture (High-Level)

```
User Query
    │
    ▼
┌─────────────┐     ┌──────────────────┐
│  Query       │────>│  Retriever       │
│  Processor   │     │  (search index)  │
└─────────────┘     └────────┬─────────┘
                             │ top-k passages
                             ▼
┌─────────────┐     ┌──────────────────┐
│  Response    │<────│  LLM Generator   │
│  (citations) │     │  (context+query) │
└─────────────┘     └──────────────────┘
```

Three core stages:
1. **Index** — ingest documents → chunk → embed → store in vector DB
2. **Retrieve** — embed query → search index → fetch top-k passages
3. **Generate** — construct prompt (system + retrieved chunks + user query) → LLM → response with citations

## RAG vs. Fine-Tuning

| Aspect | RAG | Fine-Tuning |
|---|---|---|
| **Knowledge freshness** | Real-time (update index) | Requires re-training |
| **Factual accuracy** | High (sources provided) | Moderate (compressed in weights) |
| **Cost per query** | Higher (retrieval + generation) | Lower (generation only) |
| **Latency** | +5-50ms for retrieval | Baseline |
| **Data privacy** | Documents stay in your index | Training data in model weights |
| **Complexity** | Pipeline orchestration | Training infrastructure |
| **Best for** | Facts, citations, changing data | Style, tone, domain adaptation |

**Rule of thumb:** Prefer RAG for factual recall and citations. Prefer fine-tuning for behavior modification (tone, format, instruction following). Use both in production.

## When RAG Breaks

1. **Retriever fails** — if top-k passages don't contain the answer, the LLM hallucinates regardless of context quality
2. **Lost in the middle** — LLMs pay less attention to middle passages in long contexts (Liu et al., 2023)
3. **Context length limits** — can only retrieve K passages that fit in the context window
4. **Chunk boundary issues** — relevant information split across chunks, both missed
5. **Latency budget** — retrieval + re-ranking + generation must fit within user's tolerance

These are the problems that advanced RAG patterns (hierarchical, iterative, agentic) solve. The basic pipeline is insufficient for production.

## RAG Maturity Levels

| Level | Name | Characteristics |
|---|---|---|
| L1 | Naive RAG | Single retrieval, fixed chunking, basic prompt |
| L2 | Structured RAG | Hybrid search, re-ranking, query rewriting |
| L3 | Multi-Hop RAG | Iterative retrieval, decomposition |
| L4 | Agentic RAG | Tool use, dynamic retrieval decisions |
| L5 | Self-Improving RAG | Feedback loops, learned retrieval decisions |

Most production systems operate at L2-L3. L4-L5 are emerging patterns.
