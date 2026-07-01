# Prompt Design Patterns

Recurring prompt structures that work reliably in production.

## Proven Patterns

### Persona Pattern

```
You are a [role] with expertise in [domain]. 
[Additional context about the persona's style or constraints.]
```

**When it works:** Technical explanations, code review, domain-specific writing.
**Why it works:** Activates a specific distribution of the model's training data.

### Format-First Pattern

```
You will receive an input. Output ONLY valid JSON:
{
  "answer": "string",
  "confidence": 0.0–1.0,
  "citations": ["string"]
}
```

**When it works:** Any structured output task.
**Why it works:** The model generates tokens conditioned on the expected format from the first token.

### Constraint-Last Pattern

Put the most important constraint at the end of the prompt (second attention sink):

```
[Instructions]
[Context]
[Question]

IMPORTANT: Only answer from the provided context. If the context doesn't contain the answer, say "I don't know."
```

### Chain-of-Thought Pattern

```
[Question]
Let's think step by step.
```

**Extension:** "Let's work through this carefully, considering each piece of evidence."

### Few-Shot with Reasoning Pattern

```
Q: [question]
A: [reasoning trace] The answer is [answer].

Q: [question]  
A:
```

**Key:** The reasoning trace in the example teaches the model to reason, not just to pattern-match.

### Round-Trip Validation Pattern

```
Step 1: Generate answer.
Step 2: Verify the answer against the source material.
Step 3: If verification fails, correct the answer.
```

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| **Over-promising** | "You are a perfect, infallible expert" → model becomes overconfident in errors | Use "You are knowledgeable but cautious" |
| **Vague constraints** | "Be concise" → model defines conciseness differently | "Answer in under 30 words" |
| **Instructions in examples** | Embedding instructions inside few-shot examples dilutes the system prompt | Keep instructions separate from examples |
| **Contradictory instructions** | "Be creative" + "Follow the format exactly" → model optimizes for one | Prioritize: "Format above all; within format, be creative" |
| **Too many constraints** | Model ignores or averages all constraints equally | Top 3 constraints only. Test: remove each, measure impact |

## Production Pattern Selection Guide

```
Task type?
├── Classification / Extraction → Format-First + Persona
├── Reasoning / Analysis → Chain-of-Thought + Few-Shot with Reasoning
├── Creative writing → Persona + Constraint-Last
├── RAG QA → Format-First + Constraint-Last + Chain-of-Thought
└── Multi-step task → Round-Trip Validation
```
