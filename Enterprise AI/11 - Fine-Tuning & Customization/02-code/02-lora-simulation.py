"""
LoRA fine-tuning simulation: demonstrates low-rank adaptation mechanics.

Run: python 02-lora-simulation.py

Requirements: numpy
"""

import numpy as np

print("=== LoRA Fine-Tuning Simulation ===\n")

class LoRALayer:
    def __init__(self, in_features, out_features, rank=4, alpha=8):
        self.rank = rank
        self.scaling = alpha / rank
        self.lora_a = np.random.randn(in_features, rank) * 0.01
        self.lora_b = np.random.randn(rank, out_features) * 0.01

    def forward(self, x):
        return (x @ self.lora_a @ self.lora_b) * self.scaling

class SimpleMLP:
    def __init__(self, d_in=16, d_hidden=32, d_out=8, rank=4):
        self.W1 = np.random.randn(d_in, d_hidden) * 0.1
        self.W2 = np.random.randn(d_hidden, d_out) * 0.1
        self.lora = LoRALayer(d_in, d_out, rank)

    def forward(self, x):
        h = np.maximum(0, x @ self.W1)
        base_out = h @ self.W2
        lora_out = self.lora.forward(x)
        return base_out + lora_out, base_out, lora_out

    def count_params(self):
        return self.W1.size + self.W2.size

    def count_lora_params(self):
        return self.lora.lora_a.size + self.lora.lora_b.size

mlp = SimpleMLP(d_in=16, d_hidden=32, d_out=8, rank=4)
total = mlp.count_params()
lora_total = mlp.count_lora_params()
print(f"Full model params: {total:,}")
print(f"LoRA adapter params: {lora_total:,}")
print(f"Trainable ratio: {lora_total/total*100:.2f}%\n")

np.random.seed(42)
X = np.random.randn(100, 16)
y = np.sin(X[:, :1]) @ np.random.randn(1, 8) * 0.5

print("Training with LoRA (only adapter weights updated):")
for epoch in range(20):
    losses = []
    for i in range(0, len(X), 10):
        x_batch = X[i:i+10]
        y_batch = y[i:i+10]
        out, base_out, lora_out = mlp.forward(x_batch)
        loss = np.mean((out - y_batch) ** 2)
        losses.append(loss)

        grad = 2 * (out - y_batch) / y_batch.size
        x_batch_lora = x_batch.copy()
        for _ in range(1):
            grad_a = x_batch_lora.T @ (grad @ mlp.lora.lora_b.T) * mlp.lora.scaling
            grad_b = (x_batch_lora @ mlp.lora.lora_a).T @ grad * mlp.lora.scaling
            mlp.lora.lora_a -= 0.01 * grad_a
            mlp.lora.lora_b -= 0.01 * grad_b

    if (epoch + 1) % 5 == 0:
        print(f"  Epoch {epoch+1:2d}: loss = {np.mean(losses):.6f}")

out, base_out, lora_out = mlp.forward(X[:4])
print(f"\nSample outputs (first 4):")
print(f"  Base output:  {base_out[0, :4]}")
print(f"  LoRA output:  {lora_out[0, :4]}")
print(f"  Combined:     {out[0, :4]}")

lora_magnitude = np.linalg.norm(mlp.lora.lora_a @ mlp.lora.lora_b)
print(f"\nLoRA update magnitude: {lora_magnitude:.6f}")
print(f"LoRA ||A||: {np.linalg.norm(mlp.lora.lora_a):.6f}")
print(f"LoRA ||B||: {np.linalg.norm(mlp.lora.lora_b):.6f}")
