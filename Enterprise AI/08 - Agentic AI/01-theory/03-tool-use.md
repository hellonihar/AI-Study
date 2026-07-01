# Tool Use

## Tool Integration in Agents

Tools are the agent's interface to the outside world. Each tool encapsulates a capability (API call, database query, code execution) that the agent can invoke.

## Tool Lifecycle

```
Agent decides → Selects tool → Validates params → Executes → Returns result → Agent evaluates
```

## Tool Categories

| Category | Examples | Latency | Risk |
|----------|----------|---------|------|
| Information | Search, DB query, document load | 100ms–3s | Low |
| Computation | Calculator, code execution | 500ms–30s | Medium |
| Mutation | Send email, create ticket, update DB | 1s–5s | High |
| Communication | Slack message, send SMS | 200ms–2s | High |
| System | File I/O, shell commands | 10ms–10s | Critical |

## Tool Selection Strategy

### Rule-based
Pre-define which tool handles which intent. Simple but rigid.

### Model-based
LLM selects the tool based on descriptions. Flexible but can make wrong choices.

### Hybrid
Use a classifier for common intents, fall back to LLM for ambiguous cases.

## Tool Definition Schema

```python
TOOL_REGISTRY = {
    "search": {
        "description": "Search knowledge base for relevant documents",
        "parameters": {
            "query": {"type": "string", "description": "Search query"},
            "top_k": {"type": "integer", "default": 5},
        },
        "required": ["query"],
        "timeout": 10,
        "retry_on_failure": True,
    }
}
```

## Error Recovery

| Error | Agent Action |
|-------|-------------|
| Tool not found | Report available tools, ask for clarification |
| Invalid params | Correct params based on error message, retry |
| Timeout | Retry once with longer timeout, then skip |
| Service error | Try alternative tool, escalate if critical |
| Partial result | Use available data, note incompleteness |

## Tool Composition

Tools can be composed into higher-level capabilities:

```python
def research_topic(topic):
    """High-level tool: search, summarize, and cite sources."""
    results = search(topic, top_k=10)
    summaries = [summarize(r) for r in results]
    return compile_report(summaries)
```

## Safety Considerations

- Validate all parameters server-side
- Limit destructive tool access (delete, write) with confirmation
- Audit log every tool invocation
- Set per-tool rate limits and cost budgets
- Sandbox code execution tools
