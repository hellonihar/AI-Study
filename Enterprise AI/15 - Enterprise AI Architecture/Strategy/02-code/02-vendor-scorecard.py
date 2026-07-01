"""
Vendor scorecard: evaluate and compare AI model providers.

Run: python 02-vendor-scorecard.py

Requirements: numpy
"""

import numpy as np

print("=== Vendor Scorecard ===\n")

VENDORS = {
    "OpenAI GPT-4o": {
        "quality": 9.5,
        "reliability": 9.0,
        "pricing": 6.0,
        "data_privacy": 7.0,
        "latency": 8.5,
        "ecosystem": 9.5,
    },
    "OpenAI GPT-4o-mini": {
        "quality": 8.0,
        "reliability": 9.0,
        "pricing": 9.5,
        "data_privacy": 7.0,
        "latency": 9.0,
        "ecosystem": 9.5,
    },
    "Claude 3 Sonnet": {
        "quality": 9.0,
        "reliability": 9.0,
        "pricing": 8.0,
        "data_privacy": 8.0,
        "latency": 8.0,
        "ecosystem": 7.0,
    },
    "Claude 3 Haiku": {
        "quality": 7.5,
        "reliability": 9.0,
        "pricing": 9.5,
        "data_privacy": 8.0,
        "latency": 9.5,
        "ecosystem": 6.5,
    },
    "Self-Hosted Llama 3": {
        "quality": 7.5,
        "reliability": 7.0,
        "pricing": 8.0,
        "data_privacy": 10.0,
        "latency": 7.0,
        "ecosystem": 5.0,
    },
}

WEIGHT_SETS = {
    "General Purpose": {"quality": 0.25, "reliability": 0.20, "pricing": 0.20, "data_privacy": 0.15, "latency": 0.10, "ecosystem": 0.10},
    "Cost Sensitive": {"quality": 0.15, "reliability": 0.15, "pricing": 0.35, "data_privacy": 0.10, "latency": 0.15, "ecosystem": 0.10},
    "Privacy First": {"quality": 0.20, "reliability": 0.15, "pricing": 0.10, "data_privacy": 0.35, "latency": 0.10, "ecosystem": 0.10},
    "Performance Critical": {"quality": 0.30, "reliability": 0.10, "pricing": 0.10, "data_privacy": 0.10, "latency": 0.30, "ecosystem": 0.10},
}

class VendorScorecard:
    def score(self, vendor_name, weights):
        scores = VENDORS.get(vendor_name, {})
        if not scores:
            return None
        total = sum(scores.get(dim, 0) * weight for dim, weight in weights.items())
        return round(total, 1), scores

scorecard = VendorScorecard()

for profile, weights in WEIGHT_SETS.items():
    print(f"=== {profile} ===")
    ranked = []
    for vendor in VENDORS:
        total, scores = scorecard.score(vendor, weights)
        ranked.append((total, vendor, scores))
    ranked.sort(reverse=True)
    for rank, (total, vendor, scores) in enumerate(ranked, 1):
        print(f"  {rank}. {vendor:<25} {total:.1f}/10  (", end="")
        details = []
        for dim, w in sorted(weights.items(), key=lambda x: -x[1]):
            s = scores.get(dim, 0)
            if w > 0.15:
                details.append(f"{dim}:{s}")
        print(", ".join(details[:3]), end="")
        print(")")
    print()
