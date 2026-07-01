"""
Naive RAG: basic index → retrieve → generate pipeline.

Run: python 01-naive-rag.py

Requirements: pip install sentence-transformers faiss-cpu numpy
"""

import numpy as np
from sentence_transformers import SentenceTransformer

DOCUMENTS = [
    "Python is a high-level interpreted programming language with dynamic semantics.",
    "Machine learning is a subset of artificial intelligence focused on pattern recognition.",
    "The Great Wall of China stretches over 13,000 miles across northern China.",
    "Photosynthesis converts light energy into chemical energy in plants.",
    "A CPU executes instructions fetched from memory using the fetch-decode-execute cycle.",
    "Shakespeare wrote 37 plays including tragedies, comedies, and histories.",
    "Cloud computing delivers compute, storage, and networking on demand.",
    "The human brain contains roughly 86 billion neurons connected by synapses.",
    "Quantum computing uses qubits that can exist in superposition states.",
    "DNA stores genetic information in a double-helix structure of base pairs.",
    "Natural language processing enables machines to parse and generate human language.",
    "The Earth orbits the Sun at 29.8 km/s, completing one revolution every 365.25 days.",
]

QUERIES = [
    "What is a programming language?",
    "Explain machine learning.",
    "Tell me about ancient fortifications.",
    "How does photosynthesis work?",
    "What is a CPU?",
]

print("=== Naive RAG Pipeline ===\n")

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Indexing documents...")
doc_emb = model.encode(DOCUMENTS, show_progress_bar=False)
doc_emb = doc_emb / np.linalg.norm(doc_emb, axis=1, keepdims=True)

import faiss

dim = doc_emb.shape[1]
index = faiss.IndexFlatIP(dim)
index.add(doc_emb.astype(np.float32))

LLM_MODEL = None
print("\nLLM setup: Using template-based generation (mock LLM)")
print("Install transformers for real LLM: pip install transformers torch")
print()

def mock_llm(query, context, model_name="mock"):
    context_text = "\n".join(f"[{i+1}] {c}" for i, c in enumerate(context))
    answer = f"Based on the provided context:\n\n{context_text}\n\n"
    answer += f"Answer: {context[0] if context else 'Information not found in documents.'}"
    return answer

def naive_rag(query, top_k=3):
    q_emb = model.encode([query])
    q_emb = q_emb / np.linalg.norm(q_emb)

    sims, ids = index.search(q_emb.astype(np.float32), top_k)
    retrieved = [DOCUMENTS[idx] for idx in ids[0] if idx != -1]

    context = "\n".join(f"[{i+1}] {doc}" for i, doc in enumerate(retrieved))
    prompt = f"""Answer the question using ONLY the provided context.

Context:
{context}

Question: {query}

Answer (with citations):
"""

    response = mock_llm(query, retrieved)
    return response, retrieved, prompt

for query in QUERIES:
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}")

    response, retrieved, prompt = naive_rag(query)

    print("\nRetrieved passages:")
    for i, doc in enumerate(retrieved):
        print(f"  [{i+1}] {doc}")

    print(f"\nFull prompt:\n{prompt[:200]}...\n")
    print(f"Response:\n{response}")

print("\n=== Performance ===")
import time
start = time.perf_counter()
for q in QUERIES:
    naive_rag(q, top_k=3)
elapsed = time.perf_counter() - start
print(f"Average RAG time: {elapsed/len(QUERIES)*1000:.1f}ms")

print("\n=== Failure Analysis ===")
tricky_query = "What is the population of France?"
response, retrieved, _ = naive_rag(tricky_query)
print(f"Query: '{tricky_query}'")
print(f"Retrieved: {retrieved}")
print(f"Response: {response}")
print("\nProblem: Empty retrieval leads to hallucination or irrelevant response.")
print("Fix: Add 'I don't know' instruction to the prompt and check retrieval quality.")
