"""
Incident response system: detection, triage, containment, and post-mortem.

Run: python 08-incident-response-system.py

Requirements: numpy
"""

import time
import json
from datetime import datetime, timedelta

print("=== Incident Response System ===\n")

class Incident:
    def __init__(self, incident_type, severity, description, source):
        self.id = f"INC-{int(time.time()) % 100000:06d}"
        self.type = incident_type
        self.severity = severity
        self.description = description
        self.source = source
        self.timestamp = time.time()
        self.status = "detected"
        self.timeline = [{"time": time.time(), "action": "detected", "detail": description}]

    def add_event(self, action, detail):
        self.timeline.append({"time": time.time(), "action": action, "detail": detail})

    def resolve(self):
        self.status = "resolved"
        self.add_event("resolved", "Incident resolved")
        self.resolved_at = time.time()
        self.duration_min = round((self.resolved_at - self.timestamp) / 60, 1)

    def report(self):
        return {
            "id": self.id,
            "type": self.type,
            "severity": self.severity,
            "description": self.description,
            "status": self.status,
            "duration_min": getattr(self, "duration_min", None),
            "events": len(self.timeline),
        }

class IncidentDetector:
    def __init__(self):
        self.thresholds = {
            "error_rate": 0.02,
            "p95_latency_ms": 3000,
            "hallucination_rate": 0.05,
            "cost_spike_multiplier": 2.0,
        }

    def evaluate_metrics(self, metrics):
        incidents = []
        if metrics.get("error_rate", 0) > self.thresholds["error_rate"]:
            sev = "SEV-1" if metrics["error_rate"] > 0.05 else "SEV-2"
            incidents.append(Incident("error_spike", sev, f"Error rate: {metrics['error_rate']:.1%}", "monitoring"))
        if metrics.get("p95_latency_ms", 0) > self.thresholds["p95_latency_ms"]:
            sev = "SEV-2" if metrics["p95_latency_ms"] > 5000 else "SEV-3"
            incidents.append(Incident("latency_spike", sev, f"p95 latency: {metrics['p95_latency_ms']}ms", "monitoring"))
        if metrics.get("hallucination_rate", 0) > self.thresholds["hallucination_rate"]:
            incidents.append(Incident("quality_degradation", "SEV-1", f"Hallucination rate: {metrics['hallucination_rate']:.1%}", "eval_pipeline"))
        if metrics.get("cost_spike", 1.0) > self.thresholds["cost_spike_multiplier"]:
            incidents.append(Incident("cost_anomaly", "SEV-3", f"Cost spike: {metrics['cost_spike']:.1f}x normal", "cost_monitoring"))
        return incidents

class Responder:
    def __init__(self):
        self.playbooks = {
            "error_spike": ["rollback_model", "block_traffic", "notify_oncall"],
            "latency_spike": ["check_model_server", "scale_up", "check_context_size"],
            "quality_degradation": ["rollback_prompt", "rollback_model", "run_eval_suite"],
            "cost_anomaly": ["investigate_model_routing", "check_for_retry_storm", "check_prompt_size"],
        }

    def respond(self, incident):
        actions = self.playbooks.get(incident.type, ["notify_oncall"])
        for action in actions:
            incident.add_event("action", f"Executing: {action}")
            if action == "rollback_model":
                incident.add_event("containment", "Model rolled back to previous version")
            elif action == "block_traffic":
                incident.add_event("containment", "Traffic blocked to affected endpoint")
            elif action == "rollback_prompt":
                incident.add_event("containment", "Prompt reverted to previous version")
        if incident.severity in ("SEV-1", "SEV-2"):
            incident.add_event("notification", "On-call engineer paged")

class PostMortem:
    def __init__(self, incident):
        self.incident = incident
        self.root_cause = ""
        self.action_items = []

    def analyze(self):
        if self.incident.type == "quality_degradation":
            self.root_cause = "Prompt template v4 removed grounding instruction for financial topics"
            self.action_items = [
                ("P0", "Add regression test for financial hallucination"),
                ("P1", "Add automated guardrail for financial topic accuracy"),
                ("P2", "Implement canary gate checking hallucination rate"),
            ]
        elif self.incident.type == "error_spike":
            self.root_cause = "Model server ran out of memory due to context growth"
            self.action_items = [
                ("P0", "Add context window limit enforcement"),
                ("P1", "Add OOM monitoring to alerting"),
                ("P2", "Implement circuit breaker for large contexts"),
            ]
        elif self.incident.type == "latency_spike":
            self.root_cause = "Upstream vector DB latency increased due to missing index"
            self.action_items = [
                ("P0", "Add vector DB latency monitoring"),
                ("P1", "Implement query timeout with fallback"),
                ("P2", "Add index health check to CI/CD"),
            ]
        else:
            self.root_cause = "Under investigation"
            self.action_items = [("P1", "Investigate root cause"), ("P2", "Add monitoring for this scenario")]

    def report(self):
        return {
            "incident_id": self.incident.id,
            "severity": self.incident.severity,
            "root_cause": self.root_cause,
            "action_items": [f"[{p}] {a}" for p, a in self.action_items],
        }

detector = IncidentDetector()

print("=== Incident Detection Scenarios ===")
scenarios = [
    {"error_rate": 0.031, "p95_latency_ms": 1200, "hallucination_rate": 0.01, "cost_spike": 1.1},
    {"error_rate": 0.01, "p95_latency_ms": 4500, "hallucination_rate": 0.02, "cost_spike": 1.0},
    {"error_rate": 0.005, "p95_latency_ms": 800, "hallucination_rate": 0.12, "cost_spike": 1.0},
    {"error_rate": 0.01, "p95_latency_ms": 600, "hallucination_rate": 0.01, "cost_spike": 3.5},
]

for i, metrics in enumerate(scenarios, 1):
    incidents = detector.evaluate_metrics(metrics)
    print(f"  Scenario {i}:")
    for inc in incidents:
        responder = Responder()
        responder.respond(inc)
        pm = PostMortem(inc)
        pm.analyze()
        inc.resolve()
        r = inc.report()
        print(f"    [{r['severity']}] {r['type']}: {r['description']}")
        print(f"    Duration: {r['duration_min']}min | Events: {r['events']}")
        print(f"    Timeline:")
        for event in inc.timeline[:3]:
            dt = datetime.fromtimestamp(event["time"]).strftime("%H:%M:%S")
            print(f"      {dt} [{event['action']}] {event['detail'][:70]}")
        pmr = pm.report()
        print(f"    Root cause: {pmr['root_cause']}")
        for ai in pmr["action_items"]:
            print(f"      Action: {ai}")
        print()
