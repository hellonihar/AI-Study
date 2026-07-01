# Fine-Tuning & Customization

Adapting pre-trained models to domain-specific tasks through supervised fine-tuning, parameter-efficient methods, and preference alignment.

## Module Structure

```
11 - Fine-Tuning & Customization/
├── 01-theory/          # 10 files: overview through production pipeline
├── 02-code/            # 10 scripts: data prep through production system
├── 03-best-practices/  # 5 files: data quality, PEFT, eval, deployment, governance
├── 04-resources/       # Papers, frameworks, datasets, tutorials, books
└── README.md           # This file
```

## Theory (01-theory/)

| # | File | Topic |
|---|------|-------|
| 1 | `01-fine-tuning-overview.md` | When to fine-tune vs RAG vs prompting, types of FT |
| 2 | `02-data-preparation.md` | Collection, cleaning, dedup, formatting, filtering, splitting |
| 3 | `03-peft-lora-qlora.md` | LoRA, Q-LoRA, Adapters, Prefix Tuning, IA3 — selection guide |
| 4 | `04-full-fine-tuning.md` | When full FT is justified, infrastructure, memory, checkpointing |
| 5 | `05-alignment-rlhf-dpo.md` | RLHF, DPO, ORPO, KTO — comparison and recommendations |
| 6 | `06-evaluation-metrics.md` | Three-axis evaluation, benchmarks, LLM-as-judge |
| 7 | `07-deployment-optimization.md` | vLLM, TGI, ONNX, quantization, speculative decoding |
| 8 | `08-continuous-fine-tuning.md` | Data flywheel, feedback loops, CI/CD, drift detection |
| 9 | `09-multitask-and-domain-adaptation.md` | Multi-task FT, domain adaptation, vocabulary extension |
| 10 | `10-production-fine-tuning.md` | End-to-end pipeline, infra as code, cost management, DR |

## Code Examples (02-code/)

| # | File | Description | Requirements |
|---|------|-------------|--------------|
| 1 | `01-data-preparation.py` | Dedup (exact + near), quality filter, format conversion | none (stdlib) |
| 2 | `02-lora-simulation.py` | Low-rank adaptation mechanics with attention block | numpy |
| 3 | `03-qlora-quantization.py` | 4-bit NormalFloat quantization/dequantization simulation | numpy |
| 4 | `04-full-fine-tuning-simulation.py` | Full FT memory estimation, training, checkpointing | numpy |
| 5 | `05-dpo-simulation.py` | Direct Preference Optimization alignment training | numpy |
| 6 | `06-evaluation-pipeline.py` | Three-axis evaluation with pass/fail decision | numpy |
| 7 | `07-model-export-optimization.py` | Quantization (INT8/INT4), compression metrics | numpy |
| 8 | `08-continuous-fine-tuning.py` | Feedback collection, drift detection, auto-retraining | numpy |
| 9 | `09-domain-adaptation.py` | Continued pre-training, vocabulary extension, forgetting detection | numpy |
| 10 | `10-production-fine-tuning-pipeline.py` | End-to-end pipeline: validate → train → eval → deploy | numpy |

## Best Practices (03-best-practices/)

| # | File | Topic |
|---|------|-------|
| 1 | `01-data-quality.md` | Data quality checklist, annotation guidelines, synthetic data, versioning |
| 2 | `02-peft-strategy.md` | PEFT method selection, LoRA config, hyperparameters, adapter management |
| 3 | `03-evaluation-and-regression.md` | Three-axis eval, regression testing, A/B testing, rollback criteria |
| 4 | `04-deployment-and-serving.md` | Serving framework selection, quantization strategy, auto-scaling |
| 5 | `05-iteration-and-governance.md` | Model lifecycle, versioning, experiment tracking, compliance, cost optimization |

## Key Topics

- **PEFT**: LoRA, Q-LoRA, Adapters, Prefix Tuning, IA3
- **Alignment**: RLHF, DPO, ORPO, KTO
- **Data**: Curation, deduplication, quality filtering, synthetic generation
- **Evaluation**: Task metrics, capability regression, safety/robustness
- **Deployment**: vLLM, TGI, ONNX, quantization (FP8, INT8, INT4, NF4)
- **Continuous FT**: Data flywheel, drift detection, automated retraining
- **Domain Adaptation**: Continued pre-training, vocabulary extension, forgetting mitigation
- **Production**: CI/CD pipelines, canary deployment, rollback, cost optimization

## Quick Start

```bash
# LoRA mechanics simulation
python "02-code/02-lora-simulation.py"

# DPO alignment training
python "02-code/05-dpo-simulation.py"

# Evaluation pipeline
python "02-code/06-evaluation-pipeline.py"

# Production pipeline
python "02-code/10-production-fine-tuning-pipeline.py"
```

## Prerequisites

- **Python 3.10+**
- **Core**: numpy (for most scripts)
- **Stdlib only**: Script 1 (data preparation)
