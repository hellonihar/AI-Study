# Multi-Agent Observability and Debugging

## What to Observe

### Per-Agent
- Agent name, role, capabilities
- Input prompt (truncated to 500 chars)
- Decision output (tool choice, response)
- Latency (total + LLM + tool)
- Token count (input + output)
- Cost
- Status (success, error, timeout)

### Per-Interaction
- Message ID, correlation ID
- Sender, recipient
- Message type, size
- Latency
- Number of retries

### Per-Task
- Task ID, goal
- Agent chain (all agents involved)
- Total steps, cost, latency
- Handoff count
- Final status

## Debugging Common Issues

### Issue: Agent Returns Wrong Answer
1. Check the input prompt (was context correct?)
2. Check tool results (did agent use the right data?)
3. Check reasoning trace (did agent reason correctly?)
4. Check handoff context (was context preserved?)

### Issue: High Latency
1. Check each agent's latency breakdown
2. Is one agent much slower than others?
3. Are tools taking longer than expected?
4. Is there queue contention?

### Issue: Cost Spike
1. Which agent is spending the most?
2. Is it making too many tool calls?
3. Is it using expensive models?
4. Is there a loop (same action repeatedly)?

### Issue: Agent Loop
1. Check step trace for repeated actions
2. Look for cycles in agent handoffs (A → B → A)
3. Check if agent has clear termination criteria

## Distributed Tracing Implementation

```python
class TraceExporter:
    def export(self, spans):
        # Store spans for analysis
        for span in spans:
            store_span(span)
            if span.duration_ms() > 5000:
                alert_slow_span(span)
            if span.status == "error":
                alert_error(span)
```

## Alerting

| Alert | Threshold | Severity |
|-------|-----------|----------|
| Agent error rate | > 10% in 5 min | Critical |
| Task failure rate | > 5% in 5 min | Critical |
| P95 latency | > 10s | Warning |
| Cost per task | > $1.00 | Warning |
| Handoff count | > 5 per task | Info |
| Agent loop detected | Any | Critical |

## Visualization

Render agent interaction as a directed graph:

```
Time →  0s    2s    4s    6s
Task-123:
  Supervisor   [━━━━━━━━━━━━━━━━━━━━]
  Router          [━━━━]
  Search             [━━━━━━]
  Analyze                  [━━━━━━━━]
  Format                       [━━━━]

Handoffs:
  Router → Search    @ 2.0s (classification done)
  Search → Analyze   @ 4.0s (search results ready)
  Analyze → Format   @ 6.5s (analysis complete)
```

## Structured Logging

```json
{
  "timestamp": "2024-12-01T10:00:00.123Z",
  "level": "INFO",
  "logger": "multi_agent",
  "trace_id": "t-789",
  "span_id": "s-456",
  "agent": "search_agent",
  "action": "tool_execution",
  "tool": "search_web",
  "duration_ms": 1200,
  "tokens": 350,
  "status": "success",
  "metadata": {
    "query": "latest AI research papers",
    "results_count": 5
  }
}
```

## Testing Observability

- Verify trace spans are created for every agent interaction
- Verify correlation IDs flow through the entire chain
- Test with concurrent tasks (ensure trace IDs don't mix)
- Verify alerting triggers when agents fail
- Test log aggregation (all agents log to same system)
