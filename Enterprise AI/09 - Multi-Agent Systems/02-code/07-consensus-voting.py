"""
Consensus voting: multiple agents vote on answer with weighted confidence.

Run: python 07-consensus-voting.py

Requirements: none (stdlib only)
"""

import json
import random

print("=== Consensus Voting ===\n")

class Voter:
    def __init__(self, name, expertise, accuracy=0.8):
        self.name = name
        self.expertise = expertise
        self.accuracy = accuracy
        self.weight = accuracy * 2

    def vote(self, question, options):
        correct = options[0]
        chosen = correct if random.random() < self.accuracy else random.choice(options)
        confidence = random.uniform(0.5, 1.0) if chosen == correct else random.uniform(0.3, 0.7)
        return {"voter": self.name, "choice": chosen, "confidence": confidence,
                "weight": self.weight}

VOTERS = [
    Voter("finance_agent", "financial analysis", 0.85),
    Voter("search_agent", "information retrieval", 0.75),
    Voter("data_agent", "data analysis", 0.90),
    Voter("general_agent", "general knowledge", 0.60),
    Voter("research_agent", "research", 0.80),
]

class ConsensusEngine:
    def __init__(self):
        self.voters = VOTERS

    def direct_vote(self, question, options):
        votes = {}
        for voter in self.voters:
            v = voter.vote(question, options)
            votes[voter.name] = v["choice"]
            print(f"  {voter.name:<20} → {v['choice']:<15} "
                  f"(confidence: {v['confidence']:.2f})")
        return max(set(votes.values()), key=list(votes.values()).count)

    def weighted_vote(self, question, options):
        tally = {}
        for voter in self.voters:
            v = voter.vote(question, options)
            weighted = v["weight"] * v["confidence"]
            tally[v["choice"]] = tally.get(v["choice"], 0) + weighted
            print(f"  {voter.name:<20} → {v['choice']:<15} "
                  f"(weighted: {weighted:.2f})")

        winner = max(tally, key=tally.get)
        return winner, tally

engine = ConsensusEngine()

question = "What was the revenue in Q3 2024?"
options = ["$12.4M", "$12.1M", "$11.8M"]

print(f"Question: {question}")
print(f"Options: {options}\n")

print("1. Direct Voting (majority):")
winner = engine.direct_vote(question, options)
print(f"   Winner: {winner}")

print(f"\n2. Weighted Voting (by confidence × accuracy):")
winner, tally = engine.weighted_vote(question, options)
print(f"   Tally: {tally}")
print(f"   Winner: {winner}")

print(f"\n{'='*60}")
print("Consensus Summary")
print(f"{'='*60}")
print("  Direct:       majority vote (one voter = one vote)")
print("  Weighted:     vote weighted by historical accuracy × confidence")
print("  Confidence:   higher when voter is sure of their answer")
print("  Accuracy:     historical correctness rate of each voter")
