# Model Selection

Choosing the right embedding model for your production workload.

## Decision Framework

```
Domain?
├── General English → BGE-base or OpenAI text-embedding-3-small
├── Chinese + English → BGE-base-zh or GTE-Qwen2
├── Code-heavy → Voyage-2 or OpenAI text-embedding-3
├── Multilingual → BGE-M3 or GTE-Qwen2-7B
└── Domain-specific → Fine-tune BGE-base on your domain

Latency SLA?
├── < 5ms per query embedding → MiniLM-L6 (384 dims, CPU)
├── < 15ms → BGE-base (768 dims, CPU)
├── < 50ms → BGE-large (1024 dims, GPU)
└── < 200ms → E5-mistral-7b (4096 dims, GPU)

Scale?
├── < 1M docs → Any model works
├── 1M–10M docs → 768 dims is the sweet spot
├── 10M–100M docs → Consider INT8 quantization + 384 dims
└── 100M+ docs → Binary embeddings or Matryoshka reduction
```

## The Cost-Performance Curve

For a system with 10M documents and 100K queries/day:

| Model | Dims | Storage Cost | Query Latency | Recall@10 | Monthly Embedding Cost |
|---|---|---|---|---|---|
| all-MiniLM-L6-v2 | 384 | ~3 GB | 3ms | 0.85 | $0 (self-host) |
| BGE-base | 768 | ~6 GB | 8ms | 0.90 | $0 (self-host) |
| BGE-large | 1024 | ~8 GB | 15ms | 0.92 | $0 (self-host) |
| OpenAI small | 512 | ~4 GB | API-dependent | 0.91 | ~$300 (API) |
| OpenAI large | 3072 | ~24 GB | API-dependent | 0.93 | ~$2,100 (API) |

**Key insight:** The difference between a "good" and "best" embedding model is typically 2–3% recall. The first 90% of quality is cheap; the last 5% costs 10× more.

## When to Use API vs Self-Host

| Factor | API (OpenAI, Cohere) | Self-Host (BGE, E5) |
|---|---|---|
| **Setup time** | Minutes | Hours–days |
| **Cost at low volume** | Cheap | ~$0 (if GPU already available) |
| **Cost at high volume** | Expensive | GPU depreciation |
| **Latency** | Network + API processing | Local inference |
| **Data privacy** | Sends data to third party | Data stays in your VPC |
| **Customization** | No (use provided model) | Fine-tune on domain data |
| **Model updates** | Vendor-managed | You manage |

## Recommendation by Use Case

- **Prototyping:** OpenAI text-embedding-3-small (low friction, good quality).
- **Production < 10M docs, general domain:** BGE-base (self-host, 768 dims, good quality).
- **Production > 10M docs:** BGE-small or MiniLM with INT8 quantization (storage cost dominates).
- **Domain-specific:** Fine-tune BGE-base on your data — expect 5–15% recall improvement.
- **Multilingual:** BGE-M3 or GTE-Qwen2 — don't use English-only models.
- **Lowest latency requirement:** MiniLM-L6 (384 dims, runs on CPU in < 5ms).
- **Highest quality required:** E5-mistral-7b-instruct (requires GPU, 4096 dims).
