# Pipeline Design Best Practices

## 1. Separation of Concerns
- **Extract** (source-specific connectors) → **Transform** (shared processing logic) → **Load** (sink-specific writers)
- Each stage reads from a queue/topic, processes, and writes to the next queue/topic
- This allows independent scaling and failure handling per stage

## 2. Idempotency
- Every write operation must produce the same result if retried
- Use content hashing (`MD5(content)`) as dedup keys
- Implement upsert semantics (`INSERT ON CONFLICT UPDATE` or `PUT if-match`)

## 3. Checkpointing
- Persist offsets/watermarks after each batch (not per record)
- On restart, resume from last checkpoint — never re-read the entire source
- Use atomic checkpoint storage (S3 conditional writes, ZooKeeper, or database transactions)

## 4. Batch vs Streaming Decision Guide
| Factor | Batch | Streaming |
|--------|-------|-----------|
| Latency SLA | > 5 min | < 1 min |
| Volume | > 10M records/day | Any volume |
| Source type | Files, snapshots | CDC, events, logs |
| Complexity | Lower | Higher |
| Reprocessing | Easy (replay batch) | Requires offset reset |

## 5. Observability
- Emit metrics at every pipeline stage: throughput, latency, error count, record age
- Use structured logging with correlation IDs (`trace_id`, `pipeline_run_id`)
- Alert on: error rate > 1%, throughput drop > 50%, latency > 2x p99

## 6. Error Handling
- Dead-letter queues for records that fail after N retries
- Separate transient errors (retry with backoff) from permanent errors (route to DLQ)
- Never silently drop records — log and escalate all failures

## 7. Testing
- Unit test transformation logic in isolation
- Integration test with realistic data volumes (not just 3-row samples)
- Chaos test: inject failures at each stage to verify retry/fallback behavior
