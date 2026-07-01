"""
Ethics impact assessor: stakeholder impact analysis and ethics review.

Run: python 07-ethics-impact-assessor.py

Requirements: numpy
"""

import time
import json

print("=== Ethics Impact Assessor ===\n")

STAKEHOLDER_CATEGORIES = [
    "end_users",
    "affected_non_users",
    "developers",
    "business_owners",
    "regulators",
    "society",
]

ETHICS_DIMENSIONS = [
    "beneficence",
    "non_maleficence",
    "autonomy",
    "justice",
    "transparency",
    "accountability",
]

class StakeholderImpact:
    def __init__(self, stakeholder):
        self.stakeholder = stakeholder
        self.positive_impacts = []
        self.negative_impacts = []
        self.mitigations = []
        self.risk_score = 0.0

    def add_positive(self, impact):
        self.positive_impacts.append(impact)

    def add_negative(self, impact, severity=0.3):
        self.negative_impacts.append({"impact": impact, "severity": severity})
        self.risk_score = min(1.0, self.risk_score + severity)

    def add_mitigation(self, mitigation):
        self.mitigations.append(mitigation)
        self.risk_score = max(0, self.risk_score - 0.2)

class EthicsAssessment:
    def __init__(self, system_name):
        self.system_name = system_name
        self.stakeholder_impacts = {}
        self.dimension_scores = {}
        self.recommendations = []
        self.overall_risk = 0.0
        self.approved = False

    def assess(self):
        for dim in ETHICS_DIMENSIONS:
            self.dimension_scores[dim] = {"score": 0.0, "concerns": []}
        for stakeholder in STAKEHOLDER_CATEGORIES:
            self.stakeholder_impacts[stakeholder] = StakeholderImpact(stakeholder)
        return self

    def compute_overall_risk(self):
        scores = [s.risk_score for s in self.stakeholder_impacts.values()]
        self.overall_risk = sum(scores) / len(scores) if scores else 0
        self.approved = self.overall_risk < 0.5
        return self.overall_risk

    def report(self):
        return {
            "system": self.system_name,
            "overall_risk": round(self.overall_risk, 2),
            "approved": self.approved,
            "stakeholders": {
                s: {
                    "positive_impacts": len(imp.positive_impacts),
                    "negative_impacts": len(imp.negative_impacts),
                    "mitigations": len(imp.mitigations),
                    "risk_score": round(imp.risk_score, 2),
                }
                for s, imp in self.stakeholder_impacts.items()
            },
            "recommendations": self.recommendations,
        }

def assess_chatbot():
    assessment = EthicsAssessment("Customer Support Chatbot").assess()

    users = assessment.stakeholder_impacts["end_users"]
    users.add_positive("24/7 support availability")
    users.add_positive("Faster response times")
    users.add_negative("Reduced human interaction quality", 0.2)
    users.add_mitigation("Easy escalation to human agents")
    users.add_mitigation("Opt-out option for AI-only interactions")

    non_users = assessment.stakeholder_impacts["affected_non_users"]
    non_users.add_positive("Reduced wait times for phone support")
    non_users.add_negative("Potential job displacement for support staff", 0.5)
    non_users.add_mitigation("Reskilling program for affected staff")
    non_users.add_mitigation("AI augmentation model (not replacement)")

    developers = assessment.stakeholder_impacts["developers"]
    developers.add_positive("Interesting technical challenges")
    developers.add_negative("Responsibility for system failures", 0.3)
    developers.add_mitigation("Clear testing and monitoring requirements")

    business = assessment.stakeholder_impacts["business_owners"]
    business.add_positive("Cost reduction in support operations")
    business.add_positive("Scalable customer service")
    business.add_negative("Reputational risk from AI failures", 0.4)
    business.add_mitigation("Quality monitoring and guardrails")

    regulators = assessment.stakeholder_impacts["regulators"]
    regulators.add_negative("Lack of transparency in AI decisions", 0.3)
    regulators.add_mitigation("Model cards and transparency documentation")

    society = assessment.stakeholder_impacts["society"]
    society.add_positive("Improved access to support services")
    society.add_negative("Normalization of AI customer service", 0.1)

    assessment.recommendations = [
        "Implement easy escalation to human agents",
        "Provide transparency notice to users",
        "Establish quality monitoring with human review",
        "Conduct regular bias audits",
        "Create employee reskilling program",
    ]
    assessment.compute_overall_risk()
    return assessment

def assess_hiring_tool():
    assessment = EthicsAssessment("AI Hiring Screening Tool").assess()

    users = assessment.stakeholder_impacts["end_users"]
    users.add_positive("Faster application processing")
    users.add_positive("Consistent evaluation criteria")
    users.add_negative("Potential bias against minority groups", 0.8)
    users.add_negative("Lack of transparency in rejection reasons", 0.6)
    users.add_mitigation("Comprehensive bias auditing")
    users.add_mitigation("Explainable AI techniques")
    users.add_mitigation("Right to human review of decisions")

    non_users = assessment.stakeholder_impacts["affected_non_users"]
    non_users.add_negative("Systematic exclusion of qualified candidates", 0.7)
    non_users.add_mitigation("Regular fairness audits with external reviewers")

    developers = assessment.stakeholder_impacts["developers"]
    developers.add_positive("Building impactful system")
    developers.add_negative("Ethical burden of design decisions", 0.5)

    business = assessment.stakeholder_impacts["business_owners"]
    business.add_positive("Reduced hiring costs")
    business.add_positive("Faster time-to-hire")
    business.add_negative("Legal liability from discriminatory outcomes", 0.7)
    business.add_mitigation("Legal review of deployment")

    regulators = assessment.stakeholder_impacts["regulators"]
    regulators.add_negative("NYC Local Law 144 compliance risk", 0.6)

    society = assessment.stakeholder_impacts["society"]
    society.add_negative("Reinforcement of existing biases in hiring", 0.7)
    society.add_mitigation("Public transparency reports")

    assessment.recommendations = [
        "Conduct mandatory bias audit before deployment",
        "Implement explainable AI for all screening decisions",
        "Provide right to human review for all candidates",
        "Publish transparency report annually",
        "Establish independent ethics oversight",
    ]
    assessment.compute_overall_risk()
    return assessment

print("=== Assessment 1: Customer Support Chatbot ===")
chatbot = assess_chatbot()
report = chatbot.report()
print(f"  Overall Risk: {report['overall_risk']:.2f} / 1.0")
print(f"  Decision: {'APPROVED' if report['approved'] else 'REQUIRES REVIEW'}")
print(f"  Stakeholders:")
for s, data in report["stakeholders"].items():
    print(f"    {s:<20} risk={data['risk_score']:.2f} (+{data['positive_impacts']}/-{data['negative_impacts']}/mit={data['mitigations']})")
print(f"  Recommendations:")
for r in report["recommendations"]:
    print(f"    - {r}")
print()

print("=== Assessment 2: AI Hiring Screening Tool ===")
hiring = assess_hiring_tool()
report2 = hiring.report()
print(f"  Overall Risk: {report2['overall_risk']:.2f} / 1.0")
print(f"  Decision: {'APPROVED' if report2['approved'] else 'REQUIRES REVIEW'}")
for r in report2["recommendations"]:
    print(f"    - {r}")
