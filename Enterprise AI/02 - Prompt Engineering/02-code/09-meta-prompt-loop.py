"""
Meta-prompting loop: LLM generates and iteratively improves its own prompts.

Run: python 09-meta-prompt-loop.py

Requirements: pip install ollama
"""

import ollama

MODEL = "llama3.2:3b"

# ─── Task definition ───
TASK_DESCRIPTION = """
Task: Classify customer feedback as one of: complaint, inquiry, suggestion, or praise.

Input example: "The product arrived damaged and I'm very upset."
Expected output: complaint

Input example: "What are your store hours?"
Expected output: inquiry

Input example: "You should offer a subscription option."
Expected output: suggestion

Input example: "Love the new design! Great work team."
Expected output: praise
"""

# Test cases to evaluate prompts
TEST_CASES = [
    ("My order hasn't arrived yet!", "complaint"),
    ("Do you ship internationally?", "inquiry"),
    ("It would be great if you had a loyalty program.", "suggestion"),
    ("Excellent customer service, thank you!", "praise"),
    ("The quality has gone down recently.", "complaint"),
]

META_PROMPT = """You are an expert prompt engineer. Given a task description and a current prompt,
generate an IMPROVED version of the prompt. Focus on clarity, specificity, and reliability.

Task: {task}

Current prompt: {current_prompt}

Score: {score}/10

Weaknesses observed: {weaknesses}

Generate an improved prompt. Include:
1. A clear system prompt
2. Output format specification
3. Edge case handling

Output ONLY the new prompt, no explanation."""

def evaluate_prompt(prompt, test_cases):
    """Score a prompt by running it against test cases."""
    score = 0
    errors = []
    
    for text, expected in test_cases:
        try:
            resp = ollama.chat(model=MODEL, messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ])
            result = resp["message"]["content"].strip().lower()
            
            if expected in result:
                score += 1
            else:
                errors.append(f"  '{text[:40]}...' → expected '{expected}', got '{result[:20]}'")
        except Exception as e:
            errors.append(f"  Error: {e}")
    
    return score, errors

# ─── Initial prompt ───
current_prompt = "Classify customer feedback into categories."

print("=== Meta-Prompting Loop ===\n")
print(f"Task: Customer feedback classification\n")

for iteration in range(5):
    print(f"Iteration {iteration + 1}")
    print(f"Current prompt: {current_prompt[:80]}...")
    
    # Evaluate
    score, errors = evaluate_prompt(current_prompt, TEST_CASES)
    print(f"Score: {score}/{len(TEST_CASES)}")
    
    if score == len(TEST_CASES):
        print("✅ Perfect score! Stopping.")
        break
    
    # Generate improvement
    weaknesses = "; ".join([e for e in errors[:3]]) if errors else "Inconsistent classification"
    
    meta_input = META_PROMPT.format(
        task=TASK_DESCRIPTION,
        current_prompt=current_prompt,
        score=score,
        weaknesses=weaknesses,
    )
    
    resp = ollama.chat(model=MODEL, messages=[
        {"role": "user", "content": meta_input},
    ])
    current_prompt = resp["message"]["content"]
    print(f"New prompt generated ({len(current_prompt)} chars)")
    
    # Show specific errors
    if errors:
        print("Errors:")
        for e in errors[:2]:
            print(f"  {e}")
    print()

# ─── Final result ───
print("\n=== Final Prompt ===")
print(current_prompt)

print("\n=== Key Insight ===")
print("Meta-prompting is most effective when given specific, structured feedback.")
print("Without error details, the LLM makes generic improvements.")
print("With specific error cases, it targets the actual failure modes.")
