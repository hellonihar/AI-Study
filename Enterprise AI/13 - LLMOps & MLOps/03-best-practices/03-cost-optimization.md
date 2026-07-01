# Cost Optimization Best Practices

## Cost Visibility First

### Track Everything
You cannot optimize what you do not measure. Every request must be tagged with:

| Tag | Purpose | Example |
|-----|---------|---------|
| Feature | Cost allocation per product area | chat, search, summarize |
| Model | Per-model cost comparison | gpt-4o-mini, gpt-4o |
| User tier | Per-customer cost analysis | free, pro, enterprise |
| Endpoint | API-level granularity | /chat, /search |
| Task type | Cost by complexity | simple, medium, complex |

### Cost Baseline
Establish per-feature cost baselines before optimizing:

- Cost per request (p50, p95, p99)
- Average tokens per request (prompt + completion)
- Daily/weekly monthly cost by dimension
- Cost per user by tier

## Optimization Strategies

### 1. Model Selection (Highest Impact)

| Strategy | Savings | Quality Risk | Implementation |
|----------|---------|-------------|---------------|
| Right-size model | 50-90% | Minimal | Use smallest model that meets quality bar |
| Cascade routing | 40-60% | None | Try cheap model first, escalate on confidence |
| Task-specific routing | 30-50% | None | Classify task, route to best-fit model |

Cascade pattern:
```
Task -> GPT-4o-mini -> confidence check -> if low -> GPT-4o
```
This saves 60% cost while maintaining quality for complex cases.

### 2. Prompt Optimization

| Technique | Savings | Effort |
|-----------|---------|--------|
| Remove redundant few-shot examples | 20-50% | Low |
| Compress system prompt | 10-30% | Medium |
| Dynamic context inclusion | 20-40% | High |
| Token-efficient formatting | 10-20% | Low |

### 3. Caching

| Cache Type | Implementation | Hit Rate | Savings |
|------------|---------------|----------|---------|
| Exact match | Hash-based lookup | 5-15% | 100% of hits |
| Semantic cache | Embedding similarity | 15-30% | 100% of hits |
| Prefix caching | KV cache reuse (vLLM) | 20-40% | 30-50% TTFT reduction |

### 4. Context Window Management

| Strategy | Savings | Risk |
|----------|---------|------|
| Truncate to max useful length | 30-60% | Losing relevant context |
| RAG-only (no full document) | 40-70% | Retrieval quality |
| Chat history summarization | 20-40% | Detail loss |
| Sliding window | 10-20% | Context fragmentation |

### 5. Batch Processing

| Technique | Savings | Latency Trade-off |
|-----------|---------|-------------------|
| Batch non-urgent requests | 30-50% | Higher latency (seconds to minutes) |
| Request batching (API) | 15-25% | Wait for batch to fill |
| Connection pooling | 5-10% | Lower per-request overhead |

## Budget Management

### Setting Budgets

| Scale | Monthly Budget | Strategy |
|-------|---------------|----------|
| Prototype | $100-1K | Single model, no optimization |
| Startup | $1K-10K | Model routing, basic caching |
| Growth | $10K-100K | Cascade routing, semantic cache |
| Enterprise | $100K+ | Self-hosted + API mix, aggressive optimization |

### Hard and Soft Budgets
- **Soft budget**: Alert at 80% utilization, review at 100%
- **Hard budget**: Enforce rate limits or block features at 120%
- Budget by feature, not just total

## Cost Anomaly Detection

| Signal | Investigation Path | Typical Cause |
|--------|-------------------|---------------|
| Cost spike > 2x | Check traffic, prompt size, model routing | Retry storm, misrouting |
| Tokens/request increasing | Review prompt templates, context growth | Prompt creep |
| Cost/user increasing | Check specific user segments | Power users, abuse |
| Unexpected model usage | Validate routing rules | Configuration error |

## Performance Budget Template

```
Feature: chat
Monthly budget: $2,400
Current spend: $1,890 (79%)
Breakdown:
  GPT-4o-mini: $1,230 (65%)
  GPT-4o: $660 (35%)
Avg cost/request: $0.0008
Target: $0.0006 (25% reduction via cascade routing)
```

## Common Cost Pitfalls

| Pitfall | Impact | Prevention |
|---------|--------|------------|
| Prompt bloat | 2-5x cost over time | Monitor prompt size, set max limits |
| No cost tagging | Cannot attribute spend | Enforce tags on every request |
| Over-using expensive models | 3-10x unnecessary cost | Implement cascade routing |
| No caching | Re-compute identical requests | Add exact + semantic cache |
| Retry storms | 2-100x cost during incidents | Circuit breakers, exponential backoff |
