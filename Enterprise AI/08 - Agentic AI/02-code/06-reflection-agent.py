"""
Reflection agent: self-critique and iterative improvement loop.

Run: python 06-reflection-agent.py

Requirements: none (stdlib only)
"""

import json
import time
import random

print("=== Reflection Agent ===\n")

class ReflectionAgent:
    def __init__(self, max_attempts=3):
        self.max_attempts = max_attempts
        self.reflections = []

    def attempt(self, task):
        quality = random.uniform(0.1, 0.9)
        return {
            "output": f"Solution for: {task} (quality={quality:.2f})",
            "quality": quality,
        }

    def reflect(self, task, result, attempt_num):
        issues = []
        if result["quality"] < 0.5:
            issues.append("Insufficient quality")
        if attempt_num == 1:
            issues.append("Need more thorough analysis")

        reflection = {
            "attempt": attempt_num,
            "issues": issues,
            "improvement_plan": f"Improve quality by adding more detail and verification",
        }
        self.reflections.append(reflection)
        return reflection

    def decide_retry(self, result, attempt_num):
        if attempt_num >= self.max_attempts:
            return False
        return result["quality"] < 0.7

    def run(self, task):
        print(f"Task: {task}\n")

        for attempt in range(1, self.max_attempts + 1):
            print(f"  Attempt {attempt}: generating...")
            result = self.attempt(task)
            print(f"    Output: {result['output']}")

            if attempt < self.max_attempts and self.decide_retry(result, attempt):
                reflection = self.reflect(task, result, attempt)
                print(f"    Reflection: issues={reflection['issues']}")
                print(f"    Plan: {reflection['improvement_plan']}")
                print(f"    → Retrying...\n")
            else:
                print(f"    Accepted (quality={result['quality']:.2f})")
                break

        return result

agent = ReflectionAgent(max_attempts=4)

TASKS = ["Write a function to sort a list"]

for task in TASKS:
    print("-" * 60)
    result = agent.run(task)
    print(f"\n  Final result: {result['output']}")
    print(f"  Attempts: {len(agent.reflections) + 1}")
    print()

print(f"{'='*60}")
print("Reflection Summary")
print(f"{'='*60}")
for r in agent.reflections:
    print(f"  Attempt {r['attempt']}: issues={r['issues']}")

print(f"\n{'='*60}")
print("Reflection Pattern")
print(f"{'='*60}")
print("  Execute → Evaluate → If poor → Reflect → Improve → Retry")
print("  Key: each reflection generates concrete improvement plan")
print("  Limit: max 3 attempts, then accept best result or fallback")
