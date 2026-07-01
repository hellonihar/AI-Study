"""
Data lineage simulation: track data from source through transforms to consumption.

Run: python 05-data-lineage-simulation.py

Requirements: none (stdlib only)
"""

import json
import uuid
from datetime import datetime

print("=== Data Lineage Tracking ===\n")

class LineageNode:
    def __init__(self, node_id, node_type, name, metadata=None):
        self.id = node_id
        self.type = node_type
        self.name = name
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat()

class LineageEdge:
    def __init__(self, source_id, dest_id, transform, metadata=None):
        self.source_id = source_id
        self.dest_id = dest_id
        self.transform = transform
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat()

class LineageGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = []

    def add_node(self, node):
        self.nodes[node.id] = node

    def add_edge(self, edge):
        self.edges.append(edge)

    def trace_backward(self, node_id):
        path = []
        visited = set()
        current = node_id

        while current and current not in visited:
            visited.add(current)
            node = self.nodes.get(current)
            if not node:
                break
            path.append(node)

            incoming = [e for e in self.edges if e.dest_id == current]
            if not incoming:
                break
            current = incoming[0].source_id

        return list(reversed(path))

    def trace_forward(self, node_id):
        path = []
        queue = [node_id]
        visited = set()

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            node = self.nodes.get(current)
            if node:
                path.append(node)

            outgoing = [e for e in self.edges if e.source_id == current]
            for edge in outgoing:
                queue.append(edge.dest_id)

        return path

graph = LineageGraph()

source = LineageNode("src-1", "postgresql", "prod-db.customers",
                     {"table": "customers", "host": "prod-db.internal"})
graph.add_node(source)

cdc = LineageNode("cdc-1", "debezium", "CDC Pipeline v2.1",
                  {"connector": "debezium-postgres", "offset": "lsn:12345"})
graph.add_node(cdc)

kafka = LineageNode("kafka-1", "kafka", "topic: customer_events",
                    {"partition": 3, "retention_days": 7})
graph.add_node(kafka)

transform = LineageNode("tfm-1", "python", "Transform: Format for Embedding v1.2",
                        {"code_hash": "sha256:abcd1234", "template": "customer_360_v2"})
graph.add_node(transform)

embed = LineageNode("emb-1", "embedding", "BGE-base v1.0",
                    {"dimension": 768, "model": "BAAI/bge-base-en-v1.5"})
graph.add_node(embed)

vector_db = LineageNode("vdb-1", "qdrant", "Qdrant: customer_360",
                        {"collection": "customer_360", "shards": 3, "replication": 2})
graph.add_node(vector_db)

rag_query = LineageNode("rag-1", "rag_query", "RAG Query: 'What is customer status?'",
                        {"user_id": "user-42", "timestamp": datetime.utcnow().isoformat()})
graph.add_node(rag_query)

graph.add_edge(LineageEdge("src-1", "cdc-1", "CDC capture (WAL)"))
graph.add_edge(LineageEdge("cdc-1", "kafka-1", "Produce to topic"))
graph.add_edge(LineageEdge("kafka-1", "tfm-1", "Consume + transform"))
graph.add_edge(LineageEdge("tfm-1", "emb-1", "Generate embedding"))
graph.add_edge(LineageEdge("emb-1", "vdb-1", "Index in vector DB"))
graph.add_edge(LineageEdge("vdb-1", "rag-1", "Retrieve for RAG"))

print("Lineage Graph:")
print(f"{'Node ID':<12} {'Type':<15} {'Name':<40}")
print("-" * 67)
for node_id, node in graph.nodes.items():
    print(f"{node_id:<12} {node.type:<15} {node.name:<40}")

print(f"\n{'='*60}")
print("Forward Trace: Source → Query")
print(f"{'='*60}")
forward = graph.trace_forward("src-1")
for i, node in enumerate(forward):
    arrow = "  ↓  " if i < len(forward) - 1 else "     "
    print(f"  {arrow} [{node.type}] {node.name}")

print(f"\n{'='*60}")
print("Backward Trace: Query → Source")
print(f"{'='*60}")
backward = graph.trace_backward("rag-1")
for i, node in enumerate(backward):
    arrow = "  ↓  " if i < len(backward) - 1 else "     "
    print(f"  {arrow} [{node.type}] {node.name}")

print(f"\n{'='*60}")
print("Lineage for Debugging")
print(f"{'='*60}")

scenarios = [
    ("RAG returns stale customer data", "rag-1",
     "Check: CDC pipeline freshness → kafka-1 lag → cdc-1 checkpoint"),
    ("Embedding quality degraded", "emb-1",
     "Check: model version → tfm-1 template change → src-1 schema change"),
    ("Data missing for customer 42", "vdb-1",
     "Check: src-1 has record? → cdc-1 captured it? → tfm-1 transformed it?"),
]

for problem, node_id, investigation in scenarios:
    print(f"\nProblem: {problem}")
    trace = graph.trace_backward(node_id)
    print(f"  Trace: {' → '.join(n.id for n in trace)}")
    print(f"  {investigation}")

print(f"\n{'='*60}")
print("Lineage Metadata (JSON)")
print(f"{'='*60}")
for edge in graph.edges[-3:]:
    print(json.dumps({
        "source": edge.source_id,
        "destination": edge.dest_id,
        "transform": edge.transform,
        "timestamp": edge.timestamp,
    }, indent=2))
