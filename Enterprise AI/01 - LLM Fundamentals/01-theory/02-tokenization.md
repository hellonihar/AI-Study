# Tokenization

Tokenization maps raw text to integer IDs — the only transformation that loses information in the entire LLM pipeline.

## Algorithms

| Algorithm | Used By | Characteristics |
|---|---|---|
| BPE (Byte-Pair Encoding) | GPT, LLaMA, Mistral | Iteratively merges the most frequent byte/character pair. Vocab size 32K–128K. |
| SentencePiece (Unigram) | T5, Gemma | Probabilistic: starts with large vocab, prunes least likely merges. Language-agnostic. |
| WordPiece | BERT | Similar to BPE but merges based on likelihood gain rather than frequency. |

## How BPE Works

1. Start with character vocabulary (all individual bytes/characters).
2. Count all adjacent pairs in the corpus.
3. Merge the most frequent pair into a new token.
4. Repeat until desired vocabulary size is reached.

**Example:** "low" + "est" → "lowest" as a single token after enough merges.

## Important Concepts

- **Compression ratio:** English text ~4 characters/token for GPT-4o, ~6 for LLaMA-3. Code is denser (~3 char/token).
- **Domain-specific tokens:** Fine-tuning can add tokens for domain jargon (e.g., "hyperplane" → 1 token instead of 3).
- **Special tokens:** `<|begin_of_text|>`, `<|end_of_text|>`, `<|pad|>`, `<|eos|>`, role markers.
- **Chat templates:** Models expect specific formats (ChatML, Llama chat, Mistral instruct) — mismatched templates silently degrade quality.

## Best Practices

- **Profile your domain's tokenization efficiency.** A legal document that takes 10K tokens with GPT-4's tokenizer might take 7K with LLaMA-3's — a 30% cost difference.
- **Never change the tokenizer after training** — it changes the embedding space.
- **Use the model's exact tokenizer + chat template** — using the wrong one causes subtle quality loss.
- **Watch for token bleeding** — BPE can merge across word boundaries, causing tokens like " apple" (with leading space) vs "apple".

## Code (snippet)

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")
tokens = tokenizer.encode("Hello, world!", return_tensors="pt")
print(tokenizer.convert_ids_to_tokens(tokens[0]))
# ['<|begin_of_text|>', 'Hello', ',', ' world', '!']
```
