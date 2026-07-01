# Multi-Task Fine-Tuning & Domain Adaptation

## Multi-Task Fine-Tuning

Training a single model on multiple tasks simultaneously. Each task shares the base model but may have task-specific heads or adapters.

### Architecture Patterns

#### Shared Backbone + Task-Specific Heads
```
Input → Base Model → Task A Head → Task A Output
                   → Task B Head → Task B Output
                   → Task C Head → Task C Output
```

**Best for:** Classification tasks where tasks share input features but need different output layers.

#### Shared Everything (Single Loss)
```
Input → Model → Output (all tasks mixed in training data)
```

**Best for:** Instruction-tuned models where tasks are diverse but share a common format (instruction → response).

#### Adapter Per Task
```
Input → Base Model + Adapter A → Output A
         Base Model + Adapter B → Output B
```

**Best for:** When tasks are too divergent to share weights effectively. Adapters can be combined or selected at inference.

### Data Mixing Strategies

| Strategy | Description | Best For |
|----------|-------------|----------|
| Proportional | Samples per task proportional to dataset size | Simple, unbiased |
| Temperature scaling | Adjust sampling probability: p_i = (|D_i|^α) / Σ(|D_j|^α) | Control task balance |
| Loss-weighted | Weight tasks by inverse validation loss | Focus on hard tasks |
| Curriculum | Easy tasks first, complex later | Progressive learning |

### Loss Balancing

When tasks have different scales or difficulties:

| Method | Description |
|--------|-------------|
| Equal weighting | All tasks contribute equally to total loss |
| Uncertainty weighting | Learnable task weights based on homoscedastic uncertainty |
| Dynamic prioritization | Weight tasks based on plateau detection (increase weight for stalled tasks) |
| Gradient surgery | Project conflicting gradients to avoid interference |

### Benefits vs Single-Task Models

| Aspect | Multi-Task | Single-Task |
|--------|------------|-------------|
| Parameter efficiency | 1 model vs N models | N models |
| Inference cost | 1× vs N× | N× |
| Cross-task transfer | Positive transfer possible | None |
| Task interference | Negative transfer risk | None |
| Data efficiency | Shared representations | Task-specific only |
| Maintenance | Single deployment, update cycle | N deployments |

## Domain Adaptation

Adapting a general model to a specific domain (legal, medical, finance, code) where vocabulary, style, and reasoning patterns differ from pre-training data.

### Domain Adaptation Spectrum

| Depth | Method | Data Required | Impact |
|-------|--------|---------------|--------|
| Light | Prompt engineering | None | Minimal |
| Medium | In-context examples | 10–100 | Moderate |
| Heavy | Domain-specific fine-tuning | 500–5000+ | Significant |
| Extreme | Domain-specific pre-training | 1B+ tokens | Full domain mastery |

### Techniques

#### Continued Pre-Training
Train the base model on domain-specific text using the language modeling objective (predict next token). This teaches domain vocabulary and knowledge without task-specific supervision.

**Data:** Raw domain text (papers, articles, code, transcripts)
**Duration:** 10–50 billion tokens typically
**Risk:** Catastrophic forgetting if over-trained

#### Domain-Specific Fine-Tuning
Fine-tune on task-specific (instruction, input, output) triples from the domain.

**Data:** Expert-written or curated demonstrations
**Duration:** 500–5000 examples sufficient

#### Vocabulary Extension
Add domain-specific tokens to the tokenizer:
1. Analyze domain text for common subwords the tokenizer splits inefficiently
2. Add new tokens to vocabulary (e.g., medical terms, chemical formulas, code identifiers)
3. Initialize embeddings for new tokens (average of constituent subword embeddings)
4. Fine-tune with new tokens

**Benefit:** Up to 2x inference speed improvement for domain text (fewer tokens per input).

### Domain Evaluation

| Aspect | General Benchmark | Domain Benchmark |
|--------|------------------|------------------|
| Knowledge | MMLU (general) | Domain-specific exam questions |
| Vocabulary | Standard perplexity | Domain perplexity |
| Reasoning | GSM8K, BBH | Domain-specific reasoning tasks |
| Style | General writing quality | Domain-appropriate style evaluation |

## Catastrophic Forgetting Mitigation

### Elastic Weight Consolidation (EWC)

Add a regularization term that penalizes changing important weights:

```
L_total = L_task + λ * Σ_i F_i * (θ_i - θ_base_i)²
```

Where F_i is the Fisher information matrix diagonal — a measure of weight importance.

### Replay / Experience Replay

Mix domain data with general data during training:

```
Batch = 70% domain-specific data + 30% general capability data
```

The general data replay preserves broad capabilities while the domain data drives specialization.

### Progressive Memory

Maintain separate memory buffers for different capabilities and replay proportional to forgetting rate. Tasks showing decline get higher replay frequency.

## Domain-Specific Considerations

### Legal
- **Vocabulary**: Case citations, statutes, legal Latin
- **Format**: Strict citation format, syllogistic reasoning
- **Risk**: Hallucinated precedents are unacceptable — must be verifiable
- **Strategy**: SFT on briefs and rulings + RAG for citation verification

### Medical
- **Vocabulary**: Drug names, procedures, anatomy
- **Format**: Clinical notes, discharge summaries, research abstracts
- **Risk**: Errors can cause patient harm — full factual accuracy required
- **Strategy**: Continued pre-training on medical corpus + SFT + alignment for safety

### Finance
- **Vocabulary**: Ticker symbols, financial ratios, regulatory terms
- **Format**: Reports, filings, market commentary
- **Risk**: Regulatory compliance (SEC, FCA), market-moving errors
- **Strategy**: SFT on filings + quantitative analysis capabilities

### Code
- **Vocabulary**: Language keywords, library names, patterns
- **Format**: Executable code, documentation, tests
- **Risk**: Non-deterministic outputs can introduce subtle bugs
- **Strategy**: SFT on verified code + execution-based evaluation
