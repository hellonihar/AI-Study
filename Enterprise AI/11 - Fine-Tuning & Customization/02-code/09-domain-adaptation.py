"""
Domain adaptation: continued pre-training, vocabulary extension, and domain-specific fine-tuning.

Run: python 09-domain-adaptation.py

Requirements: numpy
"""

import numpy as np

print("=== Domain Adaptation ===\n")

class Tokenizer:
    def __init__(self):
        self.vocab = {f"tok_{i}": i for i in range(1000)}
        self.inv_vocab = {v: k for k, v in self.vocab.items()}

    def encode(self, text):
        return [hash(w) % 1000 for w in text.split()]

    def decode(self, ids):
        return " ".join(self.inv_vocab.get(i, "<unk>") for i in ids)

    def add_tokens(self, new_tokens):
        next_id = len(self.vocab)
        for token in new_tokens:
            if token not in self.vocab:
                self.vocab[token] = next_id
                self.inv_vocab[next_id] = token
                next_id += 1
        return len(new_tokens)

class DomainModel:
    def __init__(self, d_model=64, vocab_size=1000):
        self.d_model = d_model
        self.embedding = np.random.randn(vocab_size, d_model) * 0.01
        self.W = np.random.randn(d_model, d_model) * 0.01

    def forward(self, token_ids):
        h = self.embedding[token_ids]
        return h @ self.W

    def log_perplexity(self, token_ids):
        h = self.forward(token_ids)
        logits = h @ self.embedding.T
        log_probs = logits - np.max(logits, axis=-1, keepdims=True)
        log_probs = log_probs - np.log(np.sum(np.exp(log_probs), axis=-1, keepdims=True))
        return -np.mean(log_probs[np.arange(len(token_ids)), token_ids])

tokenizer = Tokenizer()

DOMAIN_TEXT = """
The patient presented with acute myocardial infarction and elevated troponin levels.
ST-segment elevation was observed in leads II III and aVF.
Primary percutaneous coronary intervention was performed within 90 minutes.
"""

GENERAL_TEXT = """
The weather today is sunny with a high of 75 degrees.
Machine learning models require large amounts of data to generalize well.
The capital of France is Paris known for the Eiffel Tower.
"""

domain_tokens = set(DOMAIN_TEXT.lower().split())
general_tokens = set(GENERAL_TEXT.lower().split())
unique_domain = domain_tokens - general_tokens
print(f"Domain-specific terms found: {len(unique_domain)}")
print(f"  Terms: {sorted(unique_domain)[:10]}")

vocab_before = len(tokenizer.vocab)
tokenizer.add_tokens(list(unique_domain))
print(f"\nVocabulary extended: {vocab_before} -> {len(tokenizer.vocab)} tokens")

model = DomainModel(d_model=64, vocab_size=len(tokenizer.vocab))
domain_ids = tokenizer.encode(DOMAIN_TEXT.lower())
general_ids = tokenizer.encode(GENERAL_TEXT.lower())

domain_ppl_before = np.exp(model.log_perplexity(domain_ids))
general_ppl_before = np.exp(model.log_perplexity(general_ids))
print(f"\nBefore domain adaptation:")
print(f"  Domain perplexity: {domain_ppl_before:.2f}")
print(f"  General perplexity: {general_ppl_before:.2f}")

print("\nSimulating domain adaptation training:")
NUM_STEPS = 50
for step in range(NUM_STEPS):
    x = np.array(domain_ids)
    h = model.forward(x)
    logits = h @ model.embedding.T
    loss = -np.mean(logits[np.arange(len(x)), x] - np.log(np.sum(np.exp(logits), axis=-1)))
    grad = np.random.randn(*h.shape) * 0.01
    model.embedding[x] -= 0.01 * np.random.randn(*model.embedding[x].shape) * 0.5
    model.W -= 0.01 * np.random.randn(*model.W.shape) * 0.5

    if (step + 1) % 10 == 0:
        print(f"  Step {step+1}: loss = {loss:.4f}")

domain_ppl_after = np.exp(model.log_perplexity(domain_ids))
general_ppl_after = np.exp(model.log_perplexity(general_ids))

print(f"\nAfter domain adaptation:")
print(f"  Domain perplexity: {domain_ppl_before:.2f} -> {domain_ppl_after:.2f} ({domain_ppl_before-domain_ppl_after:+.2f})")
print(f"  General perplexity: {general_ppl_before:.2f} -> {general_ppl_after:.2f} ({general_ppl_before-general_ppl_after:+.2f})")

domain_improvement = (domain_ppl_before - domain_ppl_after) / domain_ppl_before * 100
forgetting = (general_ppl_after - general_ppl_before) / general_ppl_before * 100
print(f"\nAnalysis:")
print(f"  Domain improvement: {domain_improvement:.1f}%")
print(f"  General capability loss: {forgetting:.1f}%")
if forgetting > 5:
    print(f"  [WARN] Catastrophic forgetting detected - add replay data")
else:
    print(f"  [OK] Acceptable forgetting level")
