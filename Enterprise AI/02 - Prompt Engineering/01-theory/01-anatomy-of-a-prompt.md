# Anatomy of a Prompt

Every LLM call follows a structured message format. Understanding its components is the foundation of prompt engineering.

## Message Roles

| Role | Purpose | Characteristics |
|---|---|---|
| **system** | Sets behavior, tone, constraints | Highest attention-sink position. Most authoritative. |
| **user** | The human's input | Variable content. Can be short or long. |
| **assistant** | Model's response | Used for few-shot examples and multi-turn history. |
| **tool** | Result of a function call | Structured data returned to the model. |

## Token Budget Allocation

A well-structured prompt allocates its token budget deliberately:

```
Total Context Window
├── System Prompt (10–15%)    ← behavior, format, constraints
├── Retrieved Context (40–60%) ← factual grounding, RAG chunks
├── Conversation History (15–25%) ← recent turns, summarized older turns
└── Current User Input (5–10%) ← the actual question
     └── Response Budget (10–20%) ← max_tokens for generation
```

## The Attention Sink Effect

Research shows the first and last tokens of a prompt receive disproportionately high attention:

- **Primacy bias:** Instructions at the beginning are followed more reliably.
- **Recency bias:** Information at the end is recalled better for generation.
- **Implication:** Place the most critical instruction at the start; place format constraints at the end.

```
┌─── Most attended (put system instructions here)
│
[SYSTEM] You are a financial analyst. Answer only from the provided context.
[CONTEXT] ...
[USER] What is the P/E ratio?
│
└─── Second most attended (put format instruction here)
     For example: Always end with a citation.
```

## Delimiter Strategies

Use consistent delimiters to isolate sections:

```
[SYSTEM] ... [/SYSTEM]
[CONTEXT] ... [/CONTEXT]
[USER] ... [/USER]
```

Benefits:
- Prevents prompt injection from user content
- Makes prompt structure parseable for evaluation
- Enables automated checks (e.g., "Did response stay within `[USER]`?")

## Best Practices

- **System prompt is for behavior, not data.** Don't put dynamic context there — it evades prefix caching.
- **Examples belong in user/assistant turns,** not in the system prompt — this preserves the system prompt's cacheability.
- **Test instruction placement.** Move your most important instruction from position 1 to position 10 in the system prompt — measure the quality difference.
- **Use the model's native chat template.** Hand-rolling message formats causes subtle quality regressions.
