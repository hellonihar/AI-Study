"""
Model registry: versioning for models, prompts, datasets with lineage tracking.

Run: python 05-model-registry.py

Requirements: numpy
"""

import time
import json
import hashlib

print("=== Model & Prompt Registry ===\n")

class RegistryEntry:
    def __init__(self, artifact_type, name, version, metadata, parent=None):
        self.artifact_type = artifact_type
        self.name = name
        self.version = version
        self.metadata = metadata
        self.parent = parent
        self.created = time.time()
        self.id = hashlib.md5(f"{name}{version}{self.created}".encode()).hexdigest()[:12]
        self.stage = "registered"

class ArtifactRegistry:
    def __init__(self):
        self.entries = []
        self.stages = ["registered", "staging", "canary", "production", "deprecated", "archived"]

    def register(self, artifact_type, name, version, metadata, parent=None):
        entry = RegistryEntry(artifact_type, name, version, metadata, parent)
        self.entries.append(entry)
        return entry

    def promote(self, entry_id, target_stage):
        for e in self.entries:
            if e.id == entry_id:
                if target_stage in self.stages:
                    old_stage = e.stage
                    e.stage = target_stage
                    return {"success": True, "id": e.id, "from": old_stage, "to": target_stage}
                return {"success": False, "error": f"Invalid stage: {target_stage}"}
        return {"success": False, "error": "Entry not found"}

    def get_by_stage(self, stage):
        return [e for e in self.entries if e.stage == stage]

    def get_lineage(self, entry_id):
        lineage = []
        current = None
        for e in self.entries:
            if e.id == entry_id:
                current = e
                break
        if not current:
            return lineage
        while current:
            lineage.append({
                "id": current.id,
                "type": current.artifact_type,
                "name": current.name,
                "version": current.version,
                "stage": current.stage,
            })
            if current.parent:
                parent_id = current.parent
                current = None
                for e in self.entries:
                    if e.id == parent_id:
                        current = e
                        break
            else:
                current = None
        return lineage

    def compare_versions(self, artifact_type, name, versions):
        entries = [e for e in self.entries if e.artifact_type == artifact_type and e.name == name and e.version in versions]
        result = {}
        for e in entries:
            result[e.version] = {
                "stage": e.stage,
                "metrics": {k: v for k, v in e.metadata.items() if k in ["accuracy", "latency_p50", "cost_per_request"]},
            }
        return result

registry = ArtifactRegistry()

print("=== Registering Models ===")
models = [
    ("model", "llama-3-8b", "1.0.0", {"base": "meta-llama/Llama-3-8B", "accuracy": 0.72, "latency_p50": 45}),
    ("model", "llama-3-8b", "2.0.0", {"base": "meta-llama/Llama-3-8B", "accuracy": 0.78, "latency_p50": 48, "method": "LoRA r=8"}),
    ("model", "llama-3-8b", "2.1.0", {"base": "meta-llama/Llama-3-8B", "accuracy": 0.81, "latency_p50": 50, "method": "LoRA r=16"}),
    ("model", "gpt-4o-mini", "1.0.0", {"provider": "openai", "accuracy": 0.88, "latency_p50": 320, "cost_per_request": 0.0008}),
]
parent_id = None
for i, (typ, name, ver, meta) in enumerate(models):
    entry = registry.register(typ, name, ver, meta, parent=parent_id)
    parent_id = entry.id
    print(f"  [{entry.stage}] {name}:{ver} (id={entry.id})")

print()

print("=== Promoting to Production ===")
promotions = [
    ("llama-3-8b", "2.1.0", "staging"),
    ("llama-3-8b", "2.1.0", "production"),
    ("gpt-4o-mini", "1.0.0", "production"),
]
for name, ver, stage in promotions:
    for e in registry.entries:
        if e.name == name and e.version == ver:
            result = registry.promote(e.id, stage)
            print(f"  {name}:{ver} -> {stage}: {'OK' if result['success'] else result['error']}")
            break

print()

print("=== Registering Prompts ===")
prompts = [
    ("prompt", "chat-system", "1.0.0", {"tokens": 120, "temperature": 0.3, "relevance": 0.85}),
    ("prompt", "chat-system", "1.1.0", {"tokens": 95, "temperature": 0.3, "relevance": 0.89}),
    ("prompt", "search-rewrite", "1.0.0", {"tokens": 80, "temperature": 0.1, "relevance": 0.82}),
]
for typ, name, ver, meta in prompts:
    entry = registry.register(typ, name, ver, meta)
    print(f"  [{entry.stage}] {name}:{ver} (tokens={meta.get('tokens')})")

print()

print("=== Lineage Tracking ===")
model_entry = None
for e in registry.entries:
    if e.name == "llama-3-8b" and e.version == "2.1.0":
        model_entry = e
        break
if model_entry:
    lineage = registry.get_lineage(model_entry.id)
    print(f"  Lineage for {model_entry.name}:{model_entry.version}:")
    for l in lineage:
        print(f"    {l['type']:8s} {l['name']:<20} {l['version']:<8} [{l['stage']}]")

print()

print("=== Version Comparison ===")
comparison = registry.compare_versions("model", "llama-3-8b", ["1.0.0", "2.0.0", "2.1.0"])
for ver, data in comparison.items():
    print(f"  {ver}: stage={data['stage']}, metrics={data['metrics']}")
