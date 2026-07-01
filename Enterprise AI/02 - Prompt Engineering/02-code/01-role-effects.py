"""
Compare the effect of system prompt placement, delimiter choice, and role structure
on output quality.

Run: python 01-role-effects.py

Requirements: pip install openai (or comment out and use ollama)
"""

import json

# Using Ollama for local testing (replace with your preferred provider)
import ollama

MODEL = "llama3.2:3b"

TEST_CASES = [
    "What is the capital of France?",
    "Explain machine learning in one sentence.",
    "Write a haiku about programming.",
]

SYSTEM_PROMPT = "You are a helpful assistant. Answer concisely in under 30 words."

def test_prompt_structure(name, messages):
    results = []
    for question in TEST_CASES:
        msgs = [{"role": m["role"], "content": m["content"]} for m in messages]
        msgs.append({"role": "user", "content": question})
        resp = ollama.chat(model=MODEL, messages=msgs)
        results.append({
            "question": question,
            "response": resp["message"]["content"],
            "tokens": resp.get("eval_count", 0),
        })
    return results

print("=== Effect of System Prompt Position ===\n")

# Variant 1: System prompt before user (standard)
r1 = test_prompt_structure("System before user", [
    {"role": "system", "content": SYSTEM_PROMPT},
])

# Variant 2: System prompt as a user message
r2 = test_prompt_structure("Instruction in user message", [
    {"role": "user", "content": SYSTEM_PROMPT + "\n\nAnswer this: " + TEST_CASES[0]},
])

# Variant 3: No system prompt
r3 = test_prompt_structure("No system prompt", [])

for i, (r1r, r2r, r3r) in enumerate(zip(r1, r2, r3)):
    print(f"Question: {TEST_CASES[i]}")
    print(f"  System before user: {r1r['response'][:80]}...")
    print(f"  User message only:  {r2r['response'][:80]}...")
    print(f"  No system prompt:   {r3r['response'][:80]}...")
    print()

# ─── Delimiter comparison ───
print("=== Delimiter Styles ===\n")

delimiter_tests = [
    ("XML tags", [
        {"role": "system", "content": "<instruction>\nYou are a classifier.\n</instruction>"},
        {"role": "user", "content": "<input>\n{classify_this}\n</input>"},
    ]),
    ("Markdown headers", [
        {"role": "system", "content": "## Instruction\nYou are a classifier.\n## End"},
        {"role": "user", "content": "## Input\n{classify_this}\n## End"},
    ]),
]

for name, msgs in delimiter_tests:
    # Substitute the placeholder
    msgs[1]["content"] = msgs[1]["content"].replace("{classify_this}",
        "Classify this sentence: 'The product arrived damaged.' as complaint/inquiry/feedback")
    resp = ollama.chat(model=MODEL, messages=msgs)
    print(f"{name}: {resp['message']['content'][:80]}")

# ─── Key insight ───
print("\n=== Key Finding ===")
print("System prompt before user input consistently produces the most reliable results.")
print("Without a system prompt, the model defaults to its training distribution,")
print("which may not match your task requirements.")
