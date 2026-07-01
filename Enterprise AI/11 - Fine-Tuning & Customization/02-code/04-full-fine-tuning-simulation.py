"""
Full fine-tuning simulation: demonstrates training dynamics, memory tracking, and checkpointing.

Run: python 04-full-fine-tuning-simulation.py

Requirements: numpy
"""

import numpy as np
import time

print("=== Full Fine-Tuning Simulation ===\n")

class FullFineTuneModel:
    def __init__(self, d_model=128, num_layers=4, vocab_size=1000):
        self.d_model = d_model
        self.num_layers = num_layers
        self.embedding = np.random.randn(vocab_size, d_model) * 0.01
        self.layers = []
        for _ in range(num_layers):
            self.layers.append({
                "W_q": np.random.randn(d_model, d_model) * 0.01,
                "W_k": np.random.randn(d_model, d_model) * 0.01,
                "W_v": np.random.randn(d_model, d_model) * 0.01,
                "W_o": np.random.randn(d_model, d_model) * 0.01,
                "W_f1": np.random.randn(d_model, d_model * 4) * 0.01,
                "W_f2": np.random.randn(d_model * 4, d_model) * 0.01,
            })

    def count_params(self):
        total = self.embedding.size
        for layer in self.layers:
            for name, w in layer.items():
                total += w.size
        return total

    def forward(self, x):
        h = self.embedding[x]
        for layer in self.layers:
            attn_out = h @ layer["W_q"] @ np.random.randn(self.d_model, self.d_model)
            h = h + attn_out
            ff_out = np.maximum(0, h @ layer["W_f1"]) @ layer["W_f2"]
            h = h + ff_out
        return h

    def estimate_memory(self, batch_size, seq_len):
        param_bytes = self.count_params() * 4  # fp32
        grad_bytes = param_bytes
        opt_bytes = param_bytes * 2
        act_bytes = batch_size * seq_len * self.d_model * self.num_layers * 4
        total_mb = (param_bytes + grad_bytes + opt_bytes + act_bytes) / (1024 * 1024)
        return {
            "parameters_mb": param_bytes / (1024 * 1024),
            "gradients_mb": grad_bytes / (1024 * 1024),
            "optimizer_mb": opt_bytes / (1024 * 1024),
            "activations_mb": act_bytes / (1024 * 1024),
            "total_mb": total_mb,
        }

model = FullFineTuneModel(d_model=128, num_layers=4)
print(f"Model parameters: {model.count_params():,}")
print(f"Model layers: {model.num_layers}")

batch_sizes = [1, 4, 16]
seq_len = 512
print(f"\nMemory estimates (seq_len={seq_len}):")
print(f"{'Batch':>8} {'Params':>12} {'Gradients':>12} {'Optimizer':>12} {'Activations':>12} {'Total':>12}")
print("-" * 68)
for bs in batch_sizes:
    mem = model.estimate_memory(bs, seq_len)
    print(f"{bs:>8} {mem['parameters_mb']:>8.0f}MB {mem['gradients_mb']:>8.0f}MB {mem['optimizer_mb']:>8.0f}MB {mem['activations_mb']:>8.0f}MB {mem['total_mb']:>8.0f}MB")

NUM_STEPS = 20
print(f"\nTraining simulation ({NUM_STEPS} steps):")
total_loss = 0.0
for step in range(NUM_STEPS):
    x = np.random.randint(0, 100, size=(2, 32))
    _ = model.forward(x)
    loss = float(np.random.exponential(0.1) * (1 - step / NUM_STEPS * 0.5))
    total_loss += loss
    if (step + 1) % 5 == 0:
        print(f"  Step {step+1:3d}: loss = {loss:.4f}, avg = {total_loss/(step+1):.4f}")

print(f"\nCheckpoint simulation:")
ckpt = {
    "step": NUM_STEPS,
    "loss": total_loss / NUM_STEPS,
    "params_saved": f"{model.count_params():,}",
    "size_mb": model.count_params() * 4 / (1024 * 1024),
}
print(f"  Step saved: {ckpt['step']}")
print(f"  Final loss: {ckpt['loss']:.4f}")
print(f"  Parameters: {ckpt['params_saved']}")
print(f"  Checkpoint size: {ckpt['size_mb']:.0f} MB")
