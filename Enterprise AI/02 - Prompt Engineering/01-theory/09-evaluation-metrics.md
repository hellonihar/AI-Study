# Evaluation Metrics

Measuring prompt quality systematically — without measurement, prompt engineering is guesswork.

## Core Metrics

| Metric | What It Measures | How to Measure | Target |
|---|---|---|---|
| **Accuracy** | Correctness of output | Compare to ground truth | > 90% |
| **Faithfulness** | Output grounded in context | NLI-based entailment check | > 0.85 |
| **Completeness** | All aspects of question covered | LLM-as-judge rubric | > 0.9 |
| **Format compliance** | Output matches expected schema | Validate JSON/structured parse | > 99% |
| **Token efficiency** | Output length vs. minimal needed | Char/token ratio relative to ideal | < 1.5× ideal |
| **Latency impact** | Time added by prompt length | Measure TTFT difference vs. minimal | < 10% added |
| **Consistency** | Same output for same input | Run N times, measure variance | > 95% identical |

## Evaluation Methods

### Exact Match

Simple, fast, but fragile. Best for classification, extraction with known answers.

```
accuracy = count(prediction == ground_truth) / total
```

### Semantic Similarity

For tasks with multiple valid answers. Embed both prediction and ground truth, compare:

```
similarity = cosine_similarity(embed(prediction), embed(ground_truth))
```

**Threshold:** > 0.85 for acceptance.

### LLM-as-Judge

Use a separate LLM (preferably a different model) to score outputs:

```python
judge_prompt = """
On a scale of 1-5, rate the assistant's response for:
- Correctness: Does it answer correctly?
- Completeness: Does it cover all aspects?
- Conciseness: Is it free of unnecessary verbosity?

Ground truth: {ground_truth}
Assistant: {prediction}

Output format: {{"correctness": int, "completeness": int, "conciseness": int}}
"""
```

**Best judge models:** GPT-4o, Claude-3.5 Sonnet. Don't use the same model that generated the answers.

### Pairwise Comparison

Present two outputs (A/B) and ask: "Which is better?" Run across a dataset to compute win rate.

- More reliable than absolute scoring.
- Requires 2× LLM calls per eval item.

## Building an Eval Set

| Data Source | Size | Purpose |
|---|---|---|
| Curated golden set | 100–500 | Regression testing, release gates |
| Production logs (sampled) | 1000+ | Real-world distribution |
| Adversarial cases | 50–200 | Edge cases, injection attempts |
| Synthetic (LLM-generated) | 500+ | Coverage of rare scenarios |

**Golden set guidelines:**
- At least 100 examples per task.
- Cover all output classes/patterns.
- Include edge cases (empty input, very long input, ambiguous queries).
- Have 2+ humans review each example.

## Statistical Significance

Don't deploy a prompt change based on a handful of examples.

```
Sample size needed ≈ (Z² × p × (1-p)) / E²

95% confidence, detect 5% change:
  Z = 1.96, p = 0.90 (baseline), E = 0.05
  = (1.96² × 0.90 × 0.10) / 0.05²
  = 138 examples minimum
```

## Production Eval Pipeline

```
Deploy candidate prompt → Route 5% traffic to candidate
                         → Log all responses (baseline + candidate)
                         → Daily eval: score 500 sampled responses
                         → Compare: candidate win rate > 55%?
                           → Yes: roll out to 25% → 50% → 100%
                           → No: reject, analyze failure modes
```

## Best Practices

- **Measure before optimizing.** Establish baseline metrics before changing anything.
- **Track multiple metrics.** A prompt that improves accuracy but doubles latency may not be worth deploying.
- **Automate eval runs.** Run your eval suite on every prompt change — treat it like a CI test.
- **Beware of over-optimization.** A prompt that scores 98% on your golden set may generalize poorly. Test on held-out production samples.
- **Re-evaluate after model updates.** A prompt optimized for GPT-4-0613 may regress on GPT-4o.
