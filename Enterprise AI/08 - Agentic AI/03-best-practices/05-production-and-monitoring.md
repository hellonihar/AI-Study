# Production and Monitoring Best Practices

## Deployment Architecture

### Stateless Agent (Recommended)
```
Load Balancer → Agent Servers (stateless) → State in Redis → Tools
```
Pros: Easy to scale, simple deployment, fast recovery
Cons: Requires external state storage

### Stateful Agent
```
Load Balancer → Agent Servers (sticky sessions) → Local memory → Tools
```
Pros: Simpler architecture, no external deps
Cons: Hard to scale, state lost on restart

## Scaling Strategy

| Component | Scaling Trigger | Strategy |
|-----------|----------------|----------|
| Agent servers | Queue depth > 100 | Auto-scale group +5 instances |
| Redis (memory) | Memory > 70% | Cluster mode, add shards |
| Tool APIs | Latency > 500ms | Rate limit, add fallback |
| Observability | Throughput > 1K trace/min | Batch writes, sampling |

## Monitoring Dashboard

### Per-Agent Metrics
- Active sessions
- Steps per session (p50, p95, p99)
- Cost per session (p50, p95, p99)
- Error rate per step
- Loop rate (% of sessions with detected loops)

### Per-Tool Metrics
- Invocations per minute
- Success rate
- Average latency
- Error distribution (timeout, invalid, service error)

### Cost Dashboard
```
Daily Cost by Model:
  GPT-4o:        $45.20 (62%)
  GPT-4o-mini:   $22.10 (30%)
  Claude Haiku:  $5.80  (8%)
Total:           $73.10
Budget:          $100.00
Remaining:       $26.90
```

## Alerting Thresholds

| Alert | Threshold | Action |
|-------|-----------|--------|
| High error rate | > 10% error in 5 min | Page on-call |
| Cost spike | > 2x daily average | Investigate, kill runaway tasks |
| Loop detected | > 5% sessions with loops | Review agent prompt/logic |
| Tool timeout | > 20% tool calls timeout | Check tool availability |
| Budget exceeded | > 90% monthly budget | Reduce model tier, tighten caps |

## Canary Deployments

```python
# Deploy new agent version alongside current
canary = ProductionAgent(config_v2)
control = ProductionAgent(config_v1)

# Route 5% of traffic to canary
if random.random() < 0.05:
    result = canary.run(query)
else:
    result = control.run(query)
```

Monitor for 24 hours:
- Completion rate within 2% of control
- Cost per task within 10% of control
- No new error types

## Rollback Plan

1. Detect regression (error rate > 10%, cost > 2x)
2. Revert agent to previous version (config change, no code deploy)
3. Redirect all traffic to previous version
4. Investigate root cause from traces
5. Deploy fix and repeat canary

## Production Checklist

- [ ] Max steps limit (15–25)
- [ ] Cost budget per task ($0.50–$2.00)
- [ ] Loop detection (same action > 3x)
- [ ] Tool timeouts (10s default)
- [ ] Input/output guardrails
- [ ] Human-in-the-loop for destructive actions
- [ ] Observability pipeline (traces, metrics, logs)
- [ ] Canary deployment process
- [ ] Rollback plan documented
- [ ] Cost alerting configured
- [ ] Rate limiting per user
- [ ] Emergency stop accessible
