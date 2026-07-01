# Evaluation Metrics for Fine-Tuning

## Three-Axis Evaluation Framework

Every fine-tuned model must be evaluated on three axes:

1. **Task Performance**: How well does it do the target task?
2. **General Capability**: What did we lose?
3. **Safety & Robustness**: Did we introduce harm?

## Axis 1: Task Performance

### Task-Specific Metrics

| Task | Primary Metric | Secondary Metrics |
|------|---------------|-------------------|
| Classification | Accuracy, F1 | Precision, Recall, AUC-ROC |
| Summarization | ROUGE-L, ROUGE-1/2 | BERTScore, Factual Consistency |
| Translation | BLEU, chrF | COMET, BLEURT |
| Code Generation | Pass@k | Syntax Validity, Functional Correctness |
| QA | Exact Match, F1 | Answer Accuracy, Hallucination Rate |
| Instruction Following | LLM-as-Judge Score | Human Preference Rate |
| Text Generation | Perplexity | Repetition Rate, Diversity |

### Statistical Significance

Always report confidence intervals (95% CI via bootstrap). A 0.5% improvement on a 10,000-example test set may be significant; the same improvement on 100 examples is noise.

### Test Set Design
- Held-out: never used for any training decision
- Representative: matches production input distribution
- Sized for significance: minimum 500 examples for high-signal metrics, 2000+ for noisy metrics like ROUGE

## Axis 2: General Capability Retention

### Benchmark Suite

| Benchmark | What It Measures | Size |
|-----------|-----------------|------|
| MMLU | Knowledge across 57 subjects | ~14k questions |
| HellaSwag | Commonsense reasoning | ~10k examples |
| ARC | Science reasoning (easy/challenge) | ~8k questions |
| GSM8K | Grade school math | ~8k problems |
| HumanEval | Code generation | 164 problems |
| TruthfulQA | Factuality | 817 questions |
| BBH | Big-Bench Hard reasoning | ~6k examples |

### For Production Models

Running the full suite is costly. Maintain a **regression subset**:
- 500 examples covering each capability dimension
- Run after every training run
- Flag any metric drop > 2% for review

### Catastrophic Forgetting Detection

Track degradation across capabilities:

| Signal | Action |
|--------|--------|
| Single benchmark drops > 5% | Investigate — may need replay data |
| Multiple benchmarks drop > 3% | Stop training, adjust data mix |
| All benchmarks drop | Learning rate too high or overfitting |
| No benchmarks drop | Likely safe — but verify on production traffic |

## Axis 3: Safety & Robustness

### Safety Benchmarks

| Benchmark | Focus |
|-----------|-------|
| BBQ | Bias across social categories |
| Toxigen | Hate speech and toxicity |
| TruthfulQA | Misinformation susceptibility |
| AdvBench | Adversarial jailbreak attempts |
| RealToxicityPrompts | Continuation toxicity |

### Red Teaming

Automated red teaming using another LLM to generate adversarial inputs. Measure:
- Refusal rate for harmful requests
- Accuracy of refusals (appropriate vs over-refusal)
- Bias in refusals across demographic groups

### Perturbation Robustness

Test the model's stability under input variations:
- Typographical errors
- Synonym substitutions
- Rephrasing
- Unusual formatting

## Evaluation Infrastructure

### Automated Evaluation Pipeline

```
Training Run → Checkpoint → Evaluation Suite → Report → Decision
```

1. **Trigger**: On training completion or at checkpoint intervals
2. **Execute**: Run all benchmarks in parallel where possible
3. **Compare**: Against baseline model + previous checkpoint
4. **Report**: Structured JSON output + dashboard update
5. **Alert**: Pager if regression exceeds thresholds

### LLM-as-Judge Evaluation

Using a strong LLM (GPT-4, Claude) to evaluate output quality:

**Pros:**
- No human annotation cost per eval
- Consistent criteria across runs
- Can evaluate subjective quality (helpfulness, tone)

**Cons:**
- Judge model has its own biases
- Position bias (prefers first or second response)
- Verbosity bias (prefers longer responses)

**Mitigations:**
- Swap response order and average scores
- Use a rubric with explicit criteria
- Calibrate against human judgments periodically

## Reporting Standards

Every fine-tuning experiment report should include:

```
## Model Card
- Base model: [name, version]
- Training data: [source, size, dates]
- Hyperparameters: [LR, batch size, epochs, PEFT method]
- Compute: [hardware, hours, cost]

## Task Performance
- Primary metric: [value ± CI]
- Secondary metrics: [values]
- Test set: [size, source]

## General Capability
- MMLU: [value vs baseline]
- HellaSwag: [value vs baseline]
- GSM8K: [value vs baseline]

## Safety
- Toxicity: [score]
- Bias: [score]
- Red team: [pass/fail on key categories]

## Decision
- Approve / Flag / Reject
- Rationale:
```
