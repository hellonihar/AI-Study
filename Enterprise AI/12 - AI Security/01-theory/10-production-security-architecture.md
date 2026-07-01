# Production Security Architecture

## Defense in Depth for AI Systems

A production AI system requires security at every layer, from user input to model output, across infrastructure, data, and operations.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Security Monitoring                          │
├─────────────────────────────────────────────────────────────────┤
│  Input Layer                                                     │
│  WAF → Auth → Rate Limit → Input Guardrails → Prompt Isolation  │
├─────────────────────────────────────────────────────────────────┤
│  Model Layer                                                     │
│  Secure Enclave → Access Control → Model Versioning              │
├─────────────────────────────────────────────────────────────────┤
│  Output Layer                                                    │
│  Output Guardrails → PII Redaction → Content Safety → Audit Log │
├─────────────────────────────────────────────────────────────────┤
│  Data Layer                                                      │
│  Encryption → Access Control → Retention → Backup                │
├─────────────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                            │
│  Network Isolation → IAM → Secrets → Monitoring → Incident Resp. │
└─────────────────────────────────────────────────────────────────┘
```

## Architecture Components

### 1. Input Security Pipeline

```
Request → WAF (SQLi, XSS) → Auth → Rate Limit → Input Guardrail → LLM
                                                       ↓
                                                 Sanitized Input
```

| Component | Function | Technology |
|-----------|----------|------------|
| WAF | Block common web attacks | Cloudflare, AWS WAF |
| Auth | Verify identity | OAuth 2.0, JWT |
| Rate Limit | Prevent abuse | Redis + middleware |
| Input Guardrail | Content safety | ML classifier + LLM judge |

### 2. Model Security Layer

```
LLM → Response → Output Guardrail → PII Redact → Content Filter → User
```

| Component | Function | Technology |
|-----------|----------|------------|
| Output guardrail | Safety classification | RoBERTa, Llama Guard |
| PII redaction | Detect and mask PII | Presidio, custom NER |
| Content filter | Policy compliance | LLM-as-judge |
| Audit logger | Immutable log | Splunk, ELK, S3 |

### 3. Secure Inference

```
Encrypted Request → Decrypt → Inference → Encrypt → Response
```

For sensitive workloads, use confidential computing:
- **NVIDIA Confidential Computing**: GPU-based TEE for model inference
- **Intel SGX/TDX**: CPU-based trusted execution environment
- **AMD SEV-SNP**: Encrypted VM for model hosting

### 4. Data Security

| Data Type | Protection |
|-----------|------------|
| Training data | Encrypted at rest (AES-256), access logged |
| User inputs | Encrypted in transit, retained per policy |
| Model weights | Integrity verified (SHA-256), access controlled |
| Prompts/system instructions | Encrypted, version controlled |
| Logs | Immutable, access logged, retained 90 days |

## Operational Security

### Secrets Management

| Secret | Storage | Rotation |
|--------|---------|----------|
| API keys | Vault, AWS Secrets Manager | 90 days |
| Database credentials | Vault, dynamic secrets | Per session |
| Model access tokens | Vault | 30 days |
| Encryption keys | HSM, KMS | Annual |
| Guardrail API keys | Vault | 90 days |

### Monitoring and Alerting

| Category | Metrics | Alert |
|----------|---------|-------|
| Guardrail bypasses | ASR, bypass count | > 1% of total requests |
| Rate limit violations | Per-user throttle count | > 10/min from single user |
| PII detection | PII instances in output | Any instance → investigate |
| Anomalous traffic | Query pattern deviation | > 3σ from baseline |
| Latency degradation | Guardrail p99 latency | > 2x baseline |
| Error rate | 4xx, 5xx responses | > 1% of requests |

## Incident Response for AI Systems

### Triage Levels

| Level | Definition | Response Time |
|-------|------------|---------------|
| SEV-1 | Active harm, PII leakage, system compromise | Immediate |
| SEV-2 | Significant bypass, potential for harm | < 1 hour |
| SEV-3 | Minor bypass, policy violation | < 24 hours |
| SEV-4 | Monitoring alert, no confirmed impact | < 1 week |

### Response Playbook

```
1. DETECT (alert → confirm → classify severity)
2. CONTAIN (block user → rollback model → disable endpoint)
3. INVESTIGATE (logs → trace → root cause)
4. REMEDIATE (fix → deploy → verify)
5. DOCUMENT (incident report → update playbook)
```

### Post-Incident Review

Template for post-incident reviews:

```
## Incident: [ID]
- Date: 
- Severity: 
- Summary:
- Timeline:
- Root cause:
- Impact: 
- Remediation:
- Prevention: (what changes prevent recurrence?)
- Action items:
```

## Security Testing Cadence

| Test | Frequency | Scope |
|------|-----------|-------|
| Automated red teaming | Daily | Guardrails, known attack patterns |
| Dependency scan | Weekly | All Python/node packages |
| Penetration test | Quarterly | Infrastructure, APIs |
| Full red team | Quarterly | Full system |
| Third-party audit | Annual | All of the above |
| Tabletop exercise | Quarterly | Incident response process |

## Compliance Automation

| Requirement | Automation |
|-------------|-----------|
| Audit logging | All security events auto-logged with correlation IDs |
| Access reviews | Automated report of all keys and permissions |
| Data retention | Automated data lifecycle management |
| Model cards | Generated from training metadata |
| Evaluation reports | Generated from eval pipeline |
| Incident reports | Generated from incident tracking system |
