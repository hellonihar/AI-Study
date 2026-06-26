# Prompt Deployment Pipeline — Design Document

## Overview

A Git-based pipeline that version-controls prompts, runs eval suites on new prompt versions, gates deploys on quality thresholds, and supports canary releases with automatic rollback. This project demonstrates how CI/CD skills — pipeline automation, canary deployments, rollback strategies, A/B testing, quality gating — transfer directly to managing LLM prompts in production.

**Skills demonstrated: Prompt engineering — MLOps — CI/CD for LLMs — A/B testing for prompts**

| Enterprise CI/CD Skill | AI Equivalent | This Project |
|---|---|---|
| Pipeline automation (Jenkins/GitHub Actions) | Prompt evaluation + deployment pipeline | GitHub Actions workflow with validation, eval, gating, and deploy stages |
| Canary releases & traffic splitting | Gradual prompt rollout with metric monitoring | Traffic-splitting middleware with auto-promotion |
| Rollback strategies | Automatic regression detection + prompt rollback | Metric-threshold monitoring with instantaneous rollback |
| A/B testing (feature flags, experiments) | Prompt variant comparison with statistical significance | Traffic splitting + per-variant metric collection + significance test |
| Quality gating (unit tests, integration tests) | Eval-as-gate: faithfulness, hallucination, relevance thresholds | Pre-deploy eval suite run against baseline with pass/fail decision |
| Artifact versioning (Docker images, binaries) | Prompt version registry with Git + metadata store | YAML-based prompt spec, Git-tracked, versioned in DB |

---

## Architecture

```
                          ┌─────────────────────┐
                          │    Git Repository    │
                          │  prompts/            │
                          │  ├── chat-v1.yaml    │
                          │  ├── chat-v2.yaml    │
                          │  └── summarizer/     │
                          └─────────┬───────────┘
                                    │ push / PR
                                    ▼
              ┌─────────────────────────────────────┐
              │       GitHub Actions (CI/CD)         │
              │                                      │
              │  ┌───────────────────────────────┐  │
              │  │  Stage 1: Validate            │  │
              │  │  ✓ YAML syntax                │  │
              │  │  ✓ Template compilation        │  │
              │  │  ✓ Variable completeness       │  │
              │  │  ✓ Model config validity        │  │
              │  └──────────────┬────────────────┘  │
              │                 ▼                   │
              │  ┌───────────────────────────────┐  │
              │  │  Stage 2: Evaluate            │  │
              │  │  Run eval suite on candidate   │  │
              │  │  Compare scores vs baseline    │  │
              │  │  Generate diff report          │  │
              │  └──────────────┬────────────────┘  │
              │                 ▼                   │
              │  ┌───────────────────────────────┐  │
              │  │  Stage 3: Gate                │  │
              │  │  All metrics above threshold? │  │
              │  │  No regression > 5%?          │  │
              │  │  → PASS: proceed to deploy    │  │
              │  │  → FAIL: block + comment PR   │  │
              │  └──────────────┬────────────────┘  │
              │                 ▼ (if PASS)         │
              │  ┌───────────────────────────────┐  │
              │  │  Stage 4: Deploy              │  │
              │  │  Register prompt in registry  │  │
              │  │  Activate in staging          │  │
              │  │  → Canary: 1% → 10% → 50%    │  │
              │  │  → Full rollout               │  │
              │  └───────────────────────────────┘  │
              └────────────────┬────────────────────┘
                               │
                               ▼
              ┌─────────────────────────────────────┐
              │         Prompt Registry (API)        │
              │  ┌────────────┐  ┌────────────────┐ │
              │  │  Storage   │  │  Renderer      │ │
              │  │  Git + DB  │  │  Jinja2 + vars │ │
              │  └────────────┘  └────────────────┘ │
              └────────────────┬────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
        ┌──────────────────┐   ┌──────────────────┐
        │   App Instance 1  │   │   App Instance 2 │
        │  (prompt v3)      │   │  (prompt v3)     │
        └──────────────────┘   └──────────────────┘
                    │                     │
                    └──────────┬──────────┘
                               ▼
              ┌─────────────────────────────────────┐
              │         Monitoring Stack             │
              │  ┌──────────┐  ┌──────────┐         │
              │  │Prometheus│  │ Grafana  │         │
              │  │ (metrics │  │(dashboard│         │
              │  │ per ver) │  │ + alerts)│         │
              │  └──────────┘  └──────────┘         │
              │  ┌──────────────────────────────┐   │
              │  │ Rollback Controller           │   │
              │  │ Auto-rollback on regression   │   │
              │  └──────────────────────────────┘   │
              └─────────────────────────────────────┘
```

### Deployment Flow

```
git push feat/new-prompt
       │
       ▼
┌──────────────────────────────────────────────────┐
│  CI Pipeline (GitHub Actions)                     │
│                                                    │
│  Validate ──► Evaluate ──► Gate ──► Register      │
│         ✓           ✓         ✓         ✓         │
│                                                    │
│  On FAIL: → comment PR with eval diff report       │
│  On PASS: → merge to main, trigger CD              │
└──────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│  CD Pipeline                                      │
│                                                    │
│  Staging: activate immediately, monitor 5 min      │
│                                                    │
│  Production:                                       │
│    ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐ │
│    │Canary  │─►│Canary  │─►│Canary  │─►│Full    │ │
│    │1%      │  │10%     │  │50%     │  │100%    │ │
│    │5 min   │  │10 min  │  │15 min  │  │        │ │
│    └────────┘  └────────┘  └────────┘  └────────┘ │
│         │           │           │           │        │
│         └───────────┴───────────┴───────────┘        │
│                     │ auto-promote if metrics stable │
│                     ▼                                │
│              ┌──────────────────┐                    │
│              │  Full Rollout    │                    │
│              │  100% traffic    │                    │
│              │  + tag as stable │                    │
│              └──────────────────┘                    │
│                                                    │
│  ANY regression detected: trigger rollback          │
└──────────────────────────────────────────────────┘
```

---

## Project Structure

```
projects/prompt-deployment-pipeline/
├── app/
│   ├── __init__.py
│   ├── config.py                    # Settings via pydantic-settings
│   ├── schemas.py                   # Pydantic models for prompts, versions, deployments
│   │
│   ├── registry/
│   │   ├── __init__.py
│   │   ├── storage.py               # Prompt version store (Git ref + DB metadata)
│   │   ├── renderer.py              # Jinja2 template rendering with variable injection
│   │   └── migration.py             # Prompt format migration across versions
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── ci_workflow.py           # GitHub Actions workflow DSL (YAML generation)
│   │   ├── validator.py             # YAML syntax, template compile, var completeness
│   │   ├── gater.py                 # Eval threshold gating against baseline
│   │   ├── deployer.py              # Registry registration + target activation
│   │   ├── canary.py                # Gradual rollout: 1% → 10% → 50% → 100%
│   │   ├── rollback.py              # Auto-rollback on metric regression
│   │   └── ab_test.py               # Variant A/B traffic splitting + significance test
│   │
│   ├── deployment/
│   │   ├── __init__.py
│   │   ├── targets.py               # Deployment target abstraction (FastAPI, K8s configmap)
│   │   ├── history.py               # Deployment log + version tracking
│   │   └── reconciler.py            # Desired vs actual prompt state across instances
│   │
│   ├── monitoring/
│   │   ├── __init__.py
│   │   ├── metrics.py               # Prompt-specific Prometheus metrics
│   │   └── alert_rules.py           # Rollback trigger alert rules
│   │
│   └── api/
│       ├── __init__.py
│       ├── routes.py                # FastAPI: list, diff, activate, rollback, stats, AB
│       └── dependencies.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_registry.py
│   ├── test_renderer.py
│   ├── test_validator.py
│   ├── test_gater.py
│   ├── test_canary.py
│   ├── test_rollback.py
│   └── test_ab_test.py
│
├── data/
│   └── sample_prompts/              # Example prompt directory structure
│       ├── chat-v1.yaml
│       ├── chat-v2.yaml
│       └── summarizer/
│           ├── v1.yaml
│           └── v2.yaml
│
├── .github/
│   └── workflows/
│       └── prompt-deploy.yml        # CI/CD workflow
├── requirements.txt
└── README.md
```

---

## Prompt Format

### YAML Prompt Spec

```yaml
# prompts/chat-v2.yaml
name: customer-support-chat
version: 2.0.0
description: "Customer support chat prompt with RAG context"

template:
  system: |
    You are a helpful customer support agent for {company_name}.
    Answer the customer's question using only the provided context.
    If the context doesn't contain the answer, say "I don't have that information."
    Always cite the source document for each claim.

    Context:
    {context}

  user: |
    Customer question: {query}

  examples:
    - user: "What is your return policy?"
      assistant: "Our return policy allows returns within 30 days of purchase. [Source: return-policy.md]"
    - user: "Do you ship internationally?"
      assistant: "Yes, we ship to 47 countries worldwide. [Source: shipping-policy.md]"

variables:
  - name: company_name
    type: string
    default: "Acme Corp"
  - name: context
    type: string
    required: true
    description: "Retrieved document chunks"
  - name: query
    type: string
    required: true
    description: "User question"

model_config:
  provider: openai
  model: gpt-4o-mini
  temperature: 0.3
  max_tokens: 1024
  top_p: 0.95

metadata:
  author: jane.doe
  team: customer-support
  tags: [production, rag, customer-support]
  description: "Improved version with explicit citation instructions and few-shot examples"
  changelog: |
    v2.0.0: Added citation instruction, two few-shot examples, reduced temperature from 0.7 to 0.3
    v1.0.0: Initial prompt
```

### Prompt Interface

```python
class PromptVersion(BaseModel):
    name: str
    version: str                    # semver
    template: dict                  # system, user, examples
    variables: list[PromptVariable]
    model_config: ModelConfig
    metadata: dict

    def render(self, **kwargs) -> list[dict]:
        """Render template with variables → list of chat messages."""
        rendered = []
        if self.template.get("system"):
            rendered.append({"role": "system", "content": Template(self.template["system"]).render(**kwargs)})
        for example in self.template.get("examples", []):
            rendered.append({"role": "user", "content": Template(example["user"]).render(**kwargs)})
            rendered.append({"role": "assistant", "content": example["assistant"]})
        rendered.append({"role": "user", "content": Template(self.template["user"]).render(**kwargs)})
        return rendered
```

---

## Validation (Stage 1)

| Check | What It Does | Error If |
|---|---|---|
| **YAML syntax** | Parse with Pydantic model | Malformed YAML, missing required fields |
| **Template compilation** | Compile all Jinja2 templates with dummy vars | Syntax error, undefined variable |
| **Variable completeness** | All `required: true` variables accounted for | Missing required variable |
| **Model config** | Validate provider + model combo exists | Invalid model name, bad temperature range |
| **Version bump** | Semver check vs registry | No version bump, downgrade |
| **Changelog** | Changelog entry present for version | No changelog |

```python
class PromptValidator:
    def validate(self, prompt: PromptVersion, existing: PromptVersion | None) -> ValidationResult:
        errors = []
        errors.extend(self._check_yaml(prompt))
        errors.extend(self._check_template(prompt))
        errors.extend(self._check_variables(prompt))
        errors.extend(self._check_model_config(prompt))
        errors.extend(self._check_version(prompt, existing))
        errors.extend(self._check_changelog(prompt))
        return ValidationResult(passed=len(errors) == 0, errors=errors)
```

---

## Evaluation Gating (Stage 2 & 3)

### Gating Logic

```python
class EvalGater:
    def gate(
        self,
        candidate_scores: dict[str, float],
        baseline_scores: dict[str, float],
        thresholds: dict[str, GateThreshold],
    ) -> GateResult:
        failures = []
        for metric, threshold in thresholds.items():
            candidate = candidate_scores.get(metric, 0)
            baseline = baseline_scores.get(metric, 0)

            # Absolute threshold check
            if threshold.min and candidate < threshold.min:
                failures.append(f"{metric}: {candidate:.3f} < min {threshold.min:.3f}")
            if threshold.max and candidate > threshold.max:
                failures.append(f"{metric}: {candidate:.3f} > max {threshold.max:.3f}")

            # Regression check (compared to baseline)
            if baseline > 0:
                degradation = (baseline - candidate) / baseline * 100
                if degradation > threshold.max_regression_pct:
                    failures.append(f"{metric}: degraded {degradation:.1f}% (max {threshold.max_regression_pct:.1f}%)")

        return GateResult(passed=len(failures) == 0, failures=failures)
```

### Threshold Configuration

```yaml
# .prompt_thresholds.yaml
thresholds:
  faithfulness:
    min: 0.85
    max_regression_pct: 5.0
  hallucination_rate:
    max: 0.05
    max_regression_pct: 10.0
  relevance:
    min: 0.80
    max_regression_pct: 5.0
  toxicity:
    max: 0.01
    max_regression_pct: 0.0        # Never allow regression
  latency_p95:
    max: 2000                      # ms
    max_regression_pct: 15.0
```

---

## Canary Releases (Stage 4)

### Traffic Splitting Middleware

```python
class CanaryMiddleware:
    def __init__(self, registry: PromptRegistry):
        self.registry = registry
        self.active_rollouts: dict[str, Rollout] = {}

    async def select_prompt(self, request: Request) -> PromptVersion:
        # Determine which prompt version to use for this request
        prompt_name = request.state.prompt_name
        normal_version = self.registry.get_active(prompt_name)

        if prompt_name not in self.active_rollouts:
            return normal_version

        rollout = self.active_rollouts[prompt_name]
        # Deterministic assignment based on user_id for consistent experience
        bucket = hash(f"{rollout.candidate.id}:{request.state.user_id}") % 100
        if bucket < rollout.traffic_pct:
            return rollout.candidate
        return normal_version
```

### Canary Stages

| Stage | Traffic % | Duration | Action on Pass | Action on Fail |
|---|---|---|---|---|
| 1 - Smoke | 1% | 5 min | Promote to 10% | Rollback, alert |
| 2 - Evaluate | 10% | 10 min | Promote to 50% | Rollback, alert |
| 3 - Scale | 50% | 15 min | Promote to 100% | Rollback, alert |
| 4 - Full | 100% | — | Tag as stable | Rollback |

### Canary Controller

```python
class CanaryController:
    def __init__(self, registry, monitor, rollback):
        self.registry = registry
        self.monitor = monitor
        self.rollback = rollback

    async def start_rollout(self, prompt: PromptVersion, stages: list[CanaryStage]):
        rollout_id = str(uuid.uuid4())
        rollout = Rollout(id=rollout_id, candidate=prompt, stages=stages)
        for stage in stages:
            rollout.current_stage = stage
            self.registry.set_active_weight(prompt.name, prompt, stage.traffic_pct)
            await self._wait_and_check(stage.duration)
            if await self._has_regression(prompt.name):
                await self.rollback.execute(rollout)
                return RolloutResult.failed(rollout_id, "Regression detected")
        self.registry.set_active(prompt.name, prompt)
        return RolloutResult.success(rollout_id)
```

---

## Auto-Rollback

### Rollback Triggers

| Trigger | Metric | Window | Threshold |
|---|---|---|---|
| **Quality regression** | Faithfulness | 2 min sliding | < 0.85 mean |
| **Hallucination spike** | Hallucination rate | 2 min sliding | > 0.05 mean |
| **Latency degradation** | Latency p95 | 5 min sliding | > 2× baseline |
| **Error rate increase** | HTTP 5xx rate | 2 min sliding | > 2× baseline |
| **Toxicity increase** | Toxicity score | 5 min sliding | > 0.01 mean |

### Rollback Logic

```python
class RollbackController:
    def __init__(self, registry, monitor, alerting):
        self.registry = registry
        self.monitor = monitor
        self.alerting = alerting

    async def check_and_rollback(self, prompt_name: str):
        active = self.registry.get_active(prompt_name)
        previous = self.registry.get_previous(prompt_name)
        if not previous:
            return

        for trigger in self.rollback_triggers:
            result = await self.monitor.evaluate_trigger(trigger, prompt_name)
            if result.triggered:
                await self._execute_rollback(prompt_name, active, previous, trigger)
                return RollbackResult(
                    rolled_back=True,
                    from_version=active.version,
                    to_version=previous.version,
                    trigger=trigger.name,
                    reason=result.reason,
                )
        return RollbackResult(rolled_back=False)

    async def _execute_rollback(self, name, active, previous, trigger):
        self.registry.set_active(name, previous)
        self.registry.set_inactive(name, active)
        await self.alerting.send_alert(
            level="critical",
            title=f"Auto-rollback: {name}",
            message=f"Prompt {name} v{active.version} rolled back to v{previous.version} due to {trigger.name}: {trigger.reason}",
        )
```

---

## A/B Testing

### Experiment Lifecycle

```
1. Create variant ──► 2. Split traffic ──► 3. Collect metrics ──► 4. Analyze ──► 5. Declare winner
```

### Traffic Splitting

```python
class ABTestController:
    def __init__(self, registry):
        self.active_tests: dict[str, ABTest] = {}

    async def start_test(self, name: str, control: PromptVersion, variant: PromptVersion, split: float = 0.5):
        self.active_tests[name] = ABTest(
            name=name,
            control=control,
            variant=variant,
            split=split,                     # % of traffic to variant
            start_time=datetime.utcnow(),
            status="running",
        )

    async def select_variant(self, prompt_name: str, user_id: str) -> tuple[PromptVersion, str]:
        """Returns (prompt, group: 'control' | 'variant')."""
        test = self.active_tests.get(prompt_name)
        if not test:
            return self.registry.get_active(prompt_name), "production"
        bucket = hash(f"{test.name}:{user_id}") % 100
        if bucket < test.split * 100:
            return test.variant, "variant"
        return test.control, "control"
```

### Metrics Collection Per Variant

```python
class ABMetricsCollector:
    def __init__(self, prometheus: PrometheusClient):
        self.faithfulness = Histogram("ab_faithfulness", "Faithfulness score", ["test", "variant"])
        self.hallucination = Histogram("ab_hallucination", "Hallucination rate", ["test", "variant"])
        self.click_through = Counter("ab_click_through", "Positive feedback count", ["test", "variant"])
        self.latency = Histogram("ab_latency_ms", "Response latency", ["test", "variant"])

    async def record(self, test_name: str, variant: str, result: EvalResult, latency_ms: float):
        self.faithfulness.labels(test=test_name, variant=variant).observe(result.faithfulness)
        self.hallucination.labels(test=test_name, variant=variant).observe(result.hallucination)
        self.latency.labels(test=test_name, variant=variant).observe(latency_ms)
```

### Significance Testing

```python
class SignificanceTester:
    def test(self, control: MetricCollection, variant: MetricCollection) -> TestResult:
        """Mann-Whitney U test for non-normal metric distributions."""
        from scipy.stats import mannwhitneyu
        stat, p_value = mannwhitneyu(variant.scores, control.scores, alternative="two-sided")
        effect_size = (variant.mean - control.mean) / control.std if control.std > 0 else 0
        return TestResult(
            significant=p_value < 0.05,
            p_value=p_value,
            effect_size=effect_size,
            lift_pct=((variant.mean - control.mean) / control.mean * 100) if control.mean > 0 else 0,
            recommendation="variant" if (p_value < 0.05 and effect_size > 0) else "control" if (p_value < 0.05 and effect_size < 0) else "inconclusive",
        )
```

### Analysis & Winner Declaration

```python
class ABTestAnalyzer:
    async def analyze(self, test: ABTest, min_samples: int = 1000) -> AnalysisResult:
        control_data = await self.collect_metrics(test.name, "control")
        variant_data = await self.collect_metrics(test.name, "variant")

        if len(control_data) < min_samples or len(variant_data) < min_samples:
            return AnalysisResult(ready=False, message=f"Collecting more data ({len(control_data)}/{min_samples})")

        results = {}
        for metric in ["faithfulness", "hallucination", "latency"]:
            results[metric] = self.significance.test(control_data[metric], variant_data[metric])

        overall = all(r.recommendation == "variant" for r in results.values())
        return AnalysisResult(
            ready=True,
            metrics=results,
            winner=test.variant if overall else test.control,
            recommendation="Deploy variant" if overall else "Keep control",
        )
```

---

## Prompt Registry

### Storage

```python
class PromptRegistry:
    def __init__(self, git_repo: str, db: Database):
        self.git_repo = git_repo           # Path to Git-tracked prompts/
        self.db = db                       # SQLite/PostgreSQL metadata store

    def list_versions(self, name: str) -> list[PromptVersion]:
        """List all versions of a prompt, ordered by creation time."""
        return self.db.query("SELECT * FROM prompts WHERE name = ? ORDER BY created_at DESC", (name,))

    def get_active(self, name: str) -> PromptVersion:
        """Get currently active version."""
        row = self.db.query_one("SELECT version_id FROM active_prompts WHERE name = ?", (name,))
        return self.get_by_id(row.version_id)

    def register(self, prompt: PromptVersion) -> PromptVersion:
        """Register a new prompt version. Persists YAML to Git and metadata to DB."""
        # 1. Write YAML to git_repo/prompts/{name}/{version}.yaml
        # 2. Insert metadata row into prompts table
        # 3. Return registered prompt with generated ID
        ...

    def set_active(self, name: str, prompt: PromptVersion):
        """Set this version as active (upsert)."""
        self.db.execute("INSERT OR REPLACE INTO active_prompts (name, version_id) VALUES (?, ?)", (name, prompt.id))
        self.db.execute("INSERT INTO deployment_history (name, version_id, action, timestamp) VALUES (?, ?, 'activate', ?)", (name, prompt.id, datetime.utcnow()))

    def diff(self, v1_id: str, v2_id: str) -> DiffResult:
        """Show what changed between two prompt versions."""
        v1 = self.get_by_id(v1_id)
        v2 = self.get_by_id(v2_id)
        return DiffResult(
            version_change=f"{v1.version} → {v2.version}",
            template_changed=v1.template != v2.template,
            model_config_changed=v1.model_config != v2.model_config,
            variables_changed=v1.variables != v2.variables,
            template_diff=self._compute_diff(v1.template, v2.template),
        )
```

### Database Schema

```sql
CREATE TABLE prompts (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    version     TEXT NOT NULL,           -- semver
    file_path   TEXT NOT NULL,           -- relative path in Git repo
    git_sha     TEXT NOT NULL,           -- Git commit hash
    template    JSON NOT NULL,
    variables   JSON,
    model_config JSON,
    metadata    JSON,
    created_at  TIMESTAMP DEFAULT NOW(),
    author      TEXT,
    UNIQUE(name, version)
);

CREATE TABLE active_prompts (
    name        TEXT PRIMARY KEY,
    version_id  TEXT NOT NULL REFERENCES prompts(id),
    updated_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE deployment_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_name TEXT NOT NULL,
    version_id  TEXT NOT NULL REFERENCES prompts(id),
    action      TEXT NOT NULL,           -- activate, deactivate, rollback, canary_start, canary_promote
    traffic_pct INTEGER,                -- for canary stages
    trigger     TEXT,                    -- what triggered this action (manual, auto-rollback, CI)
    metadata    JSON,
    timestamp   TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ab_tests (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    control_id  TEXT NOT NULL REFERENCES prompts(id),
    variant_id  TEXT NOT NULL REFERENCES prompts(id),
    split       REAL NOT NULL,           -- 0.0 to 1.0
    status      TEXT NOT NULL,           -- running, completed, cancelled
    winner_id   TEXT REFERENCES prompts(id),
    started_at  TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

---

## API

### `GET /api/v1/prompts`

List all prompts with their active version.

### `GET /api/v1/prompts/{name}/versions`

List all versions of a prompt.

**Response:**
```json
{
  "name": "customer-support-chat",
  "versions": [
    {"version": "2.0.0", "author": "jane.doe", "created_at": "2026-06-27T12:00:00Z", "active": true},
    {"version": "1.0.0", "author": "john.smith", "created_at": "2026-06-01T10:00:00Z", "active": false}
  ]
}
```

### `POST /api/v1/prompts/register`

Register a new prompt version from uploaded YAML.

### `POST /api/v1/prompts/{name}/activate`

Activate a specific version. Bypasses canary if `force: true`.

**Request:**
```json
{
  "version": "2.0.0",
  "mode": "canary",
  "stages": [
    {"traffic_pct": 1, "duration_min": 5},
    {"traffic_pct": 10, "duration_min": 10},
    {"traffic_pct": 50, "duration_min": 15}
  ]
}
```

### `POST /api/v1/prompts/{name}/rollback`

Rollback to previous version (or specified version).

**Request:**
```json
{
  "version": "1.0.0",
  "reason": "Latency regression detected"
}
```

### `GET /api/v1/prompts/{name}/diff?from=1.0.0&to=2.0.0`

Show template and config diff between two versions.

### `POST /api/v1/prompts/{name}/ab/start`

Start an A/B test.

**Request:**
```json
{
  "variant_version": "2.0.0",
  "split": 0.5,
  "min_samples": 1000
}
```

### `GET /api/v1/prompts/{name}/ab/results`

Get A/B test results and significance analysis.

### `GET /api/v1/prompts/{name}/deployments`

Deployment history with timestamps, actions, and triggers.

---

## Monitoring

### Prometheus Metrics

| Metric | Type | Labels | Description |
|---|---|---|---|
| `prompt_requests_total` | Counter | prompt_name, prompt_version | Request count per prompt version |
| `prompt_latency_ms` | Histogram | prompt_name, prompt_version | Response latency per version |
| `prompt_tokens_total` | Counter | prompt_name, prompt_version, direction(prompt/completion) | Token usage per version |
| `prompt_eval_score` | Gauge | prompt_name, prompt_version, metric | Latest eval score per metric per version |
| `prompt_canary_stage` | Gauge | prompt_name, candidate_version | Current canary traffic percentage (0–100) |
| `prompt_rollbacks_total` | Counter | prompt_name | Rollback event count |
| `ab_faithfulness` | Histogram | test_name, variant (control/variant) | Faithfulness by A/B group |
| `ab_hallucination` | Histogram | test_name, variant | Hallucination by A/B group |
| `ab_click_through` | Counter | test_name, variant | Positive feedback by A/B group |
| `prompt_deploy_duration` | Histogram | prompt_name | End-to-end CI/CD pipeline duration |

### Grafana Dashboard

Three rows:
1. **Active versions** — per-prompt version gauge, canary stage tracking
2. **Quality metrics** — eval scores over time with rollback annotations
3. **A/B tests** — metric distribution comparison between control and variant

### Rollback Alerts

```yaml
groups:
  - name: prompt_rollback
    rules:
      - alert: PromptQualityDegraded
        expr: prompt_eval_score{metric="faithfulness"} < 0.85
        for: 2m
        labels: { severity: critical }
        annotations:
          summary: "Prompt {{ $labels.prompt_name }} faithfulness dropped below 0.85"

      - alert: PromptLatencySpike
        expr: histogram_quantile(0.95, rate(prompt_latency_ms_bucket[5m])) > 2000
        for: 5m
        labels: { severity: warning }
        annotations:
          summary: "Prompt {{ $labels.prompt_name }} p95 latency > 2s"
```

---

## CI/CD Workflow

### `.github/workflows/prompt-deploy.yml`

```yaml
name: Prompt Deploy
on:
  pull_request:
    paths: ['prompts/**/*.yaml']
  push:
    branches: [main]
    paths: ['prompts/**/*.yaml']

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r requirements.txt
      - name: Validate prompt YAML
        run: python -m app.pipeline.validator prompts/
      - name: Render test templates
        run: python -m app.pipeline.validator --render-test prompts/

  evaluate:
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - name: Run eval suite
        run: python -m app.pipeline.evaluate prompts/ --baseline latest --output eval_report.json
      - name: Upload eval report
        uses: actions/upload-artifact@v4
        with:
          name: eval-report
          path: eval_report.json

  gate:
    needs: evaluate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - name: Check thresholds
        run: python -m app.pipeline.gater eval_report.json --thresholds .prompt_thresholds.yaml
      - name: Comment PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('eval_report.json'));
            github.rest.issues.createComment({
              ...context.repo,
              issue_number: context.issue.number,
              body: `## Prompt Eval Report\n\n**Version:** ${report.version}\n\n| Metric | Candidate | Baseline | Threshold | Status |\n|--------|-----------|----------|-----------|--------|\n${report.results.map(r => `| ${r.metric} | ${r.candidate_score} | ${r.baseline_score} | ${r.threshold} | ${r.passed ? '✅' : '❌'} |`).join('\n')}\n\n**Overall: ${report.passed ? '✅ PASS' : '❌ FAIL'}**`
            });

  deploy:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    needs: gate
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - name: Register prompt
        run: python -m app.pipeline.deployer register prompts/ --api-url ${{ secrets.API_URL }}
      - name: Activate with canary
        run: python -m app.pipeline.deployer activate --mode canary --api-url ${{ secrets.API_URL }}
```

---

## Tech Stack

| Component | Choice | Justification |
|---|---|---|
| Prompt format | YAML + Jinja2 | Human-readable, Git-friendly, template engine standard |
| Registry storage | Git (files) + SQLite/PostgreSQL (metadata) | Audit trail in Git, fast queries in DB |
| CI/CD | GitHub Actions | Matches existing ecosystem, native PR comments |
| Prompt serving | FastAPI middleware | Consistent with other projects |
| Eval integration | Calls eval suite (project #3) as a dependency | Avoid duplication, use existing metrics |
| Canary | Custom middleware with deterministic user_id hashing | Consistent user experience during rollout |
| A/B testing | Custom controller + Mann-Whitney U test | Lightweight, no external experiment platform needed |
| Monitoring | Prometheus + Grafana | Consistent with other projects |
| Deployment targets | FastAPI (config reload), K8s ConfigMap | Covers local dev and production |

---

## Implementation Phases

| Phase | Files | Deliverable |
|---|---|---|
| **1** | `config.py`, `schemas.py`, `registry/storage.py`, `registry/renderer.py` | Prompt registry with Git-backed storage and Jinja2 rendering |
| **2** | `registry/migration.py`, `pipeline/validator.py` | Prompt version migration + validation (YAML, template, vars) |
| **3** | `pipeline/ci_workflow.py`, `pipeline/gater.py` | CI workflow generation + eval gating against thresholds |
| **4** | `pipeline/canary.py`, `deployment/targets.py`, `deployment/history.py` | Canary releases with traffic splitting and deployment history |
| **5** | `pipeline/rollback.py`, `monitoring/metrics.py`, `monitoring/alert_rules.py` | Auto-rollback controller and Prometheus alert rules |
| **6** | `pipeline/ab_test.py` | A/B testing: traffic split, metric collection, significance test, winner declaration |
| **7** | `deployment/reconciler.py`, `api/*` | State reconciliation across instances + FastAPI routes |
| **8** | `.github/workflows/prompt-deploy.yml` | Complete CI/CD workflow definition |
| **9** | Tests + `data/sample_prompts/*` | Verification with sample prompt versions |
| **10** | README | Documentation with workflow diagram |
