"""
Qdrant basics: in-memory mode (no server required), create collection,
upsert vectors, search with filters, payload indexing.

Run: python 05-qdrant-basics.py

Requirements: pip install sentence-transformers qdrant-client numpy
"""

import time
import numpy as np
from sentence_transformers import SentenceTransformer

DOCUMENTS = [
    "Python is a high-level interpreted programming language.",
    "Machine learning is a subset of artificial intelligence.",
    "The Great Wall of China is a historic fortification.",
    "Photosynthesis is the process plants use to convert sunlight to energy.",
    "The CPU executes instructions in a computer system.",
    "Cloud computing provides on-demand access to computing resources.",
    "The human brain contains approximately 86 billion neurons.",
    "Quantum computing leverages quantum mechanics for computation.",
    "Kubernetes orchestrates containerized workloads across clusters.",
    "PostgreSQL is a relational database management system.",
]

print("=== Qdrant In-Memory Demo ===\n")

model = SentenceTransformer("all-MiniLM-L6-v2")
dim = model.get_sentence_embedding_dimension()
print(f"Model dimension: {dim}")

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance,
        VectorParams,
        PointStruct,
        Filter,
        FieldCondition,
        MatchValue,
        Range,
    )
except ImportError:
    print("qdrant-client not installed. Run: pip install qdrant-client")
    print("Expected behavior demonstrates:")
    print("  - Creating in-memory Qdrant collection")
    print("  - Upserting vectors with payload")
    print("  - Searching with metadata filters")
    print("  - Payload indexing for filtered search performance")
    print("  - Scrolling and counting points")
    exit(0)

client = QdrantClient(":memory:")

collection_name = "vector_db_demo"
client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
)
print(f"Created in-memory collection '{collection_name}'.")

points = []
for i, doc in enumerate(DOCUMENTS):
    emb = model.encode(doc).tolist()
    category = "tech" if any(kw in doc.lower() for kw in ["python", "cpu", "cloud", "kubernetes", "postgresql", "quantum"]) else "science"
    points.append(
        PointStruct(
            id=i,
            vector=emb,
            payload={"text": doc, "category": category, "index": i},
        )
    )

client.upsert(collection_name=collection_name, points=points)
print(f"Upserted {len(points)} points.")

print("\n=== Basic Queries ===")
test_queries = ["programming languages", "biology"]
for query in test_queries:
    q_emb = model.encode(query).tolist()
    results = client.search(
        collection_name=collection_name,
        query_vector=q_emb,
        limit=3,
    )
    print(f"\nQuery: {query}")
    for r in results:
        print(f"  [{r.score:.4f}] {r.payload['text'][:50]}  (cat: {r.payload['category']})")

print("\n=== Filtered Search ===")
q_emb = model.encode("computer systems").tolist()
results = client.search(
    collection_name=collection_name,
    query_vector=q_emb,
    query_filter=Filter(
        must=[FieldCondition(key="category", match=MatchValue(value="tech"))]
    ),
    limit=5,
)
print(f"Filtered (category=tech): {len(results)} results")
for r in results:
    print(f"  [{r.score:.4f}] {r.payload['text'][:50]}")

print("\n=== Range Filter ===")
results = client.search(
    collection_name=collection_name,
    query_vector=q_emb,
    query_filter=Filter(
        must=[FieldCondition(key="index", range=Range(gte=5))]
    ),
    limit=10,
)
print(f"Range filter (index>=5): {len(results)} results")
for r in results:
    print(f"  [{r.score:.4f}] idx={r.payload['index']} {r.payload['text'][:40]}")

print("\n=== Payload Indexing ===")
client.create_payload_index(
    collection_name=collection_name,
    field_name="category",
    field_type="keyword",
)
client.create_payload_index(
    collection_name=collection_name,
    field_name="index",
    field_type="integer",
)
print("Created payload indexes on 'category' and 'index'.")
print("Payload indexes accelerate filtered searches significantly "
      "at scale (>100K points).")

print("\n=== Scroll (Paginated Retrieval) ===")
scroll_result, next_offset = client.scroll(
    collection_name=collection_name,
    limit=5,
    with_payload=True,
    with_vectors=False,
)
print(f"Scrolled {len(scroll_result)} points (offset for next: {next_offset})")
for p in scroll_result:
    print(f"  id={p.id}  {p.payload['text'][:40]}")

print("\n=== Count ===")
count = client.count(collection_name=collection_name)
print(f"Total points: {count.count}")

print("\n=== Cleanup ===")
client.delete_collection(collection_name=collection_name)
print(f"Deleted collection '{collection_name}'.")
