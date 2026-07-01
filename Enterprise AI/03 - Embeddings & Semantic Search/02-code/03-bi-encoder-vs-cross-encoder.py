"""
Compare bi-encoder retrieval vs cross-encoder re-ranking quality and speed.

Run: python 03-bi-encoder-vs-cross-encoder.py

Requirements: pip install sentence-transformers torch
"""

from sentence_transformers import SentenceTransformer, CrossEncoder
import numpy as np
import time

# ─── Document corpus ───
DOCUMENTS = [
    "Python is a high-level programming language designed for readability.",
    "JavaScript is primarily used for web development and runs in browsers.",
    "Rust provides memory safety without needing a garbage collector.",
    "Machine learning models learn patterns from data without explicit programming.",
    "Deep learning uses neural networks with multiple layers for complex tasks.",
    "Natural language processing helps computers understand human language.",
    "Cloud computing offers scalable resources on demand over the internet.",
    "Serverless computing lets developers focus on code without managing servers.",
    "Docker containers package applications with their dependencies for portability.",
    "Kubernetes orchestrates containerized applications across clusters.",
    "The CPU executes instructions and coordinates computer components.",
    "GPU acceleration speeds up parallel computations for machine learning.",
    "RAM provides fast temporary storage for active program data.",
    "SSD storage offers faster read/write speeds compared to HDD.",
    "Blockchain provides a decentralized, immutable ledger for transactions.",
]

QUERIES = [
    "What programming language is known for readability?",
    "How do neural networks learn?",
    "What are cloud computing benefits?",
    "Explain container orchestration.",
]

print("=== Bi-Encoder vs Cross-Encoder ===\n")

# ─── Load models ───
bi_encoder = SentenceTransformer("all-MiniLM-L6-v2")
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")

# ─── Bi-encoder: index + search ───
print("Indexing documents with bi-encoder...")
doc_emb = bi_encoder.encode(DOCUMENTS, show_progress_bar=False)
doc_emb = doc_emb / np.linalg.norm(doc_emb, axis=1, keepdims=True)

def bi_encoder_search(query, top_k=10):
    q_emb = bi_encoder.encode([query])
    q_emb = q_emb / np.linalg.norm(q_emb)
    scores = doc_emb @ q_emb.T
    top = np.argsort(scores.squeeze())[::-1][:top_k]
    return [(DOCUMENTS[i], float(scores[i])) for i in top]

def cross_encoder_rerank(query, candidates):
    pairs = [(query, doc) for doc, _ in candidates]
    scores = cross_encoder.predict(pairs)
    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    return [(doc, float(score)) for (doc, _), score in ranked]

# ─── Comparison ───
for query in QUERIES:
    print(f"\nQuery: {query}")
    
    # Bi-encoder
    start = time.perf_counter()
    bi_results = bi_encoder_search(query, top_k=10)
    bi_time = time.perf_counter() - start
    
    # Cross-encoder re-rank
    start = time.perf_counter()
    ce_results = cross_encoder_rerank(query, bi_results)
    ce_time = time.perf_counter() - start
    
    print(f"  Bi-encoder top-10 ({bi_time*1000:.1f}ms):")
    for i, (doc, score) in enumerate(bi_results[:5]):
        print(f"    {i+1}. [{score:.4f}] {doc[:50]}")
    
    print(f"  After cross-encoder re-rank (+{ce_time*1000:.1f}ms):")
    for i, (doc, score) in enumerate(ce_results[:5]):
        print(f"    {i+1}. [{score:.4f}] {doc[:50]}")
    
    # Check if re-ranking changed order
    original_order = [doc for doc, _ in bi_results[:5]]
    new_order = [doc for doc, _ in ce_results[:5]]
    changes = sum(1 for i, doc in enumerate(new_order) if doc != original_order[i])
    print(f"  Ranking changes: {changes}/5 positions")
