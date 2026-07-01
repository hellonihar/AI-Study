# Infrastructure Security for AI Systems

## Architecture Overview

```
Internet → WAF → API Gateway → Guardrails → LLM → Guardrails → User
                                                         ↓
                                              Monitoring & Audit
```

## API Security

### Authentication

| Method | Strength | Use Case |
|--------|----------|----------|
| API Key | Medium | Server-to-server |
| OAuth 2.0 | High | User-facing applications |
| JWT | High | Stateless auth with claims |
| mTLS | Very High | Internal service-to-service |

### Authorization

- User-level: What actions can this user perform?
- Rate-limit tiers: Free vs premium users get different limits
- Data scoping: User A cannot access User B's data

### Input Validation

Beyond guardrail content checks:
- Validate request schema (JSON schema validation)
- Enforce maximum request size (prevent DOS via giant payloads)
- Reject malformed requests before they reach guardrails

## Network Security

### Segmentation

| Network Zone | Contains | Access Rules |
|-------------|----------|--------------|
| Public DMZ | API Gateway, WAF | Open to internet |
| Application | Guardrails, orchestrator | API Gateway only |
| Model | LLM servers | Application layer only |
| Data | Vector DB, cache | Model layer only |
| Management | Monitoring, CI/CD | Internal team VPN |

### Encryption

- **In transit**: TLS 1.3 for all external and internal communication
- **At rest**: Encrypt model weights, training data, logs (AES-256)
- **In memory**: HSM for encryption keys, avoid storing secrets in model context

## CI/CD Security

### Pipeline Security Gates

| Stage | Security Check |
|-------|---------------|
| Code commit | SAST (static analysis) |
| Dependency install | SCA (dependency scanning) |
| Build | Image scanning (trivy, grype) |
| Deploy staging | DAST (dynamic analysis) |
| Deploy production | Signed images, approval gate |

### Model Pipeline Security

- Training data source verification (provenance tracking)
- Model weight integrity check (hash verification)
- Guardrail version pinned to deployment (no drift between train and serve)
- Rollback capability for model and guardrails independently

## Monitoring & Incident Response

### Security Monitoring

| Alert | Trigger | Response Time |
|-------|---------|---------------|
| Guardrail bypass detected | Attack success, confirmed | Immediate rollback |
| Extraction attempt | >1000 queries/min from single user | Rate limit + investigate |
| Data poisoning suspected | Evaluation metric anomaly | Quarantine training data |
| Model integrity violation | Weight hash mismatch | Restore from backup |
| API key compromised | Key used from unexpected location | Rotate key, audit logs |

### Incident Response Plan

```
1. Detect (monitoring alarm)
2. Triage (is it a real incident? severity?)
3. Contain (block user, rollback model, disable endpoint)
4. Investigate (logs, traces, impact assessment)
5. Remediate (fix vulnerability, update guardrails, retrain if needed)
6. Post-mortem (root cause, lessons learned, timeline)
```

### Tabletop Exercises

Run quarterly AI security tabletop exercises with:
- Simulated prompt injection attack
- Simulated data extraction attempt
- Simulated model integrity compromise
- Simulated supply chain attack on ML dependencies

## Compliance Controls

| Control | Implementation |
|---------|---------------|
| Access reviews | Quarterly review of all API keys and IAM roles |
| Audit logging | All security events logged with correlation ID |
| Data retention | Logs retained 90 days, training data per policy |
| Penetration testing | Annual third-party pen test including AI attack vectors |
| Vulnerability management | Monthly scan of all dependencies, critical patches within 48h |
| Incident response | Documented plan, tested quarterly |
