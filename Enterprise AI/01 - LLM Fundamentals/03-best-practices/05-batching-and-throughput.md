# Batching and Throughput

Maximizing tokens per second by processing multiple requests together.

## Static Batching

Traditional approach: collect N requests, pad them to the same length, process together.

```
Request 1: "What is AI?"                          → tokens: [5]
Request 2: "Explain the transformer architecture" → tokens: [10]
Request 3: "Hi"                                   → tokens: [2]
                              ↓
Pad to max length: [5, 10, 2] → pad to 10 → [5, 1-pad, 2-pad...]
```

**Problem:** Padding wastes compute. Every sequence processes at the slowest sequence's pace.

## Continuous Batching (vLLM)

Sequences enter and leave the batch dynamically:

```
Time →
├── [Seq1: 5 tokens remaining]
├── [Seq2: 12 tokens remaining]
├── [Seq3: 2 tokens remaining] → completes, removed
├── [Seq4: NEW, 8 tokens remaining] → added
└── [Seq5: NEW, 3 tokens remaining] → added
```

**Result:** 2–3× throughput improvement over static batching.

## Optimal Batch Size

| GPU | Model | Recommended Batch Size | Throughput (tok/s) |
|---|---|---|---|
| A100-80G | 7B (FP16) | 64–128 | ~5,000 |
| A100-80G | 13B (FP16) | 32–64 | ~2,500 |
| A100-80G | 70B (FP8, 2 GPUs) | 16–32 | ~1,200 |
| H100-80G | 70B (FP8) | 32–64 | ~3,000 |
| RTX 4090 | 7B (INT4) | 8–16 | ~400 |

**Finding your optimal batch size:**
1. Start with batch size 1, measure throughput.
2. Double until throughput stops increasing or GPU memory is full.
3. The knee point (where throughput per request starts dropping) is optimal.

## Throughput vs. Latency

```
              Batch Size →
              Small         Medium        Large
Throughput    Low           High          Highest
Latency       Low           Medium        High
```

- **Batch for throughput** when latency isn't critical (batch processing, nightly jobs).
- **Batch conservatively** for latency-sensitive tasks (chat, real-time APIs).

## Key-Value Cache and Batching

Batch size is limited by KV cache memory, not just model weights:

```
KV_cache_total = batch_size × seq_len × per_token_kv_cache_size
```

At 128K context with a 70B model, a batch size of 4 already requires 160 GB of KV cache — more than the model weights.

## Production Recommendations

| Workload | Strategy |
|---|---|
| Real-time chat (latency < 200ms) | Batch size 1–4, use smaller model |
| Batch processing | Max batch size that fits memory |
| Mixed traffic | Serve with continuous batching (vLLM) |
| Very long context | Reduce batch size proportionally to context length |
| CPU inference | GGUF with llama.cpp, batch size 1–2 |

## Monitoring

Track:
- **GPU utilization** — below 80% → increase batch size.
- **KV cache utilization** — above 90% → reduce batch size or context.
- **P50 vs P99 latency** — if P99 >> P50, batching variance is high (some sequences much longer).
- **Queue depth** — growing queue? Need more replicas or larger batch.
