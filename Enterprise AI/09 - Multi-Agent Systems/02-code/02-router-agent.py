"""
Router agent: classify intents and route to specialist agents.

Run: python 02-router-agent.py

Requirements: none (stdlib only)
"""

import json
import time

print("=== Router Agent ===\n")

SPECIALISTS = {
    "search": {
        "handler": lambda q: {"results": [f"Search result for: {q}"], "count": 3},
        "description": "Handles information retrieval queries",
    },
    "summarize": {
        "handler": lambda q: {"summary": f"Summary of: {q}", "length": len(q) // 2},
        "description": "Handles document and text summarization",
    },
    "calculate": {
        "handler": lambda q: {"result": eval(q.split()[-1]), "operation": "math"},
        "description": "Handles mathematical calculations",
    },
    "greeting": {
        "handler": lambda q: {"response": f"Hello! How can I help you today?"},
        "description": "Handles greetings and small talk",
    },
}

class Router:
    def __init__(self):
        self.routes = {
            "search": ["search", "find", "lookup", "look for", "find me"],
            "summarize": ["summarize", "summarise", "summary", "condense", "tl;dr"],
            "calculate": ["calculate", "what is", "math", "+", "-", "*", "/"],
            "greeting": ["hello", "hi", "hey", "good morning", "good evening"],
        }

    def classify(self, query):
        q = query.lower()
        scores = {}
        for intent, keywords in self.routes.items():
            score = sum(1 for kw in keywords if kw in q)
            if score > 0:
                scores[intent] = score

        if not scores:
            return "search"

        return max(scores, key=scores.get)

    def route(self, query):
        intent = self.classify(query)
        print(f"  Classified as: {intent}")

        specialist = SPECIALISTS.get(intent, SPECIALISTS["search"])
        time.sleep(0.02)
        result = specialist["handler"](query)

        return {"intent": intent, "specialist": intent, "result": result}

router = Router()

QUERIES = [
    "Hello, how are you?",
    "search for machine learning papers",
    "calculate 42 * 5",
    "summarize this document about AI",
    "What is the weather today?",
]

for q in QUERIES:
    print("-" * 60)
    print(f"Query: {q}")
    result = router.route(q)
    print(f"  Result: {json.dumps(result['result'], indent=4)}")
    print()

print(f"{'='*60}")
print("Router Summary")
print(f"{'='*60}")
print(f"  Specialists: {list(SPECIALISTS.keys())}")
print(f"  Classification: keyword matching")
print(f"  Handling: routes to appropriate specialist")
