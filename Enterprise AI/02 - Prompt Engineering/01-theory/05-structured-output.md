# Structured Output

Reliably getting LLMs to produce valid, parseable structured data (JSON, YAML, code).

## Methods (in order of reliability)

| Method | Reliability | Latency | Complexity |
|---|---|---|---|
| **Prompt-only** (instruct + examples) | 70–90% | Fastest | None |
| **Function calling** (native API) | 90–98% | Fast | Low |
| **Constrained decoding** (grammar) | 99.9% | Moderate | Medium |
| **Schema-guided + retry** | 99%+ | Variable | Medium |
| **Multi-step validation** | 99.9% | Slow | High |

## Prompt-Only

```
You are a JSON generator. Respond ONLY with valid JSON matching this schema:
{
  "name": "string",
  "age": "number",
  "tags": ["string"]
}

User: Extract info: John Doe, 32, engineer and manager.
```

**Problems:** Long outputs may get truncated mid-JSON. Temperature > 0 can produce invalid JSON. Nested schemas increase error rates.

## Function Calling (OpenAI, Anthropic, Gemini)

Define tools via API parameters — the model returns structured arguments:

```json
{
  "type": "function",
  "function": {
    "name": "extract_person",
    "parameters": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "age": {"type": "number"},
        "tags": {"type": "array", "items": {"type": "string"}}
      },
      "required": ["name", "age"]
    }
  }
}
```

- **More reliable than prompt-only** because the model was fine-tuned on tool-calling data.
- **Use `tool_choice: "required"`** to force function call every time.

## Constrained Decoding (Outlines, Guidance, lm-format-enforcer)

Modifies logits at inference time to enforce a grammar:

```python
import outlines

schema = outlines.json_schema(
    '{"name": "str", "age": "int", "tags": ["str"]}'
)
generator = outlines.generate.json(model, schema)
result = generator("Extract: John Doe, 32, engineer and manager.")
# Never fails — impossible to produce invalid JSON
```

- **100% reliability** — invalid tokens are masked from the logits.
- **Supported by:** vLLM (guided decoding), llama.cpp (grammars), Outlines, Guidance.

## Schema-Guided + Retry

```
attempt 1: generate → parse → if valid: done
attempt 2: "Your previous output was not valid JSON.
           Error: {parse_error}. Please fix and retry."
attempt 3: same as attempt 2
attempt 4: fallback to default value or human review
```

- **Good for API-based models** where constrained decoding isn't available.
- **Max retries:** 2–3. Beyond that, the model usually doesn't improve.

## Schema Design Principles

- **Flat over nested.** Deeply nested JSON confuses LLMs. Prefer 2 levels max.
- **Optional fields with defaults.** Every optional field should have a documented default.
- **Enums for constrained values.** `"role": {"type": "string", "enum": ["admin", "user", "viewer"]}` is more reliable than open-ended.
- **Avoid `anyOf`/`oneOf`.** LLMs struggle with conditional schemas. Use `allOf` or flatten instead.
- **Keep field names descriptive.** `"person_name"` > `"pn"`. LLMs use field names as hints.

## Best Practices

- **Use function calling** when available — it's the best reliability-to-effort ratio.
- **Use constrained decoding** for self-hosted models — it eliminates parse errors entirely.
- **Set `temperature: 0` for structured output** — deterministic formatting.
- **Always validate output** — never assume parse success. Have a retry or fallback path.
- **Log schema failures** — high error rates indicate a schema that's too complex for the model.
