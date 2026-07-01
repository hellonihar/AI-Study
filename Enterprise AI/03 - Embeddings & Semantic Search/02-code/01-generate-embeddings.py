"""
Compare embedding models: quality, dimensions, speed.

Run: python 01-generate-embeddings.py

Requirements: pip install sentence-transformers numpy
"""

from sentence_transformers import SentenceTransformer
import numpy as np
import time

MODELS = [
    "all-MiniLM-L6-v2",       # 384 dims, fast
    "BAAI/bge-small-en-v1.5", # 384 dims
    "BAAI/bge-base-en-v1.5",  # 768 dims
    "sentence-transformers/gtr-t5-large",  # 768 dims
]

TEXTS = [
    "The quick brown fox jumps over the lazy dog.",
    "Machine learning is transforming how we process data.",
    "The capital of France is Paris.",
    "I enjoy hiking in the mountains during summer.",
    "Python is a popular programming language for data science.",
    "The weather today is sunny with a chance of rain.",
    "Artificial intelligence and deep learning are related fields.",
    "She enjoys reading books about history and philosophy.",
]

print("=== Embedding Model Comparison ===\n")

results = []
for model_name in MODELS:
    try:
        print(f"Loading {model_name}...")
        model = SentenceTransformer(model_name)
        dims = model.get_sentence_embedding_dimension()
        
        # Warmup
        _ = model.encode("warmup")
        
        # Timed batch encode
        start = time.perf_counter()
        embeddings = model.encode(TEXTS, show_progress_bar=False)
        elapsed = time.perf_counter() - start
        
        results.append({
            "model": model_name,
            "dims": dims,
            "time_s": round(elapsed, 4),
            "time_per_text_ms": round(elapsed / len(TEXTS) * 1000, 2),
            "embeddings": embeddings,
        })
        
        print(f"  Dims: {dims}, Total: {elapsed:.3f}s, "
              f"Per text: {elapsed / len(TEXTS) * 1000:.1f}ms")
    except Exception as e:
        print(f"  Error: {e}")

# ─── Compare similarity scores across models ───
print("\n=== Similarity Consistency Across Models ===")
pairs = [
    (0, 1),  # "fox" vs "machine learning" — different topics
    (3, 5),  # "hiking" vs "weather" — somewhat related
    (4, 6),  # "Python" vs "AI" — related topics
    (0, 0),  # same text — should be 1.0
]

for model_result in results:
    model_name = model_result["model"]
    emb = model_result["embeddings"]
    emb_norm = emb / np.linalg.norm(emb, axis=1, keepdims=True)
    
    similarities = emb_norm @ emb_norm.T
    
    print(f"\n{model_name}:")
    for i, j in pairs:
        sim = similarities[i, j]
        print(f"  Text {i} vs Text {j}: {sim:.4f}")

# ─── Dimensionality impact ───
print("\n=== Dimensionality vs Similarity Consistency ===")
# Compare all-MiniLM (384) vs bge-base (768) on the same texts
if len(results) >= 2:
    emb1 = results[0]["embeddings"]
    emb2 = results[2]["embeddings"]
    emb1_norm = emb1 / np.linalg.norm(emb1, axis=1, keepdims=True)
    emb2_norm = emb2 / np.linalg.norm(emb2, axis=1, keepdims=True)
    
    sim1 = emb1_norm @ emb1_norm.T
    sim2 = emb2_norm @ emb2_norm.T
    
    diff = np.abs(sim1 - sim2)
    print(f"Mean similarity difference: {diff.mean():.4f}")
    print(f"Max similarity difference:  {diff.max():.4f}")
