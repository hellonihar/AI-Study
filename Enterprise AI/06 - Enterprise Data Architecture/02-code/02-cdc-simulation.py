"""
CDC simulation: capture changes from a simulated source database.

Run: python 02-cdc-simulation.py

Requirements: pip install numpy
"""

import time
import json
import random
import uuid
from datetime import datetime, timedelta

print("=== Change Data Capture (CDC) Simulation ===\n")

class SimulatedSourceDB:
    def __init__(self):
        self.records = {}
        self._seed_data()

    def _seed_data(self):
        for i in range(5):
            record_id = f"CUST-{1000 + i}"
            self.records[record_id] = {
                "id": record_id,
                "name": f"Customer {i}",
                "email": f"customer{i}@co.com",
                "status": "active",
                "updated_at": datetime.utcnow().isoformat(),
            }

    def get_changes_since(self, timestamp):
        changes = []
        for record_id, record in self.records.items():
            if record["updated_at"] > timestamp:
                changes.append(record)
        return changes

    def update_record(self):
        if not self.records:
            return None
        record_id = random.choice(list(self.records.keys()))
        field = random.choice(["name", "email", "status"])
        if field == "name":
            self.records[record_id]["name"] = f"Updated-{random.randint(1, 999)}"
        elif field == "email":
            self.records[record_id]["email"] = f"updated{random.randint(1,999)}@co.com"
        elif field == "status":
            self.records[record_id]["status"] = random.choice(["active", "inactive", "suspended"])
        self.records[record_id]["updated_at"] = datetime.utcnow().isoformat()
        return self.records[record_id]

    def insert_record(self):
        record_id = f"CUST-{random.randint(2000, 9999)}"
        record = {
            "id": record_id,
            "name": f"New Customer {random.randint(1, 999)}",
            "email": f"new{random.randint(1,999)}@co.com",
            "status": "active",
            "updated_at": datetime.utcnow().isoformat(),
        }
        self.records[record_id] = record
        return record

    def delete_record(self):
        if len(self.records) > 3:
            record_id = random.choice(list(self.records.keys()))
            record = self.records.pop(record_id)
            record["_deleted"] = True
            return record
        return None

class CDCPipeline:
    def __init__(self, source_db):
        self.source_db = source_db
        self.checkpoint = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        self.changelog = []

    def poll(self):
        changes = self.source_db.get_changes_since(self.checkpoint)
        for change in changes:
            change["_captured_at"] = datetime.utcnow().isoformat()
            change["_op_type"] = "DELETE" if change.get("_deleted") else "UPSERT"
            self.changelog.append(change)

        if changes:
            self.checkpoint = max(c["updated_at"] for c in changes)
        return changes

    def get_pending_changes(self):
        return [c for c in self.changelog if not c.get("_processed")]

    def mark_processed(self, change_ids):
        for c in self.changelog:
            if c["id"] in change_ids:
                c["_processed"] = True

db = SimulatedSourceDB()
pipeline = CDCPipeline(db)

print("Simulating CDC over 5 polling cycles...\n")

for cycle in range(1, 6):
    print(f"\n--- Cycle {cycle} ---")
    time.sleep(0.3)

    if random.random() < 0.6:
        updated = db.update_record()
        print(f"  UPDATE: {updated['id']} - {updated['name']}")
    if random.random() < 0.3:
        inserted = db.insert_record()
        print(f"  INSERT: {inserted['id']} - {inserted['name']}")
    if random.random() < 0.2:
        deleted = db.delete_record()
        if deleted:
            print(f"  DELETE: {deleted['id']}")

    changes = pipeline.poll()
    print(f"  Poll result: {len(changes)} changes detected "
          f"(checkpoint: {pipeline.checkpoint[:19]})")

print(f"\n{'='*50}")
print(f"Total changes captured: {len(pipeline.changelog)}")
print(f"{'='*50}")
print(f"\n{'ID':<15} {'Operation':<10} {'Captured At':<25}")
print("-" * 50)
for c in pipeline.changelog[-10:]:
    op = c.get("_op_type", "UNKNOWN")
    cap_time = c["_captured_at"][:19]
    print(f"{c['id']:<15} {op:<10} {cap_time:<25}")

print("\n=== CDC Pipeline Components ===")
print("Source DB:    Simulated PostgreSQL (WAL-based CDC)")
print("Capture:      Debezium / poll-based checkpoint")
print("Transport:    Kafka / change log in memory")
print("Sink:         Apply to vector DB / data lake")
print()
print("Key CDC considerations for production:")
print("  1. Schema changes in source → Kafka schema registry")
print("  2. Exactly-once vs at-least-once delivery semantics")
print("  3. Backfill: re-process all changes from checkpoint")
print("  4. Dead letter queue for failed transformations")
