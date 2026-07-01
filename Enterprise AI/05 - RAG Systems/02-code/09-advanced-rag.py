"""
Advanced RAG patterns: Corrective RAG, Self-RAG, and Fusion RAG demonstrations.

Run: python 09-advanced-rag.py

Requirements: pip install sentence-transformers numpy
"""

import numpy as np
from sentence_transformers import SentenceTransformer

DOCUMENTS = [
    "Python is a high-level programming language with dynamic typing and automatic memory management.",
    "JavaScript is the primary language for web frontend development and runs on servers via Node.js.",
    "Rust is a systems language focused on memory safety using a borrow checker instead of garbage collection.",
    "PostgreSQL is an ACID-compliant relational database with support for JSON and full-text search.",
    "Redis is an in-memory key-value store used for caching, session management, and real-time analytics.",
    "Kubernetes orchestrates containerized applications with scaling, load balancing, and self-healing.",
]

RELEVANCE_MAP = {
    "programming language memory management": set([0, 2]),
    "web development frontend": set([1]),
    "database storage": set([3, 4]),
    "container orchestration scaling": set([5]),
    "monitoring observability": set(),  # No relevant documents → triggers corrective path
    "What is the capital of France?": set(),  # Out of knowledge → triggers corrective path
}

print("=== Advanced RAG Patterns ===\n")

model = SentenceTransformer("all-MiniLM-L6-v2")

doc_emb = model.encode(DOCUMENTS, show_progress_bar=False)
doc_emb = doc_emb / np.linalg.norm(doc_emb, axis=1, keepdims=True)

def retrieve(query, top_k=5):
    q_emb = model.encode([query])
    q_emb = q_emb / np.linalg.norm(q_emb)
    scores = (doc_emb @ q_emb.T).squeeze()
    indices = np.argsort(scores)[::-1][:top_k]
    return [(idx, float(scores[idx])) for idx in indices]

def compute_relevance(query, retrieved, threshold=0.3):
    if not retrieved:
        return False, []
    scores = [score for _, score in retrieved]
    avg_score = np.mean(scores)
    max_score = max(scores)
    relevant = [idx for idx, score in retrieved if score > threshold]
    return (max_score > threshold and avg_score > threshold * 0.7), relevant

print("=" * 60)
print("1. Corrective RAG (CRAG)")
print("=" * 60)

def corrective_rag(query, max_retries=2):
    print(f"\nQuery: '{query}'")

    for attempt in range(max_retries + 1):
        retrieved = retrieve(query, top_k=5)
        is_relevant, relevant_ids = compute_relevance(query, retrieved)

        if is_relevant:
            print(f"  Attempt {attempt+1}: Retrieval quality ACCEPTABLE "
                  f"(max_score={retrieved[0][1]:.3f})")
            return {
                "status": "success",
                "retrieved": [DOCUMENTS[idx] for idx, _ in retrieved],
                "attempts": attempt + 1,
            }
        else:
            print(f"  Attempt {attempt+1}: Retrieval quality LOW "
                  f"(max_score={retrieved[0][1]:.3f}) — correcting")

            if attempt == 0:
                query = f"{query} document information knowledge"
                print(f"  → Expanded query: '{query}'")
            elif attempt == 1:
                query = query.split("?")[0] if "?" in query else query
                query = f"What is known about {query}"
                print(f"  → Rewritten query: '{query}'")

    print(f"  All attempts failed. Using LLM knowledge as fallback.")
    return {
        "status": "fallback",
        "retrieved": [],
        "attempts": max_retries + 1,
    }

test_queries = [
    "database storage",
    "monitoring observability",
    "What is the capital of France?",
]

for q in test_queries:
    result = corrective_rag(q)
    status_icon = "✓" if result["status"] == "success" else "✗"
    print(f"  Result: [{status_icon}] {result['status']} "
          f"({result['attempts']} attempt(s))")

print("\n" + "=" * 60)
print("2. Fusion RAG (Multi-Query)")
print("=" * 60)

def fusion_rag(query, n_variations=3):
    variations = [
        query,
        f"Information about {query}",
        f"{query} overview and details",
    ]

    all_results = []
    seen = set()
    for v in variations:
        results = retrieve(v, top_k=3)
        for idx, score in results:
            text = DOCUMENTS[idx]
            if text not in seen:
                seen.add(text)
                all_results.append((idx, score, v))

    all_results.sort(key=lambda x: x[1], reverse=True)
    return all_results[:5]

query = "programming languages"
results = fusion_rag(query)
print(f"\nQuery: '{query}'")
print(f"{'#':<3} {'Document':<55} {'Score':<10} {'From variation':<30}")
for i, (idx, score, var) in enumerate(results):
    print(f"{i+1:<3} {DOCUMENTS[idx][:50]:<55} {score:.4f} {var[:30]}")

print("\n" + "=" * 60)
print("3. Self-RAG (simulated reflection)")
print("=" * 60)

def self_rag(query, confidence_threshold=0.5):
    retrieved = retrieve(query, top_k=5)
    is_relevant, relevant_ids = compute_relevance(query, retrieved, threshold=0.25)

    max_score = retrieved[0][1] if retrieved else 0.0
    confidence = max_score

    reflection = {
        "query_understood": confidence > 0.2,
        "retrieval_quality": "high" if confidence > 0.5 else "low",
        "needs_human_review": confidence < confidence_threshold,
    }

    if reflection["needs_human_review"]:
        action = "FLAG for human review"
    elif reflection["retrieval_quality"] == "high":
        action = "PROCEED with generation"
    else:
        action = "REWRITE query and retry"

    return {
        "query": query,
        "confidence": confidence,
        "reflection": reflection,
        "action": action,
        "retrieved": [DOCUMENTS[idx] for idx, _ in retrieved[:3]],
    }

for q in ["database storage", "observability monitoring", "What is the capital of France?"]:
    result = self_rag(q)
    print(f"\nQuery: '{q}'")
    print(f"  Confidence: {result['confidence']:.3f}")
    print(f"  Retrieval quality: {result['reflection']['retrieval_quality']}")
    print(f"  Action: {result['action']}")
    if result['retrieved']:
        print(f"  Top passages:")
        for d in result['retrieved']:
            print(f"    • {d[:50]}...")

print("\n" + "=" * 60)
print("Summary")
print("=" * 60)
print("Corrective RAG: Detects low-quality retrieval and retries with rewritten query.")
print("Fusion RAG: Queries multiple variations, merges and deduplicates results.")
print("Self-RAG: Estimates retrieval confidence and decides to proceed, rewrite, or flag.")
print()
print("These patterns add 50-500ms latency but significantly improve robustness.")
