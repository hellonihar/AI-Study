"""
DSPy optimization loop: find the optimal prompt for a classification task.

Run: python 05-prompt-optimization-dspy.py

Requirements: pip install dspy-ai openai
(or configure with Ollama: pip install dspy-ai[ollama])
"""

import dspy

# ─── Configure DSPy ───
# Option A: OpenAI
# lm = dspy.LM("gpt-4o-mini")

# Option B: Ollama (local)
lm = dspy.LM("ollama_chat/llama3.2:3b", api_base="http://localhost:11434")
dspy.configure(lm=lm)

# ─── Define task ───
SENTIMENT_DATA = [
    ("This product is absolutely amazing!", "positive"),
    ("Terrible experience, would not recommend.", "negative"),
    ("It works as expected.", "neutral"),
    ("I love the new features!", "positive"),
    ("Waste of money and time.", "negative"),
    ("It's okay for the price.", "neutral"),
    ("Exceeded my expectations!", "positive"),
    ("Very disappointed with the build quality.", "negative"),
    ("Does what it's supposed to do.", "neutral"),
    ("Best purchase I've made this year.", "positive"),
]

# Split into train/test
trainset = [
    dspy.Example(text=text, sentiment=sentiment).with_inputs("text")
    for text, sentiment in SENTIMENT_DATA[:7]
]
testset = [
    dspy.Example(text=text, sentiment=sentiment).with_inputs("text")
    for text, sentiment in SENTIMENT_DATA[7:]
]

# ─── Define DSPy module ───
class SentimentClassifier(dspy.Module):
    def __init__(self):
        super().__init__()
        self.classify = dspy.Predict("text -> sentiment")
    
    def forward(self, text):
        return self.classify(text=text)

# ─── Manual baseline ───
print("=== Manual Prompt Baseline ===")
manual = SentimentClassifier()
for ex in testset:
    result = manual(text=ex.text)
    print(f"  Text: {ex.text[:40]:<45} Predicted: {result.sentiment:<10} Expected: {ex.sentiment}")

# ─── Evaluate function ───
def evaluate(model, examples):
    correct = 0
    for ex in examples:
        pred = model(text=ex.text)
        if pred.sentiment.lower().strip() == ex.sentiment.lower().strip():
            correct += 1
    return correct / len(examples) if examples else 0

baseline_acc = evaluate(manual, testset)
print(f"\nBaseline accuracy: {baseline_acc:.0%}")

# ─── Optimize with DSPy ───
print("\n=== DSPy Optimization ===")

# BootstrapFewShot: automatically generates few-shot examples
from dspy.teleprompt import BootstrapFewShot

config = dict(max_bootstrapped_demos=4, max_labeled_demos=4)
teleprompter = BootstrapFewShot(**config)

try:
    optimized = teleprompter.compile(SentimentClassifier(), trainset=trainset)
    opt_acc = evaluate(optimized, testset)
    print(f"Optimized accuracy: {opt_acc:.0%}")
    print(f"Improvement: {opt_acc - baseline_acc:+.0%}")
    
    # Show the optimized prompt
    print("\n=== Optimized Program ===")
    print(optimized)
    
except Exception as e:
    print(f"Optimization failed: {e}")
    print("This is expected with small local models. Try with GPT-4o-mini for better results.")

# ─── Manual analysis of what DSPy changes ───
print("\n=== Key Insight ===")
print("DSPy's BootstrapFewShot selects the best examples from the training set")
print("and generates reasoning traces (bootstrapped demos) to include in the prompt.")
print("The optimized prompt typically has 3-5 carefully selected examples")
print("with chain-of-thought reasoning traces.")
