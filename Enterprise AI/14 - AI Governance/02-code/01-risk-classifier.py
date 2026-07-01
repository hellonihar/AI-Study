"""
Model risk classifier: classify AI systems into risk tiers based on impact.

Run: python 01-risk-classifier.py

Requirements: numpy
"""

import json

print("=== Model Risk Classifier ===\n")

RISK_DIMENSIONS = {
    "user_impact": {
        "points": {"none": 1, "informational": 2, "decision": 3, "life_altering": 4},
        "weight": 0.30,
    },
    "data_sensitivity": {
        "points": {"public": 1, "internal": 2, "pii": 3, "regulated": 4},
        "weight": 0.20,
    },
    "autonomy": {
        "points": {"human_in_loop": 1, "human_on_loop": 2, "automated": 3, "fully_autonomous": 4},
        "weight": 0.25,
    },
    "scale": {
        "points": {"internal_tool": 1, "departmental": 2, "enterprise": 3, "public_facing": 4},
        "weight": 0.15,
    },
    "failure_impact": {
        "points": {"minor": 1, "operational": 2, "financial_legal": 3, "physical_harm": 4},
        "weight": 0.10,
    },
}

TIER_THRESHOLDS = [
    ("Tier 4: Critical", 3.5),
    ("Tier 3: High", 2.5),
    ("Tier 2: Medium", 1.5),
    ("Tier 1: Low", 0),
]

class RiskClassifier:
    def classify(self, assessments):
        total_score = 0.0
        details = {}
        for dim, config in RISK_DIMENSIONS.items():
            value = assessments.get(dim, "none")
            points = config["points"].get(value, 1)
            weighted = points * config["weight"]
            total_score += weighted
            details[dim] = {"value": value, "points": points, "weighted": round(weighted, 3)}
        for tier_name, threshold in TIER_THRESHOLDS:
            if total_score >= threshold:
                tier = tier_name
                break
        return {
            "tier": tier,
            "score": round(total_score, 2),
            "details": details,
        }

    def get_requirements(self, tier):
        requirements = {
            "Tier 4: Critical": [
                "Full risk assessment", "External audit", "Regulatory filing",
                "Continuous monitoring", "Human oversight", "Explainability",
                "Comprehensive bias audit", "Incident response plan",
            ],
            "Tier 3: High": [
                "Risk assessment", "Bias audit", "Explainability",
                "Human review provision", "Regular monitoring", "Model card",
            ],
            "Tier 2: Medium": [
                "Documentation", "Basic bias checks", "Transparency notice",
                "Periodic review", "Model card",
            ],
            "Tier 1: Low": [
                "Basic documentation", "Standard approval", "Model card",
            ],
        }
        return requirements.get(tier, ["Unknown tier"])

classifier = RiskClassifier()

TEST_SYSTEMS = [
    {
        "name": "Customer Support Chatbot",
        "assessments": {
            "user_impact": "informational",
            "data_sensitivity": "internal",
            "autonomy": "human_on_loop",
            "scale": "enterprise",
            "failure_impact": "minor",
        },
    },
    {
        "name": "Automated Loan Origination",
        "assessments": {
            "user_impact": "life_altering",
            "data_sensitivity": "regulated",
            "autonomy": "automated",
            "scale": "enterprise",
            "failure_impact": "financial_legal",
        },
    },
    {
        "name": "Internal Code Assistant",
        "assessments": {
            "user_impact": "none",
            "data_sensitivity": "internal",
            "autonomy": "human_in_loop",
            "scale": "internal_tool",
            "failure_impact": "minor",
        },
    },
    {
        "name": "Medical Diagnosis Support",
        "assessments": {
            "user_impact": "life_altering",
            "data_sensitivity": "regulated",
            "autonomy": "human_in_loop",
            "scale": "public_facing",
            "failure_impact": "physical_harm",
        },
    },
    {
        "name": "Content Moderation System",
        "assessments": {
            "user_impact": "decision",
            "data_sensitivity": "pii",
            "autonomy": "automated",
            "scale": "public_facing",
            "failure_impact": "operational",
        },
    },
]

print(f"{'System':<30} {'Tier':<20} {'Score':<8} {'Requirements':<10}")
print("-" * 85)
for system in TEST_SYSTEMS:
    result = classifier.classify(system["assessments"])
    reqs = classifier.get_requirements(result["tier"])
    print(f"{system['name']:<30} {result['tier']:<20} {result['score']:<8.2f} {len(reqs)} controls")
    for req in reqs:
        print(f"  {'':<50} - {req}")
    print()
