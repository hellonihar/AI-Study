# Scaling Best Practices

## When to Scale

| Metric | Threshold | Action |
|--------|-----------|--------|
| Agent latency (p95) | > 5s | Add replicas of the slow agent |
| Queue depth | > 1000 | Add workers, check bottleneck |
| Error rate | > 5% | Check tools, circuit breakers |
| Cost per task | > 2x baseline | Optimize model tier, cache more |
| CPU/Memory | > 80% | Scale horizontally |

## Horizontal Scaling

### Stateless Agents
Scale by adding instances behind a load balancer:

```
Load Balancer
  ├── Agent v1 (replica 1)
  ├── Agent v2 (replica 2)
  └── Agent v3 (replica N)
```

### State-Dependent Agents
Use external state store so any replica can handle any request:

```
Load Balancer → Agent replicas → Redis (external state)
```

### Queue-Based Scaling
Scale workers based on queue depth:

```python
def auto_scale(queue_depth, current_workers):
    target_workers = ceil(queue_depth / 10)  # 10 tasks per worker
    if target_workers > current_workers:
        scale_up(target_workers - current_workers)
    elif target_workers < current_workers * 0.5:
        scale_down(current_workers - target_workers)
```

## Right-Sizing Agents

| Agent Type | Memory | CPU | Replicas |
|-----------|--------|-----|----------|
| Router | 256 MB | 0.5 vCPU | 5–10 (high volume) |
| Search agent | 512 MB | 1 vCPU | 3–5 |
| Analyze agent | 1 GB | 2 vCPU | 2–3 |
| Code agent | 2 GB | 4 vCPU | 1–2 |

## Caching

### What to Cache
| Data | Cache Type | TTL | Hit Rate |
|------|-----------|-----|----------|
| Router classifications | Semantic | 24h | 40–60% |
| Tool results | Exact match | 1h | 20–40% |
| Agent responses | Semantic | 1h | 10–20% |
| Knowledge base snippets | Exact match | 7d | 50–70% |

### Cache Strategy
```
Layer 1: In-memory (Redis) — 1ms, limited size
Layer 2: Distributed (Redis Cluster) — 5ms, larger
```

## Rate Limiting

| Limit | Scope | Default |
|-------|-------|---------|
| Requests per user | Global | 100/min |
| Requests per agent | Per agent | 500/min |
| Concurrent tasks | Global | 50 |
| LLM calls per minute | Per provider | 10K TPM |

## Cost Optimization

| Strategy | Savings | Impact |
|----------|---------|--------|
| Use cheap models for simple agents | 40–60% | Minimal (simple agents are simple) |
| Cache aggressively | 20–40% | None |
| Parallelize independent agents | Same cost, faster | Better latency |
| Batch non-urgent tasks | 20–30% | Higher latency for batch tasks |
| Downscale idle agents | 30–50% (infra) | None during low traffic |
