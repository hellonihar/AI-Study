"""
Security audit logger: immutable audit trail for AI security events.

Run: python 09-security-audit-logger.py

Requirements: hashlib (stdlib)
"""

import time
import hashlib
import json

print("=== Security Audit Logger ===\n")

class AuditEvent:
    def __init__(self, event_type, user_id, details, severity="info"):
        self.timestamp = time.time()
        self.event_id = hashlib.sha256(f"{self.timestamp}{user_id}{event_type}".encode()).hexdigest()[:16]
        self.event_type = event_type
        self.user_id = user_id
        self.severity = severity
        self.details = details

    def to_dict(self):
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "user_id": self.user_id,
            "severity": self.severity,
            "details": self.details,
        }

class AuditLogger:
    def __init__(self):
        self.events = []
        self.chain = []
        self.previous_hash = "0" * 64

    def log(self, event_type, user_id, details, severity="info"):
        event = AuditEvent(event_type, user_id, details, severity)

        event_data = json.dumps(event.to_dict(), sort_keys=True)
        current_hash = hashlib.sha256(
            (self.previous_hash + event_data).encode()
        ).hexdigest()

        entry = {
            "event": event.to_dict(),
            "previous_hash": self.previous_hash,
            "hash": current_hash,
        }

        self.events.append(event)
        self.chain.append(entry)
        self.previous_hash = current_hash

        return event.event_id

    def verify_chain(self):
        for i, entry in enumerate(self.chain):
            expected_hash = hashlib.sha256(
                (entry["previous_hash"] + json.dumps(entry["event"], sort_keys=True)).encode()
            ).hexdigest()
            if expected_hash != entry["hash"]:
                return False, f"Chain broken at index {i}"
            if i > 0 and entry["previous_hash"] != self.chain[i-1]["hash"]:
                return False, f"Hash mismatch at index {i}"
        return True, "Chain intact"

    def get_events_by_severity(self, severity):
        return [e for e in self.events if e.severity == severity]

    def generate_report(self):
        print(f"Audit Log Report")
        print(f"  Total events: {len(self.events)}")
        print(f"  Chain integrity: {self.verify_chain()[1]}")

        severity_counts = {}
        event_counts = {}
        for event in self.events:
            severity_counts[event.severity] = severity_counts.get(event.severity, 0) + 1
            event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1

        print(f"  Events by severity: {severity_counts}")
        print(f"  Events by type:    {event_counts}")
        print()

        for event in self.events[-10:]:
            print(f"  [{event.severity.upper():>7}] {event.event_type:25s} | "
                  f"user={event.user_id:12s} | {event.details}")

logger = AuditLogger()

logger.log("input_guardrail", "user_abc123", {"action": "block", "reason": "jailbreak_detected", "score": 0.87}, "warning")
logger.log("input_guardrail", "user_def456", {"action": "pass", "reason": "clean", "score": 0.02}, "info")
logger.log("output_guardrail", "user_abc123", {"action": "flag", "reason": "pii_detected", "pii_types": ["email"]}, "warning")
logger.log("auth_login", "system", {"ip": "192.168.1.1", "status": "success"}, "info")
logger.log("auth_login", "unknown_user", {"ip": "10.0.0.99", "status": "failed", "reason": "invalid_key"}, "warning")
logger.log("rate_limit", "user_ghi789", {"action": "block", "requests_per_minute": 65, "limit": 60}, "warning")
logger.log("red_team_test", "security_team", {"attack_type": "prompt_injection", "blocked": False, "score": 0.32}, "critical")
logger.log("model_deploy", "ml_team", {"model": "llama-3-8b-v2", "target": "production", "version": "2.1.0"}, "info")
logger.log("guardrail_update", "ml_team", {"layer": "jailbreak", "model_version": "v3", "reason": "red_team_finding"}, "info")
logger.log("pii_leak_attempt", "user_jkl012", {"action": "blocked", "pii_type": "ssn", "context": "output_filter"}, "critical")
logger.log("input_guardrail", "user_mno345", {"action": "pass", "reason": "clean", "score": 0.01}, "info")
logger.log("auth_logout", "user_abc123", {"session_duration": 3402}, "info")

print("Recent Audit Events:\n")
logger.generate_report()

chain_valid, chain_msg = logger.verify_chain()
print(f"\nChain Verification: {chain_msg}")
print(f"Chain length: {len(logger.chain)} entries")
