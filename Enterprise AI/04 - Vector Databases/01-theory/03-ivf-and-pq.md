# IVF and PQ

Inverted File index (IVF) and Product Quantization (PQ) — the memory-efficient alternatives to HNSW.

## IVF (Inverted File Index)

IVF partitions the vector space into k clusters (via k-means) and only searches the closest clusters during query.

```
1. Build: Cluster vectors into k groups (Voronoi cells)
2. Search: 
   a. Find the nprobe nearest cluster centroids to the query
   b. Search only within those clusters
```

### Parameters

| Parameter | Range | Default | Effect |
|---|---|---|---|
| **nlist** (k) | 100–1M | 100×√n | Number of clusters. Higher = slower build, finer granularity. |
| **nprobe** | 1–nlist | 10 | Number of clusters to search. Higher = better recall, slower. |

### Tuning

```
nlist = 100:   Build fast,  search must probe many
nlist = 10000: Build slow, search probes few but each cluster is smaller

nprobe = 1:    Fast search, low recall (~0.50)
nprobe = 10:   Moderate search, good recall (~0.85)
nprobe = 50:   Slow search, high recall (~0.95)
nprobe = nlist: Equivalent to flat search
```

**Rule of thumb:** `nlist = 10 × √n`. For 1M vectors, nlist ≈ 10,000. For 10M, nlist ≈ 31,600.

## Product Quantization (PQ)

PQ compresses vectors by splitting them into sub-vectors and quantizing each independently.

```
Original vector (768 dims, FP32 = 3072 bytes)
    ↓
Split into M=8 sub-vectors of 96 dims each
    ↓
Each sub-vector → nearest centroid from 256-entry codebook
    ↓
Compressed: 8 codebook indices = 8 bytes (384× compression!)
```

### Parameters

| Parameter | Range | Default | Effect |
|---|---|---|---|
| **M** | 2–64 | 8 | Number of sub-vectors. Higher = better quality, larger index. |
| **nbits** | 4–16 | 8 | Bits per sub-index (256 centroids for 8 bits). Higher = better quality. |
| **ksub** | 2^nbits | 256 | Centroids per sub-quantizer. |

### Quality vs Compression

```
Original (768 dims, FP32): 3072 bytes → recall baseline
PQ M=8, nbits=8:           8 bytes     → recall 0.75–0.85
PQ M=16, nbits=8:          16 bytes    → recall 0.82–0.90
PQ M=32, nbits=8:          32 bytes    → recall 0.87–0.93
PQ M=64, nbits=8:          64 bytes    → recall 0.90–0.95
```

## IVF-PQ (The Production Choice)

Combining IVF's search pruning with PQ's compression:

```
1. IVF: Assign each vector to a coarse quantizer cluster (centroid).
2. PQ: Compress the residual (vector - centroid) into M bytes.
3. Search:
   a. Find nprobe nearest centroids → candidate lists
   b. Asymmetric Distance Computation: decode PQ codes on-the-fly
   c. Return top-k
```

### How ADC Works

Instead of decompressing PQ codes to compute distance, precompute distances from the query to each centroid:

```
For each sub-vector j:
  For each possible centroid c in codebook_j:
    precomputed[j][c] = distance(query_sub[j], centroid_c)

Total distance = sum(precomputed[j][code_j])  # O(M) per PQ code
```

- **No explicit decompression** — distances are computed via table lookup.
- **2–10× faster** than brute-force on compressed data.
- **Only ~1% slower** than searching the compressed index directly.

## Production Guidance

```
Memory budget?
├── Plenty of RAM (raw vectors fit) → HNSW or IVF-Flat
├── Tight RAM (vectors compressed 10×) → IVF-PQ with M=16
└── Extreme (vectors compressed 50×+) → IVF-PQ with M=8

Recall requirement?
├── > 0.95 → IVF-Flat (no PQ) or HNSW
├── > 0.85 → IVF-PQ with M=32, nprobe=100+
└── > 0.75 → IVF-PQ with M=16, nprobe=50+
```

## Best Practices

- **IVF-nprobe is cheaper to tune than PQ-M.** Change nprobe first (no rebuild needed), then adjust M if more quality is needed.
- **IVF-PQ with M=32 and nprobe=100** is a solid default for memory-constrained production (> 10M vectors).
- **PQ group size matters.** Smaller groups (M=64) give better recall but use more memory. Match group size to your SIMD width for best performance.
- **Benchmark with your data.** PQ quality varies significantly by data distribution. Don't trust generic benchmarks.
