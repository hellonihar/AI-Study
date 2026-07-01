# Production Prompt Management

Operating prompts at scale — deployment, monitoring, rollback, and lifecycle.

## Prompt Registry

A centralized service that stores and serves prompt versions:

```python
class PromptRegistry:
    def __init__(self):
        self.prompts = {}
        self.active_versions = {}
    
    def register(self, name, version, prompt_config):
        key = f"{name}:{version}"
        self.prompts[key] = prompt_config
    
    def get_active(self, name, model="gpt-4o-mini"):
        """Return the active prompt for a given task + model combination."""
        return self.active_versions.get(f"{name}:{model}")
    
    def set_active(self, name, version, model="gpt-4o-mini"):
        """Set the active prompt version for production traffic."""
        self.active_versions[f"{name}:{model}"] = self.prompts[f"{name}:{version}"]
```

## Gradual Rollout

```
Phase 1: Canary (1% traffic, 1 hour)
  → Monitor errors, latency, quality metrics
  
Phase 2: Ramp (10% → 25% → 50%, each 2 hours)
  → Compare variant metrics vs baseline
  
Phase 3: Full (100%)
  → Pin as new baseline

Phase 4 (on failure at any point):
  → Auto-rollback to previous version
  → Alert on-call engineer
```

## Rollback Automation

```python
ROLLBACK_THRESHOLDS = {
    "error_rate": 0.01,      # > 1% errors → rollback
    "latency_p99": 8.0,       # > 8s p99 → rollback  
    "accuracy": -0.05,        # > 5% drop → rollback
    "user_feedback": -0.1,    # > 10% drop in thumbs-up → rollback
}

def check_and_rollback(variant_name):
    current_metrics = get_current_metrics(variant_name)
    baseline_metrics = get_baseline_metrics()
    
    for metric, threshold in ROLLBACK_THRESHOLDS.items():
        delta = current_metrics[metric] - baseline_metrics[metric]
        if delta < threshold:
            trigger_rollback(variant_name, metric, delta)
            return True
    return False
```

## Prompt + Model Version Matrix

Different models may need different prompt versions:

| Task | GPT-4o | GPT-4o-mini | Fine-tuned 7B |
|---|---|---|---|
| Sentiment classifier | v3 | v2 | v5 |
| QA RAG | v8 | v6 | — |
| Code generator | v2 | v2 | v1 |

The registry must be **model-aware** — the same prompt rarely works optimally across models.

## Logging

Every prompt execution should log:

```json
{
    "timestamp": "2026-07-01T15:30:00Z",
    "task": "sentiment-classifier",
    "prompt_version": "v3",
    "model": "gpt-4o-mini",
    "input_tokens": 450,
    "output_tokens": 12,
    "latency_ms": 340,
    "response": "positive",
    "ground_truth": null,
    "user_feedback": null
}
```

## Lifecycle

```
Created → Tested → Staged → Active (100%) → Deprecated (10%) → Archived (0%)
              ↑          ↑                       │
              └──────────┴───────────────────────┘
                         (rollback)
```

- **Stale prompts** (no changes in 6 months) → flag for review. The model may have been updated, making the prompt suboptimal.
- **Deprecated prompts** → serve at 10% traffic for 2 weeks, then archive.
- **Archived prompts** → retain for audit purposes, never serve.

## Best Practices

- **One prompt registry to rule them all.** Don't let prompts live in code, config files, and databases simultaneously.
- **Pin prompt version in deployment manifests.** `prompt: sentiment-classifier:v3` — always explicit.
- **Log prompt version with every response.** Makes debugging quality issues 10× faster.
- **Alert on prompt not found.** If a registry lookup fails, something is misconfigured — don't silently fall back.
- **Automate prompt pruning.** Archive prompts that haven't been served in 90 days.
