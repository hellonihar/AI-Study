# Scaling and Performance

## Bottlenecks in Multi-Agent Systems

| Bottleneck | Cause | Impact |
|------------|-------|--------|
| Supervisor agent | Centralized orchestration | Limits throughput to 1 supervisor |
| State store | All agents read/write | Latency spikes under load |
| LLM API rate limits | All agents call LLM | 429 errors, queuing |
| Tool latency | External API calls | Agents wait for tools |
| Message bus | High message volume | Delivery delays |

## Horizontal Scaling

### Stateless Agents (Easy)
Agents that don't hold state can be replicated behind a load balancer.

```
Load Balancer → Agent A1, Agent A2, Agent A3
```

### Stateful Agents (Harder)
Use external state store (Redis) so any replica can handle any request.

```
Load Balancer → Agent A1, Agent A2 → Redis (state)
```

### Specialized Scaling
Scale different agents independently based on demand.

```
Search agents: 10 replicas (high demand)
Summarize agents: 3 replicas (medium demand)
Format agents: 1 replica (low demand)
```

## Queue-Based Load Leveling

Instead of direct agent-to-agent calls, use queues between stages.

```
Agent A → Queue → Agent B → Queue → Agent C
```

### Benefits
- Handles traffic spikes (queue buffers excess)
- Decouples agents (A doesn't wait for B)
- Auto-scaling based on queue depth

### Configuration
| Parameter | Recommendation |
|-----------|---------------|
| Queue type | SQS, RabbitMQ, Redis Streams |
| Max queue depth | 10,000 messages |
| Worker concurrency | Queue depth / processing time |
| Dead letter queue | After 3 retries |

## Parallel Execution

Independent tasks can execute in parallel:

```python
# Sequential: A → B → C = 6s
# Parallel: A(2s) + B(2s) + C(2s) = 2s
```

```python
async def run_parallel(*agents):
    results = await asyncio.gather(
        agent_a.run(task_a),
        agent_b.run(task_b),
        agent_c.run(task_c),
    )
    return results
```

## Latency Budget

Typical latency budget for a multi-agent task:

```
Total target: 10s
├── Router/Classifier:     500ms   (5%)
├── Search Agent:          2,000ms (20%)
│   ├── LLM call:          800ms
│   └── Tool (search):    1,000ms
├── Analyze Agent:         3,000ms (30%)
│   └── LLM call:         2,500ms
├── Generate Agent:        3,000ms (30%)
│   └── LLM call:         2,500ms
├── Synthesize:            1,000ms (10%)
└── Overhead:                500ms  (5%)
```

## Caching

Cache agent outputs to avoid redundant work:

| Cache Type | Key | TTL | Hit Rate |
|-----------|-----|-----|----------|
| Tool results | (agent, tool, params) | 1 hour | 20–40% |
| Router classifications | Query text | 24 hours | 40–60% |
| Agent responses | (agent, task_hash) | 1 hour | 10–20% |

## Performance Testing

```python
# Load test: simulate 50 concurrent tasks
async def load_test(num_tasks=50):
    tasks = [run_agent(agent, test_query) for _ in range(num_tasks)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    success = [r for r in results if not isinstance(r, Exception)]
    latency = [r.latency for r in success]
    print(f"Success rate: {len(success)/num_tasks:.0%}")
    print(f"p50 latency: {sorted(latency)[len(latency)//2]:.1f}s")
    print(f"p99 latency: {sorted(latency)[int(len(latency)*0.99)]:.1f}s")
```
