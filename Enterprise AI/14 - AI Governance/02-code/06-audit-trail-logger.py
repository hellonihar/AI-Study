"""
Audit trail logger: immutable, tamper-evident logging for compliance.

Run: python 06-audit-trail-logger.py

Requirements: hashlib, json
"""

import time
import json
import hashlib

print("=== Audit Trail Logger ===\n")

class AuditEntry:
    def __init__(self, event_type, actor, resource, action, result, metadata=None):
        self.timestamp = time.time()
        self.event_type = event_type
        self.actor = actor
        self.resource = resource
        self.action = action
        self.result = result
        self.metadata = metadata or {}
        self.entry_hash = None
        self.previous_hash = None

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "actor": self.actor,
            "resource": self.resource,
            "action": self.action,
            "result": self.result,
            "metadata": self.metadata,
            "previous_hash": self.previous_hash,
            "entry_hash": self.entry_hash,
        }

class ImmutableAuditLog:
    def __init__(self):
        self.chain = []
        self.genesis_hash = hashlib.sha256(b"genesis").hexdigest()

    def append(self, event_type, actor, resource, action, result, metadata=None):
        entry = AuditEntry(event_type, actor, resource, action, result, metadata)
        entry.previous_hash = self.chain[-1]["entry_hash"] if self.chain else self.genesis_hash
        entry_data = json.dumps(entry.to_dict(), sort_keys=True, default=str).encode()
        entry.entry_hash = hashlib.sha256(entry_data).hexdigest()
        entry_dict = entry.to_dict()
        self.chain.append(entry_dict)
        return entry_dict

    def verify_integrity(self):
        if not self.chain:
            return True, []
        violations = []
        for i, entry in enumerate(self.chain):
            expected_prev = self.chain[i - 1]["entry_hash"] if i > 0 else self.genesis_hash
            if entry["previous_hash"] != expected_prev:
                violations.append({"index": i, "issue": "broken_chain", "entry_id": entry.get("entry_hash", "")[:12]})
            entry_copy = dict(entry)
            stored_hash = entry_copy.pop("entry_hash", None)
            entry_data = json.dumps(entry_copy, sort_keys=True, default=str).encode()
            computed_hash = hashlib.sha256(entry_data).hexdigest()
            if computed_hash != stored_hash:
                violations.append({"index": i, "issue": "tampered_entry", "entry_id": stored_hash[:12]})
        return len(violations) == 0, violations

    def query(self, event_type=None, actor=None, resource=None):
        results = self.chain
        if event_type:
            results = [e for e in results if e["event_type"] == event_type]
        if actor:
            results = [e for e in results if e["actor"] == actor]
        if resource:
            results = [e for e in results if e["resource"].get("id") == resource]
        return results

audit_log = ImmutableAuditLog()

print("=== Audit Log Entries ===")
events = [
    ("model_registration", "ml-team", {"type": "model", "id": "classifier-v2", "version": "2.0.0"}, "register", "success", {"risk_tier": "T3"}),
    ("deployment_approval", "ai-review-board", {"type": "model", "id": "classifier-v2", "version": "2.0.0"}, "approve", "success", {"approver": "john.doe@company.com", "conditions": ["bias_audit_ok", "safety_test_ok"]}),
    ("deployment", "ml-platform", {"type": "deployment", "id": "deploy-042"}, "deploy", "success", {"target": "production", "traffic_pct": 5}),
    ("deployment", "ml-platform", {"type": "deployment", "id": "deploy-042"}, "promote", "success", {"target_pct": 25}),
    ("incident", "monitoring", {"type": "incident", "id": "INC-042"}, "detect", "warning", {"severity": "SEV-2", "metric": "hallucination_rate", "value": 0.08}),
    ("incident", "on-call", {"type": "incident", "id": "INC-042"}, "respond", "success", {"action": "rollback", "rolled_back_to": "classifier-v1"}),
    ("model_retirement", "ml-team", {"type": "model", "id": "classifier-v1", "version": "1.0.0"}, "retire", "success", {"replaced_by": "classifier-v2"}),
]

for event_type, actor, resource, action, result, metadata in events:
    entry = audit_log.append(event_type, actor, resource, action, result, metadata)
    print(f"  [{entry['entry_hash'][:12]}] {event_type:<22} {action:<10} {result:<8} {resource['id']}")

print()

print("=== Integrity Verification ===")
valid, violations = audit_log.verify_integrity()
print(f"  Chain valid: {valid}")
print(f"  Total entries: {len(audit_log.chain)}")
print()

print("=== Query by Event Type ===")
deployments = audit_log.query(event_type="deployment")
print(f"  Found {len(deployments)} deployment events")
for d in deployments:
    ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(d["timestamp"]))
    print(f"    {ts} {d['action']} - {d['resource']['id']} ({d['result']})")
print()

print("=== Tamper Detection Demo ===")
tampered_log = ImmutableAuditLog()
tampered_log.append("model_registration", "ml-team", {"type": "model", "id": "test-model"}, "register", "success")
tampered_log.chain[0]["result"] = "tampered"
valid, violations = tampered_log.verify_integrity()
print(f"  After tampering: valid={valid}")
for v in violations:
    print(f"  Violation: {v['issue']} at index {v['index']}")
