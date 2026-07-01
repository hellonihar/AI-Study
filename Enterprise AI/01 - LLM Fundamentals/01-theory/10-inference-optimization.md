# Inference Optimization

Techniques to reduce latency and increase throughput of LLM inference.

## Quantization

Reducing numerical precision of weights and/or activations.

| Format | Bits | Memory vs FP16 | Quality Impact | Hardware |
|---|---|---|---|---|
| FP16 | 16 | 1× | Baseline | Most GPUs |
| FP8 | 8 | 0.5× | ~0.1% loss | H100, Ada Lovelace |
| INT8 (W8A8) | 8 | 0.5× | ~0.3% loss | All GPUs |
| INT4 (GPTQ/AWQ) | 4 | 0.25× | ~1% loss | All GPUs |
| NF4 (QLoRA) | 4 | 0.25× | ~1% loss | All GPUs |
| GGUF Q4_K_M | ~4.5 | 0.28× | ~1% loss | CPU/Apple Silicon |

**Best practice:** Use FP8 for production deployments (H100), INT4-GPTQ for memory-constrained self-hosted setups.

## Speculative Decoding

Use a fast "draft" model to propose tokens, verified by the target model in one forward pass.

```
Draft model (e.g., 7B): generates K candidate tokens one-by-one
Target model (e.g., 70B): verifies all K tokens in a single parallel pass
If verification fails at position i: discard tokens from i onward, resample
```

- **Speedup:** 1.5–3× for 70B when draft is 7B.
- **No quality loss** — verifier guarantees the same distribution as target-only.

## Flash Attention

As covered in [05-attention-mechanism.md](05-attention-mechanism.md):
- Tiles attention computation to SRAM.
- 2–4× faster, O(n) memory instead of O(n²).

## Continuous Batching (vLLM)

Instead of waiting for a batch to finish, add/remove sequences dynamically:

- **Static batching:** Pad all sequences to same length, wait for slowest.
- **Continuous batching:** Process variable-length sequences together, evict finished ones immediately.

Result: **2–3× throughput increase** over static batching.

## PagedAttention (vLLM)

KV cache is stored in non-contiguous blocks (like virtual memory pages):

- Eliminates internal fragmentation.
- Enables copy-on-write for shared prefixes.
- Increases batch sizes by 2–4×.

## Tensor Parallelism

Split one layer across multiple GPUs:

```
Self-Attention: split heads across GPUs
FFN: split columns across GPUs
```

All-to-all communication after each layer. Efficient for 2–8 GPUs per model replica.

## Pipeline Parallelism

Split layers across GPUs (layer 1–20 on GPU 0, 21–40 on GPU 1). Lower communication but higher idle time (bubble). Less efficient than tensor parallelism for most workloads.

## Best Practices

| Scenario | Recommended |
|---|---|
| Single GPU, latency-sensitive | Quantize (FP8/INT4), use Flash Attention |
| Multi-GPU, throughput-sensitive | Tensor parallelism + continuous batching |
| CPU-only deployment | GGUF format with llama.cpp |
| Mixed workloads | vLLM with prefix caching + PagedAttention |
| Largest possible context | Flash Attention + INT4 quantization + GQA |
