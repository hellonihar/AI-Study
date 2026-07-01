"""
Pinecone CRUD: upsert, query, update, delete vectors.

Requires API key (free tier works for demo):
    export PINECONE_API_KEY="your-key"
    export PINECONE_ENVIRONMENT="us-east-1-aws"

Run: python 03-pinecone-crud.py

Requirements: pip install sentence-transformers pinecone-client numpy
"""

import os
import time
import numpy as np
from sentence_transformers import SentenceTransformer

API_KEY = os.environ.get("PINECONE_API_KEY")
ENV = os.environ.get("PINECONE_ENVIRONMENT", "us-east-1-aws")
INDEX_NAME = "vector-db-demo"

DOCUMENTS = [
    "Python is a high-level interpreted programming language.",
    "Machine learning is a subset of artificial intelligence.",
    "The Great Wall of China is a historic fortification.",
    "Photosynthesis is the process plants use to convert sunlight to energy.",
    "The CPU executes instructions in a computer system.",
]

QUERIES = [
    "programming languages",
    "artificial intelligence",
]

print("=== Pinecone CRUD Demo ===\n")

model = SentenceTransformer("all-MiniLM-L6-v2")
dim = model.get_sentence_embedding_dimension()

if not API_KEY:
    print("Skipping — set PINECONE_API_KEY environment variable to run.")
    print("Expected behavior demonstrates:")
    print("  - Creating serverless index with specified dimension and metric")
    print("  - Upserting vectors with metadata")
    print("  - Querying with top-k and metadata filters")
    print("  - Updating vector values and metadata")
    print("  - Deleting vectors by ID")
    print("  - Deleting the index")
    exit(0)

from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key=API_KEY)

existing = [i.name for i in pc.list_indexes()]
if INDEX_NAME in existing:
    print(f"Deleting existing index '{INDEX_NAME}'...")
    pc.delete_index(INDEX_NAME)
    time.sleep(2)

print(f"Creating index '{INDEX_NAME}'...")
pc.create_index(
    name=INDEX_NAME,
    dimension=dim,
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
)
time.sleep(2)

index = pc.Index(INDEX_NAME)

vecs = []
for i, doc in enumerate(DOCUMENTS):
    emb = model.encode(doc).tolist()
    vecs.append((f"vec-{i}", emb, {"text": doc, "category": "general"}))

print(f"Upserting {len(vecs)} vectors...")
index.upsert(vectors=vecs)
print("Upsert complete.")

time.sleep(1)

stats = index.describe_index_stats()
print(f"Index stats: {stats['total_vector_count']} vectors")

print("\n=== Queries ===")
for query in QUERIES:
    q_emb = model.encode(query).tolist()
    results = index.query(vector=q_emb, top_k=3, include_metadata=True)
    print(f"\nQuery: {query}")
    for r in results["matches"]:
        print(f"  [{r['score']:.4f}] ID={r['id']}  {r['metadata']['text'][:50]}")

print("\n=== Query with Metadata Filter ===")
q_emb = model.encode(QUERIES[0]).tolist()
results = index.query(
    vector=q_emb, top_k=5,
    filter={"category": "general"},
    include_metadata=True,
)
print(f"Filtered query (category=general): {len(results['matches'])} results")

print("\n=== Update Vector ===")
new_emb = model.encode("Updated: Python is a dynamic language.").tolist()
index.update(id="vec-0", values=new_emb, metadata={"text": "Updated document", "category": "updated"})
print("Updated vec-0 with new embedding and metadata.")

print("\n=== Delete Vector ===")
index.delete(ids=["vec-4"])
print("Deleted vec-4.")

stats = index.describe_index_stats()
print(f"Index stats after delete: {stats['total_vector_count']} vectors")

print("\n=== Cleanup ===")
pc.delete_index(INDEX_NAME)
print(f"Deleted index '{INDEX_NAME}'.")
