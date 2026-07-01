# Multi-Tenancy and Security

Isolating data and controlling access in shared vector database deployments.

## Multi-Tenancy Models

| Model | Isolation | Cost Efficiency | Complexity | Products |
|---|---|---|---|---|
| **Collection-per-tenant** | Strong (separate indexes) | Low (many small indexes) | Low | Pinecone, Milvus, Qdrant |
| **Partition-per-tenant (logical)** | Moderate (shared index, filtered access) | High (single index) | Moderate | Milvus (partition key), Qdrant (payload filter) |
| **Separate instance** | Maximum (dedicated resources) | Lowest | Highest | Any |

### Collection-Per-Tenant

```python
# Each tenant gets their own index
index_customer_a = client.create_index("customer_a", dim=768)
index_customer_b = client.create_index("customer_b", dim=768)
```

- **Pros:** Simple, strong isolation, tenant-specific configuration.
- **Cons:** Resource overhead (each index has metadata overhead), management complexity at scale (10K+ tenants).

### Partition/Label-Based

```python
# Single index, filter by tenant_id
results = client.search(
    query_vector,
    filter={"tenant_id": "customer_a"},
    top_k=10,
)
```

- **Pros:** Efficient resource utilization, single management surface.
- **Cons:** Filter performance depends on selectivity (see hybrid search), risk of noisy neighbor.

**Recommendation:** Use partition-based for > 100 tenants. Use collection-per-tenant for < 100 tenants with strict isolation requirements.

## RBAC (Role-Based Access Control)

| Role | Permissions | Typical User |
|---|---|---|
| **Admin** | Full CRUD, schema changes, user management | Platform team |
| **Writer** | Insert, update, delete vectors | Data pipeline |
| **Reader** | Query only | Application backend |
| **Read-only** | Query, no metadata visibility | Audit, analytics |

### Implementation Options

- **Database-native RBAC:** Milvus, Qdrant, Weaviate support user/role management.
- **Application-layer RBAC:** If the database doesn't support it, wrap the API with your own auth (common with Pinecone).

## Network Security

| Feature | What It Protects | Products Supporting |
|---|---|---|
| **VPC Peering** | Traffic between your VPC and the DB | Pinecone, Milvus Cloud, Weaviate Cloud |
| **IP Whitelisting** | Restrict access to known IPs | Pinecone, Qdrant Cloud, Weaviate Cloud |
| **TLS/SSL** | Encryption in transit | All major products |
| **Private Link (AWS)** | Traffic never leaves AWS network | Pinecone, Milvus Cloud |
| **API Key auth** | Simple access control | All products |

## Encryption

| At Rest | In Transit | Key Management |
|---|---|---|
| **AES-256** for stored vectors and metadata | **TLS 1.2+** for all API communication | Some products support BYOK (Bring Your Own Key) |

- **Vectors are encrypted** but decrypted for search (inevitable — computation requires plaintext vectors).
- **Metadata fields can be encrypted** if used only for filtering (some products support this).

## Compliance Considerations

| Requirement | Consideration |
|---|---|
| **GDPR** | Right to deletion: ensure delete by user ID is efficient. Data residency: choose cloud region. |
| **HIPAA** | Requires encryption at rest and in transit, access logging, BAA with provider. |
| **SOC 2** | Most managed vector DBs are SOC 2 compliant (Pinecone, Milvus Cloud, Weaviate Cloud). |
| **Data residency** | Some products restrict which regions you can deploy in. Verify before choosing. |

## Access Audit Logging

What should be logged:

| Event | Why It Matters |
|---|---|
| **Query:** Who queried what vectors? | Security investigation, usage billing |
| **Write:** Who inserted/updated/deleted? | Data lineage, rollback |
| **Schema:** Who changed index config? | Change management |
| **Auth failure:** Who failed to authenticate? | Threat detection |

**Products with audit logging:** Milvus Cloud, Qdrant Cloud, Weaviate Cloud. Pinecone provides basic request logs.

## Best Practices

- **Use partition-based tenancy** for B2B SaaS (hundreds of customers, each with thousands of documents).
- **Use collection-per-tenant** for B2C or compliance-heavy scenarios (each tenant needs guaranteed isolation).
- **Apply network-level security first** (VPC peering, IP whitelisting), then application-level auth.
- **Never expose vector DB API keys in client-side code.** Route all queries through your backend.
- **Monitor for cross-tenant data access** — a query that accesses data across partitions could indicate a bug or security issue.
- **Plan for tenant deletion.** Deleting a tenant in a shared-index system requires efficient mass deletion. Test this path.
