"""
Delta Lake simulation: time travel, schema evolution, compaction concepts.

Run: python 09-delta-lake-simulation.py

Requirements: none (stdlib only)
"""

import json
import copy
from datetime import datetime, timedelta

print("=== Delta Lake Simulation ===\n")

class DeltaVersion:
    def __init__(self, version_id, data, schema, metadata):
        self.version_id = version_id
        self.data = data
        self.schema = schema
        self.metadata = metadata
        self.timestamp = datetime.utcnow().isoformat()

class DeltaTable:
    def __init__(self, name):
        self.name = name
        self.versions = []
        self.current_version = -1
        self.schema = []

    def get_current_data(self):
        if self.current_version < 0:
            return []
        return copy.deepcopy(self.versions[self.current_version].data)

    def write(self, data, mode="overwrite", operation="write"):
        if mode == "overwrite":
            new_data = list(data)
        elif mode == "append":
            current = self.get_current_data() if self.current_version >= 0 else []
            new_data = current + data

        version_id = len(self.versions)
        metadata = {
            "operation": operation,
            "mode": mode,
            "num_records": len(data),
            "num_bytes": len(json.dumps(data)),
        }

        version = DeltaVersion(version_id, new_data, self.schema, metadata)
        self.versions.append(version)
        self.current_version = version_id

        print(f"  v{version_id}: {operation} ({len(data)} records, mode={mode})")

    def delete(self, predicate):
        current = self.get_current_data()
        new_data = [r for r in current if not predicate(r)]

        version_id = len(self.versions)
        metadata = {
            "operation": "delete",
            "num_records_before": len(current),
            "num_records_after": len(new_data),
            "num_deleted": len(current) - len(new_data),
        }

        version = DeltaVersion(version_id, new_data, self.schema, metadata)
        self.versions.append(version)
        self.current_version = version_id
        print(f"  v{version_id}: delete (removed {len(current) - len(new_data)} records)")

    def update(self, predicate, update_fn):
        current = self.get_current_data()
        new_data = []
        updates = 0
        for r in current:
            if predicate(r):
                new_data.append(update_fn(copy.deepcopy(r)))
                updates += 1
            else:
                new_data.append(r)

        version_id = len(self.versions)
        metadata = {
            "operation": "update",
            "num_records": len(new_data),
            "num_updated": updates,
        }

        version = DeltaVersion(version_id, new_data, self.schema, metadata)
        self.versions.append(version)
        self.current_version = version_id
        print(f"  v{version_id}: update ({updates} records updated)")

    def time_travel(self, version_id):
        if 0 <= version_id < len(self.versions):
            self.current_version = version_id
            return self.versions[version_id].data
        return []

    def optimize(self):
        current = self.get_current_data()
        if not current:
            return

        version_id = len(self.versions)
        metadata = {
            "operation": "optimize",
            "num_files_before": len(current) * 2,
            "num_files_after": max(1, len(current) // 100),
            "num_records": len(current),
        }

        version = DeltaVersion(version_id, current, self.schema, metadata)
        self.versions.append(version)
        self.current_version = version_id
        print(f"  v{version_id}: optimize (compacted files)")

    def vacuum(self, retain_versions=3):
        deleted = len(self.versions) - retain_versions - 1
        if deleted > 0:
            self.versions = self.versions[-(retain_versions + 1):]
            print(f"  Vacuum: removed {deleted} old versions "
                  f"(retained {retain_versions + 1} most recent)")
        else:
            print(f"  Vacuum: nothing to remove ({len(self.versions)} versions, "
                  f"retaining {retain_versions + 1})")

    def history(self, n=5):
        for v in self.versions[-n:]:
            print(f"  v{v.version_id}: {v.metadata.get('operation', 'unknown')} "
                  f"at {v.timestamp[:19]} "
                  f"({v.metadata.get('num_records', '?')} records)")

table = DeltaTable("customer_chunks")

initial_data = [
    {"chunk_id": 1, "doc_id": "doc-1", "text": "API design guide v1"},
    {"chunk_id": 2, "doc_id": "doc-1", "text": "REST conventions"},
    {"chunk_id": 3, "doc_id": "doc-2", "text": "Deployment guide"},
]

print("1. Initial Write")
table.write(initial_data, mode="overwrite", operation="ingest")

print("\n2. Append New Chunks")
new_chunks = [
    {"chunk_id": 4, "doc_id": "doc-3", "text": "Q3 Report Q3 2024 financials"},
    {"chunk_id": 5, "doc_id": "doc-3", "text": "Revenue grew 15% YoY"},
]
table.write(new_chunks, mode="append", operation="ingest")

print("\n3. Update Chunk")
table.update(lambda r: r["chunk_id"] == 1,
             lambda r: {**r, "text": "API design guide v2 - added gRPC section"})

print("\n4. Delete Chunk")
table.delete(lambda r: r["chunk_id"] == 2)

print(f"\n{'='*60}")
print("Time Travel: v0 (initial data)")
print(f"{'='*60}")
v0_data = table.time_travel(0)
for r in v0_data:
    print(f"  {r}")

print(f"\n{'='*60}")
print("Time Travel: current state (v3)")
print(f"{'='*60}")
current = table.time_travel(3)
for r in current:
    print(f"  {r}")

print(f"\n{'='*60}")
print("Table History")
print(f"{'='*60}")
table.history()

print(f"\n{'='*60}")
print("Optimize and Vacuum")
print(f"{'='*60}")
table.optimize()
table.vacuum(retain_versions=2)
table.history()

print("\n=== Delta Lake Concepts ===")
print("ACID:    Optimistic concurrency (write-ahead log)")
print("Time travel: Query data as of any previous version")
print("Schema evolution: Add/drop columns without breaking existing data")
print("Compaction: Merge small files into larger ones (OPTIMIZE)")
print("Vacuum:   Remove old versions beyond retention window")
print()
print("For real Delta Lake, use:")
print("  pip install delta-spark  # Spark-based Delta Lake")
print("  pip install deltalake     # Native Python Delta Lake")
