"""
pgvector: PostgreSQL with vector search, IVFFlat index, SQL queries.

Requires PostgreSQL with pgvector extension:
    docker run -d --name pgvector \\
        -e POSTGRES_PASSWORD=password \\
        -p 5432:5432 \\
        pgvector/pgvector:0.7.0-pg16

Run: python 06-pgvector-basics.py

Requirements: pip install sentence-transformers psycopg2-binary numpy
"""

import os
import time
import numpy as np
from sentence_transformers import SentenceTransformer

DB_CONFIG = {
    "host": os.environ.get("PGVECTOR_HOST", "localhost"),
    "port": int(os.environ.get("PGVECTOR_PORT", 5432)),
    "dbname": os.environ.get("PGVECTOR_DB", "postgres"),
    "user": os.environ.get("PGVECTOR_USER", "postgres"),
    "password": os.environ.get("PGVECTOR_PASSWORD", "password"),
}

DOCUMENTS = [
    ("Python is a high-level interpreted programming language.", "tech"),
    ("Machine learning is a subset of artificial intelligence.", "tech"),
    ("The Great Wall of China is a historic fortification.", "history"),
    ("Photosynthesis converts sunlight to chemical energy in plants.", "science"),
    ("The CPU executes instructions in a computer system.", "tech"),
    ("Shakespeare wrote 37 plays including Hamlet and Romeo and Juliet.", "literature"),
    ("Cloud computing delivers compute resources on demand.", "tech"),
    ("The human brain contains approximately 86 billion neurons.", "science"),
    ("Quantum computing uses qubits for computation.", "tech"),
    ("DNA stores genetic information in a double-helix structure.", "science"),
    ("Natural language processing helps computers understand text.", "tech"),
    ("The Earth orbits the Sun at 29.8 km/s.", "science"),
]

print("=== pgvector Demo ===\n")

model = SentenceTransformer("all-MiniLM-L6-v2")
dim = model.get_sentence_embedding_dimension()
print(f"Model dimension: {dim}")

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    print("psycopg2 not installed. Run: pip install psycopg2-binary")
    print("Expected behavior demonstrates:")
    print("  - Connecting to PostgreSQL with pgvector extension")
    print("  - Creating tables with vector(384) column")
    print("  - Generating IVFFlat index")
    print("  - Cosine similarity search via SQL")
    print("  - Metadata + vector hybrid filtering")
    print("  - Performance comparison: sequential scan vs. index scan")
    exit(0)

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
print("pgvector extension enabled.")

cur.execute("DROP TABLE IF EXISTS documents;")
cur.execute(f"""
    CREATE TABLE documents (
        id SERIAL PRIMARY KEY,
        text TEXT NOT NULL,
        category VARCHAR(50),
        embedding vector({dim})
    );
""")
print("Created 'documents' table with vector column.")

embeddings = [model.encode(doc).tolist() for doc, _ in DOCUMENTS]
data = [(text, cat, emb) for (text, cat), emb in zip(DOCUMENTS, embeddings)]

execute_values(
    cur,
    "INSERT INTO documents (text, category, embedding) VALUES %s",
    data,
)
conn.commit()
print(f"Inserted {len(DOCUMENTS)} documents.")

cur.execute(f"""
    CREATE INDEX ON documents
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 1);
""")
conn.commit()
print("Created IVFFlat index (cosine distance, lists=1).")

cur.execute("ANALYZE documents;")
print("Table analyzed.\n")

print("=== Cosine Similarity Search ===")
test_queries = [
    "programming languages",
    "artificial intelligence",
    "biology and genetics",
    "historical landmarks",
]

for query in test_queries:
    q_emb = model.encode(query).tolist()
    cur.execute(
        f"""
        SELECT text, category,
               1 - (embedding <=> %s::vector) AS similarity
        FROM documents
        ORDER BY embedding <=> %s::vector
        LIMIT 3;
        """,
        (q_emb, q_emb),
    )
    results = cur.fetchall()
    print(f"\nQuery: {query}")
    for text, cat, sim in results:
        print(f"  [{sim:.4f}] {text[:50]}  ({cat})")

print("\n=== Hybrid: Category Filter + Vector Search ===")
q_emb = model.encode("computers and systems").tolist()
cur.execute(
    f"""
    SELECT text, category,
           1 - (embedding <=> %s::vector) AS similarity
    FROM documents
    WHERE category = 'tech'
    ORDER BY embedding <=> %s::vector
    LIMIT 5;
    """,
    (q_emb, q_emb),
)
results = cur.fetchall()
print(f"Filtered (category=tech): {len(results)} results")
for text, cat, sim in results:
    print(f"  [{sim:.4f}] {text[:50]}")

print("\n=== Performance: Index Scan vs. Sequential ===")
q_emb = model.encode("test query").tolist()

start = time.perf_counter()
for _ in range(100):
    cur.execute(
        f"SELECT id FROM documents ORDER BY embedding <=> %s::vector LIMIT 10;",
        (q_emb,),
    )
    _ = cur.fetchall()
index_time = time.perf_counter() - start

cur.execute("SET enable_indexscan = off;")
cur.execute("SET enable_seqscan = on;")

start = time.perf_counter()
for _ in range(100):
    cur.execute(
        f"SELECT id FROM documents ORDER BY embedding <=> %s::vector LIMIT 10;",
        (q_emb,),
    )
    _ = cur.fetchall()
seq_time = time.perf_counter() - start

cur.execute("SET enable_indexscan = on;")
cur.execute("SET enable_seqscan = off;")

print(f"  With IVFFlat index: {index_time:.3f}s ({index_time/100*1000:.2f}ms/query)")
print(f"  Sequential scan:    {seq_time:.3f}s ({seq_time/100*1000:.2f}ms/query)")
print(f"  Speedup: {seq_time/index_time:.1f}x")
print("  Note: At scale (1M+ rows), speedup grows to 100-1000x.")

print("\n=== Collections (Schema-Level Isolation) ===")
cur.execute("DROP TABLE IF EXISTS collection_a;")
cur.execute(f"CREATE TABLE collection_a (id SERIAL PRIMARY KEY, embedding vector({dim}));")
cur.execute("DROP TABLE IF EXISTS collection_b;")
cur.execute(f"CREATE TABLE collection_b (id SERIAL PRIMARY KEY, embedding vector({dim}));")
print("Created collection_a and collection_b tables for logical isolation.")
print("Each tenant or use case can have its own table with dedicated indexes.")

cur.close()
conn.close()
print("\nConnection closed.")
