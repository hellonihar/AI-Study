"""
Approval workflow: governance review and approval processes for model deployment.

Run: python 08-approval-workflow.py

Requirements: numpy
"""

import time
import json
import hashlib
from collections import defaultdict

print("=== Approval Workflow ===\n")

class ApprovalRequest:
    def __init__(self, system_name, risk_tier, requestor, details=None):
        self.request_id = hashlib.md5(f"{system_name}{time.time()}".encode()).hexdigest()[:12]
        self.system_name = system_name
        self.risk_tier = risk_tier
        self.requestor = requestor
        self.details = details or {}
        self.created_at = time.time()
        self.status = "draft"
        self.reviews = []
        self.approvals = []

    def submit(self):
        self.status = "pending_review"
        return self

    def add_review(self, reviewer, decision, comments=""):
        review = {
            "reviewer": reviewer,
            "decision": decision,
            "comments": comments,
            "timestamp": time.time(),
        }
        self.reviews.append(review)
        return review

    def add_approval(self, approver, decision, conditions=None):
        approval = {
            "approver": approver,
            "decision": decision,
            "conditions": conditions or [],
            "timestamp": time.time(),
        }
        self.approvals.append(approval)
        if decision == "approved":
            all_approved = all(a["decision"] == "approved" for a in self.approvals)
            self.status = "approved" if all_approved else "pending_approval"
        else:
            self.status = "rejected"
        return approval

class ApprovalWorkflow:
    def __init__(self, name="default"):
        self.name = name
        self.requests = []

    def create_request(self, system_name, risk_tier, requestor, details=None):
        request = ApprovalRequest(system_name, risk_tier, requestor, details)
        self.requests.append(request)
        return request

    def get_required_approvals(self, tier):
        required = {
            "Tier 4: Critical": ["ml_platform_lead", "ai_review_board", "cairo", "legal", "ciso"],
            "Tier 3: High": ["ml_platform_lead", "ai_review_board", "legal"],
            "Tier 2: Medium": ["ml_platform_lead"],
            "Tier 1: Low": ["tech_lead"],
        }
        return required.get(tier, ["tech_lead"])

    def get_required_reviews(self, tier):
        required = {
            "Tier 4: Critical": ["security_review", "bias_audit", "safety_eval", "legal_review"],
            "Tier 3: High": ["bias_audit", "safety_eval"],
            "Tier 2: Medium": ["basic_review"],
            "Tier 1: Low": [],
        }
        return required.get(tier, [])

class WorkflowEngine:
    def __init__(self, workflow):
        self.workflow = workflow

    def execute(self, request, test_responses=None):
        test_responses = test_responses or {}
        idx = len(self.workflow.requests) - 1

        request.submit()
        print(f"  Request {request.request_id}: {request.system_name} ({request.risk_tier})")
        print(f"  Status: {request.status}")
        print()

        required_reviews = self.workflow.get_required_reviews(request.risk_tier)
        print(f"  Required Reviews: {required_reviews}")
        for review_type in required_reviews:
            response = test_responses.get(review_type, {"decision": "pass", "comments": "Auto-approved"})
            request.add_review(review_type, response["decision"], response["comments"])
            icon = "PASS" if response["decision"] == "pass" else "FAIL"
            print(f"    [{icon}] {review_type}: {response['comments'][:50]}")
        print()

        required_approvals = self.workflow.get_required_approvals(request.risk_tier)
        print(f"  Required Approvals: {required_approvals}")
        for approver in required_approvals:
            response = test_responses.get(approver, {"decision": "approved", "conditions": []})
            request.add_approval(approver, response["decision"], response.get("conditions", []))
            icon = "APPROVED" if response["decision"] == "approved" else "REJECTED"
            print(f"    [{icon}] {approver}")
            for cond in response.get("conditions", []):
                print(f"      Condition: {cond}")
        print()

        print(f"  Final Status: {request.status}")
        return request

workflow = ApprovalWorkflow("production-governance")
engine = WorkflowEngine(workflow)

print("=== High Risk Model (Approved) ===")
request1 = workflow.create_request("Loan Origination AI", "Tier 3: High", "ml-team")
engine.execute(request1, {
    "bias_audit": {"decision": "pass", "comments": "Bias audit completed, disparate impact 0.92"},
    "safety_eval": {"decision": "pass", "comments": "Safety evaluation passed all thresholds"},
    "ml_platform_lead": {"decision": "approved", "conditions": []},
    "ai_review_board": {"decision": "approved", "conditions": ["Quarterly fairness review", "Monthly monitoring report"]},
    "legal": {"decision": "approved", "conditions": ["Legal disclaimer on all outputs"]},
})
print()

print("=== Critical Risk Model (Rejected) ===")
request2 = workflow.create_request("Medical Diagnosis AI", "Tier 4: Critical", "health-team")
engine.execute(request2, {
    "security_review": {"decision": "pass", "comments": "Security review passed"},
    "bias_audit": {"decision": "fail", "comments": "Significant accuracy disparity across demographic groups"},
    "safety_eval": {"decision": "fail", "comments": "False negative rate exceeds clinical threshold"},
    "legal_review": {"decision": "pass", "comments": "Legal review pending final sign-off"},
    "ml_platform_lead": {"decision": "rejected", "conditions": ["Must address bias and safety findings first"]},
})
print()

print("=== Workflow Summary ===")
for req in workflow.requests:
    duration = time.time() - req.created_at
    print(f"  {req.request_id}: {req.system_name:<25} [{req.risk_tier:<16}] -> {req.status}")
