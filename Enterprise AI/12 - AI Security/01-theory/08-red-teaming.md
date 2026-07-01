# Red Teaming for AI Systems

## What is AI Red Teaming

Red teaming is the systematic testing of an AI system to discover vulnerabilities, bypasses, and failure modes. It simulates adversarial attacks to evaluate the system's security, safety, and alignment before real attackers do.

## Methodology

### Planning Phase

1. **Scope definition**: What systems, models, and guardrails are in scope?
2. **Threat modeling**: Who are the attackers? What are their goals? What attack vectors are available?
3. **Rules of engagement**: What is off-limits? (e.g., DoS attacks on production, social engineering of staff)
4. **Success criteria**: What constitutes a finding? Severity classification.

### Execution Phase

#### Manual Red Teaming
Human testers attempt to bypass guardrails and elicit harmful outputs.

**Techniques:**
| Category | Techniques |
|----------|------------|
| Prompt injection | Direct override, indirect injection, payload splitting |
| Jailbreaking | DAN, roleplay, hypothetical, multi-turn erosion |
| Encoding | Base64, hex, Unicode, Leetspeak |
| Multilingual | Translate attack to low-resource language |
| Context manipulation | Long context, many-shot poisoning, token smuggling |

#### Automated Red Teaming
Tools generate thousands of attack variants to find bypasses at scale.

| Tool | Approach |
|------|----------|
| Garak | LLM vulnerability scanner with 100+ probes |
| PyRIT | Microsoft's automated red teaming framework |
| Counterfit | AI security assessment tool |
| GPTFuzzer | Evolutionary fuzzing for jailbreaks |
| Custom | Use LLM to generate attack variants and evaluate defenses |

### Analysis Phase

For each finding:
1. Document the exact input and output
2. Classify severity (Critical/High/Medium/Low)
3. Identify the root cause (guardrail gap, model alignment gap, infrastructure gap)
4. Suggest remediation
5. Track as a regression test for future evaluations

## Severity Classification

| Severity | Definition | Response |
|----------|------------|----------|
| Critical | Direct harm, regulatory violation, PII leakage | Immediate remediation, system may be taken offline |
| High | Significant capability for harm, extraction of non-public info | Fix within sprint, canary until fixed |
| Medium | Policy violation, minor content policy bypass | Fix within quarter, added to regression suite |
| Low | Theoretical risk, requires chained exploits | Documented, monitored |

## Red Team Cadence

| Cadence | Focus | Scope |
|---------|-------|-------|
| Continuous (automated) | Known attack patterns | Full system, daily |
| Weekly (manual) | New attack techniques | High-priority surfaces |
| Monthly (focused) | Specific feature or model update | Changed surfaces |
| Quarterly (full) | Comprehensive red team | Full system |
| Annual (third party) | External perspective | Full system + infrastructure |

## Building a Red Team

### Internal vs External

| Aspect | Internal | External (Third Party) |
|--------|----------|----------------------|
| Domain knowledge | Deep | Shallow |
| Fresh perspective | Limited | High |
| Cost | Lower | Higher |
| Availability | Ongoing | Intermittent |
| Bias | May miss own blind spots | Objective |

**Recommendation:** Both. Internal for continuous testing, external for periodic fresh perspectives.

### Skills Required

- Prompt engineering and jailbreak knowledge
- Security testing methodology (OWASP, PTES)
- Python/scripting for automation
- Understanding of ML model behavior
- Knowledge of relevant regulations (GDPR, HIPAA, EU AI Act)

## Reporting

### Finding Template

```
## Finding: [Title]
- Severity: Critical/High/Medium/Low
- System: [Model, guardrail version, deployment]
- Attack vector: [Prompt injection / Jailbreak / Extraction / etc.]
- Input: [Exact input]
- Output: [Exact output]
- Root cause: [Why did this bypass defenses?]
- Remediation: [Suggested fix]
- Regression test: [Tracking ID]
```

### Executive Summary

For non-technical stakeholders:
- Number of findings by severity
- % of attack surface covered
- Top 3 risks and recommended actions
- Trend vs previous red team engagement

## Responsible Disclosure

If vulnerabilities are found in third-party systems (base models, guardrail providers, infrastructure):
1. Notify the vendor privately
2. Provide reproduction steps and impact analysis
3. Agree on disclosure timeline (typically 90 days)
4. Publish coordinated disclosure when fixed

## Ethics and Boundaries

Red teaming must have clear ethical boundaries:
- No targeting of real users
- No social engineering of non-consenting staff
- No data exfiltration of real user data
- All findings reported internally first
- Testing stops immediately if real user impact is discovered
