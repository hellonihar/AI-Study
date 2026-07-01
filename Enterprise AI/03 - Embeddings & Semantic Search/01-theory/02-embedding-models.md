# Embedding Models

A survey of popular embedding models and their production characteristics.

## Model Comparison

| Model | Dimensions | Max Tokens | MTEB Score | Latency (rel) | Cost | Best For |
|---|---|---|---|---|---|---|
| **OpenAI text-embedding-3-small** | 512 | 8191 | 62.3 | Fast | $0.02/1M tok | General purpose, API-friendly |
| **OpenAI text-embedding-3-large** | 3072 | 8191 | 64.6 | Moderate | $0.13/1M tok | Highest quality via API |
| **BGE-base-en-v1.5** | 768 | 512 | 63.0 | Fast | Free (self-host) | Chinese + English, strong all-rounder |
| **BGE-large-en-v1.5** | 1024 | 512 | 64.2 | Moderate | Free | Highest quality open-source |
| **E5-mistral-7b-instruct** | 4096 | 4096 | 66.6 | Slow | Free | Best open-source, huge dims |
| **Cohere Embed v3** | 1024 | 512 | 64.0 | Fast | $0.10/1M tok | Enterprise features, multilingual |
| **Voyage-2** | 1024 | 4000 | 64.1 | Fast | $0.10/1M tok | Long context, code-aware |
| **GTE-Qwen2-7B** | 3584 | 8192 | 66.2 | Slow | Free | Best multilingual open-source |
| **all-MiniLM-L6-v2** | 384 | 256 | 58.8 | Very fast | Free | Quick prototyping, small scale |

## Choosing a Model

```
Budget?
├── API ($) → OpenAI text-embedding-3-small (best price/quality)
├── Self-host (GPU) → BGE-large-en-v1.5 (fast) or E5-mistral (best quality)
└── Self-host (CPU) → all-MiniLM-L6-v2 or BGE-small

Domain?
├── General English → BGE-base or OpenAI text-embedding-3-small
├── Chinese + English → BGE-base-zh or GTE-Qwen2
├── Code-heavy → Voyage-2 or OpenAI text-embedding-3
└── Legal/Medical → fine-tune BGE-base on domain data

Latency requirement?
├── < 5ms per embedding → all-MiniLM-L6-v2 (384 dims)
├── < 20ms → BGE-base (768 dims, ONNX)
└── < 100ms → E5-mistral (requires GPU)
```

## The MTEB Benchmark

The Massive Text Embedding Benchmark (MTEB) evaluates models across:
- **Classification** (accuracy)
- **Clustering** (v-measure)
- **Pair classification** (average precision)
- **Reranking** (MAP)
- **Retrieval** (NDCG@10)
- **Semantic similarity** (Spearman)
- **Summarization** (Spearman)

- **Retrieval NDCG@10** is the most relevant score for RAG systems.
- A model with high overall MTEB may still underperform on retrieval specifically. Check per-task scores.

## Instruction Prefixes

Some models expect task-specific prefixes:

```python
# BGE requires instruction prefixes
queries = [f"Represent this sentence for searching relevant passages: {query}"]
documents = [f"{doc}" for doc in docs]

# E5 requires "query:" / "passage:" prefixes
queries = [f"query: {query}"]
documents = [f"passage: {doc}" for doc in docs]

# OpenAI / Cohere handle it automatically
```

**Mismatched prefixes silently degrade quality by 5–15%.** Always check the model's expected format.

## Best Practices

- **Benchmark on your data, not MTEB.** Domain-specific performance varies significantly from general benchmarks.
- **Test at multiple dimensions.** With Matryoshka models, you can drop dims and measure recall impact.
- **Use ONNX or model distillation** for latency-critical production. A distilled MiniLM can be 10× faster than the base model with < 2% recall loss.
- **Cache embeddings whenever possible.** The same document embedded twice wastes money and time.
