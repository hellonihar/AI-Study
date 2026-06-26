# Enterprise Governance → AI Guardrails & Safety

## The Traditional Skill

You dealt with enterprise governance: compliance requirements (GDPR, SOC 2, HIPAA), risk assessment, access control, audit trails, data retention policies, and vendor risk management. You knew where data lived, who could access it, and what happened when things went wrong.

## The AI Equivalent

AI guardrails apply the same governance principles to LLM inputs and outputs. Instead of "who can access this database," you ask "what kind of content can this model generate?" Instead of "audit who accessed the data," you log every prompt-response pair. Instead of "vendor risk assessment," you evaluate model providers and their data handling policies.

The governance mindset transfers directly:
- **Access control** → guardrails that restrict what topics the model discusses
- **Audit trails** → tracing every LLM call with input, output, and metadata
- **Data retention** → TTL policies for prompt logs, training data, and vector stores
- **Compliance** → ensuring the model doesn't generate regulated advice (medical, legal, financial) without disclaimers
- **Incident response** → runbooks for safety failures, data leaks, or model misbehavior
- **Policy enforcement** → content filters, topic restrictions, and output validation rules

## New Concepts to Learn

- **Prompt injection:** An attacker overrides system instructions — the new SQL injection
- **Content filtering:** Classifying inputs and outputs for hate speech, violence, sexual content, etc.
- **Guard models:** Dedicated models (Llama Guard, NeMo Guardrails) that watch the LLM's inputs and outputs
- **Red-teaming:** Proactively testing the model for safety vulnerabilities — the new penetration testing
- **Constitutional AI:** Defining principles that the model should follow — the new code of conduct
- **PII redaction:** Detecting and removing personal information from prompts and responses
- **Model risk:** A model update can change behavior without warning — requiring regression testing before any update

## A Concrete Translation Example

**Traditional governance:** Security review checklist → access control policy → audit logs → incident response plan

**AI governance:** Input guardrails (what can the user ask?) → Output guardrails (what can the model say?) → Audit trail (every prompt + response logged) → Red-teaming results → Incident response plan for safety failures

Same layered defense approach. The implementation tools are different (guard models vs. firewalls), but the governance structure — policy, enforcement, monitoring, incident response — is identical.

## Key Resources

- NVIDIA NeMo Guardrails — guardrail implementation framework
- Llama Guard — safety classification model
- "Constitutional AI: Harmlessness from AI Feedback" (Anthropic)
- OWASP Top 10 for LLM Applications
- "Responsible AI Practices" (Google PAIR)
