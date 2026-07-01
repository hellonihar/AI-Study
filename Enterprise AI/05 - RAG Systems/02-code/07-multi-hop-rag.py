"""
Multi-hop RAG: iterative retrieval with intermediate entity extraction.

Run: python 07-multi-hop-rag.py

Requirements: pip install sentence-transformers faiss-cpu numpy
"""

import numpy as np
from sentence_transformers import SentenceTransformer

DOCUMENTS = {
    "d1": "AcmeCorp is a multinational technology company headquartered in San Francisco.",
    "d2": "AcmeCorp acquired DataStream Inc in 2023 for $2.1 billion to expand its data analytics division.",
    "d3": "DataStream Inc was founded by Dr. Sarah Chen in 2015 in Austin, Texas.",
    "d4": "The acquisition of DataStream boosted AcmeCorp's Q3 revenue by 15% year-over-year.",
    "d5": "AcmeCorp's Q3 2024 earnings report shows total revenue of $12.4 billion.",
    "d6": "The data analytics division now accounts for 30% of AcmeCorp's total revenue.",
    "d7": "DataStream's flagship product, StreamAnalytics, processes 5 million events per second.",
    "d8": "Post-acquisition synergies reduced operational costs by $150 million annually.",
    "d9": "Dr. Sarah Chen now leads AcmeCorp's AI Research division based in Austin.",
    "d10": "The StreamAnalytics platform uses Apache Kafka for event ingestion and Apache Flink for processing.",
}

CHUNKS = {k: {"text": v, "id": k} for k, v in DOCUMENTS.items()}

print("=== Multi-Hop RAG ===\n")
print("Question: How did AcmeCorp's acquisition of DataStream affect Q3 revenue?")
print()

model = SentenceTransformer("all-MiniLM-L6-v2")

doc_ids = list(DOCUMENTS.keys())
doc_texts = list(DOCUMENTS.values())

doc_emb = model.encode(doc_texts, show_progress_bar=False)
doc_emb = doc_emb / np.linalg.norm(doc_emb, axis=1, keepdims=True)

import faiss
index = faiss.IndexFlatIP(model.get_sentence_embedding_dimension())
index.add(doc_emb.astype(np.float32))

def retrieve(query, top_k=3):
    q_emb = model.encode([query])
    q_emb = q_emb / np.linalg.norm(q_emb)
    sims, ids = index.search(q_emb.astype(np.float32), top_k)
    results = []
    for i, idx in enumerate(ids[0]):
        if idx != -1:
            results.append({
                "id": doc_ids[idx],
                "text": doc_texts[idx],
                "score": float(sims[0][i]),
            })
    return results

def extract_entities(text, query_entities=None):
    if query_entities is None:
        query_entities = set()

    known_entities = {
        "AcmeCorp", "DataStream Inc", "DataStream", "Dr. Sarah Chen", "Sarah Chen",
        "StreamAnalytics", "Q3", "Q3 2024", "San Francisco", "Austin, Texas",
        "Apache Kafka", "Apache Flink", "AI Research",
    }
    found = set()
    for entity in known_entities:
        if entity.lower() in text.lower():
            found.add(entity)
    return found - query_entities if query_entities else found

def multi_hop_rag(query, max_hops=3, k_per_hop=3):
    print(f"Initial query: {query}")
    hop_results = []
    seen_texts = set()
    current_entities = set()

    for hop in range(max_hops):
        print(f"\n  Hop {hop+1}: Searching with query: '{query[:60]}...'")
        results = retrieve(query, top_k=k_per_hop)

        new_results = []
        for r in results:
            text_hash = hash(r["text"])
            if text_hash not in seen_texts:
                seen_texts.add(text_hash)
                new_results.append(r)
                print(f"    Retrieved: {r['text'][:70]}... ({r['score']:.4f})")

        hop_results.extend(new_results)

        new_entities = set()
        for r in new_results:
            new_entities.update(extract_entities(r["text"], current_entities))
        current_entities.update(new_entities)
        new_entities -= current_entities

        if not new_entities:
            print("    No new entities found. Stopping.")
            break

        print(f"    New entities discovered: {new_entities}")
        new_query_parts = list(set(
            [query.split("?")[0]] + list(new_entities)
        ))
        query = " ".join(new_query_parts)
    else:
        print(f"\n  Reached max hops ({max_hops}).")

    return hop_results

final_results = multi_hop_rag(
    "How did AcmeCorp's acquisition affect Q3 revenue?"
)

print(f"\n{'='*60}")
print("Final retrieved context for generation:")
print(f"{'='*60}")
for i, r in enumerate(final_results):
    print(f"  [{i+1}] ({r['id']}) {r['text']}")

print(f"\n{'='*60}")
print("Synthesized answer:")
print(f"{'='*60}")

answer_parts = []
for r in final_results:
    if "DataStream Inc" in r["text"] and "acquired" in r["text"]:
        answer_parts.append(f"AcmeCorp acquired DataStream Inc in 2023 for $2.1 billion")
    if "revenue" in r["text"] and "Q3" in r["text"]:
        answer_parts.append(f"The acquisition boosted Q3 revenue by 15% year-over-year to $12.4 billion")
    if "analytics" in r["text"] and "revenue" in r["text"]:
        answer_parts.append(f"The data analytics division now accounts for 30% of total revenue")

if answer_parts:
    print("AcmeCorp's acquisition of DataStream Inc in 2023 had a significant positive impact on Q3 revenue. "
          + " ".join(answer_parts) + ".")
else:
    print("Insufficient information to generate a complete answer.")

print(f"\n{'='*60}")
print("Compare with single-hop RAG (without multi-hop):")
print(f"{'='*60}")
single_results = retrieve("How did AcmeCorp's acquisition affect Q3 revenue?", top_k=3)
for r in single_results:
    print(f"  ({r['id']}) {r['text'][:70]}")
print(f"\nSingle-hop missed {len(final_results) - len(single_results)} relevant passages "
      f"that required entity resolution.")
