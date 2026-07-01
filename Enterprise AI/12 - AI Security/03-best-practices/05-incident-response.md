# Incident Response Best Practices for AI Systems

## Incident Classification

| Severity | Definition | Examples | Response Time |
|----------|------------|----------|---------------|
| SEV-1 | Active harm, PII leakage, system compromise | Model outputs PII, successful jailbreak produces dangerous content | Immediate |
| SEV-2 | Significant bypass, potential for harm | Guardrail bypass discovered in production | < 1 hour |
| SEV-3 | Minor bypass, policy violation | Benign policy bypass, low-risk content | < 24 hours |
| SEV-4 | Monitoring alert, no confirmed impact | Anomalous traffic pattern, drift detection | < 1 week |

## Incident Response Process

### 1. Detection
Sources of incident detection:
- Automated monitoring alerts (guardrail bypass rate, error rate, latency)
- User reports (abuse report, feedback)
- Red team findings (scheduled or ad-hoc)
- Internal audit (log review, manual inspection)

### 2. Triage
```
Is this a real incident?
├── No → Document as false alarm, adjust monitoring
└── Yes → Classify severity
    ├── SEV-1 → Immediate response
    ├── SEV-2 → Response within 1 hour
    ├── SEV-3 → Next business day
    └── SEV-4 → Next sprint
```

### 3. Containment

| Severity | Containment Actions |
|----------|---------------------|
| SEV-1 | Block offending user/API key, rollback model to previous version, disable vulnerable endpoint |
| SEV-2 | Rate limit affected user, update guardrails, canary fix |
| SEV-3 | Schedule fix in current sprint, monitor for escalation |
| SEV-4 | Log for investigation, no immediate action |

### 4. Investigation

| Question | Data Source |
|----------|-------------|
| What input triggered the incident? | Audit logs, request history |
| Which guardrail failed? | Guardrail decision logs |
| How many users were affected? | Impact analysis |
| What data was exposed? | Output logs, data at rest |
| Is this a new attack or known pattern? | Attack library, red team history |
| Was the attack targeted or random? | User behavior analysis |

### 5. Remediation

| Finding | Remediation |
|---------|-------------|
| Guardrail gap | Add detection pattern, retrain classifier, update thresholds |
| Model alignment gap | Red team focused on vulnerability, schedule retraining |
| Infrastructure vulnerability | Patch, update config, restrict access |
| Process gap | Update playbook, add monitoring, train team |

### 6. Post-Incident Review

Template:

```
## Post-Incident Review
- Incident ID: 
- Date: 
- Severity:
- Duration: (detection to containment)

## Timeline
- T0: Detection
- T0+[min]: Triage complete
- T0+[min]: Containment
- T0+[hr]: Investigation complete
- T0+[hr]: Remediation deployed

## Root Cause
[Clear description of why the incident occurred]

## Impact
[Quantified impact: users affected, data exposed, downtime]

## What Went Well
- [List of effective responses]

## What Could Be Better
- [List of improvement areas]

## Action Items
1. [Action] - Owner - Due date
2. [Action] - Owner - Due date

## Prevention
[Changes to prevent recurrence]
```

## Communication Plan

| Stakeholder | SEV-1 | SEV-2 | SEV-3 | SEV-4 |
|-------------|-------|-------|-------|-------|
| Security team | Immediate | < 1 hour | Next day | Weekly |
| Engineering | Immediate | < 1 hour | Next day | Email |
| Product | < 1 hour | < 4 hours | Next day | Email |
| Legal/Compliance | < 1 hour | < 24 hours | If needed | No |
| Executive | < 1 hour | < 24 hours | Summary | No |
| Customers | If impacted | If impacted | No | No |
| Regulators | If required | If required | If required | No |

## Post-Incident Testing

After every incident:
1. Add the attack to the automated regression test suite
2. Verify the fix blocks the specific attack
3. Verify the fix does not increase false positive rate
4. Run full red team to check for similar bypass techniques
5. Update incident response playbook with lessons learned
