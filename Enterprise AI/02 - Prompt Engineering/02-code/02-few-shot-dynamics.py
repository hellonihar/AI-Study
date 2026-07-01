"""
Explore few-shot learning dynamics: example count, ordering, label balance.

Run: python 02-few-shot-dynamics.py

Requirements: pip install ollama
"""

import ollama
from collections import Counter

MODEL = "llama3.2:3b"

# ─── Task: Sentiment classification ───
def classify_with_examples(examples, test_text):
    messages = [
        {"role": "system", "content": "Classify sentiment as positive, negative, or neutral."},
    ]
    for text, label in examples:
        messages.append({"role": "user", "content": text})
        messages.append({"role": "assistant", "content": label})
    messages.append({"role": "user", "content": test_text})

    resp = ollama.chat(model=MODEL, messages=messages)
    return resp["message"]["content"].strip().lower()

TEST_SENTENCES = [
    "This product is amazing!",
    "Terrible experience, would not recommend.",
    "It works as expected.",
    "Not bad for the price.",
    "I'm disappointed with the quality.",
]

# ─── 1. Effect of example count ───
print("=== Effect of Example Count ===")
EXAMPLE_POOL = [
    ("I love this!", "positive"),
    ("This is horrible.", "negative"),
    ("It's okay.", "neutral"),
    ("Absolutely fantastic!", "positive"),
    ("Waste of money.", "negative"),
]

for n in [0, 1, 2, 5]:
    correct = 0
    examples = EXAMPLE_POOL[:n]
    for sentence in TEST_SENTENCES:
        result = classify_with_examples(examples, sentence)
        # Simple heuristic: if the sentence is positive/negative/neutral-ish
        expected = "positive" if "amazing" in sentence or "Not bad" in sentence else \
                   "negative" if "Terrible" in sentence or "disappointed" in sentence else \
                   "neutral"
        is_correct = expected in result or result in expected
        if is_correct:
            correct += 1
    print(f"  {n} examples: {correct}/{len(TEST_SENTENCES)} correct")

# ─── 2. Effect of label bias ───
print("\n=== Effect of Label Bias ===")
# Unbalanced examples
unbalanced = [
    ("I love this!", "positive"),
    ("This is great!", "positive"),
    ("Awesome!", "positive"),
    ("Fantastic!", "positive"),
]

result = classify_with_examples(unbalanced, "This is mediocre at best.")
print(f"  Unbalanced (4 positive examples): {result}")
# Should show bias toward positive

# ─── 3. Effect of ordering ───
print("\n=== Effect of Example Ordering ===")
mixed = [
    ("I love this!", "positive"),
    ("This is horrible.", "negative"),
    ("It's okay.", "neutral"),
]

# Test the last example's influence
for _ in range(3):
    result = classify_with_examples(mixed, "This is not great.")
    print(f"  Last example 'neutral': {result}")

# Move 'negative' to last
mixed_last_negative = [
    ("It's okay.", "neutral"),
    ("I love this!", "positive"),
    ("This is horrible.", "negative"),
]

for _ in range(3):
    result = classify_with_examples(mixed_last_negative, "This is not great.")
    print(f"  Last example 'negative': {result}")
