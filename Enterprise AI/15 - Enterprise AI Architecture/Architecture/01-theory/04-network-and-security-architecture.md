# Network & Security Architecture

## Network Topology

### VPC Design

```
┌─────────────────────────────────────────────────────────────────┐
│                        VPC (10.0.0.0/16)                        │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Public Subnet  │  │  Private Subnet │  │  Private Subnet │  │
│  │  10.0.1.0/24    │  │  10.0.2.0/24    │  │  10.0.3.0/24    │  │
│  │                 │  │                 │  │                 │  │
│  │  Load Balancer  │  │  Orchestrator   │  │  Model Server   │  │
│  │  API Gateway    │  │  Guardrails     │  │  GPU Instances  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Private Subnet (Data)                     │ │
│  │                    10.0.4.0/24                              │ │
│  │                                                             │ │
│  │  Vector DB │ Cache (Redis) │ Application DB │ Object Store  │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Network Security Groups

| Source | Destination | Protocol | Purpose |
|--------|-------------|----------|---------|
| Internet | LB (443) | HTTPS | User traffic |
| LB | Orchestrator (8080) | HTTP | Request routing |
| Orchestrator | Model Server (8000) | HTTP | Inference requests |
| Orchestrator | Vector DB (5432) | PostgreSQL | RAG queries |
| Orchestrator | Cache (6379) | Redis | Caching |
| Model Server | Object Store (443) | HTTPS | Model loading |

## Private Endpoints

### For Managed Services

| Service | Connection | Security |
|---------|-----------|----------|
| Azure OpenAI | Private endpoint | No internet egress |
| OpenAI | Private network + NAT | Controlled egress |
| Anthropic | Private network + NAT | Controlled egress |
| Vector DB (Pinecone) | Private endpoint | AWS PrivateLink/Azure Private Link |
| Cache (Redis) | Private endpoint | VPC-internal |

## Data-in-Transit Security

| Path | Protocol | Encryption |
|------|----------|------------|
| User to API | HTTPS (TLS 1.3) | End-to-end |
| API to Orchestrator | HTTP (internal) | mTLS |
| Orchestrator to Model | HTTP (internal) | mTLS |
| Orchestrator to DB | Native TLS | Transport |
| Cross-region replication | HTTPS | TLS 1.3 |

## Bandwidth Planning

### GPU-to-GPU Communication
- Tensor parallelism requires high-bandwidth interconnect
- NVLink/NVSwitch within nodes: 600 GB/s
- InfiniBand across nodes: 200-400 Gbps
- Ethernet fallback: 100-400 Gbps (higher latency)

### Model Loading Bandwidth
- Model checkpoint loading from object store
- 70B model at FP16: ~140 GB
- Loading time = model_size / download_bandwidth
- Target: < 60s load time
- Required bandwidth: > 2.3 GB/s

## Disaster Recovery Network

### Cross-Region Connectivity
- Direct connect or VPN between regions
- Bandwidth for replication: 1-10 Gbps minimum
- DNS failover with health probes (30s interval)
- Traffic shifting via weighted DNS or global load balancer

### Network Failover Testing
- Quarterly DR drills
- Automated failover tests
- Latency measurement post-failover
- Bandwidth validation tests
