# Agent Design Best Practices

## When to Use Agents

| Use Case | Agent? | Alternative |
|----------|--------|-------------|
| Single LLM call with no tools | No | Direct inference |
| Multi-step task with tools | Yes | — |
| Task requires memory across turns | Yes | — |
| Simple lookup with RAG | No | RAG pipeline (no agent) |
| Complex research/synthesis | Yes | — |
| User needs deterministic output | No | Rule-based system |

## Architecture Principles

### 1. Keep It Simple
- Start with a single ReAct loop
- Add reflection, memory, planning only when needed
- Each new component adds cost and latency

### 2. Fail Fast
- Validate inputs early
- Set aggressive timeouts (5s per step)
- Hard limit on total steps (15–25)

### 3. Make Every Step Observable
- Log thought, action, observation, and cost per step
- Store traces for debugging and audit
- Alert on anomalies (loops, high cost, failures)

### 4. Test in Isolation
- Test tool execution separately from the agent loop
- Mock the LLM to test tool selection logic
- Test each guardrail independently

## Common Anti-Patterns

| Anti-pattern | Problem | Solution |
|-------------|---------|----------|
| Too many tools | Model confused, picks wrong tool | Group related tools, max 10–15 |
| No step limit | Infinite loop or cost runaway | Always set max_steps |
| Reflection on every step | 2x cost, latency for marginal gain | Reflect only on failure or uncertainty |
| Full context always | Token explosion, high cost | Prune irrelevant context |
| No fallback for tools | Agent stuck when tool fails | Define fallback for every tool |

## Model Selection

| Task | Recommended Model | Rationale |
|------|------------------|-----------|
| Simple reasoning | GPT-4o-mini / Haiku | Fast, cheap, sufficient |
| Complex planning | GPT-4o / Opus | Better at multi-step reasoning |
| Reflection | GPT-4o-mini | Cheaper, good enough for evaluation |
| Code generation | GPT-4o / Claude Sonnet | Best code quality |

## Tool Design Rules

- Each tool does ONE thing
- Tool names are verbs (`search`, `calculate`, `send_email`)
- Parameters have clear descriptions
- Return structured JSON (model parses it better)
- Timeout per tool: 10s default, 30s for heavy tools
