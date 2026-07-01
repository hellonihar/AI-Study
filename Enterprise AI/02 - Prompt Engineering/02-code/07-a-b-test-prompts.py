"""
Systematic A/B testing framework for prompt variants.

Run: python 07-a-b-test-prompts.py

Requirements: pip install ollama scipy
"""

import ollama
import random
import json
from collections import defaultdict

MODEL = "llama3.2:3b"

# ─── Define variants ───
VARIANTS = {
    "default": "You are a helpful assistant. Answer the question concisely.",
    "persona": "You are a senior software architect with 20 years of experience. "
               "Answer technical questions with depth and precision.",
    "structured": "You are a technical QA bot. Answer in exactly 3 sentences: "
                  "1) Direct answer 2) Explanation 3) Example or caveat.",
}

TEST_QUESTIONS = [
    "What is the difference between TCP and UDP?",
    "Explain how garbage collection works in Python.",
    "What is a RESTful API?",
]

# ─── Run A/B test ───
def run_ab_test(variant_name, system_prompt, questions, n_runs=3):
    results = []
    for q in questions:
        for run in range(n_runs):
            resp = ollama.chat(model=MODEL, messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": q},
            ])
            content = resp["message"]["content"]
            results.append({
                "variant": variant_name,
                "question": q,
                "run": run,
                "response": content,
                "tokens": resp.get("eval_count", 0),
                "response_length": len(content),
            })
    return results

print("=== A/B Test: Prompt Variants ===\n")

all_results = []
for name, prompt in VARIANTS.items():
    print(f"Testing variant: {name}")
    results = run_ab_test(name, prompt, TEST_QUESTIONS, n_runs=3)
    all_results.extend(results)

# ─── Analyze ───
print("\n=== Analysis ===\n")

# Aggregate by variant
stats = defaultdict(lambda: {"count": 0, "total_tokens": 0, "total_length": 0, "avg_length": 0})
for r in all_results:
    v = r["variant"]
    stats[v]["count"] += 1
    stats[v]["total_tokens"] += r["tokens"]
    stats[v]["total_length"] += r["response_length"]

print(f"{'Variant':<15} {'Responses':<10} {'Avg Tokens':<12} {'Avg Length':<12}")
print("-" * 50)
for name, s in stats.items():
    s["avg_tokens"] = s["total_tokens"] / s["count"]
    s["avg_length"] = s["total_length"] / s["count"]
    print(f"{name:<15} {s['count']:<10} {s['avg_tokens']:<12.1f} {s['avg_length']:<12.1f}")

# ─── Quality scoring (LLM-as-judge) ───
print("\n=== Quality Scores (LLM-as-Judge) ===\n")

judge_system = "You evaluate response quality. Rate 1-10 based on accuracy, clarity, and completeness."

def score_response(question, response):
    resp = ollama.chat(model=MODEL, messages=[
        {"role": "system", "content": judge_system},
        {"role": "user", "content": f"Question: {question}\n\nResponse: {response}\n\nScore (1-10):"},
    ])
    # Extract number from response
    text = resp["message"]["content"]
    for word in text.split():
        try:
            score = float(word.strip(".,"))
            if 1 <= score <= 10:
                return score
        except ValueError:
            continue
    return 5.0  # default

scores = defaultdict(list)
for r in all_results:
    score = score_response(r["question"], r["response"])
    scores[r["variant"]].append(score)

for variant, variant_scores in scores.items():
    avg = sum(variant_scores) / len(variant_scores)
    print(f"{variant:<15} Avg score: {avg:.1f}/10")

# ─── Recommendation ───
print("\n=== Recommendation ===")
# Find the variant with highest average score
best = max(scores, key=lambda v: sum(scores[v]) / len(scores[v]))
print(f"Best variant: {best}")
print(f"Config: {VARIANTS[best]}")
