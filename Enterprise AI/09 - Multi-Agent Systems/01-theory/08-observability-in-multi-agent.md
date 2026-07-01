# Observability in Multi-Agent Systems

## Why Multi-Agent Observability is Harder

- **Distributed**: No single agent has the full picture
- **Concurrent**: Agents may execute in parallel
- **Complex async**: Messages, events, handoffs create complex interaction graphs
- **Harder to debug**: A bug may be in agent A's prompt, B's tool, or the communication between them

## Distributed Tracing

Each interaction between agents creates a trace span. Spans are connected by correlation IDs.

```
Trace: task-123
├── Span: supervisor.decompose [200ms]
├── Span: search_agent.run [1.5s]
│   ├── Span: search_agent.search_web [800ms]
│   └── Span: search_agent.search_docs [700ms]
├── Span: summarize_agent.run [2.0s]
│   └── Span: summarize_agent.llm_call [1.8s]
└── Span: supervisor.synthesize [300ms]

Total: 4.0s (sequential), 2.5s (parallel)
```

## Span Attributes

Every span should capture:

```python
trace_span = {
    "span_id": "s-123",
    "parent_span_id": "s-122",
    "trace_id": "t-456",
    "agent": "search_agent",
    "action": "search_web",
    "start_time": "...",
    "end_time": "...",
    "duration_ms": 800,
    "input_tokens": 150,
    "output_tokens": 50,
    "status": "success",
    "error": None,
    "metadata": {
        "query": "latest AI trends",
        "results_count": 5,
    },
}
```

## Message Tracking

Log every message between agents:

```python
message_log = {
    "message_id": "m-789",
    "type": "request",
    "from": "supervisor",
    "to": "search_agent",
    "task_id": "t-456",
    "correlation_id": "c-111",
    "size_bytes": 2048,
    "timestamp": "...",
    "latency_ms": 1500,
    "status": "success",
}
```

## Key Metrics

| Metric | What it Measures | Alert Threshold |
|--------|-----------------|-----------------|
| End-to-end latency | Task completion time | > 30s |
| Span duration | Per-agent processing time | > 10s |
| Handoff count | Number of agent transfers | > 5 |
| Communication overhead | Time spent on messages | > 30% of total |
| Agent error rate | Errors per agent type | > 10% |
| Message failure rate | Failed deliveries | > 1% |

## Visualization

A trace viewer should render the agent interaction graph:

```
Time:  0s    1s    2s    3s    4s
Supervisor [━━━━━━━━━━━━━━━━━━━━━━━━━━]
Search     [━━━━━━━]
Summarize          [━━━━━━━━━━━]
Format                      [━━━━]

Handoffs:
  supervisor → search    (1.5s)
  search → summarize     (2.0s)
  summarize → format      (3.2s)
```

## Logging Structure

Use structured logging with consistent fields across all agents:

```json
{
  "timestamp": "2024-12-01T10:00:00Z",
  "level": "INFO",
  "agent": "search_agent",
  "trace_id": "t-456",
  "span_id": "s-123",
  "message": "Search completed",
  "duration_ms": 800,
  "metadata": {...}
}
```

## Debugging Common Issues

| Symptom | Likely Cause | Check |
|---------|-------------|-------|
| High latency | One agent is slow | Check individual span durations |
| Wrong answer | Incorrect routing | Check router classification |
| Missing context | Handoff dropped context | Check handoff message size |
| Duplicate work | No idempotency | Check for duplicate task_ids |
| Agent loop | Circular delegation | Check agent handoff graph |
