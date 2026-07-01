# Data Governance Best Practices

## Data Lifecycle Management

### Data Lifecycle Stages
```
Collection → Storage → Processing → Usage → Archival → Deletion
   |            |           |          |         |          |
Consent     Encryption    Purpose   Access     Retention   Right to
notice      at rest      limitation control    policy      deletion
```

### Stage-Specific Controls

| Stage | Minimum Controls |
|-------|-----------------|
| Collection | Consent notice, purpose specification, data minimization |
| Storage | Encryption, access control, retention tagging |
| Processing | Purpose limitation, data masking, audit logging |
| Usage | Access control, usage monitoring, purpose verification |
| Archival | Encryption, retention policy, access restriction |
| Deletion | Secure deletion, deletion confirmation, record keeping |

## Consent Management

### Consent Requirements
- Obtain explicit consent before collecting personal data
- Document what data is collected and for what purpose
- Allow users to withdraw consent at any time
- Honor consent withdrawal within defined SLA
- Maintain consent history for audit purposes

### Consent States
| State | Meaning | Action Required |
|-------|---------|-----------------|
| Not obtained | No consent recorded | Collect consent before processing |
| Granted | Active consent for specific purpose | Process data per purpose |
| Withdrawn | Consent revoked | Stop processing, delete data |
| Expired | Consent period ended | Re-obtain or delete |
| Rejected | Consent denied | Do not process |

## Data Retention

### Retention Policy Design
- Define retention periods by data type
- Automate retention policy enforcement
- Document retention rationale
- Provide data deletion upon request
- Log all retention actions

### Recommended Retention Periods

| Data Type | Retention | Rationale |
|-----------|-----------|-----------|
| Training data | Lifetime of model + 2 years | Reproduction, audit |
| Inference logs | 90 days | Debugging, monitoring |
| User profiles | Duration of relationship | Service delivery |
| Audit logs | 3 years | Regulatory compliance |
| Consent records | Duration + 2 years | Demonstrate consent |
| Financial data | 7 years | Tax/accounting requirements |

## Data Quality

### Quality Dimensions

| Dimension | Definition | Monitoring |
|-----------|------------|------------|
| Accuracy | Data correctly represents reality | Sampling, validation rules |
| Completeness | No missing required fields | Schema validation |
| Consistency | Same values across systems | Cross-system reconciliation |
| Timeliness | Data is current | Age tracking, staleness alerts |
| Uniqueness | No duplicate records | Dedup detection |
| Validity | Conforms to format/schema | Format validation |

### Quality Gates

```
Ingestion → Schema Validation → Quality Checks → PII Scan → Consent Check → Ready for Use
```

Each gate must pass or data is quarantined.

## Data Lineage

### What to Track
- Source of data (collection method, origin system)
- Transformation steps (ETL/ELT pipeline)
- Usage (which models, which features)
- Access (who accessed, when, for what purpose)
- Changes (what changed, when, who authorized)

### Lineage Implementation
- Automated lineage capture at pipeline level
- Version control for datasets
- Data catalog with lineage visualization
- Impact analysis for upstream changes

## Right to Deletion

### Deletion Process
1. Receive deletion request
2. Identify all data across all systems
3. Remove from active datasets
4. Retrain or fine-tune models if user data was in training
5. Confirm deletion to user
6. Document the request and resolution

### Deletion SLA
| Data Type | Deletion SLA | Complexity |
|-----------|-------------|------------|
| User profile data | 7 days | Low |
| Inference history | 14 days | Medium |
| Training data | 30 days | High (may require retraining) |
| Backup/archival data | 90 days | High |

## Common Data Governance Pitfalls

| Pitfall | Impact | Mitigation |
|---------|--------|------------|
| Shadow data | Unknown data stores | Automated data discovery |
| Consent gaps | Regulatory violation | Consent management platform |
| Over-retention | Legal exposure | Automated retention enforcement |
| Poor data quality | Model degradation | Quality monitoring |
| No lineage | Cannot reproduce | Automated lineage tracking |
| Incomplete deletion | Privacy violation | Deletion verification process |
