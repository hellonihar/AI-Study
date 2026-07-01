"""
RAG with citations: retrieve passages, generate response with source attribution.

Run: python 06-rag-with-citations.py

Requirements: pip install sentence-transformers faiss-cpu numpy
"""

import re
import numpy as np
from sentence_transformers import SentenceTransformer

DOCUMENTS_RAW = {
    "doc_1": "Python is a high-level interpreted programming language with dynamic semantics. "
             "It was created by Guido van Rossum in 1991. Python emphasizes code readability.",
    "doc_2": "Machine learning is a subset of artificial intelligence that enables systems to "
             "learn from data. Key paradigms include supervised, unsupervised, and reinforcement learning.",
    "doc_3": "The Great Wall of China was built over several dynasties, primarily the Ming dynasty "
             "(1368-1644). It stretches approximately 21,196 kilometers.",
    "doc_4": "Photosynthesis is the process by which plants convert light energy into chemical energy. "
             "It occurs in chloroplasts and produces glucose and oxygen.",
    "doc_5": "A CPU (Central Processing Unit) executes instructions fetched from memory. "
             "Modern CPUs have multiple cores and use pipelining for performance.",
    "doc_6": "Cloud computing provides on-demand access to computing resources over the internet. "
             "Major providers include AWS, Azure, and Google Cloud.",
    "doc_7": "The human brain contains approximately 86 billion neurons connected by trillions of "
             "synapses. It consumes about 20% of the body's energy.",
    "doc_8": "Quantum computing leverages quantum mechanical phenomena like superposition and "
             "entanglement. Qubits can represent both 0 and 1 simultaneously.",
}

print("=== RAG with Citations ===\n")

model = SentenceTransformer("all-MiniLM-L6-v2")

doc_ids = list(DOCUMENTS_RAW.keys())
doc_texts = [DOCUMENTS_RAW[did] for did in doc_ids]

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
    for idx in ids[0]:
        if idx != -1:
            results.append({
                "doc_id": doc_ids[idx],
                "text": doc_texts[idx],
                "score": float(sims[0][list(ids[0]).index(idx)]),
            })
    return results

def generate_cited_response(query, retrieved):
    context_parts = []
    for i, r in enumerate(retrieved):
        context_parts.append(f"[{i+1}] {r['text']} (source: {r['doc_id']})")
    context_str = "\n".join(context_parts)

    source_map = {r["doc_id"]: i+1 for i, r in enumerate(retrieved)}

    if "wall" in query.lower() or "great wall" in query.lower():
        answer = f"The Great Wall of China was primarily built during the Ming dynasty (1368-1644) and stretches approximately 21,196 kilometers [3]."
    elif "python" in query.lower():
        answer = f"Python is a high-level interpreted programming language created by Guido van Rossum in 1991 [1]. It emphasizes code readability and dynamic semantics [1]."
    elif "machine learning" in query.lower() or "ai" in query.lower():
        answer = f"Machine learning is a subset of artificial intelligence that enables systems to learn from data [2]. It includes supervised, unsupervised, and reinforcement learning [2]."
    elif "cpu" in query.lower() or "processor" in query.lower():
        answer = f"A CPU executes instructions fetched from memory [5]. Modern CPUs have multiple cores and use pipelining for performance [5]."
    elif "brain" in query.lower() or "neuron" in query.lower():
        answer = f"The human brain contains approximately 86 billion neurons [7] connected by trillions of synapses. It consumes about 20% of the body's energy [7]."
    else:
        top_text = retrieved[0]["text"]
        answer = f"Based on the retrieved information: {top_text[:100]}... [{source_map[retrieved[0]['doc_id']]}]"

    return answer, context_str

QUERIES = [
    "Tell me about the Great Wall of China",
    "What is Python programming language?",
    "How does the CPU work?",
    "What is machine learning?",
    "How many neurons are in the human brain?",
    "Who invented Python?",  # Requires specific fact not directly in top chunk
]

for query in QUERIES:
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}")

    retrieved = retrieve(query, top_k=3)
    answer, context = generate_cited_response(query, retrieved)

    print("\nRetrieved passages:")
    for r in retrieved:
        print(f"  [{list(DOCUMENTS_RAW.keys()).index(r['doc_id'])+1}] "
              f"{r['text'][:70]}... [{r['doc_id']}]")

    print(f"\nContext:\n{context}")
    print(f"\nGenerated answer:\n{answer}")

print("\n=== Citation Verification ===")
print("Each [N] in the answer should reference a passage above.")
print("In production, add a verification step:")
print("  For each claim, check that the cited passage supports it.")
print("  If unsupported, either remove the citation or regenerate.")

def verify_citations(answer, retrieved):
    citations = re.findall(r'\[(\d+)\]', answer)
    verified = []
    for c in citations:
        idx = int(c) - 1
        if 0 <= idx < len(retrieved):
            verified.append({"citation": c, "passage": retrieved[idx]["text"][:50], "valid": True})
        else:
            verified.append({"citation": c, "passage": None, "valid": False})
    return verified

print("\nCitation verification for 'Tell me about the Great Wall':")
retrieved = retrieve("Tell me about the Great Wall of China", top_k=3)
answer, _ = generate_cited_response("Tell me about the Great Wall of China", retrieved)
verifications = verify_citations(answer, retrieved)
for v in verifications:
    status = "✓" if v["valid"] else "✗"
    print(f"  [{v['citation']}] {status} {v['passage'] if v['passage'] else 'NOT FOUND'}")
