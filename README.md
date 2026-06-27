# AI Study

A comprehensive study guide covering AI and Machine Learning foundations, modern generative AI concepts, system architecture, intelligent agents, and production deployment.

## Table of Contents

### 1. AI and Machine Learning Foundations
- [Statistics for AI](01-AI-and-Machine-Learning-Foundations/01-Statistics-for-AI/README.md)
- [Machine Learning fundamentals](01-AI-and-Machine-Learning-Foundations/02-Machine-Learning-fundamentals/README.md)
- [Deep Learning concepts](01-AI-and-Machine-Learning-Foundations/03-Deep-Learning-concepts/README.md)
- [Natural Language Processing (NLP)](01-AI-and-Machine-Learning-Foundations/04-Natural-Language-Processing/README.md)

### 2. Modern Generative AI Concepts
- [Transformers architecture](02-Modern-Generative-AI-Concepts/01-Transformers-architecture/README.md)
- [Large Language Models (LLMs)](02-Modern-Generative-AI-Concepts/02-Large-Language-Models/README.md)
- [Prompt engineering techniques](02-Modern-Generative-AI-Concepts/03-Prompt-engineering-techniques/README.md)
- [Model fine-tuning strategies](02-Modern-Generative-AI-Concepts/04-Model-fine-tuning-strategies/README.md)

### 3. Generative AI System Architecture
- [Retrieval-Augmented Generation (RAG)](03-Generative-AI-System-Architecture/01-Retrieval-Augmented-Generation/README.md)
- [Vector databases and embeddings](03-Generative-AI-System-Architecture/02-Vector-databases-and-embeddings/README.md)
- [Memory systems for AI applications](03-Generative-AI-System-Architecture/03-Memory-systems-for-AI-applications/README.md)
- [Caching strategies for LLM systems](03-Generative-AI-System-Architecture/04-Caching-strategies-for-LLM-systems/README.md)

### 4. AI Agents and Intelligent Workflows
- [AI agent architectures](04-AI-Agents-and-Intelligent-Workflows/01-AI-agent-architectures/README.md)
- [Tool usage and reasoning loops](04-AI-Agents-and-Intelligent-Workflows/02-Tool-usage-and-reasoning-loops/README.md)
- [Multi-step agent workflows](04-AI-Agents-and-Intelligent-Workflows/03-Multi-step-agent-workflows/README.md)
- [Multi-agent collaboration systems](04-AI-Agents-and-Intelligent-Workflows/04-Multi-agent-collaboration-systems/README.md)

### 5. Building and Deploying AI Applications
- [Generative AI system design](05-Building-and-Deploying-AI-Applications/01-Generative-AI-system-design/README.md)
- [API-based AI architectures](05-Building-and-Deploying-AI-Applications/02-API-based-AI-architectures/README.md)
- [FastAPI deployment for AI applications](05-Building-and-Deploying-AI-Applications/03-FastAPI-deployment-for-AI-applications/README.md)
- [Production considerations for AI systems](05-Building-and-Deploying-AI-Applications/04-Production-considerations-for-AI-systems/README.md)

### 6. Adding AI Flavor to Enterprise Experience
- [Architecture → AI system design](06-Adding-AI-flavor-to-enterprise-experience/01-Architecture-to-AI-system-design/README.md)
- [Backend → LLM workflows](06-Adding-AI-flavor-to-enterprise-experience/02-Backend-to-LLM-workflows/README.md)
- [QA/testing → AI evals](06-Adding-AI-flavor-to-enterprise-experience/03-QA-testing-to-AI-evals/README.md)
- [DevOps → AI observability & deployment](06-Adding-AI-flavor-to-enterprise-experience/04-DevOps-to-AI-observability/README.md)
- [Data pipelines → RAG & retrieval](06-Adding-AI-flavor-to-enterprise-experience/05-Data-pipelines-to-RAG-retrieval/README.md)
- [Enterprise governance → AI guardrails](06-Adding-AI-flavor-to-enterprise-experience/06-Enterprise-governance-to-AI-guardrails/README.md)
- [Stakeholder management → AI solution scoping](06-Adding-AI-flavor-to-enterprise-experience/07-Stakeholder-management-to-AI-scoping/README.md)

### Project Designs & Reference Documents

- [Projects directory — AI implementation blueprints](projects/) — 10 end-to-end project designs (RAG, multi-agent, guardrails, evaluation, etc.) with architecture diagrams, data models, API contracts, design decisions, and phased implementation plans. Each project is a deployable system designed for real-world constraints.
- [Industry-specific solutions](projects/industry-solutions/) — 20 industry verticals with tailored AI solutions. Detailed designs include:
  - [ClaimPulse](projects/industry-solutions/insurance/claimpulse/design.md): AI claims processing (document AI → fraud detection → LLM settlement). CPU-only, PHI-compliant, 50-state DOI config.
  - [FactoryRL](projects/industry-solutions/manufacturing-industrial/factoryrl/design.md): Factory energy optimization via MPC + LightGBM. CPU-only, safety-constrained, no neural networks.
- [AI solution scoping — 100 industry examples](docs/ai-solution-scoping-examples.md) — A reference catalog of successfully scoped AI solutions across 20 industries. Each entry follows a consistent pattern: concrete business problem → specific AI solution → scope deliverables (integrations, compliance, workflow changes, success metrics).
- [Industry scope detail files](docs/solution-scopes/) — Individual files for each of the 20 industries, expanding the master catalog examples with self-contained reference pages.
- [AI SDLC layers summary](docs/ai-sdlc-layers-summary.md) — A 9-layer reference architecture spanning data, model, evaluation, deployment, monitoring, and governance. Links each layer to the relevant sections and projects in this repository.