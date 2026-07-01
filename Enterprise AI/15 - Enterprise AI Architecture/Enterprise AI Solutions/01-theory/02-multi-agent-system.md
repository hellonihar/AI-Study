# Multi-Agent System Architecture

## Agent Topologies

| Topology | Best For | Complexity |
|----------|----------|------------|
| Supervisor | Single request, multiple subtasks | Medium |
| Peer-to-peer | Collaborative problem solving | High |
| Pipeline | Sequential processing stages | Low |
| Hierarchical | Enterprise workflows | Very high |
| Market | Open-ended, many agents | Extreme |

## Reference: Supervisor Agent

```
User Request
    |
    v
[Supervisor Agent] -- routes to
    |       |        |
    v       v        v
[Researcher][Coder][Critic]
    |       |        |
    +-------+--------+
            |
            v
[Synthesizer] -> aggregates results
            |
            v
         Response
```

## Design Principles

| Principle | Why |
|-----------|-----|
| Single responsibility | Each agent does one thing well |
| Bounded context | Agents don't share internal state directly |
| Structured handoff | Standardized message format between agents |
| Human in the loop for critical decisions | Safety and auditability |
| Observability | Trace all agent communication |
| Session-scoped | Context limited to single interaction |
