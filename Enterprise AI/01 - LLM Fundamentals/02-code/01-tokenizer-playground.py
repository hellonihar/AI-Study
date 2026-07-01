"""
Tokenizer Playground — explore BPE tokenization, vocabulary, and compression ratios.

Run: python 01-tokenizer-playground.py

Requirements: pip install transformers
"""

from transformers import AutoTokenizer
from collections import Counter
import random

# ─── Load a tokenizer ───
model_name = "meta-llama/Meta-Llama-3-8B"  # or "gpt2", "mistralai/Mistral-7B-v0.3"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# ─── 1. Basic encoding / decoding ───
text = "The quick brown fox jumps over the lazy dog."
tokens = tokenizer.encode(text)
print(f"Input: {text}")
print(f"Tokens (IDs): {tokens}")
print(f"Tokens (text): {tokenizer.convert_ids_to_tokens(tokens)}")
print(f"Decoded: {tokenizer.decode(tokens)}")
print(f"Compression ratio: {len(text) / len(tokens):.1f} chars/token\n")

# ─── 2. Compare domains ───
samples = {
    "general": "Artificial intelligence is transforming the way businesses operate.",
    "code": 'def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)',
    "medical": "The patient presented with acute myocardial infarction and ST-segment elevation.",
    "legal": "The aforementioned party shall indemnify and hold harmless the counterparty.",
    "math": "The Riemann zeta function ζ(s) is defined for complex s with Re(s) > 1.",
}

print("=== Compression Ratio by Domain ===")
for domain, text in samples.items():
    tokens = tokenizer.encode(text)
    ratio = len(text) / len(tokens)
    print(f"{domain:8s}: {len(tokens):3d} tokens, {ratio:.1f} chars/token")

# ─── 3. Vocabulary exploration ───
print("\n=== Vocabulary Sample ===")
vocab = list(tokenizer.vocab.items())
random.seed(42)
sample = random.sample(vocab, 10)
for token, idx in sorted(sample, key=lambda x: x[1]):
    print(f"  ID {idx:6d}: {repr(token)}")

# ─── 4. Rare vs common tokens ───
print("\n=== Token Frequency (in a sample corpus) ===")
corpus = "The cat sat on the mat. The dog sat on the log. The bird sat on the branch. " * 100
tokens = tokenizer.encode(corpus)
freq = Counter(tokens)
print(f"Total tokens: {len(tokens)}")
print(f"Unique tokens: {len(freq)}")
print(f"Most common: {tokenizer.decode([freq.most_common(1)[0][0]])!r}")
print(f"Rarest token: {tokenizer.decode([freq.most_common()[-1][0]])!r}")

# ─── 5. Subword breakdown ───
print("\n=== Subword Breakdown ===")
words = ["unbelievably", "transformers", "tokenization", "quantization", "hyperparameter"]
for word in words:
    tokens = tokenizer.tokenize(word)
    print(f"  {word:15s} → {tokens}")
