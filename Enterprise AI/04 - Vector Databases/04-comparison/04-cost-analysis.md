# Cost Comparison of Vector Databases

Total cost of ownership (TCO) across self-hosted and managed vector database options.

## Methodology

Costs calculated for 2024 US pricing (us-east-1, AWS). Self-hosted includes compute (on-demand), storage (gp3 EBS), and estimated ops overhead. Managed includes all-in SaaS pricing. Estimates exclude data transfer and backup costs unless noted.

## Scenario A: Small RAG (100K vectors, dim=768, 100 QPS)

| Option | Compute | Storage | Ops | Total/Month |
|---|---|---|---|---|
| **FAISS** (in-app, no DB) | $0 (shared) | $0.15 | $0 | **~$0** |
| **pgvector** (r6i.large, 2C/16G) | $83 | $5 | $50 | **$138** |
| **Qdrant** (single node, r6i.large) | $83 | $5 | $50 | **$138** |
| **Milvus standalone** (r6i.large) | $83 | $5 | $100 | **$188** |
| **Pinecone** (s1.x1) | — | — | — | **$70** |
| **Qdrant Cloud** (1 node, 4 GB) | — | — | — | **$25** |
| **Weaviate Cloud** (sandbox) | — | — | — | **$25** |
| **pgvector** (RDS, db.r6g.large) | — | — | — | **$213** |

**Winner:** FAISS (free), then Qdrant Cloud or Pinecone for managed.

## Scenario B: Production RAG (10M vectors, dim=768, 500 QPS)

| Option | Compute | Storage | Ops | Total/Month |
|---|---|---|---|---|
| **FAISS** (r6i.2xlarge, 8C/64G) | $332 | $50 | $100 | **$482** |
| **pgvector** (r6i.2xlarge, 8C/64G) | $332 | $100 | $150 | **$582** |
| **Qdrant** (3× r6i.2xlarge, RF=2) | $996 | $150 | $200 | **$1,346** |
| **Milvus** (3× r6i.2xlarge, RF=2) | $996 | $150 | $300 | **$1,446** |
| **Pinecone** (p1 pod, auto-scale) | — | — | — | **~$400-800** |
| **Qdrant Cloud** (3 nodes, 16 GB each) | — | — | — | **~$450** |
| **Weaviate Cloud** (standard, 3 nodes) | — | — | — | **~$500** |
| **Milvus Cloud** (3 CU) | — | — | — | **~$1,500** |

**Winner:** Self-hosted FAISS/pgvector for cost, Qdrant Cloud for managed.

## Scenario C: Large-Scale (100M vectors, dim=768, 2000 QPS)

| Option | Compute | Storage | Ops | Total/Month |
|---|---|---|---|---|
| **FAISS** (r6i.8xlarge + PQ, 32C/256G) | $1,327 | $300 | $200 | **$1,827** |
| **Milvus** (4× r6i.4xlarge, RF=2) | $2,656 | $500 | $500 | **$3,656** |
| **Qdrant** (6× r6i.4xlarge, RF=2) | $3,984 | $750 | $500 | **$5,234** |
| **Pinecone** (p2 pod, auto-scale) | — | — | — | **~$5,000-8,000** |
| **Qdrant Cloud** (6 nodes, 64 GB) | — | — | — | **~$3,500** |
| **Milvus Cloud** (8 CU) | — | — | — | **~$4,000** |

**Winner:** FAISS+PQ (cheapest, but library, not distributed DB). Milvus self-hosted for distributed.

## Cost Per 10K Queries

| Database | 100K vectors | 1M vectors | 10M vectors | 100M vectors |
|---|---|---|---|---|
| **FAISS HNSW** | $0.001 | $0.002 | $0.005 | $0.015 |
| **pgvector HNSW** | $0.002 | $0.005 | $0.01 | $0.03 |
| **Qdrant self-hosted** | $0.002 | $0.005 | $0.02 | $0.06 |
| **Milvus self-hosted** | $0.003 | $0.008 | $0.025 | $0.08 |
| **Pinecone** | $0.01 | $0.02 | $0.04 | $0.15 |
| **Qdrant Cloud** | $0.005 | $0.01 | $0.03 | $0.08 |

At scale, self-hosted is 2-5× cheaper per query than managed.

## Hidden Costs

| Cost | Self-Hosted | Managed |
|---|---|---|
| **Engineering time** | 10-40 hrs/month (tuning, patching, monitoring) | 1-5 hrs/month |
| **Opportunity cost** | Team not building product features | Higher per-query cost |
| **Data transfer** | Free (same AZ) | Variable ($0.01-0.09/GB egress) |
| **Backup storage** | 2-5× data size (WAL + snapshots) | Included |
| **Multi-region** | Complex, 2-3× cost | Premium tier, 2× cost |
| **Support** | Community (free) or vendor ($500+/month) | Included in plan |

## Cost Optimization by Scale

```
< 100K:   No vector DB needed (FAISS in-app = $0)
100K-1M:  pgvector or Qdrant single node ($25-150/month)
1M-10M:   Qdrant cluster or Pinecone ($200-800/month)
10M-100M: Milvus self-hosted or Pinecone p2 ($1,500-5,000/month)
100M+:    Custom DiskANN or Milvus cluster ($3,000-15,000/month)
```

## Break-Even: Self-Hosted vs. Managed

| Scale | Self-Hosted Cost | Managed Cost | Break-Even (months) |
|---|---|---|---|
| 100K | $138 | $70 | Never (managed always cheaper) |
| 1M | $300 | $200 | Never (managed cheaper) |
| 10M | $582 | $450 | ~12 (ops setup cost recouped) |
| 100M | $1,827 | $5,000 | ~3 (self-hosted much cheaper) |

At low scale (< 1M), managed is cheaper. At high scale (> 10M), self-hosted wins by 2-5×.

## Recommendation

- **< 1M vectors:** Use Qdrant Cloud or Pinecone. The ops savings outweigh the premium.
- **1M-10M vectors:** Qdrant Cloud or self-hosted pgvector, depending on team skills.
- **10M-100M vectors:** Self-hosted Milvus or Qdrant. The 3-month break-even is compelling.
- **100M+ vectors:** Self-hosted with PQ compression. Managed costs become prohibitive.
