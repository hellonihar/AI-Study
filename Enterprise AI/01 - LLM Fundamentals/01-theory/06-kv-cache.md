# KV Cache

The KV cache stores key and value tensors from previous decoding steps, avoiding redundant computation.

## How It Works

During autoregressive decoding, each step generates one token. Without caching:

```
Step 1: compute attention for [t0]
Step 2: compute attention for [t0, t1] — recomputes t0's keys/values
Step 3: compute attention for [t0, t1, t2] — recomputes t0, t1's keys/values
...
```

With KV cache:

```
Step 1: compute K, V for t0, store in cache. Generate t1.
Step 2: compute K, V for t1 only, append to cache. Generate t2.
Step 3: compute K, V for t2 only, append to cache. Generate t3.
...
```

Each step only computes attention for the new token, using cached K, V for all prior tokens.

## Memory Footprint

```
KV_cache_size = 2 × n_layers × n_kv_heads × seq_len × d_head × dtype_bytes
```

**Example — LLaMA-3-70B at 128K context:**
- n_layers = 80, n_kv_heads = 8, d_head = 128, dtype = FP16 (2 bytes)
- Per token KV size: 2 × 80 × 8 × 128 × 2 = 327,680 bytes ≈ 320 KB
- Full 128K context: 320 KB × 128,000 ≈ **40 GB**

This is why long-context inference is expensive — at 128K, the KV cache for a 70B model nearly fills an A100-80G.

## Prefix Caching

When multiple requests share the same prefix (e.g., system prompt), the KV cache for the prefix can be computed once and reused.

```
Request 1: [System Prompt] What is RAG?
Request 2: [System Prompt] How do I deploy?
           ^^^^^^^^^^^^^^^^
           Shared KV cache computed once
```

**Prefix caching reduces TTFT by 40–60%** in workloads with long shared system prompts.

## Optimization Techniques

| Technique | Benefit | Trade-off |
|---|---|---|
| GQA / MQA | Reduces KV cache by 4–8× | Minor quality loss |
| INT8/FP8 quantization | 2× memory reduction | 0.1–0.5% quality loss |
| Cache eviction (H2O, StreamingLLM) | Fits longer context | Quality loss at high compression |
| PagedAttention (vLLM) | Eliminates fragmentation | Implementation complexity |

## Best Practices

- **Monitor KV cache utilization** — it's the primary bottleneck for throughput.
- **Use prefix caching** for all applications with shared system prompts.
- **Set `max_model_len` carefully** — allocating for max 128K when average is 4K wastes 32× memory.
- **Profile KV cache size per request** to predict OOM conditions.
