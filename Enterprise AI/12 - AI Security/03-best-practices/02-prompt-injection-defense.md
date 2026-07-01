# Prompt Injection Defense Best Practices

## Defense Layers

### Layer 1: Input Validation
- Normalize Unicode (NFC/NFKC) before any processing
- Strip or encode control characters
- Detect and decode obfuscated inputs (base64, hex, etc.)
- Reject excessively long inputs (token limits)

### Layer 2: Prompt Isolation
Separate system prompts and user input architecturally:

**Template-based isolation:**
```python
# BAD: User input mixed with instructions
prompt = f"System: Be helpful.\nUser: {user_input}"

# GOOD: Structured format with clear boundaries
prompt = f"""<system>Be helpful.</system>
<user>{xml_escape(user_input)}</user>"""
```

**XML/JSON encoding:** Encode user input so it cannot contain instructions. Escape all special characters.

**Sandwich defense:** Wrap user content between system instructions that reinforce behavior before and after the user input.

### Layer 3: Detection
| Method | Strength | Weakness |
|--------|----------|----------|
| Pattern matching | Fast, no false negatives for known patterns | Misses novel attacks |
| Embedding similarity | Catches semantic variants | Requires attack library |
| LLM-as-judge | Most accurate | High latency, cost |
| Entropy analysis | Detects obfuscation | High false positive rate |

### Layer 4: Response Verification
- Check model output matches expected format
- Verify the model didn't reveal system prompts
- Check for unexpected content (code blocks, JSON structures)

## Attack-Specific Defenses

| Attack Type | Defense |
|-------------|---------|
| Direct override | Pattern matching on "ignore", "override", "forget" |
| DAN/roleplay | Pattern matching + embedding similarity |
| Multi-turn erosion | Session-level context analysis |
| Encoding bypass | Decode and re-check input |
| Indirect injection | Sanitize retrieved content separately |
| Payload splitting | Reconstruct fragments and re-check |

## Secure System Prompt Design

| Practice | Example |
|----------|---------|
| Use positive instructions | "You will follow these rules" vs "Do not break rules" |
| Be specific | "Never output passwords, API keys, or personal data" vs "Be safe" |
| Use structured format | XML/JSON templates with escaped user content |
| Add end-of-prompt markers | Clear delimiter between system and user content |
| Version prompts | Track and evaluate prompt changes for security impact |

## Monitoring

| Metric | Alert Threshold |
|--------|----------------|
| Injection attempt rate | >5% of total requests |
| Injection success rate | >0% |
| False positive rate | >2% |
| Guardrail p99 latency | >500ms |
