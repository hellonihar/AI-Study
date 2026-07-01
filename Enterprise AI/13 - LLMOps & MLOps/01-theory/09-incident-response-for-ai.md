# Incident Response for AI Systems

## Types of AI Incidents

| Incident Type | Example | Severity |
|---------------|---------|----------|
| Quality degradation | Model starts hallucinating more | High |
| Safety breach | Guardrail bypass produces harmful content | Critical |
| Latency spike | p99 latency increases 5x | High |
| Cost anomaly | Daily cost spikes 10x | Medium |
| Model failure | Model returns errors or empty responses | Critical |
| Data leakage | PII appears in model outputs | Critical |
| Drift event | Input distribution shifts significantly | Medium |
| Dependency failure | Vector DB, API, or cache unavailable | High |

## Incident Response Process

### Detection
Sources:
- Automated monitoring alerts (latency, errors, quality)
- User reports (abuse reports, support tickets)
- Scheduled evaluation runs (quality regression)
- Manual review (spot checks, red team findings)

### Triage (within 5 minutes)

```
1. Is this a real incident? (vs monitoring noise)
2. What is the severity? (SEV-1 through SEV-4)
3. What is the scope? (all users, specific feature, specific model)
4. Who needs to be notified? (on-call, team, leadership)
```

### Containment

| Severity | Containment Action | Time Target |
|----------|-------------------|-------------|
| SEV-1 | Rollback model, block traffic, disable feature | < 5 min |
| SEV-2 | Rollback model, rate limit users | < 15 min |
| SEV-3 | Deploy fix to staging, prepare rollback | < 2 hours |
| SEV-4 | Create ticket, investigate next sprint | < 1 week |

### Investigation

| Question | Data Source |
|----------|-------------|
| When did the incident start? | Metrics timeline |
| What changed recently? | Deployment log, config changes, data updates |
| Which users are affected? | Request logs, user segments |
| What is the failure mode? | Error messages, output samples |
| Is this a recurrence? | Incident history |

### Remediation

| Root Cause | Fix | Verification |
|------------|-----|-------------|
| Bad model deployment | Rollback to previous version | Eval on regression suite |
| Bad prompt change | Revert prompt | Run golden test set |
| Upstream data change | Update retrieval pipeline | End-to-end integration test |
| Infrastructure failure | Restart/rescale services | Load test |
| Training data issue | Retrain with corrected data | Full evaluation |

### Post-Incident Review (within 72 hours)

Template:

```
## Post-Incident Review
Incident ID: INC-2026-001
Date: 2026-07-01
Duration: 1h 23min (detection to full resolution)
Severity: SEV-2

## Summary
Brief description of what happened and impact.

## Timeline
- 14:23 - Alert: Quality score dropped below threshold
- 14:25 - On-call engineer triaged as SEV-2
- 14:28 - Rollback initiated (model v2.1.0 → v2.0.0)
- 14:35 - Rollback confirmed, metrics stabilizing
- 15:46 - Full recovery confirmed

## Root Cause
The new prompt template (v4) removed a critical instruction
that prevented hallucination on financial topics.

## Impact
- 23 min of degraded responses (hallucination rate: 8.2% vs 1.1% baseline)
- ~12,000 affected requests
- 3 user complaints received

## Action Items
1. [P0] Add regression test for financial hallucination - Due: 2026-07-02
2. [P1] Add automated guardrail for financial topic accuracy - Due: 2026-07-07
3. [P2] Implement canary gate that checks hallucination rate - Due: 2026-07-14
```

## Post-Incident Testing

After every incident:
1. Add the failing case to the regression test suite
2. Verify the fix resolves the issue
3. Run full regression suite to check for side effects
4. Update monitoring thresholds if needed
5. Update incident response playbook

## Common Failure Modes

| Failure Mode | Detection | Prevention |
|-------------|-----------|------------|
| Prompt regression | Eval score drop | CI gate for prompt changes |
| Model hallucination spike | LLM-as-judge score drop | Output guardrails |
| Latency spike from context growth | p99 latency alarm | Context window limits |
| Cost explosion from retry storms | Cost anomaly alert | Circuit breakers |
| Dependency cascade failure | Error rate increase | Bulkheads, fallbacks |
| Data poisoning | Quality metric degradation | Training data validation |
