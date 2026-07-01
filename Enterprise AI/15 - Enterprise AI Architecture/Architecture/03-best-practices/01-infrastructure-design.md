# Infrastructure Design Best Practices

## GPU Sizing Rules

| Model Size | Minimum GPU | Recommended GPU | Expected Throughput |
|------------|------------|----------------|-------------------|
| < 7B params | T4 (16GB) | L4 (24GB) | 5-10K tokens/s |
| 7B-13B params | A10G (24GB) | A100 (80GB) | 2-5K tokens/s |
| 13B-70B params | A100 (80GB) | H100 (80GB) | 400-1.5K tokens/s |
| > 70B params | 2x A100/H100 | 4-8x H100 | 200-800 tokens/s |

## Availability Targets

| SLA | Monthly Downtime | Architecture Required |
|-----|-----------------|----------------------|
| 99.9% | 43 min | Multi-AZ, single region |
| 99.95% | 21 min | Multi-AZ, active-active |
| 99.99% | 4.3 min | Multi-region, active-passive |
| 99.999% | 26 sec | Multi-region, active-active |

## Key Design Decisions

| Decision | Recommendation |
|----------|---------------|
| Start with API | Use managed APIs initially, migrate to self-hosted at scale |
| Always cache | Implement exact + semantic cache from day 1 |
| Multi-AZ from day 1 | Do not deploy to single AZ, even for MVP |
| Plan for 2x growth | Design capacity for 2x initial traffic |
| Monitor everything | Instrument latency, cost, quality from request 1 |
