"""
Sampling Comparison — compare greedy, temperature, top-k, top-p, and min-p
side-by-side on the same prompt.

Run: python 05-sampling-comparison.py

Requirements: pip install transformers torch
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
model.eval()

prompt = "The best way to learn artificial intelligence is"
inputs = tokenizer(prompt, return_tensors="pt")

def generate(method, **kwargs):
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=30,
            do_sample=method != "greedy",
            pad_token_id=tokenizer.eos_token_id,
            **kwargs,
        )
    return tokenizer.decode(output[0])[len(prompt):]

print(f"Prompt: {prompt}\n")
print(f"{'Method':<25} {'Output'}")
print("-" * 80)

methods = [
    ("Greedy", {"do_sample": False}),
    ("Temp=0.3", {"temperature": 0.3}),
    ("Temp=0.8", {"temperature": 0.8}),
    ("Temp=1.5", {"temperature": 1.5}),
    ("Top-K=10", {"temperature": 0.8, "top_k": 10}),
    ("Top-K=100", {"temperature": 0.8, "top_k": 100}),
    ("Top-P=0.8", {"temperature": 0.8, "top_p": 0.8}),
    ("Top-P=0.95", {"temperature": 0.8, "top_p": 0.95}),
    ("Temp=0.5, Top-P=0.9", {"temperature": 0.5, "top_p": 0.9}),
]

for name, params in methods:
    # Set seed for reproducibility
    torch.manual_seed(42)
    output = generate(name, **params)
    print(f"{name:<25} {output.strip()[:60]}")

# ─── Determinism test: greedy gives same result every time ───
print("\n=== Determinism Check ===")
for i in range(3):
    torch.manual_seed(99)
    out1 = generate("greedy", do_sample=False)
    out2 = generate("greedy", do_sample=False)
    print(f"Run {i+1}: {'Identical' if out1 == out2 else 'DIFFERENT'}")

for i in range(3):
    torch.manual_seed(99)
    out1 = generate("Temp=0.8", temperature=0.8)
    out2 = generate("Temp=0.8", temperature=0.8)
    print(f"Run {i+1} (sampling): {'Identical' if out1 == out2 else 'DIFFERENT'}")
