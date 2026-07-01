"""
Data preparation pipeline: curation, deduplication, filtering, and formatting.

Run: python 01-data-preparation.py

Requirements: none (stdlib only)
"""

import json
import hashlib
from collections import Counter

print("=== Data Preparation Pipeline ===\n")

SAMPLE_DATA = [
    {"instruction": "What is gradient descent?", "response": "Gradient descent is an optimization algorithm that minimizes the loss function by iteratively moving in the direction of steepest descent."},
    {"instruction": "What is gradient descent?", "response": "Gradient descent is an optimization algorithm that minimizes the loss function by iteratively moving in the direction of steepest descent."},
    {"instruction": "Explain transformers", "response": "Transformers use self-attention mechanisms to process sequential data in parallel."},
    {"instruction": "What is overfitting?", "response": "Overfitting happens when a model learns the training data too well, including noise, and performs poorly on new data."},
    {"instruction": "", "response": "Empty instruction example."},
    {"instruction": "Very short", "response": "Ok."},
    {"instruction": "What is gradient descent?", "response": "Gradient descent is an optimization algorithm."},
    {"instruction": "Explain LSTM", "response": "LSTM (Long Short-Term Memory) networks are a type of recurrent neural network designed to handle long-range dependencies."},
    {"instruction": "What is dropout?", "response": "Dropout is a regularization technique where random neurons are dropped during training to prevent co-adaptation."},
    {"instruction": "Explain transformers", "response": "Transformers use self-attention mechanisms to process sequential data."},
]

def exact_dedup(examples):
    seen = set()
    deduped = []
    for ex in examples:
        key = json.dumps(ex, sort_keys=True)
        if key not in seen:
            seen.add(key)
            deduped.append(ex)
    return deduped

def near_dedup(examples, threshold=0.9):
    def ngram_set(text, n=3):
        return set(text[i:i+n] for i in range(len(text)-n+1))

    deduped = []
    signatures = []
    for ex in examples:
        instr = ex.get("instruction", "") + " " + ex.get("response", "")
        sig = ngram_set(instr)
        if all(len(sig & existing) / max(len(sig), len(existing)) < threshold for existing in signatures):
            deduped.append(ex)
            signatures.append(sig)
    return deduped

def quality_filter(examples):
    filtered = []
    for ex in examples:
        instr = ex.get("instruction", "")
        resp = ex.get("response", "")
        if len(instr) < 3 or len(resp) < 10:
            continue
        filtered.append(ex)
    return filtered

def format_dataset(examples, template="chat"):
    if template == "chat":
        formatted = []
        for ex in examples:
            formatted.append({
                "messages": [
                    {"role": "user", "content": ex["instruction"]},
                    {"role": "assistant", "content": ex["response"]}
                ]
            })
        return formatted
    return examples

def compute_stats(examples, label):
    print(f"\n{label}:")
    print(f"  Count: {len(examples)}")
    if examples:
        instr_lens = [len(e.get("instruction", "")) for e in examples]
        resp_lens = [len(e.get("response", "")) for e in examples]
        print(f"  Instruction length: min={min(instr_lens)}, max={max(instr_lens)}, avg={sum(instr_lens)/len(instr_lens):.0f}")
        print(f"  Response length: min={min(resp_lens)}, max={max(resp_lens)}, avg={sum(resp_lens)/len(resp_lens):.0f}")

compute_stats(SAMPLE_DATA, "Raw Data")

quality_passed = quality_filter(SAMPLE_DATA)
compute_stats(quality_passed, "After Quality Filter")

deduped = exact_dedup(quality_passed)
compute_stats(deduped, "After Exact Dedup")

near_deduped = near_dedup(deduped, threshold=0.85)
compute_stats(near_deduped, "After Near Dedup")

formatted = format_dataset(near_deduped, template="chat")
print(f"\nFormatted Example:")
print(json.dumps(formatted[0], indent=2))
