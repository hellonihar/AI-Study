# Output Guardrails

## Purpose

Output guardrails inspect and filter model responses before they reach the user. They catch harmful content the model might generate despite safety training, and prevent PII or sensitive information leakage.

## Guardrail Architecture

```
LLM → Output → Content Safety → PII Redaction → Policy Check → User
                      ↓
                Audit Log
```

## Output Guardrail Layers

### Layer 1: Content Safety

Classify model output for harmful content:

| Category | Examples | Detection |
|----------|----------|-----------|
| Hate speech | Racial slurs, targeted harassment | Toxicity classifier |
| Violence | Physical harm descriptions, weapons | Violence classifier |
| Sexual content | Explicit descriptions | NSFW classifier |
| Self-harm | Suicide methods, self-injury | Self-harm classifier |
| Harassment | Bullying, intimidation | Harassment classifier |

**Implementation:** Use a dedicated content safety API or fine-tuned classifier. For high-throughput, use a small transformer model (e.g., roberta-toxicity). For maximum accuracy, use LLM-as-judge with a safety rubric.

### Layer 2: PII Redaction

Detect and redact personally identifiable information:

| PII Type | Pattern | Action |
|----------|---------|--------|
| Email addresses | `[\w.+-]+@[\w-]+\.[\w.-]+` | Redact or replace |
| Phone numbers | `\+?\d{1,3}[-.\s]?\d{3}[-.\s]?\d{4}` | Redact |
| SSN | `\d{3}-\d{2}-\d{4}` | Redact |
| Credit card | `\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}` | Redact |
| API keys | `sk-[a-zA-Z0-9]{20,}` | Redact |
| IP addresses | `\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}` | Redact or anonymize |
| Names | NER-based detection | Anonymize (replace with placeholder) |
| Addresses | NER + regex | Anonymize |

**Redaction strategies:**
- **Mask**: Replace with `[REDACTED]`
- **Anonymize**: Replace with type-based placeholder `[EMAIL]`
- **Pseudonymize**: Replace with consistent fake value for same real value
- **Partial**: Show first/last characters only (`j***@***.com`)

### Layer 3: Policy Compliance

Check output against business-specific policies:

| Policy | Check | Action |
|--------|-------|--------|
| Competitor mentions | Does output reference competitors? | Flag for review |
| Pricing claims | Does output quote prices? | Verify against current pricing |
| Legal disclaimers | Required disclaimers present? | Append if missing |
| Brand voice | Matches tone guidelines? | LLM-as-judge evaluation |
| Factual claims | Verifiable statements? | Check against knowledge base |

### Layer 4: Format Validation

Ensure output matches expected structure:

| Expected Format | Validation |
|----------------|------------|
| JSON | Parseable, matches schema |
| HTML | Well-formed, no XSS |
| Markdown | Valid syntax |
| CSV | Correct column count |
| Code | Syntax-valid for target language |

## Response Handling

| Guardrail Result | Action | User Facing |
|-----------------|--------|-------------|
| Pass | Deliver response | Normal output |
| Block (safety) | Replace with canned response | "I cannot provide that response." |
| Block (PII) | Redact and deliver | Redacted output |
| Flag (policy) | Escalate for human review | Hold with explanation |
| Format error | Retry with stricter format prompt | Brief delay |

## Performance Considerations

| Guardrail | Typical Latency | Cost |
|-----------|----------------|------|
| Regex PII | < 1ms | Free |
| ML toxicity classifier | 5–20ms | Low |
| LLM-as-judge (safety) | 200–1000ms | Medium |
| LLM-as-judge (policy) | 300–1500ms | Medium |
| Format validation | < 5ms | Free |

## Feedback Loop

When an output guardrail blocks content:
1. Log the full context (input, output, guardrail scores)
2. Periodically sample blocked outputs for human review
3. If false positives are found, adjust thresholds or retrain classifiers
4. If false negatives are found, add patterns or harden classifiers

## Common Bypass Techniques

| Technique | Defense |
|-----------|---------|
| Output splitting | Check per-sentence and aggregate |
| Encoding output | Decode before checking |
| Incremental disclosure | Contextual analysis across turns |
| Code-switching (mixing languages) | Multi-lingual classifiers |
| Gradual escalation | Track topic trajectory over session |
