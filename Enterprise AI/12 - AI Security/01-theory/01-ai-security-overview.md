# AI Security Overview

## The AI Threat Landscape

AI systems introduce a new attack surface beyond traditional security. Models can be manipulated through their inputs, outputs, training data, and infrastructure.

### Attack Categories

| Category | Target | Example |
|----------|--------|---------|
| Prompt Injection | Model input | Attacker injects instructions to override system prompt |
| Jailbreaking | Model alignment | Bypassing safety training to elicit harmful outputs |
| Data Poisoning | Training data | Malicious examples in training set cause targeted misbehavior |
| Model Inversion | Model weights | Extract training data from model outputs |
| Membership Inference | Model responses | Determine if specific data was in training set |
| Evasion | Model classification | Craft inputs that bypass content filters |
| Extraction | Model API | Steal model functionality through API queries |
| Supply Chain | Dependencies | Compromised packages in ML pipeline |

### Threat Modeling for AI Systems

Use STRIDE adapted for AI:

| Threat | AI Example |
|--------|-----------|
| Spoofing | Attacker impersonates a trusted user to the AI |
| Tampering | Modify training data or model weights |
| Repudiation | Model output with no audit trail |
| Information Disclosure | Training data leakage through model responses |
| Denial of Service | Resource exhaustion via crafted inputs |
| Elevation of Privilege | Prompt injection to bypass system prompt restrictions |

## The Security Stack for AI

```
┌─────────────────────────────────────┐
│         Application Layer           │
│  Input Guardrails → LLM → Output   │
│         Guardrails                  │
├─────────────────────────────────────┤
│         API Security                │
│  Auth, Rate Limiting, Audit Logs   │
├─────────────────────────────────────┤
│         Model Security              │
│  Access Control, Versioning, Eval  │
├─────────────────────────────────────┤
│         Infrastructure              │
│  Network Isolation, Encryption, IAM │
├─────────────────────────────────────┤
│         Training Pipeline           │
│  Data Validation, Provenance, Audit │
└─────────────────────────────────────┘
```

## Key Principles

### Defense in Depth
No single layer is sufficient. Multiple overlapping controls ensure that if one fails, others still protect the system.

### Fail Closed
When a security component cannot make a decision, it should deny rather than allow. A guardrail that times out should block the response, not pass it through.

### Least Privilege
The model and its supporting systems should have only the permissions needed for their function. An LLM should not have direct database access — it should use a tool with scoped permissions.

### Auditable by Design
Every security decision must be logged with sufficient context for post-incident analysis. This includes inputs, outputs, guardrail decisions, and any human review actions.

## Security Risk Classification

| Risk Level | Description | Examples |
|------------|-------------|----------|
| Critical | Direct harm, regulatory violation | PII leakage, hate speech generation, weaponization |
| High | Significant operational or reputational damage | Prompt injection, data extraction, brand damage |
| Medium | Limited impact, requires chained exploits | Benign policy violations, non-sensitive data leakage |
| Low | Minor policy violations | Off-topic responses, mild profanity |
