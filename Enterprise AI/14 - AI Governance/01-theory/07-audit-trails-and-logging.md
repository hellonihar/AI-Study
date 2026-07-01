# Audit Trails & Logging for Compliance

## Why Audit Trails Matter

Audit trails provide the evidence needed to demonstrate compliance, investigate incidents, and maintain accountability. Without them, organizations cannot prove they followed required processes.

## What to Log

### Model Lifecycle Events

| Event | Data to Log | Retention |
|-------|-------------|-----------|
| Model registration | Name, version, type, developer, date | Lifetime of model |
| Training run | Dataset version, config, hyperparameters, metrics | 3 years |
| Evaluation run | Test set, metrics, comparison to baseline | 3 years |
| Approval | Approver, date, conditions | Lifetime of deployment |
| Deployment | Target environment, version, rollback version | 3 years |
| Rollback | Trigger, version rolled to, impact | 3 years |
| Retirement | Date, replacement, data disposition | 2 years |

### Inference Events

| Event | Data to Log | Notes |
|-------|-------------|-------|
| Request | User ID (pseudonymized), input hash, timestamp | No raw PII in logs |
| Guardrail decision | Guardrail name, score, action taken | Full detail needed |
| Model inference | Model version, latency, token count | No raw output in compliance logs |
| Output delivery | Output hash, delivery status | Verifiable delivery |
| User feedback | Rating, correction (anonymized) | Aggregated after collection |

### Governance Events

| Event | Data to Log |
|-------|-------------|
| Policy change | Before/after diff, approver, date |
| Risk assessment | Score, tier, assessor, approver |
| Incident | Detection time, severity, response actions, resolution time |
| Audit | Auditor, scope, findings, remediation plan |
| Review | Reviewer, model, date, outcome |

## Logging Requirements

### Integrity
- Logs must be tamper-evident (append-only, hashed chain)
- Access to logs must be logged
- Logs must be immutable after creation

### Availability
- Logs must be available within defined SLA (e.g., 99.9%)
- Backup strategy with defined RTO/RPO
- Disaster recovery for log infrastructure

### Confidentiality
- No raw PII in audit logs
- Access control on log storage
- Encryption at rest and in transit

## Audit Log Architecture

```
Application → Structured Logger → Buffer → Log Storage → Index → Query
                    ↓                              ↓
               Schema v1.0                    Retention Policy
```

### Storage Backend Options

| Backend | Pros | Cons | Best For |
|---------|------|------|----------|
| Cloud object store (S3, Blob) | Cheap, durable, scalable | No built-in query | Long-term archive |
| Time-series DB (Elasticsearch) | Fast queries, aggregation | Expensive at scale | Active logs |
| Blockchain-based | Tamper-evident by design | Complex, slow | High-trust requirements |
| Append-only DB (Immuta) | Purpose-built | Cost | Enterprise compliance |

## Log Format Standards

### Recommended Fields

```json
{
  "version": "1.0",
  "timestamp": "2026-07-01T14:23:00.000Z",
  "source": "model-server",
  "event_type": "inference_complete",
  "severity": "INFO",
  "trace_id": "abc123def456",
  "actor_id": "user_12345",
  "resource": {
    "type": "model",
    "id": "gpt-4o-mini-v2.1.0"
  },
  "action": "infer",
  "result": "success",
  "hash": {
    "input": "sha256:abc...",
    "output": "sha256:def..."
  },
  "metadata": {
    "latency_ms": 320,
    "tokens": 570,
    "temperature": 0.3
  }
}
```

## Log Retention & Disposal

| Log Category | Retention | Disposal Method |
|--------------|-----------|-----------------|
| System logs | 30-90 days | Secure deletion |
| Audit logs | 1-3 years | Cryptographic erasure |
| Compliance evidence | Lifetime + 2 years | Secure archival |
| Legal hold | Until released | Preserved in place |

## Automated Compliance Checking

```
Log → Compliance Rules Engine → Report → Dashboard
          ↓
    Violation → Alert → Remediation
```

Rules example:
- Every model deployment must have an associated approval record
- Every Tier 3+ model must have a bias audit within the last 6 months
- Every incident must have a post-mortem within 72 hours

## Common Audit Failures

| Failure | Impact | Prevention |
|---------|--------|------------|
| Missing logs | Cannot prove compliance | Automated logging, no opt-out |
| Tampered logs | Evidence inadmissible | Immutable storage, hash chain |
| PII in logs | Privacy violation | PII redaction at source |
| Incomplete coverage | Audit gaps | Log coverage testing |
| Late logs | Missed events | Real-time log shipping |
