# Quantization Guide

Reducing model precision to fit on fewer GPUs or run faster.

## Format Overview

| Format | Bits | Memory (70B) | Quality | Hardware | Use Case |
|---|---|---|---|---|---|
| FP16 | 16 | 140 GB | Baseline | All GPUs | Maximum quality, multi-GPU |
| FP8 | 8 | 70 GB | ~0.1% loss | H100, Ada | Production inference on H100 |
| INT8 (W8A16) | 8 weights | 70 GB | ~0.3% loss | All GPUs | Balanced quality/memory |
| INT4 (GPTQ) | 4 weights | 35 GB | ~1% loss | All GPUs | Single-GPU 70B deployment |
| INT4 (AWQ) | 4 weights | 35 GB | ~0.8% loss | All GPUs | Better than GPTQ for same bits |
| INT4 (GGUF Q4_K_M) | 4.5 mixed | ~40 GB | ~1% loss | CPU/Apple | Consumer hardware |
| NF4 (QLoRA) | 4 | 35 GB | ~1% loss | All GPUs | Fine-tuning on consumer GPU |
| INT3 | 3 | ~26 GB | ~3% loss | CPU only | Extreme memory saving |
| INT2 | 2 | ~18 GB | ~5% loss | CPU only | Last resort |

## Which Format to Use

```
GPU available?
├── H100 → FP8 (no quality loss, 2× memory savings)
├── A100/A6000 → INT4-AWQ (single GPU for 70B)
├── RTX 4090 → INT4-GGUF (runs via llama.cpp)
├── RTX 3090 → INT4-GGUF or QLoRA NF4
└── No GPU → GGUF Q4_K_M via llama.cpp (CPU)
```

## Calibration Data Matters

GPTQ and AWQ require calibration data — a small set of representative examples:

```python
# AWQ example
from awq import AutoAWQForCausalLM

model = AutoAWQForCausalLM.from_pretrained("meta-llama/Llama-2-7b")
model.quantize(
    quant_config={"bits": 4, "group_size": 128},
    calib_data=["Your domain-specific text..."]  # ~128 samples
)
model.save_quantized("llama-7b-awq")
```

- **Use domain-specific calibration** for best quality (e.g., legal text for a legal model).
- **128–256 samples** is sufficient — more doesn't help.
- **Never use test data** as calibration (information leak).

## Quality Impact by Task

| Task | FP16 → FP8 | FP16 → INT4 |
|---|---|---|
| Summarization | ~0.1% drop | ~0.5% drop |
| QA (factual) | ~0.2% drop | ~1.0% drop |
| Code generation | ~0.1% drop | ~0.8% drop |
| Creative writing | ~0.1% drop | ~0.3% drop |
| Math reasoning | ~0.5% drop | ~2.0% drop |

**Math is the most sensitive** — consider keeping FP16 for math-heavy workloads.

## Best Practices

- **Always eval after quantization** — run your eval suite on the quantized model before deploying.
- **Group size 128** is the sweet spot for INT4 — smaller (32) is better quality but slower, larger (256) is faster but worse.
- **FP8 is "free" on H100** — no quality loss, use it as default.
- **Mixing quantization** — keep attention layers at higher precision than FFN layers (AWQ does this automatically).
- **Avoid dynamic quantization** for production — static quantization (pre-computed scales) is faster and more stable.
