"""
RAG evaluation: faithfulness, answer relevance, context precision, recall.

Run: python 08-rag-evaluation.py

Requirements: pip install sentence-transformers numpy
"""

import numpy as np
from sentence_transformers import SentenceTransformer

QA_PAIRS = [
    {
        "query": "What is Python?",
        "answer": "Python is a high-level interpreted programming language created by Guido van Rossum.",
        "retrieved": [
            "Python is a high-level interpreted programming language with dynamic semantics.",
            "It was created by Guido van Rossum in 1991.",
            "Python emphasizes code readability and has a large standard library.",
        ],
        "relevant_docs": [0, 1],
    },
    {
        "query": "What is machine learning?",
        "answer": "Machine learning is a subset of AI that enables systems to learn from data.",
        "retrieved": [
            "Machine learning is a subset of artificial intelligence.",
            "It enables systems to learn and improve from experience without explicit programming.",
            "The CPU executes instructions in a computer system.",
        ],
        "relevant_docs": [0, 1],
    },
    {
        "query": "How does photosynthesis work?",
        "answer": "Photosynthesis is the process by which plants convert light energy into chemical energy.",
        "retrieved": [
            "Photosynthesis converts light energy into chemical energy in plants.",
            "Cloud computing provides on-demand access to computing resources.",
            "The human brain contains approximately 86 billion neurons.",
        ],
        "relevant_docs": [0],
    },
    {
        "query": "What is quantum computing?",
        "answer": "Quantum computing uses qubits that exploit superposition and entanglement.",
        "retrieved": [
            "Quantum computing leverages quantum mechanics for computation.",
            "Qubits can exist in superposition states representing both 0 and 1 simultaneously.",
            "DNA stores genetic information in a double-helix structure.",
        ],
        "relevant_docs": [0, 1],
    },
    {
        "query": "What is the Great Wall of China?",
        "answer": "Photosynthesis is the process by which plants convert sunlight into energy.",
        "retrieved": [
            "Photosynthesis is the process by which plants convert sunlight into energy.",
            "The CPU is the brain of the computer, executing instructions.",
            "Cloud computing provides on-demand access to computing resources.",
        ],
        "relevant_docs": [0],
        "note": "This answer is WRONG on purpose to test faithfulness detection.",
    },
]

print("=== RAG Evaluation Harness ===\n")

model = SentenceTransformer("all-MiniLM-L6-v2")

def compute_recall(retrieved_ids, relevant_ids, k=5):
    if not relevant_ids:
        return 0.0
    hits = sum(1 for r in relevant_ids if r in retrieved_ids[:k])
    return hits / len(relevant_ids)

def compute_precision(retrieved_ids, relevant_ids, k=5):
    if not retrieved_ids[:k]:
        return 0.0
    hits = sum(1 for r in retrieved_ids[:k] if r in relevant_ids)
    return hits / k

def compute_mrr(retrieved_ids, relevant_ids):
    for rank, idx in enumerate(retrieved_ids):
        if idx in relevant_ids:
            return 1.0 / (rank + 1)
    return 0.0

def compute_faithfulness(answer, retrieved):
    answer_emb = model.encode(answer)
    retrieved_embs = model.encode(retrieved) if retrieved else np.zeros((1, 384))

    answer_emb = answer_emb / np.linalg.norm(answer_emb)
    retrieved_embs = retrieved_embs / np.linalg.norm(retrieved_embs, axis=1, keepdims=True)

    if len(retrieved_embs.shape) == 1 or retrieved_embs.shape[0] == 0:
        return 0.0

    similarities = retrieved_embs @ answer_emb
    max_sim = float(np.max(similarities))
    return max(0.0, min(1.0, max_sim))

def compute_answer_relevance(query, answer):
    q_emb = model.encode(query)
    a_emb = model.encode(answer)
    q_emb = q_emb / np.linalg.norm(q_emb)
    a_emb = a_emb / np.linalg.norm(a_emb)
    return float(q_emb @ a_emb)

def compute_context_precision(query, retrieved, relevant_ids):
    scores = []
    for k in range(1, len(retrieved) + 1):
        retrieved_k = list(range(min(k, len(retrieved))))
        precision_k = compute_precision(retrieved_k, relevant_ids, k)
        if precision_k > 0:
            scores.append(precision_k)
    return np.mean(scores) if scores else 0.0

def compute_context_recall(retrieved_ids, relevant_ids):
    if not relevant_ids:
        return 0.0
    hits = sum(1 for r in relevant_ids if r in retrieved_ids)
    return hits / len(relevant_ids)

print(f"{'Metric':<22} {'Avg':<10} {'Min':<10} {'Max':<10} {'Target':<10}")
print("-" * 62)

metrics_data = {
    "faithfulness": [],
    "answer_relevance": [],
    "context_precision": [],
    "context_recall": [],
    "recall@3": [],
    "precision@3": [],
    "mrr": [],
}

for item in QA_PAIRS:
    query = item["query"]
    answer = item["answer"]
    retrieved = item["retrieved"]
    relevant = item["relevant_docs"]
    retrieved_ids = list(range(len(retrieved)))

    metrics_data["faithfulness"].append(
        compute_faithfulness(answer, retrieved))
    metrics_data["answer_relevance"].append(
        compute_answer_relevance(query, answer))
    metrics_data["context_precision"].append(
        compute_context_precision(query, retrieved, relevant))
    metrics_data["context_recall"].append(
        compute_context_recall(retrieved_ids, relevant))
    metrics_data["recall@3"].append(
        compute_recall(retrieved_ids, relevant, k=3))
    metrics_data["precision@3"].append(
        compute_precision(retrieved_ids, relevant, k=3))
    metrics_data["mrr"].append(
        compute_mrr(retrieved_ids, relevant))

metric_targets = {
    "faithfulness": 0.85,
    "answer_relevance": 0.80,
    "context_precision": 0.70,
    "context_recall": 0.85,
    "recall@3": 0.90,
    "precision@3": 0.70,
    "mrr": 0.85,
}

for metric in metrics_data:
    values = metrics_data[metric]
    target = metric_targets[metric]
    avg = np.mean(values)
    status = "✓" if avg >= target else "✗"
    print(f"{metric:<22} {avg:<10.3f} {np.min(values):<10.3f} "
          f"{np.max(values):<10.3f} {target:<10.2f} {status}")

print("\n=== Per-Item Analysis ===")
for i, item in enumerate(QA_PAIRS):
    faithfulness = compute_faithfulness(item["answer"], item["retrieved"])
    relevance = compute_answer_relevance(item["query"], item["answer"])
    print(f"\nItem {i+1}: {item['query'][:40]}")
    print(f"  Faithfulness:    {faithfulness:.3f} "
          f"{'✓' if faithfulness > 0.85 else '✗ deliberate wrong answer'}")
    print(f"  Relevance:       {relevance:.3f}")
    if "note" in item:
        print(f"  Note: {item['note']}")

print("\n" + "=" * 60)
print("Evaluation Guidelines")
print("=" * 60)
print("1. Faithfulness: Measure if answer claims are supported by retrieved passages.")
print("2. Answer Relevance: Measure if answer addresses the query (semantic similarity).")
print("3. Context Precision: Proportion of retrieved passages that are relevant.")
print("4. Context Recall: Proportion of relevant passages that were retrieved.")
print("5. For production, use LLM-as-judge (GPT-4, Claude) for more accurate metrics.")
print("6. Run on 500+ labeled queries for statistically meaningful results.")
