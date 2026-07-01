"""
Minimal transformer inference — single forward pass with a pre-trained model.

Run: python 03-transformer-forward-pass.py

Requirements: pip install transformers torch
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ─── Load model and tokenizer ───
model_name = "gpt2"  # small, fast — good for understanding
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
model.eval()

# ─── Tokenize input ───
prompt = "The future of AI is"
inputs = tokenizer(prompt, return_tensors="pt")
print(f"Input IDs: {inputs['input_ids']}")
print(f"Input tokens: {[tokenizer.decode(i) for i in inputs['input_ids'][0]]}")

# ─── Forward pass ───
with torch.no_grad():
    outputs = model(**inputs, output_attentions=True, output_hidden_states=True)

logits = outputs.logits
last_token_logits = logits[0, -1, :]  # logits for the last position

# ─── Top-k predictions ───
probs = torch.softmax(last_token_logits, dim=-1)
top_probs, top_indices = torch.topk(probs, 10)

print("\n=== Top 10 Next Token Predictions ===")
for prob, idx in zip(top_probs, top_indices):
    print(f"  {tokenizer.decode(idx):15s}  {prob.item():.2%}")

# ─── Inspect hidden states ───
print(f"\n=== Hidden States ===")
print(f"Number of layers: {len(outputs.hidden_states)}")
for i, h in enumerate(outputs.hidden_states):
    print(f"  Layer {i:2d}: shape {tuple(h.shape)}")

# ─── Generate text ───
generated = model.generate(
    **inputs,
    max_new_tokens=20,
    do_sample=True,
    temperature=0.8,
    pad_token_id=tokenizer.eos_token_id,
)
print(f"\n=== Generated ===")
print(tokenizer.decode(generated[0]))

# ─── Investigate: how does prompt length affect logit magnitude? ───
print("\n=== Prompt Length vs Logit Stats ===")
for length in [1, 5, 10, 20, 50]:
    test_prompt = "hello " * length
    test_inputs = tokenizer(test_prompt, return_tensors="pt")
    with torch.no_grad():
        out = model(**test_inputs)
    last_logits = out.logits[0, -1, :]
    print(f"  Length {length:3d}: max={last_logits.max():.2f}, "
          f"mean={last_logits.mean():.2f}, std={last_logits.std():.2f}")
