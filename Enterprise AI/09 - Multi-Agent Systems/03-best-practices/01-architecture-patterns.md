# Multi-Agent Architecture Best Practices

## Pattern Selection Guide

| Scenario | Recommended Pattern | Why |
|----------|-------------------|-----|
| Fixed workflow with defined steps | Supervisor | Clear control flow, easy to debug |
| High-volume classification | Router | Fast, scalable, simple |
| Exploratory/problem-solving | Delegation | Flexible, agent decides when to delegate |
| Deep task decomposition | Hierarchical | Natural for tree-structured tasks |
| Quality-critical decisions | Debate/Consensus | Multiple perspectives reduce errors |

## Design Principles

### 1. Start with One Agent
Don't build a multi-agent system until a single agent fails. Multi-agent adds complexity, latency, and cost. Prove that a single agent can't meet requirements first.

### 2. Clear Boundaries
Every agent must know:
- What it handles (its domain)
- What it does NOT handle (its boundaries)
- Where to send what it doesn't handle

### 3. Fail Gracefully
When an agent fails:
1. Retry (once)
2. Try alternative agent
3. Escalate to supervisor
4. Return graceful error to user

### 4. Minimize Communication
Every message between agents adds latency. Design agents to communicate once per decision point, not every step.

## Common Anti-Patterns

| Anti-pattern | Problem | Solution |
|-------------|---------|----------|
| Too many agents | Coordination overhead dominates | Max 5–7 agents per task |
| Overlapping domains | Agents conflict, duplicate work | Clear responsibility boundaries |
| Deep hierarchies | Latency explosion (sequential) | Max depth 3 levels |
| No fallback | Single agent failure kills task | Alternative agent or supervisor |
| Shared context everywhere | Context blowup, token waste | Only pass relevant context |
| All agents use same model | Cost waste, no differentiation | Use cheaper models for simple agents |

## Communication Design

- Use structured messages (JSON) with consistent schema
- Include `correlation_id` for tracing
- Include `reply_to` for response routing
- Size limit: max 10KB per message (summarize before sending)
- Timeout: 10s per agent response

## Testing Multi-Agent Systems

| Test Type | What | How |
|-----------|------|-----|
| Unit | Each agent in isolation | Mock other agents |
| Integration | Two agents communicating | Real messages, verify flow |
| End-to-end | Full workflow | All agents, real tools |
| Chaos | Random agent failures | Kill agents mid-task, verify recovery |
| Load | N concurrent tasks | Measure throughput, latency |
