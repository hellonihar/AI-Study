"""
RAG pipeline simulation: end-to-end RAG with retrieval and generation.

Run: python 01-rag-pipeline-sim.py

Requirements: sentence-transformers, numpy
"""

import numpy as np

print("=== RAG Pipeline Simulation ===\n")

try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("[INFO] sentence-transformers not installed; using random embeddings")

CORPUS = [
    "Enterprise AI systems require robust governance frameworks.",
    "RAG combines retrieval with LLM generation for accurate answers.",
    "Vector databases store embeddings for similarity search.",
    "Model monitoring detects drift in production AI systems.",
    "Fine-tuning adapts pre-trained models to domain-specific tasks.",
]

class RAGPipeline:
    def __init__(self):
        if EMBEDDINGS_AVAILABLE:
            self.doc_embeddings = model.encode(CORPUS, normalize_embeddings=True)
        else:
            np.random.seed(42)
            self.doc_embeddings = np.random.randn(len(CORPUS), 384)
            self.doc_embeddings = self.doc_embeddings / np.linalg.norm(self.doc_embeddings, axis=1, keepdims=True)

    def retrieve(self, query, top_k=2):
        if EMBEDDINGS_AVAILABLE:
            q_emb = model.encode(query, normalize_embeddings=True)
        else:
            q_emb = np.random.randn(384)
            q_emb = q_emb / np.linalg.norm(q_emb)
        scores = self.doc_embeddings @ q_emb
        indices = np.argsort(scores)[-top_k:][::-1]
        return [(CORPUS[i], float(scores[i])) for i in indices]

    def generate(self, query, context):
        prompt = f"Context:\n{chr(10).join(c for c, _ in context)}\n\nQuestion: {query}\n\nAnswer based on context."
        return f"[Simulated LLM response based on {len(context)} retrieved documents]"

pipeline = RAGPipeline()

QUERIES = [
    "How does RAG work?",
    "What is model drift?",
    "Tell me about AI governance.",
]

for q in QUERIES:
    print(f"Query: {q}")
    results = pipeline.retrieve(q)
    print(f"  Retrieved {len(results)} docs:")
    for doc, score in results:
        print(f"    [{score:.3f}] {doc[:60]}")
    answer = pipeline.generate(q, results)
    print(f"  Answer: {answer}")
    print()
