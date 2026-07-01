# Production Agent

## Complete Architecture

Combining all patterns into a production-ready agent:

```
User Request
    │
    ▼
┌─────────────────────────────────────┐
│          API Gateway                │
│  (auth, rate limit, routing)        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       Orchestrator                  │
│  ┌──────────────────────────────┐  │
│  │ Safety Layer                 │  │
│  │  → Input guardrails          │  │
│  │  → Output guardrails         │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │ Memory Layer                 │  │
│  │  → Working memory (context)  │  │
│  │  → Semantic memory (vector)  │  │
│  │  → Episodic memory (logs)    │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │ Reasoning Layer              │  │
│  │  → ReAct / Plan-and-Solve   │  │
│  │  → Reflection loop          │  │
│  │  → Cost tracker              │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │ Action Layer                 │  │
│  │  → Tool registry             │  │
│  │  → Tool executor             │  │
│  │  → Error handler             │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │ Observability Layer          │  │
│  │  → Step tracing              │  │
│  │  → Metrics emission          │  │
│  │  → Log aggregation           │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Execution Flow

```python
class ProductionAgent:
    def __init__(self):
        self.safety = SafetyLayer()
        self.memory = MemoryManager()
        self.reasoning = ReasoningEngine()
        self.tools = ToolRegistry()
        self.observability = ObservabilityLayer()
        self.budget = BudgetManager(max_cost=1.00)
        self.max_steps = 25

    async def run(self, user_request):
        # 1. Safety check input
        self.safety.check_input(user_request)

        # 2. Retrieve relevant memories
        context = self.memory.retrieve(user_request)

        # 3. Initialize tracking
        task_id = self.observability.start_trace(user_request)

        # 4. Agent loop
        step = 0
        while step < self.max_steps and self.budget.within_budget():
            step += 1

            # Reason
            action = self.reasoning.decide(context)

            # Execute
            if action.type == "tool":
                result = self.tools.execute(action)
                context.add_tool_result(result)
            elif action.type == "respond":
                response = action.content
                break
            elif action.type == "reflect":
                improvement = self.reasoning.reflect(context)
                context.apply_improvement(improvement)

            # Track
            self.observability.log_step(task_id, step, action)
            self.budget.track_step(action.cost)

        # 5. Safety check output
        response = self.safety.check_output(response)

        # 6. Store in memory
        self.memory.store(task_id, user_request, response)

        # 7. Finalize
        self.observability.finalize_trace(task_id)
        return response
```

## Deployment Considerations

| Component | HA Strategy | Scaling |
|-----------|-------------|---------|
| API Gateway | Active-active | Horizontal |
| Orchestrator | Active-active with state in Redis | Horizontal |
| Memory (vector) | Active-passive replication | Cluster |
| Tools (external API) | Circuit breaker + fallback | Rate limited |
| Observability | Sidecar pattern | Buffer + batch write |

## Configuration

```python
AGENT_CONFIG = {
    "model": {
        "primary": "gpt-4o",
        "fallback": "gpt-4o-mini",
        "reflection_model": "gpt-4o-mini",
    },
    "limits": {
        "max_steps": 25,
        "max_cost": 1.00,
        "max_tokens_per_step": 4000,
        "max_reflection_cycles": 3,
        "timeout_per_step": 30,
    },
    "memory": {
        "working_memory_turns": 20,
        "semantic_top_k": 5,
        "episodic_top_k": 3,
    },
    "tools": {
        "default_timeout": 10,
        "max_retries": 2,
    },
}
```

## Production Checklist

- [ ] Input/output guardrails implemented
- [ ] Cost budget and alerting configured
- [ ] Max steps limit enforced
- [ ] Loop detection active
- [ ] Memory pruning scheduled
- [ ] Observability pipeline deployed
- [ ] Human-in-the-loop for destructive actions
- [ ] Emergency stop accessible
- [ ] Rate limiting per user
- [ ] A/B testing framework ready
