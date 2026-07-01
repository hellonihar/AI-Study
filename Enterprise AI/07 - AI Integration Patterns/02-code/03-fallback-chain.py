"""
Fallback chain: tiered model routing with cascading fallback and latency tracking.

Run: python 03-fallback-chain.py

Requirements: none (stdlib only)
"""

import time
import random
from datetime import datetime

print("=== Fallback Chain ===\n")

class ModelTier:
    def __init__(self, name, simulate_success=True, latency_range=(0.1, 2.0)):
        self.name = name
        self.simulate_success = simulate_success
        self.latency_range = latency_range
        self.success_count = 0
        self.failure_count = 0
        self.skipped = False

    def invoke(self, prompt):
        if self.skipped:
            raise Exception(f"Circuit open for {self.name}")

        latency = random.uniform(*self.latency_range)
        time.sleep(latency * 0.01)

        if not self.simulate_success or random.random() < 0.2:
            self.failure_count += 1
            raise Exception(f"{self.name} failed (simulated)")

        self.success_count += 1
        return {
            "model": self.name,
            "response": f"[Response from {self.name}]",
            "latency_s": round(latency, 3),
            "tokens": random.randint(50, 200),
        }

class FallbackChain:
    def __init__(self, tiers):
        self.tiers = tiers

    def execute(self, prompt):
        for tier in self.tiers:
            try:
                result = tier.invoke(prompt)
                return result
            except Exception as e:
                print(f"  ⚠ {tier.name}: {e}")

        return {
            "model": "static-fallback",
            "response": "I'm sorry, I'm unavailable right now. Please try again later.",
            "latency_s": 0,
            "tokens": 0,
        }

tiers = [
    ModelTier("gpt-4", simulate_success=True, latency_range=(1.0, 2.0)),
    ModelTier("gpt-4o-mini", simulate_success=True, latency_range=(0.3, 1.0)),
    ModelTier("claude-haiku", simulate_success=True, latency_range=(0.2, 0.8)),
    ModelTier("local-llama-8b", simulate_success=False, latency_range=(0.5, 1.5)),
]

chain = FallbackChain(tiers)

print("Testing fallback chain with 5 queries...\n")

for i in range(5):
    prompt = f"Query {i+1}: What is AI?"
    print(f"[{i+1}] {prompt}")

    result = chain.execute(prompt)
    print(f"  → Used: {result['model']} ({result['latency_s']}s, "
          f"{result['tokens']} tokens)")
    print()

print(f"\n{'='*60}")
print("Tier Statistics")
print(f"{'='*60}")
for tier in tiers:
    total = tier.success_count + tier.failure_count
    rate = tier.success_count / total * 100 if total > 0 else 0
    print(f"  {tier.name:<25} successes={tier.success_count:<3} "
          f"failures={tier.failure_count:<3} success_rate={rate:.0f}%")

avg_latency = sum(chain.execute("test")["latency_s"] for _ in range(5)) / 5
print(f"\nEffective availability: {sum(1 for t in tiers if not t.skipped)}/{len(tiers)} tiers")
print("Fallback ensures 100% uptime even when individual models fail")
