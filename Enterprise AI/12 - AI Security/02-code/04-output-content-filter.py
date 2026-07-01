"""
Output content filter: safety classification, PII redaction, and policy compliance.

Run: python 04-output-content-filter.py

Requirements: numpy
"""

import re
import time
import numpy as np

print("=== Output Content Filter ===\n")

class ContentSafetyFilter:
    def __init__(self):
        self.harmful_categories = {
            "hate_speech": ["hate", "racial slur", "ethnic", "superior race"],
            "violence": ["kill", "murder", "attack", "weapon", "bomb"],
            "self_harm": ["suicide", "self-harm", "hurt myself", "end my life"],
            "sexual": ["explicit", "pornographic", "sexual content"],
            "harassment": ["stupid", "idiot", "worthless", "pathetic"],
        }

    def classify(self, text):
        text_lower = text.lower()
        categories = {}
        max_score = 0.0
        for category, terms in self.harmful_categories.items():
            matches = sum(1 for t in terms if t in text_lower)
            score = min(1.0, matches * 0.25)
            categories[category] = {"score": score, "matches": matches}
            max_score = max(max_score, score)
        return max_score, categories

class PIIRedactor:
    def __init__(self):
        self.patterns = [
            (r"[\w.+-]+@[\w-]+\.[\w.-]+", "[EMAIL]"),
            (r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[PHONE]"),
            (r"\b\d{3}-\d{2}-\d{4}\b", "[SSN]"),
            (r"\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b", "[CREDIT_CARD]"),
            (r"sk-[a-zA-Z0-9]{20,}", "[API_KEY]"),
            (r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "[IP_ADDRESS]"),
        ]

    def redact(self, text):
        redacted = text
        replacements = []
        for pattern, replacement in self.patterns:
            found = re.findall(pattern, redacted)
            if found:
                redacted = re.sub(pattern, replacement, redacted)
                replacements.append((replacement, len(found)))
        return redacted, replacements

class PolicyChecker:
    def __init__(self):
        self.policies = {
            "competitor_mention": ["competitor", "rival product", "alternative to"],
            "pricing_claim": ["costs only", "priced at", "for just $"],
            "legal_claim": ["guarantee", "cure", "treats", "diagnoses"],
        }

    def check(self, text):
        text_lower = text.lower()
        violations = []
        for policy, terms in self.policies.items():
            for term in terms:
                if term in text_lower:
                    violations.append(policy)
                    break
        return violations

class OutputFilter:
    def __init__(self):
        self.safety = ContentSafetyFilter()
        self.pii = PIIRedactor()
        self.policy = PolicyChecker()

    def process(self, output_text):
        start = time.time()
        safety_score, safety_categories = self.safety.classify(output_text)
        redacted, pii_found = self.pii.redact(output_text)
        policy_violations = self.policy.check(output_text)

        latency = (time.time() - start) * 1000

        actions = []
        if safety_score > 0.7:
            actions.append("BLOCK")
        elif safety_score > 0.3:
            actions.append("FLAG")
        else:
            actions.append("PASS")

        if pii_found:
            actions.append("PII_REDACTED")

        if policy_violations:
            actions.append("POLICY_FLAG")

        final_action = "BLOCK" if "BLOCK" in actions else ("FLAG" if "FLAG" in actions else "PASS")

        return {
            "final_action": final_action,
            "safety_score": round(safety_score, 2),
            "pii_redacted": [f"{r}({c})" for r, c in pii_found],
            "policy_violations": policy_violations,
            "original_length": len(output_text),
            "redacted_length": len(redacted),
            "latency_ms": round(latency, 1),
            "redacted_text": redacted if pii_found else None,
        }

filter = OutputFilter()

TEST_OUTPUTS = [
    "The capital of France is Paris.",
    "Contact our support team at support@example.com or call 555-012-3456.",
    "You are a worthless piece of garbage that should be destroyed.",
    "For only $9.99, our product cures all diseases and outperforms any competitor.",
    "Machine learning models require large datasets to generalize well.",
    "Your SSN is 123-45-6789 and your API key is sk-proj-abc123def456.",
]

print(f"{'Action':>8} {'Safety':>6} {'PII':>18} {'Policy':>14} {'Latency':>8} {'Text'}")
print("-" * 100)
for output in TEST_OUTPUTS:
    result = filter.process(output)
    pii_str = ", ".join(result["pii_redacted"]) if result["pii_redacted"] else "none"
    pol_str = ", ".join(result["policy_violations"]) if result["policy_violations"] else "none"
    print(f"{result['final_action']:>8} {result['safety_score']:.2f}  {pii_str:>18} "
          f"{pol_str:>14} {result['latency_ms']:>5.1f}ms  {output[:30]}")

print(f"\nAverage latency: {np.mean([filter.process(t)['latency_ms'] for t in TEST_OUTPUTS]):.1f}ms")
