"""
Decision framework: recommend RAG, fine-tuning, or prompt engineering.

Run: python 01-decision-framework.py

Requirements: none (stdlib only)
"""

import json

print("=== AI Integration Decision Framework ===\n")

QUESTIONS = [
    {
        "id": "knowledge_type",
        "question": "Is the required knowledge public and stable (e.g., general facts)?",
        "yes": "prompt",
        "no": "source_type",
    },
    {
        "id": "source_type",
        "question": "Is the knowledge available in structured documents or databases?",
        "yes": "rag",
        "no": "finetune",
    },
    {
        "id": "prompt",
        "question": "Can prompt engineering (system prompt, few-shot) achieve your accuracy goal?",
        "yes": "prompt_engineering",
        "no": "source_type",
    },
    {
        "id": "rag",
        "question": "Will retrieval latency (200ms+) be acceptable for your use case?",
        "yes": "rag_system",
        "no": "finetune",
    },
]

RECOMMENDATIONS = {
    "prompt_engineering": {
        "approach": "Prompt Engineering",
        "description": "Use system prompts and few-shot examples",
        "effort": "Low (hours)",
        "cost": "$0 setup, $0.001–0.01/query",
        "maintenance": "Edit prompt text",
        "best_for": "Simple tasks, stable knowledge, prototyping",
        "limitations": "No new knowledge, limited style control",
    },
    "rag_system": {
        "approach": "RAG (Retrieval-Augmented Generation)",
        "description": "Index documents and retrieve relevant context per query",
        "effort": "Medium (days–weeks)",
        "cost": "$50–500 setup, $0.002–0.02/query",
        "maintenance": "Update document index",
        "best_for": "Queryable knowledge, frequent updates, compliance",
        "limitations": "Retrieval latency, requires document pipeline",
    },
    "finetune": {
        "approach": "Fine-Tuning",
        "description": "Train model on domain-specific dataset",
        "effort": "High (weeks)",
        "cost": "$50–500 setup, $0.001–0.01/query",
        "maintenance": "Retrain on data changes",
        "best_for": "Custom output style, new capabilities, offline",
        "limitations": "Long update cycle, risk of overfitting",
    },
}

def ask_question(q):
    print(f"\n  Q: {q['question']}")
    answer = input("  Answer (y/n): ").strip().lower()
    if answer not in ("y", "n", "yes", "no"):
        print("  Please enter y or n")
        return ask_question(q)

    result = q["yes"] if answer.startswith("y") else q["no"]
    if result in RECOMMENDATIONS:
        return result
    for q2 in QUESTIONS:
        if q2["id"] == result:
            return ask_question(q2)
    return result

print("This tool helps decide between Prompt Engineering, RAG, and Fine-Tuning.\n")

current_id = "knowledge_type"
for q in QUESTIONS:
    if q["id"] == current_id:
        result = ask_question(q)
        break

rec = RECOMMENDATIONS.get(result)

print(f"\n{'='*60}")
print("Recommendation")
print(f"{'='*60}")
print(f"  Approach:   {rec['approach']}")
print(f"  {rec['description']}")
print(f"  Effort:     {rec['effort']}")
print(f"  Cost:       {rec['cost']}")
print(f"  Best for:   {rec['best_for']}")
print(f"  Limits:     {rec['limitations']}")
print(f"  Maintenance: {rec['maintenance']}")

print(f"\n{'='*60}")
print("All Recommendations Summary")
print(f"{'='*60}")

for key, rec in RECOMMENDATIONS.items():
    print(f"\n  {rec['approach']}")
    print(f"    Effort:       {rec['effort']}")
    print(f"    Cost:         {rec['cost']}")
    print(f"    Maintenance:  {rec['maintenance']}")

print(f"\n{'='*60}")
print("Hybrid Strategy")
print(f"{'='*60}")
print("  Most production systems combine approaches:")
print("  • Prompt engineering + RAG for grounded QA")
print("  • Prompt engineering + fine-tuning for custom behavior")
print("  • All three: prompt (tone) + RAG (knowledge) + FT (style)")
