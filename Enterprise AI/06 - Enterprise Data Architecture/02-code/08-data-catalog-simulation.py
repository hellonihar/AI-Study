"""
Data catalog simulation: discover, register, and query data assets.

Run: python 08-data-catalog-simulation.py

Requirements: none (stdlib only)
"""

import json
from datetime import datetime

print("=== Data Catalog Simulation ===\n")

class DataAsset:
    def __init__(self, name, asset_type, source, schema, description, owner, tags=None):
        self.name = name
        self.type = asset_type
        self.source = source
        self.schema = schema
        self.description = description
        self.owner = owner
        self.tags = tags or []
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = self.created_at
        self.lineage = []

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "source": self.source,
            "schema": self.schema,
            "description": self.description,
            "owner": self.owner,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "lineage": self.lineage,
        }

class DataCatalog:
    def __init__(self):
        self.assets = {}

    def register(self, asset):
        self.assets[asset.name] = asset
        print(f"  Registered: [{asset.type}] {asset.name} (owner: {asset.owner})")

    def search(self, query):
        query = query.lower()
        results = []
        for name, asset in self.assets.items():
            if (query in name.lower() or
                query in asset.description.lower() or
                any(query in tag.lower() for tag in asset.tags)):
                results.append(asset)
        return results

    def get_lineage(self, asset_name):
        asset = self.assets.get(asset_name)
        if not asset:
            return []
        return asset.lineage

    def list_by_type(self, asset_type):
        return [a for a in self.assets.values() if a.type == asset_type]

    def list_by_owner(self, owner):
        return [a for a in self.assets.values() if a.owner.lower() == owner.lower()]

catalog = DataCatalog()

print("Registering data assets...\n")

assets = [
    DataAsset("customers_raw", "table", "postgresql://prod-db:5432/orders",
              {"columns": ["id", "name", "email", "phone", "status", "created_at"]},
              "Raw customer data from production database",
              "data-engineering", tags=["pii", "customer", "core"]),

    DataAsset("orders_raw", "table", "postgresql://prod-db:5432/orders",
              {"columns": ["id", "customer_id", "total", "status", "created_at"]},
              "Raw order data from production database",
              "data-engineering", tags=["customer", "core"]),

    DataAsset("customer_chunks", "dataset", "delta-lake://data/chunks/customer_360",
              {"columns": ["chunk_id", "doc_id", "text", "embedding", "metadata"]},
              "Chunked and embedded customer data for RAG",
              "ai-platform", tags=["rag", "embedding", "customer"]),

    DataAsset("customer_embeddings", "vector_index", "qdrant://cluster/customer_360",
              {"dimension": 768, "distance": "cosine", "vectors": 50000},
              "Qdrant collection: customer 360 vectors",
              "ai-platform", tags=["vector-db", "qdrant"]),

    DataAsset("product_catalog", "dataset", "delta-lake://data/chunks/products",
              {"columns": ["chunk_id", "product_id", "text", "embedding"]},
              "Product catalog chunks for product search RAG",
              "product-team", tags=["rag", "product", "search"]),

    DataAsset("customer_features", "feature_table", "delta-lake://features/customer",
              {"columns": ["customer_id", "order_count", "total_revenue", "avg_order_value"]},
              "Customer features for ML model training",
              "ml-platform", tags=["ml", "features", "training"]),
]

for asset in assets:
    catalog.register(asset)

print(f"\n{'='*60}")
print("Search: 'customer'")
print(f"{'='*60}")
results = catalog.search("customer")
for r in results:
    print(f"  [{r.type}] {r.name:<30} {r.description[:40]}")

print(f"\n{'='*60}")
print("Search: 'rag'")
print(f"{'='*60}")
results = catalog.search("rag")
for r in results:
    print(f"  [{r.type}] {r.name:<30} {r.description[:40]}")

print(f"\n{'='*60}")
print("All Assets by Type")
print(f"{'='*60}")
for asset_type in sorted(set(a.type for a in catalog.assets.values())):
    type_assets = catalog.list_by_type(asset_type)
    print(f"\n  {asset_type}s:")
    for a in type_assets:
        print(f"    • {a.name:<30} (owner: {a.owner}, tags: {', '.join(a.tags)})")

print(f"\n{'='*60}")
print("Relationship: RAG Pipeline Data Flow")
print(f"{'='*60}")

rag_flow = [
    "customers_raw",
    "orders_raw",
    "customer_chunks",
    "customer_embeddings",
]

for i, name in enumerate(rag_flow):
    asset = catalog.assets.get(name)
    if asset:
        arrow = "  ↓  " if i < len(rag_flow) - 1 else "     "
        print(f"  {arrow} [{asset.type}] {asset.name:<30}")
        if i < len(rag_flow) - 1:
            print(f"  │    transform+embed")
