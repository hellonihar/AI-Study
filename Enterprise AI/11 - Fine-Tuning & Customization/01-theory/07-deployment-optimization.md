# Deployment & Optimization of Fine-Tuned Models

## Serving Options

### vLLM

The most popular open-source serving framework for fine-tuned LLMs.

**Key features:**
- PagedAttention for near-zero memory waste from KV cache fragmentation
- Continuous batching — add/remove sequences dynamically
- Tensor parallelism across GPUs
- LoRA adapter hot-swapping (serve multiple fine-tuned models from one deployment)

**Performance:**
- 2–4x throughput vs Hugging Face Transformers
- 10–20x higher throughput than text-generation-inference (older versions)
- Supports FP16, FP8, INT4, INT8 quantization

**LoRA support:**
- Load multiple LoRA adapters simultaneously
- Route requests by model name in the API
- Max ~100–200 adapters depending on GPU memory

### TGI (Text Generation Inference)

Hugging Face's serving solution.

**Key features:**
- Continuous batching
- Tensor parallelism
- Flash Attention integration
- Messages API (native chat template support)

**Best for:** Tight integration with Hugging Face ecosystem, simpler setup than vLLM.

### ONNX Runtime

Microsoft's optimized inference engine for cross-platform deployment.

**Key features:**
- CPU/GPU/Edge deployment with same model
- Graph optimizations (operator fusion, constant folding)
- INT8/FP16 quantization via ONNX Runtime quantization tools
- DML (DirectML) support for Windows GPU deployment

**Best for:** Enterprise deployments requiring flexibility across hardware targets.

## Model Optimization

### Quantization

| Type | Bits | Memory Reduction | Quality Impact | Speed Impact |
|------|------|-----------------|----------------|--------------|
| FP16 | 16 | 1x | None (training precision) | 1x |
| FP8 | 8 | 2x | Minimal (~0–1% metric drop) | 1.5–2x |
| INT8 | 8 | 2x | Small (~1–2% drop) | 1.5–2x |
| INT4 | 4 | 4x | Moderate (~2–5% drop) | 2–3x |
| NF4 | 4 | 4x | Small (~1–3% drop) | 2–3x |
| INT3 | 3 | 5.3x | Significant (~5%+ drop) | 2–3x |

**Recommendation:** Start with FP8 for cloud deployment, INT4 or NF4 for edge/consumer hardware.

### Quantization Methods

| Method | Type | When to Use |
|--------|------|-------------|
| GPTQ | Post-training, weight-only | Highest quality at INT4 |
| AWQ | Post-training, weight-only | Better than GPTQ for some models |
| GGUF/GGML | Post-training, CPU-friendly | llama.cpp ecosystem |
| BitsAndBytes | Post-training, easy setup | Quick prototyping |
| QuIP# | Post-training, weight-only | Emerging, high quality |

### Speculative Decoding

Use a small "draft" model to generate candidate tokens that a large model verifies in parallel.

**Speedup:** 2–3x on latency-bound workloads.

**Trade-off:** No quality loss (verification ensures same distribution), but requires a compatible draft model.

## Memory Optimization for Serving

### KV Cache Management

The KV cache is the dominant memory consumer in LLM serving:

| Model Size | KV Cache per Token | Context Length | Total KV Cache per Request |
|------------|-------------------|----------------|---------------------------|
| 7B (FP16) | ~1 MB | 4096 | ~4 GB |
| 7B (FP16) | ~1 MB | 32768 | ~32 GB |
| 70B (FP16) | ~10 MB | 4096 | ~40 GB |
| 70B (FP16) | ~10 MB | 32768 | ~320 GB |

**Optimizations:**
- Use vLLM's PagedAttention (eliminates fragmentation)
- Multi-Query Attention (MQA) or Grouped-Query Attention (GQA) — fewer KV heads
- Sliding window attention (Mistral, etc.)
- KV cache quantization (FP16 → FP8 reduces cache by 2x)

### Batching

| Strategy | Throughput | Latency | Memory |
|----------|-----------|---------|--------|
| Static batching | Moderate | High | Efficient |
| Continuous batching | High | Low | Efficient |
| Dynamic batching | High | Moderate | Moderate |

Continuous batching (vLLM, TGI) is the standard for production.

## Deployment Architecture

### Single Model Deployment

```
Client → Load Balancer → Model Server (vLLM) → GPU
```

Simple, cost-effective for one fine-tuned model.

### Multi-Adapter Deployment

```
Client → Router → Model Server (vLLM + LoRA adapters)
```

Serve 100+ fine-tuned models from one GPU cluster. The base model is loaded once; adapters are swapped per request.

### Multi-Model Deployment

```
Client → Gateway → Model Server A (7B)
                 → Model Server B (13B)
                 → Model Server C (70B)
```

Route requests based on complexity and latency requirements.

## Monitoring for Serving

| Metric | What It Tells You | Alert Threshold |
|--------|-------------------|-----------------|
| TTFT (Time to First Token) | Perceived latency | > 500ms p95 |
| ITL (Inter-Token Latency) | Generation speed | > 50ms p95 |
| Throughput (tokens/s) | System capacity | < 80% target |
| GPU Memory Utilization | Capacity planning | > 90% |
| P50/P95/P99 Latency | User experience | Degradation > 20% |
| Error Rate | System health | > 1% |
| Queue Depth | Load vs capacity | Growing queue |

## Auto-Scaling Strategy

| Metric | Scale Up | Scale Down | Cooldown |
|--------|----------|------------|----------|
| Queue depth > 100 | +1 replica | -1 replica when < 10 | 5 min |
| GPU utilization > 80% | +1 replica | -1 replica when < 40% | 10 min |
| P95 latency > 1s | +1 replica | -1 replica when < 500ms | 5 min |

Always provision 20% headroom for traffic spikes.
