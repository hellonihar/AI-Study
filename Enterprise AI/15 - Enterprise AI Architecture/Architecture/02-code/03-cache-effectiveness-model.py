"""
Cache effectiveness model: simulate cache hit rates and cost savings.

Run: python 03-cache-effectiveness-model.py

Requirements: numpy
"""

import numpy as np
from collections import defaultdict

print("=== Cache Effectiveness Model ===\n")

class CacheSimulator:
    def __init__(self, cache_type, max_size=10000, ttl_hours=24):
        self.cache_type = cache_type
        self.max_size = max_size
        self.ttl_seconds = ttl_hours * 3600
        self.cache = {}
        self.hits = 0
        self.misses = 0
        self.total_cost = 0
        self.cache_cost = 0

    def query(self, query_vec, cost=0.001):
        self.total_cost += cost
        key = self._get_key(query_vec)
        if key in self.cache:
            self.hits += 1
            return True
        self.misses += 1
        if len(self.cache) < self.max_size:
            self.cache_cost += cost * 0.1
            self.cache[key] = True
        return False

    def _get_key(self, query_vec):
        if self.cache_type == "exact":
            return hash(tuple(query_vec))
        elif self.cache_type == "semantic":
            quantized = tuple(np.round(query_vec * 10, 0))
            return hash(quantized)

    def hit_rate(self):
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0

    def savings(self):
        return round(self.hits * self.total_cost / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0, 4)

np.random.seed(42)
n_queries = 5000
unique_queries = 6000

exact_cache = CacheSimulator("exact", max_size=5000)
semantic_cache = CacheSimulator("semantic", max_size=5000)

for i in range(n_queries):
    if np.random.random() < 0.15:
        idx = np.random.randint(0, 200)
    elif np.random.random() < 0.35:
        idx = np.random.randint(0, 1000)
    else:
        idx = np.random.randint(0, unique_queries)
    query_vec = np.array([float(idx)])
    exact_cache.query(query_vec)
    semantic_cache.query(query_vec + np.random.normal(0, 0.5, 1))

print(f"Total queries: {n_queries}")
print(f"Unique queries in pool: {unique_queries}")
print()
print(f"{'Cache Type':<15} {'Hits':>6} {'Misses':>8} {'Hit Rate':>10} {'Cost':>10}")
print("-" * 50)
for name, cache in [("Exact Match", exact_cache), ("Semantic", semantic_cache)]:
    print(f"{name:<15} {cache.hits:>6} {cache.misses:>8} {cache.hit_rate():>9.1%} ${cache.savings():<.4f}")

print()

print("=== Cache Performance Scaling ===")
sizes = [100, 500, 1000, 2000, 5000, 10000, 20000]
for size in sizes:
    cache = CacheSimulator("semantic", max_size=size)
    np.random.seed(123)
    for i in range(3000):
        idx = np.random.randint(0, 4000)
        query_vec = np.array([float(idx)])
        cache.query(query_vec + np.random.normal(0, 0.5, 1))
    print(f"  Size {size:>6}: hit rate {cache.hit_rate():>7.2%}, savings ${cache.savings():.4f}")
