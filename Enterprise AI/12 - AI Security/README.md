# AI Security

Protecting LLM systems from adversarial attacks, data leakage, and policy violations.

## Key Topics
- Prompt injection: direct, indirect, multi-turn, encoded — detection and prevention
- Guardrails: input filters (jailbreak, topic), output filters (PII, policy, toxicity)
- Data leakage: least-privilege context, sandboxed retrieval, output redaction
- Red-teaming: automated and manual adversarial testing methodologies
- Authentication & authorization: API keys, OAuth, RBAC for tool access
- Rate limiting, anomaly detection, and DoS protection
- Audit logging: every input, output, and tool call for forensics
- Fail-closed architecture: guardrails default to blocking
