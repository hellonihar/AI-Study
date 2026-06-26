# DevOps → AI Observability & Deployment

## The Traditional Skill

You built CI/CD pipelines, monitored system health (CPU, memory, latency, error rates), set up alerting (PagerDuty), managed infrastructure as code, and practiced incident response. You ensured that when something broke, you knew about it within minutes.

## The AI Equivalent

AI observability extends traditional monitoring with LLM-specific signals. A 200 OK response could still be a failure — the model might hallucinate, generate unsafe content, or cost 10× more than expected. The monitoring stack now includes token usage, hallucination rates, prompt quality, and guardrail hit rates alongside traditional metrics.

Everything you know about DevOps transfers:
- **CI/CD** → prompt versioning, eval-driven deployment gates, canary deployments for model changes
- **Monitoring** → LLM-specific metrics: token cost, latency p50/p95, hallucination rate, tool success rate
- **Alerting** → threshold-based alerts for cost spikes, error rate increases, quality score drops
- **Incident response** → runbooks for "hallucination spike," "cost surge," "LLM provider outage"
- **IaC** → infrastructure for vector stores, embedding services, LLM endpoints
- **Rollback** → revert to previous prompt version or model version when quality degrades

## New Concepts to Learn

- **LLM tracing:** End-to-end spans showing the full request lifecycle — input → retrieval → prompt → LLM call → output → guardrail check
- **Quality metrics:** Beyond error rate — faithfulness, relevancy, grounding, safety scores
- **Guardrail monitoring:** Counts of blocked inputs/outputs — too few may mean guardrails aren't catching issues, too many may mean they're over-filtering
- **Cost attribution:** Per-user, per-feature, or per-trace token cost — not just aggregate billing
- **Canary for prompts:** Graduate a new prompt version from 5% → 50% → 100% with automated quality gates
- **Red-teaming automation:** Continuous adversarial testing as part of the CI/CD pipeline

## A Concrete Translation Example

**Traditional dashboards:** Request count, error rate (5xx), latency p99, CPU utilization

**AI dashboards:** Request count, hallucination rate, latency p50/p95, token cost per request, tool call success rate, guardrail block rate, quality score over time

Same dashboarding discipline. Same alerting philosophy. New metrics to instrument.

## Key Resources

- LangFuse — open-source LLM observability
- LangSmith — tracing and evaluation for LLM workflows
- OpenTelemetry semantic conventions for LLMs (emerging standard)
- "A Practical Guide to LLM Observability" (LangFuse blog)
