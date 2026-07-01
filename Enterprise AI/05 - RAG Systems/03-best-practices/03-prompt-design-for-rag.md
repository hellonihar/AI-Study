# Prompt Design for RAG

Crafting system prompts that produce grounded, cited, faithful answers.

## The RAG System Prompt Template

```markdown
You are a helpful assistant that answers questions based on provided passages.

## Rules
1. Answer using ONLY the provided passages below.
2. If the passages do not contain sufficient information to answer the question,
   say "I cannot find this information in the provided passages."
   Do NOT make up or infer information not in the passages.
3. For every factual claim, cite the source passage number in brackets: [1], [2], etc.
4. Use multiple citations when a claim requires evidence from multiple passages: [1][2].
5. Do NOT combine information from different passages without citing each.
6. If passages contradict each other, present both perspectives and note the contradiction.

## Passages
{retrieved_passages}

## Question
{user_query}

## Answer
```

## Key Prompt Design Decisions

### Instruction Placement

Place the most critical instruction (answer using ONLY provided passages) at the START and END of the system prompt. LLMs pay most attention to the first and last instructions (primacy and recency effects).

### Negative Instruction

"Don't make up information" is weaker than "Say 'I cannot find this information.'" The explicit refusal phrase gives the model a concrete behavior to follow rather than a prohibition to follow.

### Citation Format

Specify the exact citation format in the prompt. Without explicit formatting instructions, LLMs cite inconsistently (some inline, some footnotes, some not at all). Demonstrate the format in a few-shot example if possible.

## Few-Shot Examples

Always include 2-3 examples in the system prompt:

```
## Examples

Passages:
[1] The Eiffel Tower was built in 1889 for the World's Fair in Paris.
[2] The Eiffel Tower is 330 meters tall including its antennas.

Question: When was the Eiffel Tower built and how tall is it?
Answer: The Eiffel Tower was built in 1889 for the World's Fair in Paris [1].
It currently stands at 330 meters including its antennas [2].

Question: Who designed the Eiffel Tower?
Answer: I cannot find this information in the provided passages. The passages
mention the construction year and height but do not specify the designer.
```

## Handling Edge Cases

### No Relevant Passages
```
Passages: [No relevant information found.]

Question: What is the capital of France?
Answer: I cannot find this information in the provided passages.
```

### Multiple Possible Answers
```
Passages:
[1] The meeting is scheduled for Monday at 2 PM.
[2] The meeting has been rescheduled to Tuesday at 3 PM.
[3] The meeting agenda includes budget review.

Question: When is the meeting?
Answer: There is conflicting information. Passage [1] states the meeting
is Monday at 2 PM, while passage [2] states it has been rescheduled to
Tuesday at 3 PM.
```

### Partial Information
```
Passages:
[1] The company reported Q3 revenue of $12.4 billion.

Question: What was Q3 revenue and profit?
Answer: According to passage [1], Q3 revenue was $12.4 billion. However,
the provided passages do not contain information about Q3 profit.
```

## Temperature and Generation Settings

| Setting | RAG Value | Rationale |
|---|---|---|
| temperature | 0.0-0.3 | Low temperature reduces hallucination risk |
| top_p | 0.9 | Standard nucleus sampling |
| presence_penalty | 0.0 | Avoid introducing new topics |
| frequency_penalty | 0.0 | Stick to passage content |
| max_tokens | 512-2048 | Match expected answer length |
| stop | ["\n\nUser:", "\n\n---"] | Avoid generating beyond answer |

## Prompt Anti-Patterns

| Anti-pattern | Why It Fails |
|---|---|
| "Use your knowledge to answer" | Causes hallucination (model prefers parametric memory) |
| "You are an expert" | Encourages the model to rely on its training, not provided passages |
| No citation format | Model cites inconsistently or not at all |
| One-shot example for complex task | Insufficient pattern guidance for reliable behavior |
| "Be concise" | Can lead to omitted citations in the name of brevity |

## Structured Output Prompt

For programmatic consumption:

```markdown
Return a JSON object with:
- "answer": string (the answer)
- "citations": array of objects with "passage_id" and "text"
- "confidence": "high" | "medium" | "low"
- "missing_information": array of strings (what couldn't be answered)

Example:
{
  "answer": "The Eiffel Tower was built in 1889.",
  "citations": [{"passage_id": 1, "text": "built in 1889"}],
  "confidence": "high",
  "missing_information": []
}
```

Use JSON mode (OpenAI) or constrained decoding (vLLM, Guidance) for reliable parsing.

## Testing Prompt Variations

A/B test prompt changes systematically:

| Variant | System Prompt Change | Faithfulness | Citation Accuracy |
|---|---|---|---|
| Baseline | Standard template | 0.92 | 0.88 |
| No citations | Remove citation requirement | 0.94 | 0.00 |
| Strict refusal | Strengthen "I don't know" language | 0.96 | 0.89 |
| Few-shot (3) | Add 3 examples | 0.95 | 0.93 |
| Few-shot (5) | Add 5 examples | 0.95 | 0.94 |
| Placebo | "You are helpful" only | 0.85 | 0.00 |

Changes to the system prompt can shift faithfulness by 5-10%. Test before deploying.
