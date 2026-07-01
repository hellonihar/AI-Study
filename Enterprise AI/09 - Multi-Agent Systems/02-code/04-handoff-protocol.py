"""
Handoff protocol: transfer control and context between agents.

Run: python 04-handoff-protocol.py

Requirements: none (stdlib only)
"""

import json
import time
import uuid
from datetime import datetime

print("=== Handoff Protocol ===\n")

class Agent:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.handoffs_received = 0

    def can_handle(self, task):
        return False

    def handle(self, task, context):
        return {"result": f"{self.name} processed: {task}"}

class SupportAgent(Agent):
    def can_handle(self, task):
        return task in ["password_reset", "account_status", "general_inquiry"]

    def handle(self, task, context):
        if task == "password_reset":
            return {"result": "Password reset link sent to email", "tier": "support"}
        return {"result": f"Support handled: {task}", "tier": "support"}

class BillingAgent(Agent):
    def can_handle(self, task):
        return task in ["refund", "invoice", "payment_failure", "billing_inquiry"]

    def handle(self, task, context):
        if task == "refund":
            return {"result": "Refund initiated: $49.99", "tier": "billing"}
        return {"result": f"Billing handled: {task}", "tier": "billing"}

class EscalationAgent(Agent):
    def can_handle(self, task):
        return True

    def handle(self, task, context):
        return {"result": f"Escalated: {task} — assigned to human agent",
                "tier": "escalation", "priority": "high"}

class HandoffManager:
    def __init__(self):
        self.agents = []
        self.handoff_log = []

    def register(self, agent):
        self.agents.append(agent)

    def transfer(self, task, context, from_agent, to_agent):
        handoff = {
            "handoff_id": uuid.uuid4().hex[:8],
            "task": task,
            "from": from_agent.name if from_agent else "system",
            "to": to_agent.name,
            "context": context,
            "timestamp": datetime.now().isoformat(),
        }
        self.handoff_log.append(handoff)
        to_agent.handoffs_received += 1
        print(f"  Handoff: {handoff['from']} → {handoff['to']} "
              f"(task: {task})")
        return handoff

    def route(self, task, context=None):
        context = context or {"conversation": [], "findings": {}}
        print(f"\nRouting task: '{task}'")
        current_agent = None

        for agent in self.agents:
            if agent.can_handle(task):
                if current_agent:
                    self.transfer(task, context, current_agent, agent)
                current_agent = agent
                result = agent.handle(task, context)
                context["result"] = result
                context["conversation"].append({"agent": agent.name, "result": result})
                print(f"  {agent.name} ({agent.role}): {result['result']}")

                if result.get("tier") == "escalation":
                    break
                return result

        if current_agent:
            return current_agent.handle(task, context)

        escalation_agent = self.agents[-1]
        if current_agent:
            self.transfer(task, context, current_agent, escalation_agent)
        return escalation_agent.handle(task, context)

manager = HandoffManager()
manager.register(SupportAgent("support_bot", "support"))
manager.register(BillingAgent("billing_bot", "billing"))
manager.register(EscalationAgent("escalation_bot", "escalation"))

TASKS = [
    ("password_reset", "Customer forgot password"),
    ("refund", "Customer wants refund for order #12345"),
    ("hacking_attempt", "Customer reports compromised account"),
]

for task, description in TASKS:
    print("-" * 60)
    result = manager.route(task)
    print()

print(f"{'='*60}")
print("Handoff Log")
print(f"{'='*60}")
for h in manager.handoff_log:
    print(f"  {h['handoff_id']}: {h['from']} → {h['to']} ({h['task']})")

print(f"\n{'='*60}")
print("Handoff Protocol Summary")
print(f"{'='*60}")
print("  Task → Support Agent → Billing Agent → Escalation Agent")
print("  Each handoff transfers full context")
print("  Escalation = last resort (human agent)")
