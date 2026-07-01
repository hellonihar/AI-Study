# Transformer Architecture

## Overview

The Transformer (Vaswani et al., 2017) replaced RNNs with a purely attention-based architecture, enabling parallel processing of all tokens. Modern LLMs are almost exclusively **decoder-only** variants.

## Encoder-Decoder vs. Decoder-Only

| Architecture | Used By | Characteristics |
|---|---|---|
| Encoder-Decoder | T5, BART, original Transformer | Bidirectional encoder context + autoregressive decoder. Best for seq2seq (translation, summarization). |
| Encoder-Only | BERT, RoBERTa | Bidirectional attention. Best for understanding tasks (classification, NER, retrieval). |
| Decoder-Only | GPT, LLaMA, Mistral, Claude | Causal (unidirectional) attention. Best for generation. Scales better — ~all frontier models are decoder-only. |

## Core Components

```
Input Tokens → [Embedding + Positional Encoding] → [N× Decoder Blocks] → [LM Head] → Output Logits
```

Each decoder block contains:

1. **Causal Self-Attention** — each token attends only to itself and previous tokens (masked future).
2. **Feed-Forward Network** — two or three linear layers with a non-linearity (SwiGLU, ReLU, GELU).
3. **Residual Connections** — skip connections around each sub-layer: `output = LayerNorm(x + sublayer(x))`.
4. **Pre-Norm vs Post-Norm** — modern models use Pre-LayerNorm (stabler training, no warmup needed).

## Key Architectural Decisions

- **Depth (layers):** 12 (7B) to 96 (GPT-4). Deeper → better reasoning, higher latency.
- **Width (d_model):** 768 (BERT-base) to 12288 (GPT-4). Wider → more capacity per layer.
- **FFN ratio:** Typically 4× d_model. SwiGLU reduces to ~2.7× but with 3 matrices instead of 2.
- **Head dimension:** Usually 64 or 128. Fixed head_dim means more heads = wider model.
- **Vocab size:** 32K (LLaMA-1) to 128K (GPT-4, LLaMA-3). Larger vocab → fewer tokens per word → faster inference.

## Best Practice

- Decoder-only with Pre-LayerNorm and SwiGLU FFN is the current Pareto-optimal architecture.
- For custom training, use an existing architecture (LLaMA, Mistral) rather than designing from scratch — the hyperparameters are already optimized.
