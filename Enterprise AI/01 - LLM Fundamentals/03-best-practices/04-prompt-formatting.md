# Prompt Formatting

Using the correct chat template and prompt structure. Mismatched formats silently degrade quality.

## Chat Templates

Every model expects a specific format. Using the wrong one can cause 5–20% quality loss.

| Model | Template | Example |
|---|---|---|
| **LLaMA-3** | `<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n...<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n...<|eot_id|><|start_header_id|>assistant<|end_header_id|>` |
| **Mistral** | `<s>[INST] ... [/INST]` or `[INST] ... [/INST]` |
| **ChatML** (GPT-4, Qwen) | `<|im_start|>system\n...<|im_end|>\n<|im_start|>user\n...<|im_end|>\n<|im_start|>assistant\n` |
| **Gemma** | `<bos><start_of_turn>user\n...<end_of_turn>\n<start_of_turn>model\n` |
| **Claude** | Uses special XML tags internally. System prompt goes in `system` parameter, not appended to messages. |

## Loading the Correct Template

```python
from transformers import AutoTokenizer

# ✅ Correct: loads the model's native chat template
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is RAG?"},
]
prompt = tokenizer.apply_chat_template(messages, tokenize=False)
print(prompt)
# <|begin_of_text|><|start_header_id|>system<|...>
```

## System Prompt Best Practices

1. **Keep it short.** Every token costs money and consumes context. Target 200–500 tokens.
2. **Put instructions first.** The model pays more attention to the beginning (attention sink).
3. **Be specific.** "Output JSON with fields: answer, confidence, citations" → more reliable than "Be concise."
4. **Use delimiters for variable sections:**

```
[SYSTEM]
You are a financial analyst. Answer based only on the provided context.

[CONTEXT]
{retrieved_chunks}

[USER]
{user_question}
```

## Common Mistakes

| Mistake | Impact | Fix |
|---|---|---|
| No system prompt | Model fills in its own (inconsistent) | Always provide one |
| Role markers missing | Model confuses user/assistant roles | Use `apply_chat_template()` |
| Extra whitespace | Tokenizer includes BOS twice or wrong | Don't manually construct |
| Few-shot in wrong format | Examples ignored or confused | Match template's role structure |
| Trailing newlines | Model starts with "\n" instead of actual content | Strip before sending |

## Production Checklist

- [ ] Use `apply_chat_template()` — never hand-roll the format.
- [ ] Validate template output with a unit test.
- [ ] Cache the template — don't re-apply for every request.
- [ ] Log the formatted prompt (truncated) for debugging.
- [ ] Test with and without system prompt to measure impact.
