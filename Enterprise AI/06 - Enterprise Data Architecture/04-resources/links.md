# Resources — Enterprise Data Architecture

## Foundational Papers

| Paper | Year | Contribution |
|-------|------|-------------|
| [Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics](https://www.cidr.org/papers/cidr2021-paper73.pdf) | 2021 | Lakehouse architecture paper (Armbrust et al., Databricks) |
| [Delta Lake: High-Performance ACID Table Storage over Cloud Object Stores](https://databricks.com/research/delta-lake-high-performance-acid-table-storage-over-cloud-object-stores) | 2020 | Delta Lake: ACID on data lakes |
| [Apache Iceberg: A Table Format for Huge Analytic Datasets](https://iceberg.apache.org/) | 2020 | Iceberg table format spec |
| [Apache Hudi: Upserts And Incremental Processing on Big Data](https://hudi.apache.org/) | 2019 | Hudi: record-level upserts |
| [The Dataflow Model: A Practical Approach to Balancing Correctness, Latency, and Cost](https://research.google/pubs/the-dataflow-model/) | 2015 | Google's streaming data processing model |
| [Google's Dremel: Interactive Analysis of Web-Scale Datasets](https://research.google/pubs/dremel-interactive-analysis-of-web-scale-datasets/) | 2010 | Columnar storage for nested data |
| [schema.org](https://schema.org/) | 2011 | Structured data schema vocabulary |

## Data Pipeline Frameworks

| Framework | Description |
|-----------|-------------|
| [Apache Spark](https://spark.apache.org/) | Unified analytics engine for large-scale data processing |
| [Apache Flink](https://flink.apache.org/) | Stream processing framework |
| [Apache Kafka](https://kafka.apache.org/) | Distributed event streaming platform |
| [Apache Airflow](https://airflow.apache.org/) | Workflow orchestration (batch) |
| [Dagster](https://dagster.io/) | Data orchestrator with asset-based design |
| [Prefect](https://www.prefect.io/) | Modern workflow orchestration |
| [dbt](https://www.getdbt.com/) | Data transformation in warehouse |
| [Kafka Streams](https://kafka.apache.org/documentation/streams/) | Stream processing library (JVM) |
| [Delta Live Tables](https://www.databricks.com/product/delta-live-tables) | Declarative ETL on Databricks |

## Storage & Table Formats

| Tool | Description |
|------|-------------|
| [Delta Lake](https://delta.io/) | ACID transactions on data lakes (open source) |
| [Apache Iceberg](https://iceberg.apache.org/) | Open table format for analytic datasets |
| [Apache Hudi](https://hudi.apache.org/) | Incremental processing + upserts |
| [Apache Parquet](https://parquet.apache.org/) | Columnar storage format |
| [Apache Avro](https://avro.apache.org/) | Row-oriented serialization |
| [Apache Arrow](https://arrow.apache.org/) | In-memory columnar format |

## Data Quality & Observability

| Tool | Description |
|------|-------------|
| [Great Expectations](https://greatexpectations.io/) | Data quality validation framework |
| [Deequ](https://github.com/awslabs/deequ) | Quality checks on Spark |
| [Soda](https://www.soda.io/) | Data observability and monitoring |
| [Monte Carlo](https://www.montecarlodata.com/) | Data observability platform |
| [Sifflet](https://www.siffletdata.com/) | Data observability and lineage |
| [DQLabs](https://www.dqlabs.ai/) | Automated data quality |

## Schema Management

| Tool | Description |
|------|-------------|
| [Confluent Schema Registry](https://docs.confluent.io/platform/current/schema-registry/) | Avro/Protobuf/JSON schema registry |
| [AWS Glue Schema Registry](https://aws.amazon.com/glue/features/schema-registry/) | Managed schema registry on AWS |
| [Apicurio Registry](https://www.apicur.io/registry/) | Open-source schema registry |
| [Protobuf](https://protobuf.dev/) | Google's language-neutral serialization |
| [Apache Avro](https://avro.apache.org/) | Schema-based serialization with evolution |

## Data Lineage & Catalog

| Tool | Description |
|------|-------------|
| [Apache Atlas](https://atlas.apache.org/) | Data governance and lineage |
| [DataHub](https://datahubproject.io/) | Modern data catalog (LinkedIn) |
| [Amundsen](https://www.amundsen.io/) | Data discovery platform (Lyft) |
| [Marquez](https://marquezproject.ai/) | Open-source data lineage |
| [OpenMetadata](https://open-metadata.org/) | Unified metadata platform |
| [Apache Ranger](https://ranger.apache.org/) | Data security governance |

## PII / Data Privacy

| Tool | Description |
|------|-------------|
| [Microsoft Presidio](https://microsoft.github.io/presidio/) | PII detection and anonymization |
| [Amazon Macie](https://aws.amazon.com/macie/) | S3 PII scanning |
| [Azure Purview](https://azure.microsoft.com/en-us/services/purview/) | Data governance + classification |
| [Tonic.ai](https://www.tonic.ai/) | Synthetic data generation |
| [Mostly AI](https://mostly.ai/) | Synthetic data for privacy compliance |
| [Google DLP](https://cloud.google.com/dlp) | Data Loss Prevention API |

## Tutorials & Guides

- [Delta Lake Documentation](https://docs.delta.io/latest/index.html) — Official Delta Lake guide
- [Apache Iceberg Documentation](https://iceberg.apache.org/docs/latest/) — Iceberg table format docs
- [Building a Lakehouse with Databricks](https://www.databricks.com/discover/data-lakehouse) — Databricks lakehouse guide
- [Streaming 101: The Dataflow Model](https://www.oreilly.com/radar/the-world-beyond-batch-streaming-101/) — Tyler Akidau's streaming guide
- [Data Contracts: A Practical Guide](https://www.dataengineeringweekly.com/p/data-contracts-the-ultimate-guide) — Data contracts for schema management
- [Great Expectations Documentation](https://docs.greatexpectations.io/docs/) — GX documentation
- [AWS Data Engineering Best Practices](https://docs.aws.amazon.com/whitepapers/latest/best-practices-data-engineering/best-practices-data-engineering.html) — AWS data engineering whitepaper
- [Azure Data Architecture Guide](https://learn.microsoft.com/en-us/azure/architecture/data-guide/) — Microsoft data architecture guide

## Books

| Title | Author | Year |
|-------|--------|------|
| Designing Data-Intensive Applications | Martin Kleppmann | 2017 |
| Streaming Systems | Tyler Akidau et al. | 2018 |
| The Data Warehouse Toolkit | Ralph Kimball | 2013 |
| Fundamentals of Data Engineering | Joe Reis, Matt Housley | 2022 |
| Data Management at Scale | Piethein Strengholt | 2020 |
