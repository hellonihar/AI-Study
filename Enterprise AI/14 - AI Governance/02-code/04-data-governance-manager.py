"""
Data governance manager: consent management, retention, right-to-deletion.

Run: python 04-data-governance-manager.py

Requirements: numpy
"""

import time
import json
import hashlib
from collections import defaultdict

print("=== Data Governance Manager ===\n")

class ConsentRecord:
    def __init__(self, user_id, purpose, granted=True):
        self.user_id = user_id
        self.purpose = purpose
        self.granted = granted
        self.timestamp = time.time()
        self.consent_id = hashlib.md5(f"{user_id}{purpose}{time.time()}".encode()).hexdigest()[:16]

class ConsentManager:
    def __init__(self):
        self.records = []

    def grant_consent(self, user_id, purpose):
        record = ConsentRecord(user_id, purpose, True)
        self.records.append(record)
        return record

    def revoke_consent(self, user_id, purpose):
        record = ConsentRecord(user_id, purpose, False)
        self.records.append(record)
        return record

    def check_consent(self, user_id, purpose):
        user_records = [r for r in self.records if r.user_id == user_id and r.purpose == purpose]
        if not user_records:
            return False
        return user_records[-1].granted

    def get_user_consents(self, user_id):
        consents = defaultdict(list)
        for r in self.records:
            if r.user_id == user_id:
                consents[r.purpose].append({"granted": r.granted, "timestamp": r.timestamp})
        return dict(consents)

class RetentionPolicy:
    def __init__(self, data_type, max_days, action="delete"):
        self.data_type = data_type
        self.max_days = max_days
        self.action = action

    def is_expired(self, created_at):
        age_days = (time.time() - created_at) / 86400
        return age_days > self.max_days

class RetentionManager:
    def __init__(self):
        self.policies = {}
        self.data_records = []

    def add_policy(self, data_type, max_days, action="delete"):
        self.policies[data_type] = RetentionPolicy(data_type, max_days, action)

    def add_record(self, data_type, user_id, created_at=None):
        record = {
            "id": hashlib.md5(f"{data_type}{user_id}{time.time()}".encode()).hexdigest()[:12],
            "data_type": data_type,
            "user_id": user_id,
            "created_at": created_at or time.time(),
        }
        self.data_records.append(record)
        return record

    def find_expired(self):
        expired = []
        for record in self.data_records:
            policy = self.policies.get(record["data_type"])
            if policy and policy.is_expired(record["created_at"]):
                expired.append(record)
        return expired

    def delete_records(self, records):
        ids_to_delete = {r["id"] for r in records}
        self.data_records = [r for r in self.data_records if r["id"] not in ids_to_delete]
        return len(ids_to_delete)

class DeletionRequest:
    def __init__(self, user_id):
        self.user_id = user_id
        self.requested_at = time.time()
        self.request_id = hashlib.md5(f"deletion_{user_id}_{time.time()}".encode()).hexdigest()[:12]
        self.status = "pending"
        self.completed_steps = []

class DeletionManager:
    def __init__(self, consent_mgr, retention_mgr):
        self.consent_mgr = consent_mgr
        self.retention_mgr = retention_mgr
        self.requests = []

    def request_deletion(self, user_id):
        req = DeletionRequest(user_id)
        self.requests.append(req)
        return req

    def process_deletion(self, request):
        steps = [
            ("Revoking all consents", self._revoke_consents),
            ("Marking data for deletion", self._mark_data),
            ("Removing from active datasets", self._remove_active),
            ("Scheduling model retraining", self._schedule_retrain),
            ("Confirming deletion", self._confirm),
        ]
        for step_name, step_fn in steps:
            step_fn(request)
            request.completed_steps.append(step_name)
        request.status = "completed"
        return request

    def _revoke_consents(self, request):
        pass

    def _mark_data(self, request):
        pass

    def _remove_active(self, request):
        expired = self.retention_mgr.find_expired()
        self.retention_mgr.delete_records(expired)

    def _schedule_retrain(self, request):
        pass

    def _confirm(self, request):
        request.completed_at = time.time()

print("=== Consent Management ===")
consent_mgr = ConsentManager()
consent_mgr.grant_consent("user_001", "model_training")
consent_mgr.grant_consent("user_001", "personalization")
consent_mgr.grant_consent("user_002", "model_training")

print(f"  user_001 consent for training: {consent_mgr.check_consent('user_001', 'model_training')}")
print(f"  user_001 consent for marketing: {consent_mgr.check_consent('user_001', 'marketing')}")

consent_mgr.revoke_consent("user_001", "personalization")
print(f"  user_001 consent for personalization after revoke: {consent_mgr.check_consent('user_001', 'personalization')}")
print()

print("=== Retention Management ===")
retention_mgr = RetentionManager()
retention_mgr.add_policy("training_logs", 730)
retention_mgr.add_policy("inference_logs", 90)
retention_mgr.add_policy("user_feedback", 365)

old_time = time.time() - (800 * 86400)
retention_mgr.add_record("training_logs", "user_001", old_time)
retention_mgr.add_record("inference_logs", "user_001", time.time() - 10 * 86400)
retention_mgr.add_record("user_feedback", "user_002", old_time)

expired = retention_mgr.find_expired()
print(f"  Expired records found: {len(expired)}")
for e in expired:
    age_days = (time.time() - e["created_at"]) / 86400
    print(f"    {e['data_type']} for {e['user_id']} ({age_days:.0f} days old)")
deleted = retention_mgr.delete_records(expired)
print(f"  Deleted: {deleted}")
print(f"  Remaining records: {len(retention_mgr.data_records)}")
print()

print("=== Right to Deletion ===")
deletion_mgr = DeletionManager(consent_mgr, retention_mgr)
req = deletion_mgr.request_deletion("user_001")
result = deletion_mgr.process_deletion(req)
print(f"  Request {result.request_id}: {result.status}")
print(f"  Steps completed: {len(result.completed_steps)}")
for step in result.completed_steps:
    print(f"    - {step}")
