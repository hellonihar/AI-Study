"""
Schema evolution: handle changing data structures across pipeline versions.

Run: python 04-schema-evolution.py

Requirements: none (stdlib only)
"""

import json
from datetime import datetime

print("=== Schema Evolution Demo ===\n")

SCHEMA_V1 = {
    "version": 1,
    "fields": ["id", "name", "email"],
    "types": {"id": "int", "name": "str", "email": "str"},
}

SCHEMA_V2 = {
    "version": 2,
    "fields": ["id", "full_name", "email", "phone"],
    "types": {"id": "int", "full_name": "str", "email": "str", "phone": "str"},
    "changes": [
        {"type": "rename", "from": "name", "to": "full_name"},
        {"type": "add", "field": "phone"},
    ],
}

SCHEMA_V3 = {
    "version": 3,
    "fields": ["id", "full_name", "email", "phone", "status"],
    "types": {"id": "int", "full_name": "str", "email": "str", "phone": "str", "status": "str"},
    "changes": [
        {"type": "add", "field": "status", "default": "active"},
    ],
}

print("Available schemas:")
for s in [SCHEMA_V1, SCHEMA_V2, SCHEMA_V3]:
    print(f"  v{s['version']}: fields={s['fields']}")

class SchemaRegistry:
    def __init__(self):
        self.schemas = {}

    def register(self, schema):
        self.schemas[schema["version"]] = schema

    def get(self, version):
        return self.schemas.get(version)

    def latest(self):
        return max(self.schemas.values(), key=lambda s: s["version"])

    def can_upgrade(self, from_ver, to_ver):
        current = self.schemas.get(from_ver)
        target = self.schemas.get(to_ver)
        if not current or not target:
            return False

        current_fields = set(current["fields"])
        target_fields = set(target["fields"])
        removed = current_fields - target_fields
        renamed_from = set()
        renamed_to = set()

        if "changes" in target:
            for change in target["changes"]:
                if change["type"] == "rename":
                    renamed_from.add(change["from"])
                    renamed_to.add(change["to"])

        effective_removed = removed - renamed_from
        return len(effective_removed) == 0

class SchemaTransformer:
    def __init__(self, registry):
        self.registry = registry

    def transform(self, record, source_version, target_version):
        if source_version == target_version:
            return record

        current_schema = self.registry.get(source_version)
        target_schema = self.registry.get(target_version)
        result = dict(record)

        for v in range(source_version + 1, target_version + 1):
            schema = self.registry.get(v)
            if not schema or "changes" not in schema:
                continue

            for change in schema["changes"]:
                if change["type"] == "rename":
                    if change["from"] in result:
                        result[change["to"]] = result.pop(change["from"])
                elif change["type"] == "add":
                    if change["field"] not in result:
                        result[change["field"]] = change.get("default", None)

        result["_schema_version"] = target_version
        result["_transformed_at"] = datetime.utcnow().isoformat()
        return result

registry = SchemaRegistry()
for s in [SCHEMA_V1, SCHEMA_V2, SCHEMA_V3]:
    registry.register(s)

transformer = SchemaTransformer(registry)

sample_v1_records = [
    {"id": 1, "name": "Alice", "email": "alice@co.com"},
    {"id": 2, "name": "Bob", "email": "bob@co.com"},
]

print(f"\n{'='*60}")
print("Schema Migration: v1 → v2")
print(f"{'='*60}")
is_compat = registry.can_upgrade(1, 2)
print(f"Backward compatible: {is_compat}")

for record in sample_v1_records:
    transformed = transformer.transform(record, 1, 2)
    print(f"  v1: {record}")
    print(f"  v2: {transformed}")
    print()

print(f"{'='*60}")
print("Schema Migration: v2 → v3")
print(f"{'='*60}")
is_compat = registry.can_upgrade(2, 3)
print(f"Backward compatible: {is_compat}")

v2_records = [
    {"id": 1, "full_name": "Alice", "email": "alice@co.com", "phone": "555-0100"},
    {"id": 3, "full_name": "Charlie", "email": "charlie@co.com", "phone": "555-0300"},
]

for record in v2_records:
    transformed = transformer.transform(record, 2, 3)
    print(f"  v2: {record}")
    print(f"  v3: {transformed}")
    print()

print(f"{'='*60}")
print("Embedding Input Stability")
print(f"{'='*60}")

def format_for_embedding(record, template_version):
    if template_version == 1:
        return f"Customer: {record.get('name', record.get('full_name', ''))} | Email: {record['email']}"
    elif template_version == 2:
        return f"Customer: {record['full_name']} | Email: {record['email']} | Phone: {record.get('phone', 'N/A')}"

v1_record = {"id": 1, "name": "Alice", "email": "alice@co.com"}
v3_record = transformer.transform(v1_record, 1, 3)

template_v1 = format_for_embedding(v1_record, 1)
template_v2 = format_for_embedding(v3_record, 2)

print(f"  Original:   {template_v1}")
print(f"  After v3:   {template_v2}")
print()
print("  NOTE: Embedding input changed → vectors will differ → rerieval may break")
print("  Action: Always test embedding stability when templates change.")
print("  See 01-theory/05-schema-evolution.md for full guidance.")
