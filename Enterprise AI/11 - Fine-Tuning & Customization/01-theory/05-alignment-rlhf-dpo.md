# Alignment: RLHF, DPO, and Beyond

## Why Alignment Matters

A base model is trained to predict the next token — not to be helpful, harmless, or honest. Alignment tuning steers the model toward human preferences.

### The Alignment Problem

Without alignment, models may:
- Produce technically correct but unhelpful responses
- Generate harmful or biased content
- Fail to follow instructions accurately
- Be overly verbose or evasive

## RLHF (Reinforcement Learning from Human Feedback)

### The Three-Step Process

#### Step 1: Supervised Fine-Tuning (SFT)
Fine-tune the base model on high-quality demonstrations of desired behavior. This teaches the model the basic format and style of good responses.

#### Step 2: Reward Model Training
Train a separate reward model to predict human preferences:
1. Collect comparisons: For the same prompt, ask humans to rank two or more responses
2. Train a model to predict which response humans prefer
3. The reward model outputs a scalar score for any (prompt, response) pair

**Dataset size**: 50k–200k comparisons typically sufficient.

**Architecture**: Same as the base model with the LM head replaced by a regression head.

#### Step 3: Reinforcement Learning
Use PPO (Proximal Policy Optimization) to maximize the reward model's score while staying close to the SFT model:
- The policy (our model) generates responses
- The reward model scores them
- PPO updates the policy to increase expected reward
- A KL penalty prevents the policy from drifting too far from the SFT model

### RLHF Challenges

| Challenge | Impact | Mitigation |
|-----------|--------|------------|
| Reward hacking | Model finds shortcuts to high reward | KL penalty, regular reward model updates |
| Reward model bias | Amplifies annotator biases | Diverse annotator pool, debiasing |
| Training instability | PPO is sensitive to hyperparameters | Careful tuning, trust region constraints |
| Computational cost | 3 models (policy, reward, reference) | DPO eliminates reward model |
| Reward model quality | Bottleneck on alignment quality | High-quality comparisons, regular eval |

## DPO (Direct Preference Optimization)

### Key Insight

DPO eliminates the need for a separate reward model and RL loop. It directly optimizes the policy using preference pairs.

**Mathematical insight:** The optimal policy under the RLHF objective has a closed form in terms of the reward function. DPO reparameterizes the reward function in terms of the policy, making the reward model implicit.

### DPO vs RLHF

| Aspect | RLHF | DPO |
|--------|------|-----|
| Components | SFT + RM + PPO | SFT + DPO loss |
| Complexity | High (3 stages) | Low (2 stages) |
| Stability | PPO sensitive | More stable |
| Compute | ~3x SFT | ~1.5x SFT |
| Performance | Baseline | Comparable or better |
| Reward model | Explicit | Implicit |
| Preference data | Required | Required |

### When to Use DPO
- Limited compute budget (no reward model training)
- Preference data already available
- Stability is a concern

### When to Use RLHF
- You have a dedicated reward modeling team
- The task benefits from iterative RM improvement
- You can afford the compute overhead

## ORPO (Odds Ratio Preference Optimization)

ORPO combines SFT and alignment into a single stage. It adds a preference loss term to the standard language modeling objective using an odds ratio.

**Key advantage:** No separate SFT phase needed. The model learns to follow instructions and prefer chosen responses simultaneously.

**Trade-off:** More hyperparameters to tune, less mature ecosystem.

## KTO (Kahneman-Tversky Optimization)

KTO only requires binary feedback (good/bad) instead of pairwise comparisons. Based on prospect theory from behavioral economics.

**Key advantage:** Easier data collection — just thumbs up/down instead of ranking pairs.

**Trade-off:** Less signal per annotation, may need more data.

## Comparison Summary

| Method | Data Required | Stages | Stability | Maturity | Compute |
|--------|--------------|--------|-----------|----------|---------|
| RLHF (PPO) | Comparisons | 3 | Low | High | Very High |
| DPO | Comparisons | 2 | High | High | Medium |
| ORPO | Comparisons | 1 | Medium | Low | Medium |
| KTO | Binary feedback | 1 | High | Low | Low |
| SimPO | Comparisons | 2 | High | Medium | Medium |

## Practical Recommendations

### For First Alignment Project
1. Start with DPO — simplest to implement, most robust
2. Use 5k–20k high-quality preference pairs
3. Evaluate on held-out preference test set + safety benchmarks

### Data Quality Rules
- Chosen responses must be *clearly* better than rejected
- Avoid ties or ambiguous pairs
- Diverse prompts covering the full input distribution
- Include edge cases and adversarial examples

### Evaluation Metrics
| Metric | What It Measures | How |
|--------|-----------------|-----|
| Reward score | Alignment quality | RM score (if available) |
| Win rate | Relative preference | A/B comparison vs baseline |
| Safety benchmarks | Harm reduction | TruthfulQA, BBQ, etc. |
| Capability retention | General competence | MMLU, HumanEval, etc. |

## Common Failure Modes

| Mode | Symptom | Fix |
|------|---------|-----|
| Collapse | Model outputs safe but useless responses | Reduce KL penalty, add capability retention eval |
| Over-optimization | Reward high but human preference low | Regular RM refresh, diversity penalty |
| Amplified bias | Model becomes more biased | Diverse annotators, bias evaluation |
| DPO degradation | Training loss diverges | Lower learning rate, smaller beta |
