# Capacity & Cost Best Practices

## Capacity Planning

### Sizing Methodology
1. Estimate peak RPS and average tokens per request
2. Calculate required tokens/second
3. Select GPU and serving framework
4. Apply utilization target (70-80%)
5. Add N+1 redundancy

### Buffer Planning
| Component | Buffer | Rationale |
|-----------|--------|-----------|
| GPU compute | +30% | Traffic spikes, retries |
| Memory | +20% | KV cache growth, overhead |
| Network bandwidth | +50% | Model loading, replication |
| Storage | +100% | Log growth, model versions |

## Cost Optimization

### API vs Self-Hosted Decision

| Factor | API | Self-Hosted |
|--------|-----|-------------|
| < 1M req/mo | Cheaper | More expensive |
| 1-10M req/mo | Comparable | Comparable |
| > 10M req/mo | More expensive | Cheaper |
| Variable traffic | Good (pay-per-use) | Poor (fixed cost) |
| Steady traffic | Less efficient | More efficient |

### Cost Levers
- Right-size model for each task (not every task needs GPT-4)
- Cache aggressively (20-40% reduction)
- Batch non-urgent requests
- Use cheaper models for internal tools
- Monitor and alert on cost anomalies
