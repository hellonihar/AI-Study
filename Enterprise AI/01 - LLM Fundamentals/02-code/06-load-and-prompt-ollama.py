"""
Load and prompt models via Ollama — inspect tokens, logits, and timing.

Prerequisites:
  1. Install Ollama from https://ollama.com
  2. Pull a model: ollama pull llama3.2:1b

Run: python 06-load-and-prompt-ollama.py

Requirements: pip install ollama
"""

import ollama
import time

# ─── List available models ───
models = ollama.list()
print("=== Available Models ===")
for m in models["models"]:
    print(f"  {m['name']:<25s} size: {m['size'] / 1e9:.1f}GB")

# ─── Pick a model ───
model_name = "llama3.2:1b"  # small, fast

# ─── Prompt with verbosity ───
prompt = "Explain what a transformer is in 2 sentences."

print(f"\n=== Prompting {model_name} ===")
print(f"Prompt: {prompt}\n")

start = time.perf_counter()
response = ollama.chat(
    model=model_name,
    messages=[{"role": "user", "content": prompt}],
)
elapsed = time.perf_counter() - start

print(f"Response: {response['message']['content']}")
print(f"\nTime: {elapsed:.2f}s")
print(f"Eval count: {response.get('eval_count', 'N/A')} tokens")
print(f"Eval duration: {response.get('eval_duration', 0) / 1e9:.2f}s")
print(f"Tokens/sec: {response.get('eval_count', 0) / (response.get('eval_duration', 1) / 1e9):.1f}")

# ─── Compare model sizes ───
print("\n=== Model Comparison (same prompt) ===")
models_to_test = ["llama3.2:1b", "llama3.2:3b"]
prompt2 = "What is the capital of France?"

for model in models_to_test:
    start = time.perf_counter()
    resp = ollama.chat(model=model, messages=[{"role": "user", "content": prompt2}])
    elapsed = time.perf_counter() - start
    print(f"\n  {model}:")
    print(f"  Response: {resp['message']['content'][:80]}...")
    print(f"  Time: {elapsed:.2f}s")

# ─── Streaming demo ───
print("\n=== Streaming Response ===")
stream = ollama.chat(
    model=model_name,
    messages=[{"role": "user", "content": "Count from 1 to 5."}],
    stream=True,
)
for chunk in stream:
    print(chunk["message"]["content"], end="", flush=True)
print()
