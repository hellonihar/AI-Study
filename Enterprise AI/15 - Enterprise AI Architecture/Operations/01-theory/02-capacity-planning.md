# Capacity Planning

## GPU Throughput Estimation

| Model Size | Parameters | GPU Required | Throughput (tokens/s/GPU) |
|-----------|-----------|-------------|--------------------------|
| Small | 1-3B | 1x A10 (24GB) | 500-1500 |
| Medium | 7-8B | 1x A100-40GB | 200-600 |
| Large | 13-20B | 2x A100-80GB | 100-300 |
| XL | 70B+ | 8x A100-80GB | 50-150 |

## Scaling Rules

| Scenario | Approach |
|----------|----------|
| Steady growth | Auto-scaling with buffer (20% headroom) |
| Spiky traffic | Burst capacity + queue for overage |
| Predictable peaks | Pre-scale ahead of known events |
| Cost-sensitive | Spot instances + fallback to on-demand |
| Latency-sensitive | Keep idle pool, pay for availability |
