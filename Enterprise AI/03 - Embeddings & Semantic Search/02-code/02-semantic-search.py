"""
End-to-end semantic search: index documents, query, return results.

Run: python 02-semantic-search.py

Requirements: pip install sentence-transformers numpy
"""

from sentence_transformers import SentenceTransformer
import numpy as np

# ─── Document corpus ───
DOCUMENTS = [
    "Python is a high-level, interpreted programming language.",
    "Machine learning is a subset of artificial intelligence.",
    "The Great Wall of China is a historic fortification.",
    "Photosynthesis is the process by which plants convert sunlight into energy.",
    "The CPU is the brain of the computer, executing instructions.",
    "Shakespeare wrote many famous plays including Hamlet and Romeo and Juliet.",
    "Cloud computing provides on-demand access to computing resources.",
    "The human brain contains approximately 86 billion neurons.",
    "Quantum computing leverages quantum mechanics for computation.",
    "DNA is the hereditary material in humans and almost all other organisms.",
    "Natural language processing enables computers to understand human language.",
    "The Earth orbits the Sun at an average distance of 93 million miles.",
]

QUERIES = [
    "programming languages",
    "artificial intelligence",
    "historical landmarks",
    "biology and genetics",
    "computer hardware",
]

print("=== Semantic Search Demo ===\n")

# ─── Load model and index documents ───
model = SentenceTransformer("all-MiniLM-L6-v2")
print(f"Model dimension: {model.get_sentence_embedding_dimension()}")

doc_embeddings = model.encode(DOCUMENTS, show_progress_bar=False)
doc_embeddings = doc_embeddings / np.linalg.norm(doc_embeddings, axis=1, keepdims=True)

# ─── Search function ───
def search(query, top_k=3):
    query_emb = model.encode([query])
    query_emb = query_emb / np.linalg.norm(query_emb)
    similarities = doc_embeddings @ query_emb.T
    top_indices = np.argsort(similarities.squeeze())[::-1][:top_k]
    results = []
    for idx in top_indices:
        results.append({
            "doc": DOCUMENTS[idx],
            "score": float(similarities[idx]),
        })
    return results

# ─── Run queries ───
for query in QUERIES:
    print(f"Query: {query}")
    results = search(query)
    for i, r in enumerate(results):
        print(f"  {i+1}. [{r['score']:.4f}] {r['doc']}")
    print()

# ─── Batch search speed ───
import time
start = time.perf_counter()
for _ in range(100):
    _ = search("test query")
elapsed = time.perf_counter() - start
print(f"100 searches: {elapsed:.3f}s ({elapsed/100*1000:.1f}ms per search)")

# ─── Investigate failure cases ───
print("\n=== Failure Analysis ===")
test_queries = [
    ("computers", "CPU"),
    ("biology", "DNA"),
]
for query, expected_topic in test_queries:
    results = search(query, top_k=1)
    print(f"Query '{query}': top result = '{results[0]['doc'][:40]}...' "
          f"(expected about '{expected_topic}')")
