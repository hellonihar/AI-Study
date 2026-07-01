# Production LLMOps Architecture

## Reference Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Request                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                      API Gateway                                 │
│            Auth, Rate Limit, Request Routing                     │
└───────────┬──────────────────────────────────┬──────────────────┘
            │                                  │
┌───────────▼──────────┐           ┌───────────▼──────────┐
│   Input Guardrails   │           │   Observability      │
│   Safety, PII, JB    │           │   Metrics, Logs,     │
│   Detection          │           │   Traces             │
└───────────┬──────────┘           └───────────┬──────────┘
            │                                  │
┌───────────▼──────────────────────────────────▼──────────┐
│                    LLM Orchestrator                       │
│    Prompt Assembly → Model Selection → Inference         │
│    → Output Processing                                   │
│                                                         │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│    │ Prompt   │  │ Model    │  │ Cache    │            │
│    │ Registry │  │ Registry │  │ Layer    │            │
│    └──────────┘  └──────────┘  └──────────┘            │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                   Model Serving                         │
│         vLLM / TGI / API-based Models                   │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                   Output Guardrails                     │
│            Safety, PII, Policy, Format                  │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                      Response                           │
└────────────────────────────────────────────────────────┘
```

## Backing Services

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Vector DB   │  │  Cache       │  │  Message     │
│  (Pinecone,  │  │  (Redis,     │  │  Queue       │
│   Milvus)    │  │   Momento)   │  │  (Kafka,     │
│              │  │              │  │   RabbitMQ)  │
└──────────────┘  └──────────────┘  └──────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Monitoring  │  │  Registry    │  │  Feature     │
│  (Datadog,   │  │  (MLflow,    │  │  Store       │
│   Grafana)   │  │   W&B)       │  │  (Redis,     │
│              │  │              │  │   Fennel)    │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Deployment Architecture

### Kubernetes-Native

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-orchestrator
spec:
  replicas: 6
  strategy:
    rollingUpdate:
      maxSurge: 2
      maxUnavailable: 1
  template:
    spec:
      containers:
        - name: orchestrator
          image: llm-orch:v2.1.0
          env:
            - name: MODEL_SERVER_URL
              value: "http://vllm-service:8000"
          resources:
            requests:
              cpu: 500m
              memory: 512Mi
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: vllm-service
spec:
  selector:
    app: vllm
  ports:
    - port: 8000
```

### Auto-Scaling Configuration

| Service | Metric | Scale-Out | Scale-In |
|---------|--------|-----------|----------|
| API Gateway | CPU > 70% | +1 | -1 @ < 30% |
| Orchestrator | Queue depth > 50 | +1 | -1 @ < 10 |
| Model Server | GPU util > 80% | +1 | -1 @ < 40% |
| Guardrails | Request latency > 500ms | +1 | -1 @ < 200ms |

## CI/CD Pipeline

```
                         ┌──────────┐
                         │   Git    │
                         └────┬─────┘
                              │
                    ┌─────────▼─────────┐
                    │   CI Pipeline     │
                    │   Lint → Test →   │
                    │   Build Image     │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Staging Deploy   │
                    │  Integration Test │
                    │  Load Test        │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Canary (5%)      │
                    │  24h Monitor      │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Production       │
                    │  25% → 50% → 100% │
                    └───────────────────┘
```

## Disaster Recovery

| Scenario | RTO | RPO | Strategy |
|----------|-----|-----|----------|
| Single pod failure | < 1min | N/A | Kubernetes auto-restart |
| Node failure | < 5min | N/A | Multi-AZ spread |
| Region failure | < 15min | < 5min | Active-passive multi-region |
| Data corruption | < 1hr | < 1hr | Point-in-time recovery |
| Model corruption | < 10min | N/A | Model registry rollback |
