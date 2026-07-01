"""
Caching patterns: response cache and semantic cache for LLM queries.

Run: python 08-caching-patterns.py

Requirements: pip install sentence-transformers numpy
"""

import time
import hashlib
import json
import numpy as np

print("=== Caching Patterns ===\n")

try:
    from sentence_transformers import SentenceTransformer
    MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("Note: sentence-transformers not installed.")
    print("Semantic cache will use simple Jaccard similarity fallback.\n")

    def simple_embed(text):
        words = set(text.lower().split())
        return {"words": words, "len": len(words)}

class ResponseCache:
    def __init__(self, ttl_seconds=3600):
        self.cache = {}
        self.ttl = ttl_seconds
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def _make_key(self, prompt, model="default", temperature=0):
        raw = f"{prompt}:{model}:{temperature}"
        return hashlib.md5(raw.encode()).hexdigest()

    def get(self, prompt, model="default", temperature=0):
        key = self._make_key(prompt, model, temperature)
        entry = self.cache.get(key)
        if entry and time.time() - entry["time"] < self.ttl:
            self.hits += 1
            return entry["response"]
        if entry:
            del self.cache[key]
            self.evictions += 1
        self.misses += 1
        return None

    def set(self, prompt, response, model="default", temperature=0):
        key = self._make_key(prompt, model, temperature)
        self.cache[key] = {"response": response, "time": time.time()}

    def stats(self):
        total = self.hits + self.misses
        return {
            "entries": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / total * 100 if total else 0,
            "evictions": self.evictions,
        }

class SemanticCache:
    def __init__(self, threshold=0.92):
        self.cache = []
        self.threshold = threshold
        self.hits = 0
        self.misses = 0

    def get(self, query):
        if not EMBEDDINGS_AVAILABLE:
            query_words = set(query.lower().split())
            for entry in self.cache:
                sim = self._jaccard_similarity(query_words, entry["words"])
                if sim >= self.threshold:
                    self.hits += 1
                    return entry["response"]
            self.misses += 1
            return None

        query_embed = MODEL.encode(query)
        for entry in self.cache:
            sim = self._cosine_similarity(query_embed, entry["embedding"])
            if sim >= self.threshold:
                entry["access_count"] += 1
                self.hits += 1
                return entry["response"]
        self.misses += 1
        return None

    def set(self, query, response, metadata=None):
        if EMBEDDINGS_AVAILABLE:
            embedding = MODEL.encode(query)
        else:
            embedding = None

        self.cache.append({
            "query": query,
            "embedding": embedding,
            "words": set(query.lower().split()) if not EMBEDDINGS_AVAILABLE else None,
            "response": response,
            "metadata": metadata or {},
            "access_count": 1,
            "created": time.time(),
        })

    def _cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def _jaccard_similarity(self, a, b):
        if not a or not b:
            return 0
        return len(a & b) / len(a | b)

    def stats(self):
        total = self.hits + self.misses
        return {
            "entries": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / total * 100 if total else 0,
        }

resp_cache = ResponseCache(ttl_seconds=3600)
sem_cache = SemanticCache(threshold=0.90)

QUERIES = [
    "What is the refund policy?",
    "Can I get a refund?",
    "How do I return an item?",
    "What is your return policy?",
    "Tell me about refunds",
    "What is the capital of France?",
]

print("1. Exact Response Cache")
print("-" * 40)

for q in QUERIES[:3]:
    cached = resp_cache.get(q)
    if cached:
        print(f"  HIT:  \"{q[:40]:<40}\" → {cached}")
    else:
        response = f"Response to: {q[:30]}..."
        resp_cache.set(q, response)
        print(f"  MISS: \"{q[:40]:<40}\" → cached")

print()

dup_query = QUERIES[0]
cached = resp_cache.get(dup_query)
print(f"  Same query again: \"{dup_query}\" → {'HIT' if cached else 'MISS'}")

print(f"\n  Cache stats: {json.dumps(resp_cache.stats(), indent=4)}")

print(f"\n2. Semantic Cache (similarity-based)")
print("-" * 40)

for q in QUERIES:
    cached = sem_cache.get(q)
    if cached:
        print(f"  HIT:  \"{q[:40]:<40}\" → {cached[:40]}...")
    else:
        response = f"Semantic response for: {q[:30]}..."
        sem_cache.set(q, response)
        print(f"  MISS: \"{q[:40]:<40}\" → cached")

print(f"\n  Semantic cache stats: {json.dumps(sem_cache.stats(), indent=4)}")
print(f"\n  Note: 'Can I get a refund?' semantically matches 'What is the refund policy?'")
print(f"  because cosine similarity > {sem_cache.threshold}")
