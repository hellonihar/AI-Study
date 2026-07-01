# Enterprise Data Architecture

Data pipelines, storage architecture, quality, schema management, and governance for powering AI systems at scale.

## Module Structure

```
06 - Enterprise Data Architecture/
├── 01-theory/          # 10 files: overview, pipelines, ingestion, freshness, schema, lineage, quality, PII, lakehouse, architecture
├── 02-code/            # 10 scripts: data quality checks through architecture analyzer
├── 03-best-practices/  # 5 files: pipeline design, data quality, schema management, PII governance, lakehouse ops
├── 04-resources/       # Papers, frameworks, tools, tutorials, books
└── README.md           # This file
```

## Theory (01-theory/)

| # | File | Topic |
|---|------|-------|
| 1 | `01-overview.md` | Enterprise data architecture for AI: motivations, challenges, principles |
| 2 | `02-structured-data-pipelines.md` | Batch ingestion, ETL vs ELT, CDC, data warehouses |
| 3 | `03-unstructured-data-ingestion.md` | Document parsing, OCR, chunking strategies, embedding |
| 4 | `04-data-freshness-sla.md` | Latency tiers, SLA definitions, trade-off analysis |
| 5 | `05-schema-evolution.md` | Schema registry, backward/forward compatibility, versioning |
| 6 | `06-data-lineage.md` | Lineage tracking, column-level, impact analysis |
| 7 | `07-data-quality.md` | Quality dimensions, monitoring, anomaly detection |
| 8 | `08-pii-and-privacy.md` | Classification, detection, anonymization, compliance |
| 9 | `09-lakehouse-architecture.md` | Delta Lake, Iceberg, Hudi: ACID on data lakes |
| 10 | `10-architecture-for-ai.md` | End-to-end architecture combining all concepts for RAG/ML |

## Code Examples (02-code/)

| # | File | Description | Requirements |
|---|------|-------------|--------------|
| 1 | `01-data-quality-checks.py` | Completeness, uniqueness, consistency, freshness checks | `numpy` |
| 2 | `02-cdc-simulation.py` | Change data capture with before/after images | none (stdlib) |
| 3 | `03-pii-detection.py` | Regex + ML hybrid PII detection with remediation | `numpy` |
| 4 | `04-schema-evolution.py` | Avro-like schema evolution with compatibility checks | none (stdlib) |
| 5 | `05-data-lineage.py` | Column-level lineage with impact analysis | none (stdlib) |
| 6 | `06-batch-ingestion.py` | Batch pipeline with chunking, checkpointing | `numpy` |
| 7 | `07-streaming-simulation.py` | Event stream processing with sliding windows | `numpy` |
| 8 | `08-data-catalog-simulation.py` | Data asset registration, search, relationship mapping | none (stdlib) |
| 9 | `09-delta-lake-simulation.py` | Delta Lake time travel, compaction, vacuum concepts | none (stdlib) |
| 10 | `10-architecture-analyzer.py` | Pipeline health, bottleneck, cost, freshness analysis | `numpy` |

## Best Practices (03-best-practices/)

| # | File | Topic |
|---|------|-------|
| 1 | `01-pipeline-design.md` | Separation of concerns, idempotency, checkpointing, batch vs streaming |
| 2 | `02-data-quality.md` | Quality dimensions, automated checks, remediation, SLAs |
| 3 | `03-schema-management.md` | Schema registry, evolution rules, compatibility, serialization formats |
| 4 | `04-pii-governance.md` | Classification tiers, detection strategy, remediation, regional regulations |
| 5 | `05-lakehouse-ops.md` | Table layout, lifecycle, optimization, concurrency, DR |

## Key Topics

- **Pipelines:** Batch ingestion, CDC, streaming, checkpointing, idempotency
- **Storage:** Data lake, warehouse, lakehouse (Delta Lake, Iceberg, Hudi), object stores
- **Schema:** Registry, evolution (backward/forward/full), Avro, Protobuf, Parquet
- **Data Quality:** Completeness, uniqueness, timeliness, consistency, accuracy
- **PII/Privacy:** Detection, classification (4 tiers), masking, tokenization, encryption
- **Lineage:** Column-level, impact analysis, upstream/downstream dependencies
- **Architecture:** End-to-end design for RAG and ML pipelines, cost analysis

## Quick Start

```bash
# Data quality checks
pip install numpy
python "02-code/01-data-quality-checks.py"

# PII detection
python "02-code/03-pii-detection.py"

# Architecture analyzer
python "02-code/10-architecture-analyzer.py"
```

## Prerequisites

- **Python 3.10+**
- Core: `numpy`
- Most scripts run with stdlib only (simulation-based design)
- For real production use: `pyspark`, `delta-spark`, `kafka-python`, `great-expectations`
