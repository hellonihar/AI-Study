# Stakeholder Management → AI Solution Scoping

## The Traditional Skill

You worked with stakeholders to understand requirements, assess feasibility, estimate effort, and set expectations. You translated between business needs and technical solutions. You managed scope creep, communicated trade-offs, and aligned executive expectations with engineering reality.

## The AI Equivalent

AI solution scoping requires all of these skills but with a new set of technical constraints to explain. The key difference: non-deterministic outputs, cost per token, hallucination risk, and data requirements are now the primary constraints — replacing traditional limits like server capacity or database size.

Your stakeholder management toolkit transfers directly:
- **Requirements gathering** → "What should the model do?" → "What does success look like?" → "What data is available?"
- **Feasibility assessment** → "Can this be done with prompting, or does it need fine-tuning?" → "Do we have enough data?" → "What's the accuracy target?"
- **Effort estimation** → "How much data curation? How many eval cycles? What infrastructure needed?"
- **Cost estimation** → "Token cost per query × expected volume = monthly LLM cost" + training cost
- **Expectation setting** → "The model will be 90% accurate, not 100%. Here's how we handle the other 10%."
- **Scope management** → "Adding this capability means fine-tuning a separate model" → "Here's the cost impact"

## New Concepts to Learn

- **Accuracy vs. reliability:** Stakeholders need to understand that AI systems don't produce deterministic outputs. 95% accuracy means 5% of responses will be wrong — what's the mitigation strategy?
- **Cost per query:** Unlike traditional software (infra cost fixed), AI systems have a variable cost per request based on token usage. High-volume features can be surprisingly expensive.
- **Training data requirements:** "How many examples do we need?" is a common question. Answer: 500–10K for fine-tuning, depending on task complexity.
- **Hallucination as a feature of the technology:** Stakeholders need to understand that hallucination is not a bug to be fixed — it's a property of the technology to be managed.
- **Model dependency:** The system is built on a model you don't control. A model provider update can change behavior overnight. What's the contingency plan?
- **Prototyping timeline:** A demo can be built in days. A production system takes months (data curation, eval sets, guardrails, monitoring).

## A Concrete Translation Example

**Traditional scoping:** Stakeholder: "Build a search feature." You: "We need 2 months for indexing, query optimization, and testing."

**AI scoping:** Stakeholder: "Add an AI chat feature." You: "We can prototype a demo in 3 days. For production: we need to (1) curate a knowledge base and eval set (2 weeks), (2) build a RAG pipeline with guardrails (1 week), (3) test and tune (2 weeks), (4) set up monitoring and incidents (1 week). Total: ~6 weeks to production. Ongoing cost: ~$X per 1K queries."

Same scoping process. New vocabulary and constraints.

## Key Resources

- "Building LLM Applications for Production" (Huyen, 2024) — Chapter 1 covers scoping
- Andrej Karpathy's "State of GPT" talk — explaining AI capabilities to non-technical audiences
- Google's "People + AI Guidebook" — user-facing AI considerations
