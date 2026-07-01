"""
Milvus self-hosted: connect, create collection, insert, search, drop.

Run Milvus via Docker first:
    docker run -d --name milvus-standalone \\
        -p 19530:19530 -p 9091:9091 \\
        milvusdb/milvus:v2.4.0-standalone

Run: python 04-milvus-basics.py

Requirements: pip install sentence-transformers pymilvus numpy
"""

import time
import numpy as np
from sentence_transformers import SentenceTransformer

MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"
COLLECTION_NAME = "vector_db_demo"

DOCUMENTS = [
    "Python is a high-level interpreted programming language.",
    "Machine learning is a subset of artificial intelligence.",
    "The Great Wall of China is a historic fortification.",
    "Photosynthesis is the process plants use to convert sunlight to energy.",
    "The CPU executes instructions in a computer system.",
    "Cloud computing provides on-demand access to computing resources.",
    "The human brain contains approximately 86 billion neurons.",
    "Quantum computing leverages quantum mechanics for computation.",
]

print("=== Milvus Self-Hosted Demo ===\n")

model = SentenceTransformer("all-MiniLM-L6-v2")
dim = model.get_sentence_embedding_dimension()
print(f"Model dimension: {dim}")

try:
    from pymilvus import (
        connections,
        utility,
        Collection,
        FieldSchema,
        CollectionSchema,
        DataType,
    )
except ImportError:
    print("pymilvus not installed. Run: pip install pymilvus")
    print("Expected behavior demonstrates:")
    print("  - Connecting to Milvus gRPC endpoint")
    print("  - Creating collection with vector + scalar fields")
    print("  - Building IVF_FLAT index")
    print("  - Inserting and searching vectors")
    print("  - Dropping collection")
    exit(0)

print(f"Connecting to Milvus at {MILVUS_HOST}:{MILVUS_PORT}...")
connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)

if utility.has_collection(COLLECTION_NAME):
    utility.drop_collection(COLLECTION_NAME)
    print(f"Dropped existing collection '{COLLECTION_NAME}'.")

fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=500),
    FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=100),
]
schema = CollectionSchema(fields, description="Vector DB demo collection")
collection = Collection(name=COLLECTION_NAME, schema=schema)
print(f"Created collection '{COLLECTION_NAME}'.")

entities = [
    [model.encode(doc).tolist() for doc in DOCUMENTS],
    DOCUMENTS,
    ["general"] * len(DOCUMENTS),
]

print(f"Inserting {len(DOCUMENTS)} vectors...")
insert_result = collection.insert(entities)
print(f"Inserted IDs: {insert_result.primary_keys}")

index_params = {
    "metric_type": "IP",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 8},
}
collection.create_index(field_name="vector", index_params=index_params)
print("Created IVF_FLAT index with nlist=8.")

collection.load()
print("Collection loaded to memory.")

print("\n=== Queries ===")
search_params = {"metric_type": "IP", "params": {"nprobe": 4}}

test_queries = ["programming languages", "artificial intelligence", "history"]
for query in test_queries:
    q_emb = model.encode([query]).tolist()
    results = collection.search(
        data=q_emb,
        anns_field="vector",
        param=search_params,
        limit=3,
        output_fields=["text", "category"],
    )
    print(f"\nQuery: {query}")
    for r in results[0]:
        print(f"  [{r.score:.4f}] {r.entity.get('text')[:50]}  [{r.entity.get('category')}]")

print("\n=== Hybrid Search (placeholder) ===")
print("Milvus >= 2.4 supports hybrid search via PyMilvus' hybrid_search API.")
print("This combines dense vector similarity with BM25 sparse scoring.")
print("See pymilvus docs for hybrid_search with rerank.")

collection.release()
utility.drop_collection(COLLECTION_NAME)
print(f"\nDropped collection '{COLLECTION_NAME}'.")

connections.disconnect("default")
print("Disconnected from Milvus.")
