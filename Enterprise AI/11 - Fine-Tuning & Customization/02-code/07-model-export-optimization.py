"""
Model export and optimization: quantization, ONNX export simulation, and inference benchmarking.

Run: python 07-model-export-optimization.py

Requirements: numpy
"""

import numpy as np
import time

print("=== Model Export & Optimization ===\n")

class QuantizedModel:
    def __init__(self, weights, bits=8):
        self.bits = bits
        self.original_weights = weights.copy()
        self.quantize(weights)

    def quantize(self, weights):
        w = weights.flatten()
        self.abs_max = np.max(np.abs(w))

        if self.bits == 8:
            levels = 256
            self.scale = self.abs_max / 127.0
            self.q_weights = np.clip(np.round(w / self.scale), -127, 127).astype(np.int8)
        elif self.bits == 4:
            levels = 16
            self.q_weights = np.zeros(len(w), dtype=np.uint8)
            quantized = np.round((w / self.abs_max + 1) * 7.5).astype(np.uint8)
            self.q_weights = np.clip(quantized, 0, 15)
            self.scale = self.abs_max / 7.5

    def dequantize(self):
        if self.bits == 8:
            return self.q_weights.astype(np.float32) * self.scale
        else:
            return (self.q_weights.astype(np.float32) - 7.5) * self.scale

    def compute_metrics(self):
        deq = self.dequantize()
        orig = self.original_weights.flatten()
        mse = np.mean((orig - deq) ** 2)
        snr = 10 * np.log10(np.var(orig) / mse) if mse > 0 else float('inf')
        max_err = np.max(np.abs(orig - deq))

        orig_size = orig.nbytes
        quant_size = self.q_weights.nbytes
        return {
            "mse": float(mse),
            "snr_db": float(snr),
            "max_error": float(max_err),
            "original_size_mb": orig_size / (1024 * 1024),
            "quantized_size_mb": quant_size / (1024 * 1024),
            "compression_ratio": orig_size / quant_size,
        }

LAYER_WEIGHTS = {
    "embedding": np.random.randn(32000, 4096).astype(np.float32),
    "attention_q": np.random.randn(4096, 4096).astype(np.float32),
    "attention_k": np.random.randn(4096, 4096).astype(np.float32),
    "attention_v": np.random.randn(4096, 4096).astype(np.float32),
    "attention_o": np.random.randn(4096, 4096).astype(np.float32),
    "ffn_gate": np.random.randn(4096, 11008).astype(np.float32),
    "ffn_up": np.random.randn(4096, 11008).astype(np.float32),
    "ffn_down": np.random.randn(11008, 4096).astype(np.float32),
}

total_fp32 = sum(w.nbytes for w in LAYER_WEIGHTS.values())
print(f"Original model (fp32): {total_fp32 / (1024**3):.2f} GB")
print(f"Original model (fp16): {total_fp32 / (1024**3) / 2:.2f} GB")

print(f"\nQuantization results:")
print(f"{'Bits':>6} {'Original':>12} {'Quantized':>12} {'Ratio':>8} {'MSE':>14} {'SNR (dB)':>10}")
print("-" * 62)

for bits in [8, 4]:
    quantizer = QuantizedModel(LAYER_WEIGHTS["attention_q"], bits=bits)
    metrics = quantizer.compute_metrics()
    print(f"{bits:>4}bit {metrics['original_size_mb']:>8.2f}MB "
          f"{metrics['quantized_size_mb']:>8.2f}MB "
          f"{metrics['compression_ratio']:>7.1f}x "
          f"{metrics['mse']:>12.8f} "
          f"{metrics['snr_db']:>8.2f}")

print(f"\nInference speed simulation:")
model_sizes = [
    ("7B  (fp16)", 7, 2),
    ("7B  (int8)", 7, 1),
    ("7B  (int4)", 7, 0.5),
    ("70B (fp16)", 70, 2),
    ("70B (int8)", 70, 1),
    ("70B (int4)", 70, 0.5),
]

print(f"{'Model':>14} {'Memory':>10} {'Speedup':>10}")
print("-" * 36)
for name, size_gb, factor in model_sizes:
    mem = size_gb * factor
    speedup = 2.0 / factor
    print(f"{name:>14} {mem:>6.1f}GB {speedup:>8.1f}x")

print(f"\nExport format summary:")
print(f"  ONNX:     graph-level optimizations, cross-platform")
print(f"  TorchScript: PyTorch-native, limited platform support")
print(f"  GGUF:     llama.cpp ecosystem, CPU-focused")
print(f"  SafeTensors: zero-copy loading, fast startup")
