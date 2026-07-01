"""
Agent with memory: conversation context + vector-based recall.

Run: python 04-agent-with-memory.py

Requirements: none (stdlib only) — uses dict for vector storage
"""

import json
import time
import hashlib
import numpy as np

print("=== Agent with Memory ===\n")

try:
    from sentence_transformers import SentenceTransformer
    MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    EMBEDDINGS = True
except ImportError:
    EMBEDDINGS = True
    print("Note: using simplified embedding (install sentence-transformers for real vectors)\n")

    class SimpleEmbed:
        def encode(self, texts):
            return [np.array([hash(t) % 1000 / 1000.0 for _ in range(384)]) for t in texts]

    MODEL = SimpleEmbed()

class VectorMemory:
    def __init__(self):
        self.memories = []

    def add(self, text, metadata=None):
        embedding = MODEL.encode([text])[0]
        self.memories.append({
            "text": text,
            "embedding": embedding,
            "metadata": metadata or {},
            "timestamp": time.time(),
        })

    def search(self, query, top_k=3):
        query_emb = MODEL.encode([query])[0]
        scored = []
        for mem in self.memories:
            sim = np.dot(query_emb, mem["embedding"]) / (
                np.linalg.norm(query_emb) * np.linalg.norm(mem["embedding"])
            )
            scored.append((sim, mem))
        scored.sort(key=lambda x: -x[0])
        return scored[:top_k]

class ConversationMemory:
    def __init__(self, max_turns=10):
        self.turns = []
        self.max_turns = max_turns

    def add(self, role, content):
        self.turns.append({"role": role, "content": content})
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]

    def get_context(self):
        return self.turns

class MemoryAgent:
    def __init__(self):
        self.vector_memory = VectorMemory()
        self.conversation = ConversationMemory(max_turns=6)
        self.call_count = 0

    def run(self, query):
        self.call_count += 1
        print(f"  [{self.call_count}] User: {query}")

        self.conversation.add("user", query)
        similar = self.vector_memory.search(query, top_k=2)

        response = self.generate_response(query, similar)
        self.conversation.add("assistant", response)
        self.vector_memory.add(query, {"type": "user_query"})
        self.vector_memory.add(response, {"type": "response"})

        print(f"     Agent: {response}")
        if similar and similar[0][0] > 0.85:
            print(f"     (recalled: \"{similar[0][1]['text'][:40]}...\")")
        return response

    def generate_response(self, query, similar):
        recall = ""
        if similar and similar[0][0] > 0.85:
            recall = f" [recalled: {similar[0][1]['text'][:30]}]"

        prev_turns = len(self.conversation.turns)
        turn_info = f" (turn {prev_turns})" if prev_turns > 1 else ""

        return f"Processed: {query[:30]}...{recall}{turn_info}"

agent = MemoryAgent()

print("Memory Agent Demo:\n")

agent.run("What is the capital of France?")
agent.run("Tell me about machine learning")
agent.run("What did I just ask about France?")
agent.run("Explain deep learning")
agent.run("What was my first question?")

print(f"\n{'='*60}")
print("Memory Stats")
print(f"{'='*60}")
print(f"  Vector memories: {len(agent.vector_memory.memories)}")
print(f"  Conversation turns: {len(agent.conversation.turns)}")
print(f"  Memory types: semantic (vector recall) + working (recent turns)")
print()
print("Memory Architecture:")
print("  Semantic: vector DB for long-term fact storage")
print("  Working: recent conversation turns (context window)")
print("  Episodic: past task outcomes (not shown)")
