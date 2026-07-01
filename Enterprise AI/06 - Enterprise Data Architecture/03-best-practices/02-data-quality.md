# Data Quality Best Practices

## 1. Define Quality Dimensions
| Dimension | Definition | Example Check |
|-----------|-----------|---------------|
| Completeness | No missing required fields | `email IS NOT NULL` |
| Uniqueness | No duplicate keys | `COUNT(DISTINCT id) = COUNT(*)` |
| Timeliness | Data within freshness SLA | `created_at > NOW() - INTERVAL '1 day'` |
| Consistency | Values match expected format | `email ~ '.*@.*\..*'` |
| Accuracy | Values match source of truth | Sampled cross-checks |

## 2. Automated Quality Checks
- Run checks at **ingestion time** (gatekeeper pattern)
- Run checks **periodically** on stored data (data observability)
- Classify failures:
  - **Critical**: Block pipeline, page on-call
  - **Warning**: Log, alert, continue processing
  - **Informational**: Record in quality dashboard only

## 3. Remediation Strategy
- **Bad records at source**: DLQ + notify source owner
- **Schema violations**: Skip record, log schema diff, alert on threshold
- **Late data**: Accept if within grace period, reject otherwise
- **Duplicates**: Dedup by content hash or composite key

## 4. Monitoring & Alerting
- Track per-dataset quality scores over time
- Alert on trend degradation (e.g., completeness dropping 5% week-over-week)
- Dashboard: pass/fail rate by check type, by dataset, by source system

## 5. Quality SLAs
- Define minimum quality thresholds per dataset (e.g., completeness ≥ 99.5%)
- Quality SLA breach = pipeline incident (same severity as availability)
- Quarterly quality reviews with data producers and consumers

## 6. Tools
- **Great Expectations**: Python-based data quality framework
- **dbt tests**: Built-in schema and data tests
- **Deequ**: Apache Spark-based quality library
- Custom: simple SQL checks + alerting (good for starting out)
