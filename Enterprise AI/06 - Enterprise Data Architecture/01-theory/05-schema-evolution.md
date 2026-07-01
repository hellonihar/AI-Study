# Schema Evolution and Versioning

Managing changing data structures without breaking downstream AI pipelines.

## Why Schema Evolution Matters

AI pipelines are brittle to schema changes:
- Embedding models produce different vectors if the input format changes
- RAG prompt templates reference specific fields
- Vector DB metadata schemas are typically immutable after creation
- Training pipelines fail silently on unexpected columns

A schema change in a source system can silently break RAG retrieval quality for weeks before detection.

## Types of Schema Changes

| Change | Backward Compatible | AI Pipeline Impact | Mitigation |
|---|---|---|---|
| Add optional column | Yes | Low (ignore) | Auto-detect, pass through |
| Add required column | No | Medium (may need re-embedding) | Backfill default values |
| Remove column | No | High (broken references) | Dual-write during deprecation |
| Rename column | No | High (broken references) | Alias for transition period |
| Change data type | No | High (runtime errors) | Cast in transform layer |
| Split table/collection | No | Very high (pipeline redesign) | Merge view during transition |
| Change semantics | No | Very high (embedding shift) | Re-embed affected records |

## Schema Registry

A schema registry stores and versions all data schemas in the pipeline:

```
Schema Registry (Confluent Schema Registry or custom)
  ├── Schema v1 (2024-01-01): {"name": "customer", "fields": ["id", "name", "email"]}
  ├── Schema v2 (2024-06-01): {"name": "customer", "fields": ["id", "name", "email", "phone"]}
  └── Schema v3 (2024-12-01): {"name": "customer", "fields": ["id", "full_name", "email", "phone"]}

Compatibility checks:
  v1 → v2: BACKWARD compatible (added optional field)
  v2 → v3: NOT compatible (renamed field)
```

### Compatibility Rules

| Type | Rule | Example Allowed |
|---|---|---|
| BACKWARD | Consumers using new schema can read old data | Adding a field with default |
| FORWARD | Consumers using old schema can read new data | Adding an optional field |
| FULL | Both backward and forward compatible | Adding optional field with default |
| NONE | No compatibility required | Any change allowed |

**Recommendation:** Enforce BACKWARD compatibility for all production pipelines. This catches breaking changes before they reach vector DBs and RAG systems.

## Schema Evolution Strategies

### 1. Additive Changes (Safe)

```python
# Old schema (v1)
{"id": 1, "name": "Alice", "email": "alice@co.com"}

# New schema (v2) — added "phone"
{"id": 1, "name": "Alice", "email": "alice@co.com", "phone": null}
```

**Pipeline handling:** Add column, set null for existing records. No embedding change needed.

### 2. Rename with Alias (Transition)

```
Phase 1: Dual-write old_name + new_name (30 days)
Phase 2: Remove old_name
```

```python
def transform_record(record):
    return {
        "full_name": record.get("full_name") or record.get("name"),
        "email": record["email"],
    }
```

### 3. Type Change (Migration)

```python
# Old: "price" is a string
# New: "price" is a float

def transform_price(record):
    price = record.get("price")
    if isinstance(price, str):
        price = float(price.replace("$", "").replace(",", ""))
    return price
```

### 4. Schema-on-Read (Data Lake)

Store raw data as JSON/Parquet (schema-on-read). Define the schema at query time.

```sql
-- Read the same data with different schemas
SELECT id, name::TEXT, email FROM raw_customers;    -- old schema
SELECT id, full_name::TEXT, email FROM raw_customers;  -- new schema
```

**Best for:** Data lakes where the same raw data is consumed by multiple pipelines with different schema expectations.

## Embedding Sensitivity to Schema Changes

Schema changes can silently degrade embedding quality:

| Change | Effect on Embeddings | Action |
|---|---|---|
| Add field to embedding input | Different vector for same record | Re-embed affected records |
| Remove field from input | Different vector, potential info loss | Re-embed all records |
| Change field order in template | Different vector (tokenization changes) | Re-embed with consistent template |
| Change field semantics | Vector doesn't represent the right thing | Retrain/fine-tune embedding model |

```python
# Bad: schema change in template creates different embeddings
# Old template
template_v1 = f"Customer {name}: {email}"
# New template  
template_v2 = f"Customer profile: {name} ({email})"

# Same customer produces different vectors → retrieval breaks
```

**Rule:** When the embedding input template changes, re-embed all affected records. Track the template version in metadata.

## Versioning in Vector DBs

Vector DBs have limited schema evolution capabilities:

| DB | Schema Change Handling |
|---|---|
| Pinecone | Metadata fields are dynamic (no fixed schema) |
| Qdrant | Payload fields are dynamic (no fixed schema) |
| Milvus | Schema is fixed at collection creation. Add field = drop + recreate |
| pgvector | SQL DDL (standard Postgres schema evolution) |

**For Milvus and pgvector**, plan for schema changes:
- Use JSON/BLOB columns for flexible metadata
- Store versioned documents in separate collections
- Maintain a schema version field on every record

## Schema Change Workflow

```yaml
schema_change:
  detection:
    - automated: "Schema registry comparison"
    - manual: "Source system change notification"
  
  impact_assessment:
    - fields_changed: []
    - downstream_pipelines: ["RAG pipeline", "ML training", "Analytics"]
    - embedding_template_affected: true/false
    - re_embedding_required: true/false
    - estimated_effort: "2 hours"
  
  rollout:
    - phase_1: "Add new fields, dual-write old + new"
    - phase_2: "Verify downstream pipelines still work"
    - phase_3: "Re-embed records (if template changed)"
    - phase_4: "Remove deprecated fields (30+ days later)"
  
  rollback:
    - condition: "Faithfulness drops > 2%"
    - action: "Revert to previous schema version"
```

## Best Practices

1. **Immutable embedding templates** — once a template is in production, treat it as immutable. Create a new version for changes.
2. **Schema version in metadata** — store `schema_version` with every chunk in the vector DB. This lets you filter or reprocess by version.
3. **Monitor embedding drift** — if the average embedding vector shifts significantly, a schema change may be the cause.
4. **Test schema changes** — run your eval set against both old and new schemas before deploying.
5. **Document schema decisions** — for every field, note when it was added, why, and which pipelines depend on it.
