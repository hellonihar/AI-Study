# Deployment & Serving Best Practices

## Serving Framework Selection

| Framework | Best For | Avoid If |
|-----------|----------|----------|
| vLLM | High-throughput, multi-adapter, production | Don't need continuous batching |
| TGI | Hugging Face ecosystem integration | Need multi-adapter hot-swap |
| ONNX Runtime | Cross-platform (cloud + edge) | Need latest model architectures immediately |
| llama.cpp | CPU inference, edge devices | High-throughput serving |
| TensorRT-LLM | Maximum GPU throughput | Development speed matters |

## Quantization Strategy

| Deployment Target | Recommended Precision | Rationale |
|------------------|---------------------|-----------|
| Cloud GPU (A100/H100) | FP16 or FP8 | Maximum quality, sufficient memory |
| Cloud GPU (cost-optimized) | INT8 or FP8 | 2x memory savings, minimal quality loss |
| Consumer GPU | INT4 or NF4 | 4x memory savings, enables larger models |
| CPU | INT4 (GGUF) | Only practical option for CPU inference |
| Edge/mobile | INT4 | Smallest footprint, acceptable quality |

## LoRA Adapter Serving

- Use vLLM for multi-adapter serving (load base model once, switch adapters per request)
- Max 100–200 adapters per GPU (depends on adapter size and sequence length)
- Merge adapters into base model for single-adapter production deployments
- Benchmark TTFT (Time to First Token) with adapter loading overhead

## Auto-Scaling Configuration

| Metric | Scale-Up Threshold | Scale-Down Threshold |
|--------|-------------------|---------------------|
| GPU utilization | >80% for 5 minutes | <40% for 10 minutes |
| Queue depth | >50 pending requests | <10 pending requests |
| P95 latency | >1 second | <500ms |

Always maintain N+1 redundancy for production traffic.

## Monitoring Dashboard

Essential metrics to display:
- **Throughput**: Requests/second, tokens/second
- **Latency**: TTFT, ITL, end-to-end (p50/p95/p99)
- **Errors**: 4xx rate, 5xx rate, timeout rate
- **Hardware**: GPU utilization, memory, temperature
- **Quality**: LLM-as-judge score (sampled), user feedback rate

## Deployment Checklist

- [ ] Model passes all evaluation gates
- [ ] Quantization tested for quality impact
- [ ] Batch size tuned for throughput/latency trade-off
- [ ] Auto-scaling configured with proper thresholds
- [ ] Monitoring dashboard updated with model-specific metrics
- [ ] Rollback plan documented and tested
- [ ] Canary deployment configured
- [ ] Load tested at 2x expected peak traffic
