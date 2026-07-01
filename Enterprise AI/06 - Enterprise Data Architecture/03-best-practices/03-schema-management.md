# Schema Management Best Practices

## 1. Schema Registry Pattern
- Central registry (e.g., Confluent Schema Registry, Glue Schema Registry)
- Producers register schemas; consumers read schemas from registry
- Backward compatibility enforced at registration time

## 2. Evolution Rules
| Change | Backward Compatible | Forward Compatible |
|--------|--------------------|--------------------|
| Add optional field | Yes | Yes |
| Add required field | No | No |
| Remove field | No | No |
| Rename field | No | No |
| Widen type (int→long) | Yes | No |
| Narrow type | No | No |

## 3. Compatibility Modes
- **BACKWARD** (default): New schema can read data written with old schema
- **FORWARD**: Old schema can read data written with new schema
- **FULL**: Both directions supported
- **NONE**: No compatibility checks (avoid in production)

## 4. Versioning Strategy
- Schema version = monotonically increasing integer
- Store all historical versions (never delete)
- Tag breaking changes as major version bumps
- Document migration guide for each breaking change

## 5. Schema-on-Write vs Schema-on-Read
- **Schema-on-Write** (enforced): Stricter, more predictable, higher quality
- **Schema-on-Read** (flexible): Better for exploratory/ML workloads
- Hybrid: enforce write schema at ingestion tier; allow read-time projections at consumption tier

## 6. Polyglot Serialization
| Format | Best For | Trade-off |
|--------|----------|-----------|
| Avro | Streaming (Kafka) | Row-oriented, schema embedded |
| Parquet | Analytics (S3/ADLS) | Columnar, efficient for aggregation |
| JSON | APIs, debugging | Human-readable, ~2x larger |
| Protobuf | Low-latency services | Binary, strongly typed |

## 7. Automation
- CI pipeline validates schema changes before merge
- Auto-register schemas on deploy
- Auto-evolve schemas for non-breaking changes (add optional field)
- Break glass procedure for emergency evolution
