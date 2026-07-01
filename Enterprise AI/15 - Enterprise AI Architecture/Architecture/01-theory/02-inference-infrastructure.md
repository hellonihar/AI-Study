# Inference Infrastructure

## Serving Frameworks

| Framework | Throughput | Latency | Ease of Use | Best For |
|-----------|-----------|---------|------------|----------|
| vLLM | Excellent | Good | Good | High-throughput, open models |
| TGI (HF) | Good | Good | Excellent | Hugging Face ecosystem |
| Triton | Excellent | Excellent | Complex | Multi-model, multi-framework |
| ONNX Runtime | Good | Excellent | Good | Production optimization |
| llama.cpp | Low | Good | Excellent | Local/edge deployment |

## Serving Patterns

### Replica Sets
Multiple identical model replicas behind a load balancer:
- Simple, stateless
- Scales horizontally
- Each replica loads full model weights
- High memory overhead for large models

### Tensor Parallelism
Split model layers across GPUs:
- Required for models that don't fit on single GPU
- Communication overhead between GPUs (NVLink/NVSwitch)
- Scales with GPU count
- Lower memory per GPU

### Pipeline Parallelism
Split model layers across stages:
- Each GPU holds different layers
- Throughput determined by slowest stage
- Higher throughput than tensor parallelism for large models
- More complex scheduling

### Combined Approach
For very large models (70B+):
- Tensor parallelism within a node (NVLink)
- Pipeline parallelism across nodes (network)
- Sequence parallelism for long contexts

## GPU Selection

| GPU | Memory | FP16 TFLOPS | VRAM Bandwidth | Best For |
|-----|--------|-------------|----------------|----------|
| A100 80GB | 80 GB | 312 | 2 TB/s | Llama 3 70B, Mixtral |
| H100 80GB | 80 GB | 989 | 3.3 TB/s | Training + inference |
| A10G | 24 GB | 125 | 600 GB/s | Smaller models, batch |
| L4 | 24 GB | 121 | 300 GB/s | Cost-effective inference |
| T4 | 16 GB | 65 | 320 GB/s | Edge, low-throughput |

## Auto-Scaling Configuration

| Metric | Scale Out | Scale In | Cooldown |
|--------|-----------|----------|----------|
| GPU utilization > 80% | +1 pod | < 40% for 5 min | 60s |
| Queue depth > 50 | +1 pod | < 10 for 5 min | 60s |
| Request latency > p95 | +2 pods | < p50 for 10 min | 120s |
| Concurrent requests > N | +1 pod per 100 | < N/2 for 5 min | 60s |

## Model Loading Strategy

### Lazy Loading
- Load model on first request
- Faster startup, slower first request
- Best for infrequently used models

### Pre-loading
- Load all models on startup
- Slow startup, consistent latency
- Best for high-traffic models

### Dynamic Loading
- Load/unload based on traffic patterns
- Complex orchestration
- Best for cost-sensitive deployments

## Inference Optimization

### Continuous Batching
- Dynamically add/remove requests from batch
- vLLM default, 2-4x throughput improvement
- Reduces queue wait time

### PagedAttention (vLLM)
- Manage KV cache in non-contiguous blocks
- Near-zero memory waste
- Higher batch sizes possible

### Quantization

| Type | Precision | Memory Reduction | Quality Impact |
|------|-----------|-----------------|---------------|
| FP16 | 16-bit | 0% | None |
| INT8 | 8-bit | 50% | Minimal |
| INT4 | 4-bit | 75% | Slight |
| FP8 (H100) | 8-bit | 50% | None (H100 native) |

### Speculative Decoding
- Use small draft model to propose tokens
- Large model verifies in single forward pass
- 2-3x latency improvement
- No quality loss
