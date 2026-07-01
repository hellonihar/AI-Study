# Cost and Performance

## Cost Breakdown

### Per-Step Costs

| Component | Cost Range | Typical |
|-----------|-----------|---------|
| LLM call (input) | $0.0001–0.01 | $0.001 |
| LLM call (output) | $0.0003–0.03 | $0.003 |
| Tool execution | $0–0.001 | $0.0002 |
| Memory retrieval | $0–0.001 | $0.0001 |
| Reflection (extra LLM call) | $0.0005–0.01 | $0.002 |

### Per-Task Costs

| Task Complexity | Steps | Typical Cost |
|----------------|-------|-------------|
| Simple (1–2 steps) | 2–3 | $0.005–0.02 |
| Medium (3–7 steps) | 5–10 | $0.02–0.10 |
| Complex (8–20 steps) | 10–25 | $0.10–0.50 |
| Very complex (20+ steps) | 25–50 | $0.50–$2.00 |

## Performance Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| Task completion rate | % of tasks successfully completed | > 85% |
| Average steps per task | Total steps / completed tasks | Minimize |
| Cost per completed task | Total cost / completed tasks | Minimize |
| Average latency per step | Total time / total steps | < 5s |
| Reflection overhead | % of steps that are reflection | < 20% |
| Loop rate | % of tasks with repeated actions | < 5% |

## Optimization Strategies

### Reduce Steps
- Combine independent tool calls into parallel execution
- Use batch APIs where available
- Cache tool results within a task

### Reduce Tokens
- Compress long documents before feeding to LLM
- Summarize intermediate results
- Prune irrelevant context
- Use shorter reasoning traces

### Reduce Latency
- Use faster models for routine decisions (Haiku, Mini)
- Reserve expensive models for complex reasoning only
- Parallelize independent tool calls
- Pre-warm tool connections

### Reduce Cost
- Set per-task budget caps ($0.10, $0.50, $2.00)
- Use cheaper models for non-critical tasks
- Cache semantically similar requests across tasks
- Batch non-urgent tasks during off-peak

## Budget Management

```python
class BudgetManager:
    def __init__(self, max_cost_per_task=0.50):
        self.max_cost = max_cost_per_task
        self.spent = 0

    def can_proceed(self):
        return self.spent < self.max_cost

    def spend(self, amount):
        self.spent += amount
        if self.spent > self.max_cost * 0.8:
            self.warn_approaching_limit()
        if self.spent > self.max_cost:
            raise BudgetExceededError()
```

## Cost vs. Quality Trade-offs

| Strategy | Cost Impact | Quality Impact |
|----------|-------------|----------------|
| Use cheap model for decisions | -60% | -5–10% (for simple tasks) |
| Skip reflection | -20% | -5–15% |
| Reduce context window | -30% | -10–30% (if relevant context lost) |
| Fewer retries | -15% | -5% |
| Parallel tool calls | Same cost, lower latency | Same quality |

## Monitoring Cost

```python
cost_tracker = {
    "task_id": "task-123",
    "steps": [
        {"step": 1, "model": "gpt-4o-mini", "input_tokens": 500, "output_tokens": 100, "cost": 0.0007},
        {"step": 2, "model": "gpt-4o", "input_tokens": 1200, "output_tokens": 300, "cost": 0.006},
        {"step": 3, "model": "gpt-4o-mini", "input_tokens": 800, "output_tokens": 150, "cost": 0.001},
    ],
    "total_cost": 0.0077,
    "total_tokens": 3050,
    "avg_latency_ms": 1200,
}
```
