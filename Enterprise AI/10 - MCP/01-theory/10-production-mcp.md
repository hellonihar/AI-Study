# Production MCP

## Architecture

```
Load Balancer
    │
    ├── MCP Server (SSE) - Replica 1
    ├── MCP Server (SSE) - Replica 2
    └── MCP Server (SSE) - Replica N
         │
         └── Backend Services
              ├── Database
              ├── Search Engine
              └── Internal APIs
```

## Deployment

### Docker Deployment
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py .

EXPOSE 8080
CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
```

```yaml
# docker-compose.yml
services:
  mcp-server:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DB_URL=postgresql://db:5432/mydb
      - API_KEY=${API_KEY}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 512M
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: myregistry/mcp-server:latest
        ports:
        - containerPort: 8080
        env:
        - name: DB_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        resources:
          requests:
            cpu: 250m
            memory: 256Mi
          limits:
            cpu: "1"
            memory: 512Mi
---
apiVersion: v1
kind: Service
metadata:
  name: mcp-server
spec:
  selector:
    app: mcp-server
  ports:
  - port: 8080
    targetPort: 8080
```

## Monitoring

### Health Check
```python
@app.get("/health")
async def health():
    try:
        db_status = check_database()
        return {
            "status": "healthy",
            "database": db_status,
            "uptime": time.time() - start_time,
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

### Metrics
```python
from prometheus_client import Counter, Histogram

tool_calls = Counter("mcp_tool_calls_total",
                     "Total tool calls", ["tool", "status"])
tool_latency = Histogram("mcp_tool_latency_seconds",
                         "Tool call latency", ["tool"])
active_connections = Counter("mcp_active_connections",
                             "Active SSE connections")
```

### Logging
```python
import structlog
logger = structlog.get_logger()

@server.tool()
def sensitive_operation(data: str) -> str:
    logger.info("tool.sensitive_operation",
                params=data[:50],
                user=request_context.user)
    result = process(data)
    logger.info("tool.sensitive_operation.complete")
    return result
```

## Performance Optimization

### Caching
```python
from cachetools import TTLCache

cache = TTLCache(maxsize=1000, ttl=300)

@server.tool()
def expensive_search(query: str) -> list:
    if query in cache:
        return cache[query]
    result = perform_search(query)
    cache[query] = result
    return result
```

### Rate Limiting
```python
from slowapi import Limiter

limiter = Limiter(key_func=lambda: request.client.host)

@app.post("/message")
@limiter.limit("100/minute")
async def handle_message(request):
    return await process_request(request)
```

### Connection Pooling
```python
import asyncpg

class DatabasePool:
    def __init__(self):
        self.pool = None

    async def initialize(self):
        self.pool = await asyncpg.create_pool(
            min_size=5,
            max_size=20,
        )
```

## Production Checklist

- [ ] Docker container for reproducible deployment
- [ ] Health check endpoint
- [ ] Prometheus metrics
- [ ] Structured logging
- [ ] Rate limiting
- [ ] Authentication for SSE transport
- [ ] TLS encryption
- [ ] Resource limits (CPU, memory)
- [ ] Connection pooling for databases
- [ ] Caching for expensive operations
- [ ] Graceful shutdown handling
- [ ] Configuration via environment variables
- [ ] Secrets management (not hardcoded)
- [ ] Monitoring and alerting configured
- [ ] Load testing completed
- [ ] Rollback plan documented
