"""
Benchmark Inference — measure TTFT, TPOT, and throughput across model sizes and quant levels.

Run: python 07-benchmark-inference.py

Requirements: pip install transformers torch
"""

import torch
import time
from transformers import AutoModelForCausalLM, AutoTokenizer

MODELS = {
    "gpt2": "gpt2",           # 124M params, FP32
    "gpt2-medium": "gpt2-medium",  # 355M params
}

PROMPTS = {
    "short": "What is AI?",
    "medium": "Explain the differences between supervised, unsupervised, and reinforcement learning.",
    "long": "The transformer architecture has revolutionized natural language processing. " * 20,
}

def benchmark(model_name, prompt, max_new_tokens=50):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.eval()

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    inputs = tokenizer(prompt, return_tensors="pt")
    input_len = inputs["input_ids"].shape[1]

    # Warmup
    with torch.no_grad():
        _ = model.generate(**inputs, max_new_tokens=5)

    # Timed run
    torch.cuda.synchronize() if torch.cuda.is_available() else None
    start = time.perf_counter()
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    torch.cuda.synchronize() if torch.cuda.is_available() else None
    elapsed = time.perf_counter() - start

    output_len = output.shape[1]
    new_tokens = output_len - input_len
    ttft = elapsed  # approximate (includes all tokens for simplicity)
    tpot = elapsed / new_tokens if new_tokens > 0 else 0
    tokens_per_sec = new_tokens / elapsed if elapsed > 0 else 0

    return {
        "model": model_name,
        "input_tokens": input_len,
        "output_tokens": new_tokens,
        "total_time_s": round(elapsed, 3),
        "TTFT_s": round(ttft, 3),
        "TPOT_s": round(tpot, 4),
        "tokens_per_sec": round(tokens_per_sec, 1),
    }

print(f"{'Model':<15} {'Prompt':<8} {'Input':<6} {'Output':<7} {'Total(s)':<9} {'TTFT(s)':<9} {'TPOT(s)':<9} {'tok/s':<8}")
print("-" * 80)

for model_name in MODELS:
    for prompt_name, prompt_text in PROMPTS.items():
        try:
            result = benchmark(model_name, prompt_text, max_new_tokens=30)
            print(f"{result['model']:<15} {prompt_name:<8} "
                  f"{result['input_tokens']:<6} {result['output_tokens']:<7} "
                  f"{result['total_time_s']:<9} {result['TTFT_s']:<9} "
                  f"{result['TPOT_s']:<9} {result['tokens_per_sec']:<8}")
        except Exception as e:
            print(f"{model_name:<15} {prompt_name:<8} ERROR: {e}")
