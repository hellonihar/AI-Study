"""
RAG caching and fallback: reduce latency and improve reliability with cache-aside pattern.

Run: python 10-caching-and-fallback.py

Requirements: pip install sentence-transformers numpy
"""

import time
import hashlib
import json
import numpy as np
from sentence_transformers import SentenceTransformer

DOCUMENTS = [
    "Python is a high-level programming language with dynamic typing and automatic memory management.",
    "JavaScript is the primary language for web frontend development and runs on servers via Node.js.",
    "Rust is a systems language focused on memory safety using a borrow checker instead of garbage collection.",
    "PostgreSQL is an ACID-compliant relational database with support for JSON and full-text search.",
    "Redis is an in-memory key-value store used for caching, session management, and real-time analytics.",
]

QUERIES = [
    "programming languages",
    "database technologies",
    "web development",
    "programming languages",
    "database technologies",
]

class InMemoryCache:
    def __init__(self):
        self._store = {}
        self._ttl = {}
        self.hits = 0
        self.misses = 0

    def get(self, key):
        if key in self._store:
            if time.time() < self._ttl.get(key, float("inf")):
                self.hits += 1
                return self._store[key]
            else:
                del self._store[key]
                del self._ttl[key]
        self.misses += 1
        return None

    def set(self, key, value, ttl=60):
        self._store[key] = value
        self._ttl[key] = time.time() + ttl

    def stats(self):
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        return {"hits": self.hits, "misses": self.misses, "hit_rate": hit_rate}

class EmbeddingCache:
    def __init__(self):
        self._store = {}

    def get(self, text):
        h = hashlib.md5(text.encode()).hexdigest()
        return self._store.get(h)

    def set(self, text, embedding):
        h = hashlib.md5(text.encode()).hexdigest()
        self._store[h] = embedding

print("=== RAG Caching and Fallback ===\n")

print("Initializing cache and model...")
query_cache = InMemoryCache()
embedding_cache = EmbeddingCache()

model = SentenceTransformer("all-MiniLM-L6-v2")

doc_emb = model.encode(DOCUMENTS, show_progress_bar=False)
doc_emb = doc_emb / np.linalg.norm(doc_emb, axis=1, keepdims=True)

def get_embedding(text):
    cached = embedding_cache.get(text)
    if cached is not None:
        return cached
    emb = model.encode([text])
    emb = emb / np.linalg.norm(emb)
    embedding_cache.set(text, emb)
    return emb

def retrieve(query, top_k=3):
    q_emb = get_embedding(query)
    sims = doc_emb @ q_emb.T
    indices = np.argsort(sims.squeeze())[::-1][:top_k]
    return [DOCUMENTS[idx] for idx in indices if idx != -1]

def generate(query, retrieved):
    time.sleep(0.05)  # Simulate 50ms LLM call
    return f"Based on retrieved documents: {retrieved[0][:50]}..." if retrieved else "No information found."

FALLBACK_RESPONSES = [
    "I couldn't find specific information about that in our knowledge base.",
    "That question is outside the scope of my current knowledge sources.",
    "Please try rephrasing your question with more specific terms.",
]

fallback_index = 0

def rag_with_cache_and_fallback(query, cache):
    cache_key = f"rag:{hashlib.md5(query.encode()).hexdigest()}"
    cached_response = cache.get(cache_key)
    if cached_response:
        return cached_response, "cache_hit"

    try:
        retrieved = retrieve(query, top_k=3)

        if not retrieved or np.random.random() < 0.05:
            raise ValueError("Retrieval returned empty results")

        response = generate(query, retrieved)
        cache.set(cache_key, response, ttl=30)
        return response, "success"

    except Exception as e:
        global fallback_index
        fallback_response = FALLBACK_RESPONSES[fallback_index % len(FALLBACK_RESPONSES)]
        fallback_index += 1
        return fallback_response, "fallback"

print(f"\n{'Query':<40} {'Response':<45} {'Source':<12} {'Time':<8}")
print("-" * 105)

for i, query in enumerate(QUERIES):
    start = time.perf_counter()
    response, source = rag_with_cache_and_fallback(query, query_cache)
    elapsed = (time.perf_counter() - start) * 1000

    print(f"{query[:38]:<40} {response[:42]:<45} {source:<12} {elapsed:<8.1f}")

print(f"\nCache stats: {query_cache.stats()}")

print("\n=== Cache Hit Rate Simulation ===")

def simulate_cache_performance(n_queries, n_unique, cache):
    local_cache = InMemoryCache()
    queries = [f"query_{i % n_unique}" for i in range(n_queries)]

    for q in queries:
        cache_key = f"rag:{hashlib.md5(q.encode()).hexdigest()}"
        cached = local_cache.get(cache_key)
        if not cached:
            local_cache.set(cache_key, "response", ttl=60)

    return local_cache.stats()

print(f"\n{n_queries=}, {n_unique=}:")
for n_queries, n_unique, label in [
    (1000, 100, "90% repeat rate"),
    (1000, 500, "50% repeat rate"),
    (1000, 950, "5% repeat rate"),
]:
    stats = simulate_cache_performance(n_queries, n_unique, query_cache)
    print(f"  {label:<30} Hit rate: {stats['hit_rate']:.1%}")

print("\n=== Fallback Chain ===")
print("Fallback levels (simulated):")
fallback_query = "very specific unknown topic nobody asked about"
for level, strategy in enumerate([
    "Cache check",
    "Embedding + retrieval",
    "Re-rank retrieved passages",
    "Query rewrite + retry",
    "Generic fallback response",
], 1):
    if level < 5:
        print(f"  Level {level}: {strategy} → fail (simulated)")
    else:
        response = FALLBACK_RESPONSES[0]
        print(f"  Level {level}: {strategy} → '{response}'")

print("\n=== Recommendations ===")
print("1. Cache query results: 30-60s TTL, 20-40% hit rate at production scale")
print("2. Cache embeddings: 24h TTL, 30-50% hit rate across repeated content")
print("3. Use circuit breaker pattern for LLM API (3 failures → 30s cooldown)")
print("4. Define at least 3 fallback levels before returning error")
print("5. Log cache miss ratio per tenant to detect query diversity spikes")
