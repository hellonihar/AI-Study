"""
Benchmark multiple embedding models on speed, recall, and dimensionality.

Run: python 10-benchmark-embedding-models.py

Requirements: pip install sentence-transformers numpy
"""

from sentence_transformers import SentenceTransformer
import numpy as np
import time

MODELS = [
    "all-MiniLM-L6-v2",        # 384 dims
    "BAAI/bge-small-en-v1.5",  # 384 dims
    "BAAI/bge-base-en-v1.5",   # 768 dims
    "BAAI/bge-large-en-v1.5",  # 1024 dims
]

CORPUS_SIZE = 500
QUERY_COUNT = 20

# Generate synthetic corpus
corpus = [f"Document {i}: The topic of this document is {i % 50}." for i in range(CORPUS_SIZE)]
queries = [f"Find documents about topic {i}" for i in range(QUERY_COUNT)]
# Ground truth: relevant docs are those with matching topic number
def get_relevant(query, corpus):
    topic = int(query.split()[-1])
    return [i for i, doc in enumerate(corpus) if f"topic {topic}" in doc]

print("=== Embedding Model Benchmark ===\n")

results = {}

for model_name in MODELS:
    try:
        print(f"Testing {model_name}...")
        model = SentenceTransformer(model_name)
        model.max_seq_length = 128
        dims = model.get_sentence_embedding_dimension()
        
        # ─── Warmup ───
        _ = model.encode("warmup text")
        
        # ─── Indexing speed ───
        start = time.perf_counter()
        doc_emb = model.encode(corpus, show_progress_bar=False)
        index_time = time.perf_counter() - start
        doc_emb = doc_emb / np.linalg.norm(doc_emb, axis=1, keepdims=True)
        
        # ─── Query speed ───
        start = time.perf_counter()
        q_emb = model.encode(queries, show_progress_bar=False)
        query_time = time.perf_counter() - start
        q_emb = q_emb / np.linalg.norm(q_emb, axis=1, keepdims=True)
        
        # ─── Recall ───
        recalls = {1: [], 5: [], 10: []}
        for i, query in enumerate(queries):
            scores = doc_emb @ q_emb[i]
            top_k = np.argsort(scores)[::-1][:10]
            relevant = get_relevant(query, corpus)
            for k in [1, 5, 10]:
                hits = sum(1 for r in relevant if r in top_k[:k])
                recalls[k].append(hits / len(relevant) if relevant else 0)
        
        results[model_name] = {
            "dims": dims,
            "index_time_ms": index_time / len(corpus) * 1000,
            "query_time_ms": query_time / len(queries) * 1000,
            "recall_1": np.mean(recalls[1]),
            "recall_5": np.mean(recalls[5]),
            "recall_10": np.mean(recalls[10]),
        }
    except Exception as e:
        print(f"  ERROR: {e}")

# ─── Results table ───
print(f"\n{'Model':<25} {'Dims':<6} {'Idx(ms/doc)':<12} {'Qry(ms)':<9} {'R@1':<7} {'R@5':<7} {'R@10':<7}")
print("-" * 80)
for name, r in sorted(results.items(), key=lambda x: x[1]["recall_5"], reverse=True):
    print(f"{name:<25} {r['dims']:<6} {r['index_time_ms']:<12.3f} "
          f"{r['query_time_ms']:<9.3f} {r['recall_1']:<7.3f} "
          f"{r['recall_5']:<7.3f} {r['recall_10']:<7.3f}")

# ─── Recommendation ───
print("\n=== Recommendation ===")
if results:
    best_recall = max(results, key=lambda n: results[n]["recall_5"])
    fastest_query = min(results, key=lambda n: results[n]["query_time_ms"])
    print(f"Best recall@5: {best_recall}")
    print(f"Fastest query: {fastest_query}")
    
    if best_recall != fastest_query:
        print(f"\nTrade-off: Switching from {best_recall} to {fastest_query}")
        r1 = results[best_recall]
        r2 = results[fastest_query]
        print(f"  Recall change: {r1['recall_5']:.4f} → {r2['recall_5']:.4f} "
              f"({(r2['recall_5'] - r1['recall_5']) * 100:+.1f}%)")
        print(f"  Speed change:  {r1['query_time_ms']:.1f}ms → {r2['query_time_ms']:.1f}ms "
              f"({(1 - r2['query_time_ms']/r1['query_time_ms']) * 100:.0f}% faster)")
