# Agent Observability

## Why Observability Matters

Agents are non-deterministic and multi-step. Without observability, you cannot:
- Debug why an agent made a wrong decision
- Measure performance and cost per task
- Detect loops, stalls, or failures
- Audit agent behavior for compliance

## What to Observe

### Per-Step Data
- Step number and timestamp
- Input to the LLM (full prompt, including context + tools)
- LLM output (reasoning trace, action choice, parameters)
- Tool execution result or error
- Tokens used (input + output)
- Latency per step
- Cumulative cost

### Per-Task Data
- Task goal and completion status
- Total steps, tokens, cost, latency
- Number of retries and reflection cycles
- Tools used and frequency
- Errors encountered and resolution

### Aggregate Data
- Tasks per hour/day
- Success rate by task type
- Average steps per task
- Average cost per task
- Common failure modes

## Instrumentation Pattern

```python
class ObservableAgent:
    def __init__(self):
        self.traces = []
        self.current_trace = []

    def step(self, prompt, action):
        start = time.time()
        trace = {
            "step": len(self.current_trace) + 1,
            "prompt_tokens": count_tokens(prompt),
            "timestamp": datetime.now().isoformat(),
        }

        try:
            result = self.llm.generate(prompt)
            trace["response"] = result
            trace["status"] = "success"
        except Exception as e:
            trace["status"] = "error"
            trace["error"] = str(e)

        trace["latency_ms"] = (time.time() - start) * 1000
        trace["total_tokens"] = count_tokens(prompt) + count_tokens(result)
        self.current_trace.append(trace)

        return result
```

## Storage and Query

| Storage | Use Case | Retention |
|---------|----------|-----------|
| Structured logs (JSON) | Debugging, development | 7 days |
| Database (PostgreSQL) | Analytics, dashboards | 30 days |
| Data warehouse | Long-term trend analysis | 90 days |
| Vector DB | Similar trace search | 30 days |

## Alerting Rules

| Alert Condition | Severity | Action |
|----------------|----------|--------|
| Agent loop (same action > 3x) | Critical | Kill agent, notify |
| Cost per task > $1 | Warning | Log, investigate |
| Success rate < 80% | Critical | Pause agent, review |
| Latency per step > 30s | Warning | Check tool availability |
| Total steps > 20 | Warning | Task too complex, suggest replan |

## Visualization

```python
# Trace visualization as a tree
trace = [
    {"step": 1, "action": "search('capital of France')", "status": "ok"},
    {"step": 2, "action": "generate response", "status": "ok"},
]

# Render:
# ┌─ Step 1: search('capital of France') [200ms, 150 tokens] ✓
# └─ Step 2: generate response [500ms, 300 tokens] ✓
# Total: 2 steps, 700ms, 450 tokens, $0.002
```

## Privacy Considerations

- Never log raw tool call parameters that contain PII
- Redact sensitive fields before storing traces
- Hash user IDs for analytics, store separately
- Implement trace retention policies per data sensitivity tier
