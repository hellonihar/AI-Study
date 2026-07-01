"""
Maturity assessment: evaluate AI capability maturity across dimensions.

Run: python 04-maturity-assessment.py

Requirements: numpy
"""

import numpy as np

print("=== AI Maturity Assessment ===\n")

DIMENSIONS = {
    "Strategy & Governance": 0.20,
    "Data & Infrastructure": 0.20,
    "Model Development": 0.20,
    "Operations": 0.20,
    "Talent & Culture": 0.20,
}

CRITERIA = {
    "Strategy & Governance": [
        ("AI strategy documented", ["none", "draft", "approved", "board-level", "continuously updated"]),
        ("Risk management", ["none", "basic", "defined", "measured", "automated"]),
        ("Compliance framework", ["none", "awareness", "manual", "automated", "continuous"]),
        ("Executive sponsorship", ["none", "aware", "supportive", "champion", "driving"]),
    ],
    "Data & Infrastructure": [
        ("Data platform", ["none", "ad-hoc", "centralized", "unified", "self-service"]),
        ("GPU/ compute access", ["none", "cloud only", "dedicated", "auto-scaling", "multi-region"]),
        ("Model serving platform", ["none", "single API", "multi-modal", "platform", "self-service"]),
        ("ML pipeline", ["none", "manual", "semi-automated", "CI/CD", "continuous delivery"]),
    ],
    "Model Development": [
        ("Prompt engineering", ["ad-hoc", "documented", "templated", "version controlled", "automated eval"]),
        ("Fine-tuning capability", ["none", "experimental", "production PEFT", "RLHF/DPO", "continuous"]),
        ("Evaluation practice", ["manual", "basic metrics", "automated eval", "LLM-as-judge", "multi-method"]),
        ("RAG capability", ["none", "basic", "production RAG", "advanced", "multi-modal RAG"]),
    ],
    "Operations": [
        ("Monitoring", ["none", "uptime only", "quality monitoring", "cost + quality", "predictive"]),
        ("Incident response", ["none", "manual", "defined process", "automated", "self-healing"]),
        ("Cost management", ["none", "manual tracking", "budget alerts", "auto-optimization", "chargeback"]),
        ("CI/CD for AI", ["none", "manual deploy", "basic pipeline", "automated gates", "continuous deploy"]),
    ],
    "Talent & Culture": [
        ("AI training", ["none", "self-service", "formal program", "continuous learning", "AI-first culture"]),
        ("Team structure", ["none", "individuals", "dedicated team", "CoE", "federated platform"]),
        ("Community of practice", ["none", "informal", "regular meetups", "cross-team", "industry leading"]),
        ("AI ethics awareness", ["none", "awareness", "training", "embedded", "champion-led"]),
    ],
}

class MaturityAssessment:
    def assess(self, responses):
        dimension_scores = {}
        total_score = 0.0
        for dim, weight in DIMENSIONS.items():
            dim_total = 0.0
            max_total = 0.0
            for criterion, levels in CRITERIA[dim]:
                response = responses.get(criterion, 0)
                score = response / (len(levels) - 1)
                dim_total += score
                max_total += 1.0
            dim_avg = dim_total / max_total if max_total > 0 else 0
            dimension_scores[dim] = round(dim_avg * 10, 1)
            total_score += dim_avg * weight * 10
        overall = round(total_score, 1)
        if overall < 3:
            level = "Level 1: Ad-hoc"
        elif overall < 5:
            level = "Level 2: Foundational"
        elif overall < 7:
            level = "Level 3: Scaling"
        elif overall < 9:
            level = "Level 4: Optimized"
        else:
            level = "Level 5: Autonomous"
        return {"overall": overall, "level": level, "dimensions": dimension_scores}

assessor = MaturityAssessment()

ORGANIZATIONS = [
    {
        "name": "Startup Corp",
        "responses": {
            "AI strategy documented": 1, "Risk management": 0, "Compliance framework": 0, "Executive sponsorship": 2,
            "Data platform": 0, "GPU/ compute access": 2, "Model serving platform": 1, "ML pipeline": 0,
            "Prompt engineering": 1, "Fine-tuning capability": 0, "Evaluation practice": 0, "RAG capability": 1,
            "Monitoring": 0, "Incident response": 0, "Cost management": 0, "CI/CD for AI": 0,
            "AI training": 1, "Team structure": 1, "Community of practice": 0, "AI ethics awareness": 0,
        },
    },
    {
        "name": "Enterprise Mid",
        "responses": {
            "AI strategy documented": 3, "Risk management": 2, "Compliance framework": 2, "Executive sponsorship": 3,
            "Data platform": 2, "GPU/ compute access": 2, "Model serving platform": 2, "ML pipeline": 2,
            "Prompt engineering": 3, "Fine-tuning capability": 2, "Evaluation practice": 2, "RAG capability": 2,
            "Monitoring": 2, "Incident response": 1, "Cost management": 1, "CI/CD for AI": 2,
            "AI training": 2, "Team structure": 2, "Community of practice": 1, "AI ethics awareness": 1,
        },
    },
    {
        "name": "AI Native Co",
        "responses": {
            "AI strategy documented": 4, "Risk management": 3, "Compliance framework": 3, "Executive sponsorship": 4,
            "Data platform": 3, "GPU/ compute access": 4, "Model serving platform": 3, "ML pipeline": 3,
            "Prompt engineering": 4, "Fine-tuning capability": 3, "Evaluation practice": 4, "RAG capability": 3,
            "Monitoring": 3, "Incident response": 3, "Cost management": 2, "CI/CD for AI": 3,
            "AI training": 3, "Team structure": 3, "Community of practice": 3, "AI ethics awareness": 2,
        },
    },
]

for org in ORGANIZATIONS:
    result = assessor.assess(org["responses"])
    print(f"=== {org['name']} ===")
    print(f"  Overall: {result['overall']}/10 - {result['level']}")
    for dim, score in result["dimensions"].items():
        bar = "#" * int(score) + "." * (10 - int(score))
        print(f"  {dim:<25} {bar} {score}/10")
    print()
