"""
Compliance dashboard: aggregate compliance status across models.

Run: python 03-compliance-dashboard.py
"""

import random

print("=== Compliance Dashboard ===\n")

class ComplicanceCheck:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight

CHECKS = [
    ComplicanceCheck("Model Card", 0.20),
    ComplicanceCheck("Bias Audit", 0.25),
    ComplicanceCheck("Data Privacy", 0.25),
    ComplicanceCheck("Risk Classification", 0.10),
    ComplicanceCheck("Version Pinned", 0.10),
    ComplicanceCheck("Deployment Approval", 0.10),
]

MODEL_NAMES = [
    "chatbot-prod", "hiring-v3", "search-rag", "code-assist",
    "sentiment-v2", "translator-v1", "voice-agent", "fraud-detection",
]

models = []
for name in MODEL_NAMES:
    scores = {}
    for c in CHECKS:
        scores[c.name] = random.uniform(0.4, 1.0)
    score = sum(scores[c.name] * c.weight for c in CHECKS)
    models.append({"name": name, "scores": scores, "total": round(score, 3)})

models.sort(key=lambda m: m["total"])

print(f"{'Model':<22} {'Compliance':>10} {'Critical Issues':>16}")
print("-" * 50)
for m in models:
    bar = "#" * int(m["total"] * 10) + "." * (10 - int(m["total"] * 10))
    critical = sum(1 for c in CHECKS if m["scores"][c.name] < 0.5)
    print(f"  {m['name']:<20} {bar} {m['total']:.0%}     {critical} issues")
print()

print("=== Status Distribution ===")
for c in CHECKS:
    passing = sum(1 for m in models if m["scores"][c.name] >= 0.7)
    print(f"  {c.name:<22} {passing}/{len(models)} passing ({(passing/len(models))*100:.0f}%)")
