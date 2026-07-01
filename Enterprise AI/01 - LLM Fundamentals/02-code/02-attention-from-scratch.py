"""
Scaled Dot-Product Attention from scratch in NumPy.
Shows every computation step with a tiny sequence.

Run: python 02-attention-from-scratch.py
"""

import numpy as np

def softmax(x, axis=-1):
    e_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
    return e_x / np.sum(e_x, axis=axis, keepdims=True)

def scaled_dot_product_attention(Q, K, V, mask=None):
    """
    Q: (seq_len_q, d_k)
    K: (seq_len_k, d_k)
    V: (seq_len_k, d_v)
    mask: (seq_len_q, seq_len_k) — True positions are masked
    """
    d_k = Q.shape[-1]
    scores = np.dot(Q, K.T) / np.sqrt(d_k)  # (seq_len_q, seq_len_k)

    if mask is not None:
        scores = scores + mask * -1e9

    weights = softmax(scores, axis=-1)
    output = np.dot(weights, V)
    return output, weights

# ─── Tiny example: "I love AI" ───
# 3 tokens, embedding dim = 4
np.random.seed(42)
seq_len = 3
d_k = 4
d_v = 4

# Random embeddings (in practice these come from the embedding layer)
x = np.random.randn(seq_len, d_k)

# Learned projection matrices (random for demo)
W_Q = np.random.randn(d_k, d_k) * 0.1
W_K = np.random.randn(d_k, d_k) * 0.1
W_V = np.random.randn(d_v, d_v) * 0.1

Q = x @ W_Q
K = x @ W_K
V = x @ W_V

print("Q (queries):")
print(np.round(Q, 3))
print("\nK (keys):")
print(np.round(K, 3))
print("\nV (values):")
print(np.round(V, 3))

# ─── Attention without mask (bidirectional, like BERT) ───
output, weights = scaled_dot_product_attention(Q, K, V)
print("\n=== Bidirectional Attention Weights ===")
print(np.round(weights, 3))
print("Row sums (should be 1.0):", weights.sum(axis=-1))

# ─── Attention with causal mask (decoder-only, like GPT) ───
causal_mask = np.triu(np.ones((seq_len, seq_len)), k=1).astype(bool)
print("\nCausal mask (True = blocked):")
print(causal_mask)

output_causal, weights_causal = scaled_dot_product_attention(Q, K, V, causal_mask)
print("\n=== Causal Attention Weights ===")
print(np.round(weights_causal, 3))
print("Row sums (should be 1.0):", weights_causal.sum(axis=-1))

# ─── Multi-head: 2 heads, each sees d_k//2 = 2 ───
print("\n=== Multi-Head (2 heads) ===")
n_heads = 2
d_head = d_k // n_heads

# Split Q, K, V into heads
Q_heads = Q.reshape(seq_len, n_heads, d_head)
K_heads = K.reshape(seq_len, n_heads, d_head)
V_heads = V.reshape(seq_len, n_heads, d_head)

outputs = []
for h in range(n_heads):
    out, w = scaled_dot_product_attention(
        Q_heads[:, h, :], K_heads[:, h, :], V_heads[:, h, :], causal_mask
    )
    outputs.append(out)
    print(f"Head {h} attention weights:")
    print(np.round(w, 3))

# Concatenate heads and project
concat = np.concatenate(outputs, axis=-1)  # (seq_len, d_k)
W_O = np.random.randn(d_k, d_k) * 0.1
mha_output = concat @ W_O
print(f"\nMulti-head output shape: {mha_output.shape}")
