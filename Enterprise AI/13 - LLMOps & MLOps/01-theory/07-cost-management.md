# Cost Management & Optimization

## Understanding LLM Costs

LLM costs are dominated by inference (not training). For most production systems, serving costs are 10–100x training costs.

### Cost Components

| Component | Cost Driver | Typical Share |
|-----------|-------------|---------------|
| API inference | Tokens per request × price per token | 60–80% |
| Self-hosted inference | GPU hours × instance cost | 40–70% |
| Embedding | Vector generation per document | 5–15% |
| Vector DB | Storage + compute + bandwidth | 5–10% |
| Guardrails | LLM-as-judge, classifiers | 5–15% |
| Monitoring | Logging, tracing, storage | 2–5% |
| Human review | Annotation, QA | 1–5% |

## Cost Tracking

### Per-Request Cost Attribution

```python
def calculate_request_cost(prompt_tokens, completion_tokens, model_pricing):
    input_cost = prompt_tokens * model_pricing.input_per_token
    output_cost = completion_tokens * model_pricing.output_per_token
    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": input_cost + output_cost,
        "tokens": prompt_tokens + completion_tokens,
    }
```

### Cost Aggregation Dimensions

| Dimension | Example | Use |
|-----------|---------|-----|
| Feature | Chat, Search, Summarize | Feature-level cost allocation |
| User tier | Free, Pro, Enterprise | Per-customer cost analysis |
| Model | GPT-4, GPT-4o-mini, Claude | Model selection decisions |
| Time | Hourly, daily, monthly | Trend analysis, anomaly detection |
| Endpoint | /chat, /search, /embed | Per-endpoint optimization |

## Cost Optimization Strategies

### 1. Model Selection

| Strategy | Savings | Quality Impact |
|----------|---------|---------------|
| Use smaller model for simple tasks | 50–90% | Minimal (right-size) |
| Cascade (try cheap first, escalate) | 40–60% | None (fallback to strong model) |
| Model routing by task difficulty | 30–50% | None with good classifier |

### 2. Prompt Optimization

| Strategy | Savings | Implementation |
|----------|---------|---------------|
| Fewer examples | 20–50% | Remove redundant few-shot examples |
| Shorter system prompts | 10–30% | Compress instructions |
| Token-efficient formatting | 10–20% | Use concise formatting |
| Dynamic prompt assembly | 20–40% | Only include relevant context |

### 3. Caching

| Cache Type | Hit Rate | Savings |
|------------|----------|---------|
| Exact match (same input → same output) | 5–15% | 100% of cached requests |
| Semantic cache (similar input → same output) | 15–30% | 100% of cached requests |
| Prefix cache (common prefix → reuse KV cache) | 20–40% | Reduced TTFT, lower cost |

### 4. Batch Processing

| Strategy | Savings | Latency Impact |
|----------|---------|---------------|
| Batch non-urgent requests | 30–50% | Higher (batched) |
| Asynchronous processing | 0% (same compute) | Lower for user (fire-and-forget) |
| Payload compression | 10–20% | Lower (fewer tokens) |

### 5. Context Window Management

| Strategy | Savings | Risk |
|----------|---------|------|
| Truncate long contexts | 30–60% | Losing relevant information |
| Chunk and retrieve only relevant | 40–70% | Retrieval quality dependency |
| Summarize conversation history | 20–40% | Loss of detail |

## Cost Allocation

### Per-Feature Cost Model

```python
feature_costs = {
    "chat": {
        "model": "gpt-4o-mini",
        "avg_prompt_tokens": 1200,
        "avg_completion_tokens": 350,
        "cost_per_request": 0.0008,
        "requests_per_day": 100000,
        "daily_cost": 80.00,
    },
    "search": {
        "model": "gpt-4o-mini",
        "avg_prompt_tokens": 2500,
        "avg_completion_tokens": 200,
        "cost_per_request": 0.0011,
        "requests_per_day": 50000,
        "daily_cost": 55.00,
    }
}
```

## Cost Anomaly Detection

| Signal | Possible Cause | Action |
|--------|---------------|--------|
| Cost spike > 2x | Traffic surge, prompt bloat, model misconfiguration | Investigate, rollback if needed |
| Average tokens/request rising | Prompt creep, context accumulation | Review prompt design, implement truncation |
| Cost per user increasing | Power user behavior, abuse | Rate limit, tier check |
| Unexpected model usage | Routing misconfiguration | Fix routing rules |

## Budgeting for LLMs

| Scale | Monthly Budget | Typical Setup |
|-------|---------------|---------------|
| Prototype | $100–1K | API-based, single model |
| Startup | $1K–10K | API-based, model routing |
| Growth | $10K–100K | Mix of API and self-hosted |
| Enterprise | $100K+ | Self-hosted, optimized stack |
