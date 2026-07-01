# Embedding Quantization

Reducing the precision of embeddings to save memory and speed up search.

## Why Quantize?

Storage cost of 1M embeddings:

| Precision | Dimensions | Size | Recall@10 vs FP32 |
|---|---|---|---|
| FP32 | 768 | 3.0 GB | Baseline |
| FP16 | 768 | 1.5 GB | ~0% loss |
| INT8 (SQ) | 768 | 768 MB | -0.5% |
| INT8 (PQ) | 768 → 96 | 96 MB | -1.5% |
| Binary | 768 → 96 bytes | 96 MB | -3–5% |

**Production insight:** INT8 scalar quantization is the sweet spot — 2× memory compression with negligible recall loss.

## Scalar Quantization (SQ)

Map FP32 values to INT8:

```python
import numpy as np

def quantize_sq(embeddings):
    """Scalar quantize to INT8 using min-max range."""
    # embeddings: (n, d)
    mins = embeddings.min(axis=0)
    maxs = embeddings.max(axis=0)
    # Quantize to [0, 255]
    quantized = ((embeddings - mins) / (maxs - mins + 1e-9) * 255).astype(np.uint8)
    return quantized, mins, maxs

def dequantize_sq(quantized, mins, maxs):
    return (quantized / 255.0) * (maxs - mins) + mins
```

**FAISS implementation:** `IndexIVFFlat` with `IndexScalarQuantizer`.

## Product Quantization (PQ)

Compress vectors by splitting them into sub-vectors and quantizing each:

```
Original: [0.2, 0.5, -0.1, 0.8, 0.3, -0.6, ...]  (768 dims)
                         ↓
Split into 8 sub-vectors: [0.2, 0.5, -0.1, ...], [0.8, 0.3, -0.6, ...], ...
                         ↓
Each sub-vector → nearest centroid from 256-entry codebook
                         ↓
Compressed: [42, 187, 95, 203, 12, 156, 73, 210]  (8 bytes)
```

- **Compression:** 768 FP32 values (3072 bytes) → M codebook indices (M bytes).
- **M=8 (96× compression):** Fastest, reasonable quality.
- **M=32 (24× compression):** Best quality.
- **Search:** Asymmetric Distance Computation (ADC) — precompute distances to centroids.

## Binary Embeddings

Extreme quantization — each dimension → 1 bit:

```python
def binarize(embeddings):
    """Convert to binary embeddings: sign of each dimension."""
    return (embeddings > 0).astype(np.int8)
```

- **Storage:** 768 dims → 96 bytes (96× compression vs FP32, 4× vs FP16).
- **Search:** Hamming distance (XOR + popcount) — extremely fast (CPU SIMD).
- **Quality:** 3–5% recall drop for most tasks. Acceptable for very large-scale (100M+ documents) where full precision is infeasible.

## Matryoshka Representation Learning (MRL)

A different approach: train the model to produce embeddings where prefix truncation preserves quality:

```python
# One model, multiple effective dimensions
vec_768 = model.encode("text", truncate_dim=768)
vec_256 = model.encode("text", truncate_dim=256)  # same model, smaller output
```

- **Advantage:** Single model, flexible storage/speed trade-off.
- **Recall@10:** 768 dim → 256 dim ≈ -2% for most tasks.
- **Used by:** Nomic Embed Text v1.5, BGE M3.

## Quantization Strategy Guide

```
Storage budget?
├── Unlimited → FP32 (baseline)
├── Moderate → FP16 or INT8 SQ
│   (-0.5% recall, 2× memory savings)
├── Tight → INT8 PQ (M=32)
│   (-1.5% recall, 8× memory savings)
└── Extreme (100M+ vectors) → Binary + rerank with full precision
    (-4% recall, 32× memory savings)
```

## Best Practices

- **Always evaluate recall after quantization.** The recall drop varies significantly by dataset and model.
- **INT8 SQ is free on modern hardware.** CPU SIMD (AVX-512) and GPU (INT8 tensor cores) process INT8 at 2× the throughput of FP32.
- **PQ search requires ADC distance computation.** It's not a simple dot product — make sure your vector DB supports it natively.
- **Binary + re-ranking is the cost-accuracy sweet spot** for large-scale search: search in binary space, re-rank top 100 with full precision embeddings.
- **Matryoshka models simplify deployment** — deploy one model, choose dimension per use case.
