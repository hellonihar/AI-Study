# Resources — Fine-Tuning & Customization

## Foundational Papers

| Paper | Year | Contribution |
|-------|------|-------------|
| [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685) | 2021 | Introduced low-rank adaptation for efficient fine-tuning |
| [QLoRA: Efficient Finetuning of Quantized LLMs](https://arxiv.org/abs/2305.14314) | 2023 | 4-bit NormalFloat quantization + LoRA |
| [Direct Preference Optimization](https://arxiv.org/abs/2305.18290) | 2023 | Preference optimization without RL |
| [Training Language Models to Follow Instructions with Human Feedback](https://arxiv.org/abs/2203.02155) | 2022 | RLHF with InstructGPT |
| [Scaling Down: Pruning and Quantization](https://arxiv.org/abs/2301.00774) | 2023 | Model compression survey |
| [ORPO: Monolithic Preference Optimization](https://arxiv.org/abs/2403.07691) | 2024 | Combined SFT + preference optimization |
| [KTO: Model Alignment as Prospect Theoretic Optimization](https://arxiv.org/abs/2402.01306) | 2024 | Binary feedback alignment |
| [PEFT: Parameter-Efficient Fine-Tuning](https://arxiv.org/abs/2307.00292) | 2023 | Comprehensive PEFT survey |
| [Elastic Weight Consolidation](https://arxiv.org/abs/1612.00796) | 2016 | Catastrophic forgetting mitigation |
| [The Power of Scale for Parameter-Efficient Prompt Tuning](https://arxiv.org/abs/2104.08691) | 2021 | Prompt tuning methodology |

## Frameworks & Libraries

| Framework | Description |
|-----------|-------------|
| [Hugging Face PEFT](https://github.com/huggingface/peft) | LoRA, Q-LoRA, Adapters, IA3 |
| [Hugging Face TRL](https://github.com/huggingface/trl) | RLHF, DPO, ORPO trainers |
| [Axolotl](https://github.com/OpenAccess-AI-Collective/axolotl) | Streamlined fine-tuning framework |
| [Unsloth](https://github.com/unslothai/unsloth) | Optimized Q-LoRA (2x faster) |
| [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) | Unified fine-tuning framework |
| [DeepSpeed](https://github.com/microsoft/DeepSpeed) | Distributed training optimization |
| [vLLM](https://github.com/vllm-project/vllm) | High-throughput serving with LoRA |
| [TGI](https://github.com/huggingface/text-generation-inference) | Hugging Face model serving |
| [ONNX Runtime](https://github.com/microsoft/onnxruntime) | Cross-platform inference engine |
| [TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM) | NVIDIA optimized inference |
| [bitsandbytes](https://github.com/TimDettmers/bitsandbytes) | 4-bit/8-bit quantization |
| [AWQ](https://github.com/mit-han-lab/llm-awz) | Activation-aware weight quantization |
| [GPTQ](https://github.com/IST-DASLab/gptq) | Post-training quantization |
| [llama.cpp](https://github.com/ggerganov/llama.cpp) | CPU inference with GGUF format |
| [MLflow](https://mlflow.org/) | Experiment tracking and model registry |
| [Weights & Biases](https://wandb.ai/) | Experiment tracking platform |
| [Neptune](https://neptune.ai/) | Experiment tracking and model registry |

## Datasets

| Dataset | Description | Size |
|---------|-------------|------|
| [OpenAssistant Conversations](https://huggingface.co/datasets/OpenAssistant/oasst1) | Multi-turn human conversations | ~88k messages |
| [ShareGPT](https://huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered) | User-ChatGPT conversations | ~90k conversations |
| [Dolly](https://huggingface.co/datasets/databricks/databricks-dolly-15k) | Instruction-following examples | ~15k examples |
| [Alpaca](https://huggingface.co/datasets/tatsu-lab/alpaca) | Self-instruct generated data | ~52k examples |
| [UltraFeedback](https://huggingface.co/datasets/openbmb/UltraFeedback) | Preference data for alignment | ~64k comparisons |
| [No Robots](https://huggingface.co/datasets/HuggingFaceH4/no_robots) | High-quality human-written instructions | ~10k examples |
| [LMSYS Chat](https://huggingface.co/datasets/lmsys/lmsys-chat-1m) | Real user conversations | ~1M conversations |

## Evaluation

| Tool | Description |
|------|-------------|
| [LM Eval Harness](https://github.com/EleutherAI/lm-evaluation-harness) | Standardized benchmark evaluation |
| [MT Bench](https://github.com/lm-sys/FastChat/tree/main/fastchat/llm_judge) | Multi-turn judge evaluation |
| [AlpacaEval](https://github.com/tatsu-lab/alpaca_eval) | Automated LLM evaluation |
| [Arena Hard Auto](https://github.com/lm-sys/arena-hard-auto) | Hard task auto-evaluation |
| [HumanEval](https://github.com/openai/human-eval) | Code generation evaluation |
| [TruthfulQA](https://github.com/sylinrl/TruthfulQA) | Factuality benchmark |

## Tutorials & Guides

- [Hugging Face PEFT Documentation](https://huggingface.co/docs/peft) — PEFT library guide
- [Hugging Face TRL Documentation](https://huggingface.co/docs/trl) — RLHF/DPO training guide
- [LoRA Fine-Tuning Guide](https://huggingface.co/blog/peft) — Practical LoRA tutorial
- [QLoRA Fine-Tuning](https://huggingface.co/blog/4bit-transformers-bitsandbytes) — 4-bit quantization guide
- [DPO Training Tutorial](https://huggingface.co/blog/dpo-trl) — DPO with TRL
- [Fine-Tuning with Axolotl](https://github.com/OpenAccess-AI-Collective/axolotl#readme) — Axolotl quickstart
- [vLLM LoRA Serving](https://docs.vllm.ai/en/latest/features/lora.html) — Multi-adapter serving with vLLM
- [DeepSpeed Tutorial](https://www.deepspeed.ai/tutorials/) — Distributed training setup

## Books

| Title | Author | Year |
|-------|--------|------|
| Natural Language Processing with Transformers | Lewis Tunstall, Leandro von Werra, Thomas Wolf | 2022 |
| Deep Learning | Ian Goodfellow, Yoshua Bengio, Aaron Courville | 2016 |
| Speech and Language Processing | Daniel Jurafsky, James H. Martin | 2024 (online) |
| Understanding Deep Learning | Simon J.D. Prince | 2023 |
