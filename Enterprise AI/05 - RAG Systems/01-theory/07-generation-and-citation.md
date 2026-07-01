# Generation and Citation

Producing grounded, attributable answers from retrieved passages.

## The Generation Stage

```
System: "Answer using ONLY the provided passages. Cite each claim.
If passages don't contain the answer, say 'I cannot find this information.'"

Context:
[1] European division revenue reached €12.4M in Q3 2024...
[2] The strategy change focused on expanding Nordic markets...
[3] Nordic market entry costs were €2.1M in Q3 2024...

User: "What was the impact of the European strategy change on Q3 revenue?"
```

Expected output:
```
The European strategy change focused on expanding into Nordic markets [2].
This incurred €2.1M in entry costs during Q3 2024 [3]. Despite these costs,
European division revenue reached €12.4M in Q3 2024 [1].
```

## Citation Formats

### Inline Brackets
```
Revenue grew 15% YoY [1][3], driven by European expansion [2].
```
- Pros: Granular, easy to parse
- Cons: Cluttered for many citations

### Superscript
```
Revenue grew 15% YoY^(1,3), driven by European expansion^(2).
```
- Pros: Clean for human readers
- Cons: Harder for automated parsing

### Markdown Links
```
Revenue grew 15% YoY[^1][^3], driven by European expansion[^2].
```
- Pros: Clickable in rendered output
- Cons: Only works in markdown-supported UIs

### Lettered References
```
Revenue grew 15% YoY [A][C], driven by European expansion [B].
```
- Pros: Reduces visual clutter for many citations
- Cons: Requires legend for prose

## Prompt Engineering for Citation

### System Prompt Template

```
You are a helpful assistant that answers questions based on provided passages.

RULES:
1. Answer using ONLY the provided passages below.
2. If passages do not contain sufficient information, say:
   "I cannot find this information in the provided passages."
3. For every factual claim, cite the source passage number.
4. Use inline citation format: [1], [2, 3], [1-3].
5. Do not combine information from different passages without citing each.
6. If passages contradict each other, note the contradiction.
```

### Few-Shot Examples

Adding 1-3 examples in the system prompt improves citation accuracy by 10-20%:

```
Examples:

Passages:
[1] The sky appears blue due to Rayleigh scattering.
[2] The sky can appear red during sunrise and sunset.

Query: Why is the sky blue?
Answer: The sky appears blue due to Rayleigh scattering of sunlight [1].

Query: Can the sky be red?
Answer: Yes, the sky can appear red during sunrise and sunset [2].
```

## Faithfulness Mechanisms

### 1. Constrained Decoding

Force the model to cite by interleaving retrieval tokens with generation:

```python
# Pseudocode: force citation after each factual claim
logits = model.generate(context, query)
if claim_detected(logits):
    force_token("[")   # begin citation
```

Practical implementation: Guidance, LMQL, Outlines, or vLLM's guided decoding.

### 2. Post-Hoc Citation Verification

Verify each claim against retrieved passages after generation:

```
Generated answer:
"European revenue grew 15% in Q3 [1]. Nordic entry costs were €2.1M [3]."

Verification:
Claim 1: "European revenue grew 15% in Q3" → check [1] → PASS
Claim 2: "Nordic entry costs were €2.1M" → check [3] → PASS
```

If a claim lacks a valid citation, either regenerate or flag for human review.

### 3. Self-Check

Ask the LLM to verify its own citations:

```
User: "Did you cite correctly? For each [N], check that passage N supports the claim."
LLM: "[1] supports 'revenue grew 15%' — yes, the passage states '€12.4M... 15% increase'."
```

Catch rate: ~70% of citation errors. Better than nothing, but not a replacement for post-hoc verification.

## Handling Insufficient Context

When passages don't contain the answer, the model must refuse — not hallucinate.

```python
# Bad: model tries to answer anyway → hallucination
"European division revenue increased slightly in Q3."

# Good: explicit refusal
"I cannot find the specific financial figures for the European division
in Q3 2024 in the provided passages. The passages mention the strategy
change (source [2]) but do not include revenue numbers."
```

**Prompt instruction:**
```
If the provided passages do not contain enough information to answer
the question completely, state what you know and clearly indicate
what information is missing. Do NOT make up information.
```

## Citation Accuracy Metrics

| Metric | Definition | Target |
|---|---|---|
| Citation precision | % of citations that correctly support the claim | > 0.95 |
| Citation recall | % of claims that have a supporting citation | > 0.90 |
| Faithfulness | % of statements supported by at least one passage | > 0.98 |
| Refusal rate | % of unanswerable queries correctly refused | > 0.95 |

## Generation Configuration

```python
generation_config = {
    "temperature": 0.1,        # low for factual Q&A
    "top_p": 0.9,
    "max_tokens": 1024,
    "stop": ["\n\nHuman:", "\n\nUser:"],
    "presence_penalty": 0.0,   # avoid encouraging new topics
    "frequency_penalty": 0.0,
}
```

**Temperature:** 0.1-0.3 for RAG. Higher temperatures increase hallucination risk.

## Structured Output

For programmatic consumption, request structured JSON:

```
System: Return a JSON object with "answer" (string) and "citations" (array of {id, text}).
```

```json
{
  "answer": "European division revenue reached €12.4M in Q3 2024.",
  "citations": [
    {"id": 1, "text": "European division revenue reached €12.4M in Q3 2024, a 15% increase."}
  ],
  "confidence": "high",
  "missing_information": []
}
```

Use JSON mode (OpenAI) or constrained decoding (vLLM, Guidance) for reliable parsing.
