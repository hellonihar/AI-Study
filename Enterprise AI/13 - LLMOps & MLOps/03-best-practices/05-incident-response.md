# Incident Response Best Practices

## Incident Classification

### Severity Levels

| Severity | Description | Response Time | Example |
|----------|-------------|---------------|---------|
| SEV-1 | Critical user-facing impact | < 5 min | Safety breach, full outage |
| SEV-2 | Significant degradation | < 15 min | Quality drop, high latency |
| SEV-3 | Minor impact, no user visibility | < 2 hours | Cost spike, single user issue |
| SEV-4 | Cosmetic, low priority | < 1 week | Dashboard display issue |

### Common AI Incident Types

| Type | Typical Severity | Detection Signal |
|------|-----------------|-----------------|
| Safety breach (guardrail bypass) | SEV-1 | Output guardrail score spike |
| Quality degradation | SEV-2 | Quality metric drop below threshold |
| Latency spike | SEV-2 | p99 latency > 3s |
| Cost anomaly | SEV-3 | Cost > 2x daily average |
| Model failure (empty/error responses) | SEV-1 | Error rate spike |
| Data leakage (PII in outputs) | SEV-1 | PII detection alert |
| Drift event | SEV-3 | Embedding drift > 3 sigma |
| Dependency failure | SEV-2 | Upstream service error rate |

## Response Process

### 1. Detection (Automated)
Sources in priority order:
- Monitoring alerts (latency, errors, quality)
- Scheduled evaluation runs (quality regression)
- User reports (abuse reports, support tickets)
- Red team findings (scheduled security testing)

### 2. Triage (Within 5 Minutes)

```
Is this real?     -> Not monitoring noise?
What severity?    -> SEV-1 through SEV-4?
What scope?       -> All users? Specific feature? Specific model?
Who to notify?    -> On-call engineer? Team? Leadership?
```

### 3. Containment (Within Target Time)

| Severity | First Action | Alternative | Target |
|----------|-------------|-------------|--------|
| SEV-1 | Rollback model/prompt | Block traffic to feature | < 5 min |
| SEV-2 | Rollback to previous version | Rate limit affected users | < 15 min |
| SEV-3 | Deploy fix to staging | Prepare rollback | < 2 hours |
| SEV-4 | Create ticket | Investigate next sprint | < 1 week |

### 4. Investigation

Key questions to answer:
- When did the incident start? (Check metrics timeline)
- What changed recently? (Deployment log, config diff)
- Which users/customers affected? (Request logs)
- What is the exact failure mode? (Error messages, output samples)
- Is this a recurrence? (Check incident history)

### 5. Remediation

| Root Cause | Fix | Verification |
|------------|-----|-------------|
| Bad model deployment | Rollback to previous version | Eval on regression suite |
| Bad prompt change | Revert prompt | Run golden test set |
| Upstream data change | Fix retrieval pipeline | End-to-end integration test |
| Infrastructure failure | Restart/rescale services | Load test |
| Training data issue | Retrain with corrected data | Full evaluation |

### 6. Post-Incident Review (Within 72 Hours)

Required for all SEV-1 and SEV-2 incidents:

```
## Post-Incident Review
- Incident ID, date, duration, severity
- What happened and impact
- Timeline (detection -> triage -> containment -> resolution)
- Root cause analysis
- Action items with owners and due dates
```

## Action Item Classification

| Priority | Definition | Due |
|----------|------------|-----|
| P0 | Must fix immediately to prevent recurrence | 24 hours |
| P1 | Should fix to improve detection/prevention | 1 week |
| P2 | Nice to have, process improvement | 1 month |

## Post-Incident Testing

After every incident:
1. Add the failing case to the regression test suite
2. Verify the fix resolves the specific issue
3. Run full regression suite to check for side effects
4. Update monitoring thresholds if incident was missed by alerts
5. Update incident response playbook

## Prevention Measures

| Measure | Effort | Impact |
|---------|--------|--------|
| Pre-deployment eval gate | Medium | Prevents bad deployments |
| Canary with auto-rollback | Medium | Limits blast radius |
| Drift detection | Medium | Early warning on quality changes |
| Cost anomaly alerts | Low | Prevents budget overruns |
| Incident drills | High | Improves response time |
| Runbook documentation | Medium | Ensures consistent response |

## Common Failure Modes

| Failure Mode | Why It Happens | Prevention |
|-------------|---------------|------------|
| Prompt regression | Unintended change in prompt | CI gate, golden set eval |
| Model hallucination spike | Distribution shift or model update | Output guardrails, quality monitoring |
| Latency from context growth | Accumulated conversation history | Context window limits |
| Cost explosion from retries | Cascading failures | Circuit breakers |
| Dependency cascade | Single upstream failure | Bulkheads, fallbacks |
| Silent quality degradation | No quality monitoring | LLM-as-judge on sampled traffic |
