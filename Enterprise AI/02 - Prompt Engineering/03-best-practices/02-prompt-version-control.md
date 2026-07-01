# Prompt Version Control

Treat prompts as production code — version them, review them, test them.

## Why Version Prompts?

| Problem | Without VCS | With VCS |
|---|---|---|
| Who changed what? | Check Slack history | `git log` |
| Why did quality drop? | "Maybe the prompt changed?" | `git bisect` finds the change |
| Can we roll back? | Hope someone has a backup | `git revert` |
| Is this prompt reviewed? | Maybe | PR approval required |

## Storage Format

Store prompts as structured YAML or JSON:

```yaml
# prompts/classifier/v2.yaml
name: sentiment-classifier
version: 2
model: gpt-4o-mini
system_prompt: |
  You are a sentiment classifier. Classify as positive, negative, or neutral.
  
  Rules:
  - Output only the label, no explanation.
  - If ambiguous, default to neutral.
  - Consider sarcasm.

temperature: 0.0
max_tokens: 10
examples:
  - input: "This is amazing!"
    output: positive
  - input: "Terrible experience."
    output: negative

metadata:
  author: jane.doe
  created: 2026-06-15
  accuracy_on_eval: 0.94
  parent: v1
```

## Directory Structure

```
prompts/
├── sentiment-classifier/
│   ├── v1.yaml
│   ├── v2.yaml
│   └── current.yaml → v2.yaml  (symlink)
├── qa-rag/
│   ├── v1.yaml
│   ├── v2.yaml
│   └── current.yaml → v2.yaml
└── shared/
    └── system-persona.yaml
```

## Workflow

```
1. Create prompt file → git branch feature/new-prompt
2. Submit PR → review by peer
3. Automated validation (see CI section below)
4. Merge → auto-deploy to staging
5. Run eval suite → compare scores
6. If scores pass threshold → deploy to 10% traffic
7. Monitor → roll out to 100% or revert
```

## CI Validation

```yaml
# .github/workflows/prompt-validation.yml
on: [pull_request]
jobs:
  validate-prompt:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate prompt schema
        run: python scripts/validate-prompt-schema.py prompts/*
      - name: Run eval suite
        run: python scripts/eval-prompt.py prompts/changed-file.yaml
      - name: Check quality threshold
        run: python scripts/check-threshold.py --min-accuracy 0.85
```

## Diffing Prompts

Standard git diff works for YAML/JSON prompts. For semantic diff:

```python
def semantic_prompt_diff(old_prompt, new_prompt):
    changes = []
    if old_prompt["system_prompt"] != new_prompt["system_prompt"]:
        changes.append("system_prompt modified")
    if old_prompt["temperature"] != new_prompt["temperature"]:
        changes.append(f"temperature: {old} → {new}")
    if old_prompt["examples"] != new_prompt["examples"]:
        added = len(new) - len(old)
        changes.append(f"examples: {added:+d}")
    return changes
```

## Best Practices

- **Pin prompt version in deployment config.** A staging deploy should use a specific version, not `current.yaml`.
- **Tag prompt versions with model version.** `v2-gpt4o` vs `v2-gpt4o-mini` — same prompt but different models.
- **Include eval scores in the prompt file.** Makes rollback decisions data-driven.
- **Automate rollback.** If accuracy drops > 5% after deploy, auto-revert to previous version.
- **Review prompts like code.** Require at least one peer review before merging prompt changes.
