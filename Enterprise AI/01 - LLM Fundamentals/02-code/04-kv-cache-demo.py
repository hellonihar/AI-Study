"""
KV Cache Demo — measure time-to-first-token (TTFT) vs. per-token latency
with and without KV cache enabled.

Run: python 04-kv-cache-demo.py

Requirements: pip install transformers torch
"""

import torch
import time
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
model.eval()

prompt = "The history of artificial intelligence began in the 1950s when Alan Turing proposed the Turing Test. Since then, the field has evolved through multiple waves of innovation."
inputs = tokenizer(prompt, return_tensors="pt")

input_len = inputs["input_ids"].shape[1]
print(f"Prompt length: {input_len} tokens")

# ─── Without KV cache (recompute every step) ───
print("\n=== Without KV Cache ===")
generated = inputs["input_ids"]
start = time.perf_counter()

for step in range(20):
    with torch.no_grad():
        outputs = model(generated)
    next_logits = outputs.logits[0, -1, :]
    next_token = torch.argmax(next_logits).unsqueeze(0).unsqueeze(0)
    generated = torch.cat([generated, next_token], dim=-1)

total_time = time.perf_counter() - start
print(f"Total: {total_time:.3f}s, Average: {total_time/20:.3f}s/token")
# Note: each step recomputes attention for ALL tokens seen so far

# ─── With KV cache ───
print("\n=== With KV Cache ===")
generated = inputs["input_ids"]
past_key_values = None
start = time.perf_counter()

for step in range(20):
    with torch.no_grad():
        outputs = model(
            generated if past_key_values is None else generated[:, -1:],
            past_key_values=past_key_values,
            use_cache=True,
        )
    past_key_values = outputs.past_key_values
    next_logits = outputs.logits[0, -1, :]
    next_token = torch.argmax(next_logits).unsqueeze(0).unsqueeze(0)
    generated = torch.cat([generated, next_token], dim=-1)

total_time = time.perf_counter() - start
print(f"Total: {total_time:.3f}s, Average: {total_time/20:.3f}s/token")

# ─── KV cache memory estimation ───
print("\n=== KV Cache Memory Estimate ===")
config = model.config
n_layers = config.n_layer
n_heads = config.n_head
d_head = config.n_embd // n_heads
dtype_bytes = 2  # FP16

# Per token per layer: 2 (K + V) × n_heads × d_head × dtype_bytes
per_token_per_layer = 2 * n_heads * d_head * dtype_bytes
total_per_token = per_token_per_layer * n_layers

print(f"Model: {model_name}")
print(f"Layers: {n_layers}, Heads: {n_heads}, d_head: {d_head}")
print(f"KV cache per token: {total_per_token / 1024:.1f} KB")
print(f"KV cache for {input_len + 20} tokens: {total_per_token * (input_len + 20) / 1024 / 1024:.1f} MB")
