# Index Tuning Strategy

How to configure ANN index parameters for optimal recall, latency, and memory.

## Index Selection Guide

| Scenario | Index | Rationale |
|---|---|---|
| < 100K vectors, simplicity | Flat (brute force) | No tuning, perfect recall, latency is acceptable |
| 100K-10M, balanced | HNSW | Log(n) search, good recall, moderate memory |
| 10M+, memory-constrained | IVF+PQ | Compresses vectors, lowest memory per vector |
| 100M+, disk-friendly | DiskANN | SSD-backed graph, handles vector data on disk |
| Exact results required | Flat | Only option for guaranteed exact nearest neighbors |

## HNSW Parameter Tuning

### M (max connections per node)
- **Default:** 16
- **Range:** 8–64
- **Effect:** Higher M = higher recall, more memory (M × 8 bytes per edge)
- **Tuning rule:** Double M until recall improvement drops below 0.5%
- **Memory cost:** Graph = 2 × M × ntotal × 4 bytes ≈ 128 bytes/node at M=16

### efConstruction (build-time search width)
- **Default:** 40
- **Range:** 20–200
- **Effect:** Higher = better graph quality, slower build
- **Tuning rule:** Set to 2× target efSearch. Don't exceed 200 (diminishing returns)

### efSearch (search-time search width)
- **Default:** 16
- **Range:** 4–256
- **Effect:** Higher = better recall, slower search (linear in efSearch)
- **Tuning rule:** Start at 2× M, increase by 2× until target recall is met

**Typical HNSW tuning path:**
```
M=16, efC=40, efSearch=16  →  ~0.90 recall @ 1M vectors
M=16, efC=80, efSearch=32  →  ~0.95 recall @ 1M vectors
M=32, efC=100, efSearch=64 →  ~0.98 recall @ 1M vectors
M=32, efC=200, efSearch=128 → ~0.99 recall @ 1M vectors
```

Each step costs ~2× latency and ~1.5× memory for ~2-5% recall gain.

## IVF Parameter Tuning

### nlist (number of centroids)
- **Default:** sqrt(n) or 4× sqrt(n)
- **Range:** 1–4096
- **Effect:** More centroids = more accurate partitioning, slower training
- **Heuristic:** nlist = 4 × sqrt(N) for N < 1M; nlist = sqrt(N) for N > 1M

### nprobe (number of cells to search)
- **Default:** 1
- **Range:** 1–nlist
- **Effect:** More probes = higher recall, slower search (linear in nprobe)
- **Tuning rule:** Double nprobe until recall plateaus

**IVF tuning path (N=1M, dim=768):**
```
nlist=512, nprobe=4   →  ~0.80 recall
nlist=512, nprobe=16  →  ~0.93 recall
nlist=512, nprobe=64  →  ~0.98 recall
nlist=2048, nprobe=64 →  ~0.99 recall
```

## IVF+PQ (Product Quantization)

### M (number of subvectors)
- **Default:** dim / 2
- **Effect:** Higher M = more accurate, slower search
- **Storage:** 4 bits per sub-vector (SQ4) or 8 bits (SQ8)
- **Compression:** Original dim × 4 bytes → M × 1 byte

| Dim | M=32 | M=64 | M=128 |
|---|---|---|---|
| 384 | 87.5% compression | 75% compression | 50% compression |
| 768 | 93.5% compression | 87% compression | 74% compression |
| 1024 | 95% compression | 90% compression | 80% compression |

**Tuning rule:** Start with M = dim / 4. Increase M if recall is insufficient. Compromise: target 75-80% compression for good recall.

## DiskANN Tuning

- **L (build quality):** 40-100, higher = better index
- **R (degree):** 32-128, similar to HNSW M
- **beamwidth (search):** 2-8, wider = more accurate, higher IO
- **PQ dimensions:** 16-64, fewer = more compression, worse recall

## Practical Tuning Workflow

1. **Profile your data:** sample 10K vectors, build all index types
2. **Measure baseline:** Flat index for ground truth
3. **Tune one parameter at a time:** sweep efSearch, nprobe individually
4. **Set recall target:** typically 0.95-0.99 (not 1.0 — diminishing returns are brutal)
5. **Latency budget:** set index parameters to fit your P99 latency target
6. **Validate at scale:** retune at full scale (parameters change with N)

## Parameter Sweep Checklist

```
Before going to production, run a sweep:

HNSW: M ∈ [8, 16, 32], efSearch ∈ [8, 16, 32, 64, 128]
IVF:  nlist ∈ [sqrt(N)/2, sqrt(N), 2*sqrt(N)], nprobe ∈ [1, 2, 4, 8, 16, 32, 64]
PQ:   M ∈ [dim/8, dim/4, dim/2], nbits ∈ [4, 8]

Measure: recall@10, P50/P95/P99 latency, QPS, memory
Target:  recall > 0.95, P99 latency < latency_SLA, memory < available_RAM
```
