# Enterprise AI Reference Architecture

## Layered Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         Client Layer                               │
│  Web App │ Mobile App │ API Clients │ Internal Tools               │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────────┐
│                       API Gateway / Load Balancer                   │
│  Auth │ Rate Limit │ Request Routing │ TLS Termination              │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────────┐
│                    AI Orchestration Layer                           │
│  Prompt Assembly │ Model Router │ Context Builder │ Cache          │
│  Guardrails │ RAG Pipeline │ Tool Integration                       │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────────┐
│                       Model Serving Layer                           │
│  vLLM │ TGI │ Triton │ ONNX │ Managed API (OpenAI, Anthropic)       │
│  Auto-scaling │ GPU Pooling │ Model Loading                          │
└──────────────┬─────────────────────────────────┬──────────────────┘
               │                                 │
┌──────────────▼──────────┐  ┌───────────────────▼──────────────────┐
│    Vector / Data Store   │  │      Monitoring & Observability      │
│  Vector DB │ Cache │ DB  │  │  Metrics │ Logs │ Traces │ Alerts    │
└─────────────────────────┘  └──────────────────────────────────────┘
```

## Core Components

### API Gateway
- Request authentication and authorization
- Rate limiting per user/feature/tier
- Request routing to appropriate model endpoints
- Response caching for identical requests

### Orchestration Layer
- Prompt assembly from templates and context
- Model selection based on task, cost, and quality requirements
- Context window management (truncation, summarization)
- RAG pipeline integration
- Guardrail evaluation (input + output)
- Multi-agent coordination

### Model Serving
- Self-hosted: vLLM, TGI, Triton Inference Server
- Managed: OpenAI, Anthropic, Azure, Bedrock
- Hybrid: sensitive workloads on-premise, public for non-sensitive

### Data Layer
- Vector database for semantic search
- Cache layer (Redis/Momento) for response and prefix caching
- Relational/NoSQL for application state
- Object store for documents and artifacts

## Deployment Topologies

### Single-Region Active-Active
```
Region A                     Region B
┌─────────────────┐         ┌─────────────────┐
│ API Gateway     │←───LB──→│ API Gateway     │
│ Orchestrator    │         │ Orchestrator    │
│ Model Serving   │         │ Model Serving   │
│ Vector DB (R/W) │←─repl──→│ Vector DB (R)   │
│ Cache           │         │ Cache           │
└─────────────────┘         └─────────────────┘
```

### Multi-Region Active-Passive (Disaster Recovery)
Primary region handles all traffic. Secondary region is ready for failover.

| Component | Primary | Secondary | Replication |
|-----------|---------|-----------|-------------|
| API Gateway | Active | Standby | DNS failover |
| Orchestrator | Active | Standby | Config sync |
| Model Serving | Active | Standby | Model artifact sync |
| Vector DB | Active | Read replica | Async replication |
| Cache | Active | Cold | Rebuild on failover |

## Capacity Planning

### GPU Sizing Formula
```
Required GPUs = (Requests/sec × Avg tokens per request) / (GPU throughput × Utilization target)
```

Example:
- 100 req/s, avg 500 tokens = 50,000 tokens/s
- A100 throughput: ~3,000 tokens/s (Llama 3 8B)
- Utilization target: 70%
- GPUs needed = 50,000 / (3,000 × 0.7) = ~24 A100s

### Memory Considerations
- Model weights: 8B params × 2 bytes (FP16) = 16 GB
- KV cache: batch_size × seq_len × layers × hidden_dim × 2 × 2 bytes
- Overhead: 20-30% for serving framework
- Total per GPU: weights + KV cache partition + overhead

## High Availability Design

| Failure Scenario | RTO | RPO | Mitigation |
|-----------------|-----|-----|------------|
| Single pod crash | < 1 min | N/A | Kubernetes auto-restart |
| Node failure | < 5 min | N/A | Node pool with spread |
| AZ failure | < 10 min | < 1 min | Multi-AZ deployment |
| Region failure | < 15 min | < 5 min | Multi-region failover |
| Model corruption | < 10 min | N/A | Model registry rollback |
| Data corruption | < 1 hr | < 1 hr | Point-in-time recovery |
