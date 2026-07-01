# Incident Response for AI Systems

## AI-Specific Incidents

| Incident Type | Example | Response |
|--------------|---------|----------|
| Quality degradation | Hallucination increase | Rollback model, investigation |
| Latency spike | P95 > 5s | Scale out, investigate bottleneck |
| Cost anomaly | 10x normal spend | Circuit break, rate limiting |
| Security | Prompt injection | Block input pattern, audit |
| Safety | Toxic output | Content filter, review |
| Data leak | PII in responses | Immediate block, incident declared |

## Response Playbook

1. **Detect** — Automated monitoring, user reports
2. **Triage** — Severity assessment, initial investigation
3. **Contain** — Block traffic, rate limit, rollback
4. **Resolve** — Fix root cause, deploy fix
5. **Review** — Postmortem within 48 hours

## Severity Levels

| Level | Response Time | SLA Impact |
|-------|--------------|------------|
| Sev1 (critical) | < 15 min | System down or data leak |
| Sev2 (high) | < 1 hour | Degraded for > 10% users |
| Sev3 (medium) | < 4 hours | Minor degradation |
| Sev4 (low) | < 48 hours | Cosmetic or non-production |
