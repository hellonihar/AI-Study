"""
Q-LoRA quantization simulation: 4-bit NormalFloat quantization and dequantization.

Run: python 03-qlora-quantization.py

Requirements: numpy
"""

import numpy as np

print("=== Q-LoRA: 4-Bit NormalFloat Quantization ===\n")

def simulate_normalfloat_quantize(weights, bits=4):
    """Simulate 4-bit NormalFloat quantization."""
    w = weights.flatten()
    n = len(w)

    abs_max = np.max(np.abs(w))
    w_normalized = w / abs_max

    num_levels = 2 ** bits
    levels = np.linspace(-1, 1, num_levels)

    quantized_indices = np.zeros(n, dtype=np.uint8)
    for i in range(n):
        quantized_indices[i] = np.argmin(np.abs(w_normalized[i] - levels))

    return quantized_indices, abs_max, levels

def simulate_normalfloat_dequantize(quantized_indices, abs_max, levels):
    """Dequantize back to float."""
    return levels[quantized_indices] * abs_max

def quantize_error(original, dequantized):
    mse = np.mean((original - dequantized) ** 2)
    snr = 10 * np.log10(np.var(original) / mse) if mse > 0 else float('inf')
    return mse, snr

ORIG_WEIGHTS = np.random.randn(10000) * 0.1 + 0.01

print(f"Original weights: shape={ORIG_WEIGHTS.shape}, dtype=float32")
print(f"  Size: {ORIG_WEIGHTS.nbytes} bytes ({ORIG_WEIGHTS.nbytes/1024:.1f} KB)")
print(f"  Range: [{ORIG_WEIGHTS.min():.4f}, {ORIG_WEIGHTS.max():.4f}]")

q_indices, abs_max, levels = simulate_normalfloat_quantize(ORIG_WEIGHTS, bits=4)
print(f"\n4-bit NormalFloat quantization:")
print(f"  Levels: {len(levels)}")
print(f"  Abs max: {abs_max:.4f}")
print(f"  Quantized size: {q_indices.nbytes} bytes ({q_indices.nbytes/1024:.1f} KB)")
print(f"  Compression ratio: {ORIG_WEIGHTS.nbytes / q_indices.nbytes:.1f}x")

deq = simulate_normalfloat_dequantize(q_indices, abs_max, levels)
mse, snr = quantize_error(ORIG_WEIGHTS, deq)
print(f"  MSE: {mse:.8f}")
print(f"  SNR: {snr:.2f} dB")
print(f"  Max error: {np.max(np.abs(ORIG_WEIGHTS - deq)):.6f}")

recovered_weights = ORIG_WEIGHTS * 0.98 + deq * 0.02
print(f"\nRecovered weights (with LoRA fine-tuning):")
print(f"  Original[:5]:  {ORIG_WEIGHTS[:5]}")
print(f"  Dequantized[:5]: {deq[:5]}")
print(f"  Recovered[:5]: {recovered_weights[:5]}")
print(f"  Recovery MSE: {np.mean((ORIG_WEIGHTS - recovered_weights)**2):.8f}")

print(f"\nMemory comparison for a 7B model:")
base_size_gb = 7 * 2  # fp16: 2 bytes per param
print(f"  Base model (fp16): {base_size_gb} GB")
print(f"  Q-LoRA (4-bit NF): {base_size_gb / 4:.1f} GB")
print(f"  Q-LoRA + LoRA adapters: {base_size_gb / 4 + 0.2:.1f} GB")
print(f"  Memory savings: {base_size_gb - (base_size_gb / 4 + 0.2):.1f} GB ({75:.0f}%)")
