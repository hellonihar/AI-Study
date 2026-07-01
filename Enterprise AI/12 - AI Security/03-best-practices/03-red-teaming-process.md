# Red Teaming Process Best Practices

## Building a Red Team Program

### Team Composition
| Role | Background | Responsibility |
|------|------------|----------------|
| Red team lead | Security + AI experience | Plan, execute, report |
| Security engineer | Penetration testing | Infrastructure, API testing |
| ML engineer | LLM internals | Model-specific attacks |
| Domain expert | Business knowledge | Policy violation testing |
| Recorder | Technical writing | Documentation, findings management |

### Skills Required
- Prompt engineering and jailbreak techniques
- Web security testing (OWASP Top 10)
- Python automation
- Understanding of ML model behavior and alignment
- Knowledge of AI regulations (EU AI Act, NIST AI RMF)

## Execution Methodology

### Phase 1: Reconnaissance
1. Understand system architecture (guardrails, models, infrastructure)
2. Review documentation (system prompts, model cards, past findings)
3. Identify attack surface (API endpoints, input types, output formats)

### Phase 2: Attack Development
Create a library of attack vectors organized by:

| Category | Attack Types |
|----------|-------------|
| Prompt injection | Direct, indirect, payload splitting |
| Jailbreaking | DAN, roleplay, hypothetical, encoding |
| Extraction | System prompt, training data, PII |
| Evasion | Encoding, token smuggling, incremental disclosure |
| Infrastructure | API abuse, rate limit bypass, auth bypass |

### Phase 3: Execution
1. Automated scanning (Garak, PyRIT, custom scripts)
2. Manual testing (focused on high-value targets)
3. Chain attacks (combining multiple techniques)
4. Document every attempt with exact inputs and outputs

### Phase 4: Analysis

| Finding Severity | Definition | Response Time |
|-----------------|------------|---------------|
| Critical | Active harm, PII leakage | Immediate fix |
| High | Significant bypass capability | Fix within sprint |
| Medium | Policy violation, minor bypass | Fix within quarter |
| Low | Theoretical risk, chained exploits | Document and monitor |

## Report Template

```

## Red Team Engagement Report
- Date: YYYY-MM-DD
- Scope: [Systems tested]
- Team: [Red team members]
- Duration: [Hours/days]

## Executive Summary
- Total findings: [N]
- Critical: [N] | High: [N] | Medium: [N] | Low: [N]
- Block rate: [X]% (attacks successfully blocked)
- Top risk: [Brief description]

## Detailed Findings
### Finding 1: [Title]
- Severity: [Critical/High/Medium/Low]
- Attack: [Input]
- Result: [Output]
- Root cause: [Why did it bypass?]
- Remediation: [Fix description]
- Status: [Open/In Progress/Fixed]

## Regression Tests Added
- [Test ID]: [Description of attack preserved for future testing]

## Recommendations
1. [Priority action item]
2. [Secondary action item]
3. [Long-term improvement]
```

## Automation

| Tool | Purpose | Integration |
|------|---------|-------------|
| Garak | LLM vulnerability scanning | CI/CD pipeline |
| PyRIT | Automated red teaming | Nightly runs |
| Custom test suite | Known attack regression | Pre-deployment gate |
| Monitoring | Live attack detection | Production alerting |

## Continuous Improvement

### After Each Engagement
1. Update attack library with new techniques discovered
2. Add successful attacks to regression test suite
3. Share anonymized findings with the ML community
4. Update guardrail thresholds based on findings

### Metrics to Track
- Block rate over time (should increase)
- False positive rate over time (should decrease)
- Novel attack types discovered per engagement
- Time from finding to fix
