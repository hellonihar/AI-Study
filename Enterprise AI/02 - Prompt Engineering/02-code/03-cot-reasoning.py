"""
Compare chain-of-thought vs direct answering on reasoning tasks.

Run: python 03-cot-reasoning.py

Requirements: pip install ollama
"""

import ollama

MODEL = "llama3.2:3b"

REASONING_TASKS = [
    {
        "question": "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?",
        "answer": "$0.05",
    },
    {
        "question": "If it takes 5 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?",
        "answer": "5 minutes",
    },
    {
        "question": "In a lake, there is a patch of lily pads. Every day, the patch doubles in size. If it takes 48 days for the patch to cover the entire lake, how long would it take for the patch to cover half of the lake?",
        "answer": "47 days",
    },
]

def ask_direct(question):
    resp = ollama.chat(model=MODEL, messages=[
        {"role": "user", "content": question},
    ])
    return resp["message"]["content"]

def ask_cot(question):
    resp = ollama.chat(model=MODEL, messages=[
        {"role": "user", "content": f"{question}\n\nLet's think step by step."},
    ])
    return resp["message"]["content"]

def ask_cot_fewshot(question):
    examples = """Q: Roger has 5 tennis balls. He buys 2 more cans of tennis balls. Each can has 3 balls. How many tennis balls does he have now?
A: Roger started with 5 balls. 2 cans of 3 balls each is 6 balls. 5 + 6 = 11. The answer is 11.

Q: The cafeteria had 23 apples. They used 20 to make lunch and bought 6 more. How many apples do they have?
A: The cafeteria had 23 apples originally. They used 20 so they had 23 - 20 = 3. They bought 6 more so they have 3 + 6 = 9. The answer is 9."""

    resp = ollama.chat(model=MODEL, messages=[
        {"role": "user", "content": f"{examples}\n\nQ: {question}\nA:"},
    ])
    return resp["message"]["content"]

print("=== Direct vs CoT vs Few-shot CoT ===\n")

for task in REASONING_TASKS:
    print(f"Question: {task['question']}")
    print(f"Expected: {task['answer']}")
    print()

    direct = ask_direct(task["question"])
    cot = ask_cot(task["question"])
    cot_fs = ask_cot_fewshot(task["question"])

    def contains_answer(response, expected):
        return expected.lower().strip("$.") in response.lower()

    print(f"  Direct:     {direct[:100]}...")
    print(f"  → Contains expected answer: {contains_answer(direct, task['answer'])}")
    print()
    print(f"  CoT:        {cot[:200]}...")
    print(f"  → Contains expected answer: {contains_answer(cot, task['answer'])}")
    print()
    print(f"  Few-shot CoT: {cot_fs[:200]}...")
    print(f"  → Contains expected answer: {contains_answer(cot_fs, task['answer'])}")
    print("-" * 60)
    print()

# ─── Consistency check ───
print("\n=== Consistency: Running CoT 3 times ===")
for task in REASONING_TASKS[:1]:
    for i in range(3):
        result = ask_cot(task["question"])
        has_answer = task["answer"].lower().strip("$.") in result.lower()
        print(f"  Run {i+1}: Contains expected answer? {has_answer}")
