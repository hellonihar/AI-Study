# Resources — AI Integration Patterns

## Foundational Papers

| Paper | Year | Contribution |
|-------|------|-------------|
| [Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/abs/2302.04761) | 2023 | LM self-supervised tool use |
| [Gorilla: Large Language Model Connected with Massive APIs](https://arxiv.org/abs/2305.15334) | 2023 | Fine-tuned model for API calling |
| [ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs](https://arxiv.org/abs/2307.16789) | 2023 | API discovery + tool learning |
| [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) | 2022 | Reasoning + acting interleaved |
| [Circuit Breaker Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker) | 2016 | Cloud design pattern (Azure) |
| [Resilience Patterns: Retry, Circuit Breaker, Bulkhead](https://learn.microsoft.com/en-us/azure/architecture/patterns/category/resiliency) | 2016 | Azure resilience patterns |

## Frameworks & Libraries

| Tool | Description |
|------|-------------|
| [LangChain](https://www.langchain.com/) | Tool calling, chains, fallbacks, streaming |
| [LlamaIndex](https://www.llamaindex.ai/) | Data-centric AI with tool integration |
| [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling) | Native tool calling API |
| [Anthropic Tool Use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) | Claude's tool use API |
| [Instructor](https://github.com/jxnl/instructor) | Structured output extraction for LLMs |
| [Marvin](https://www.askmarvin.ai/) | AI-powered function generation |
| [Vercel AI SDK](https://sdk.vercel.ai/docs) | Streaming and tool calling for web apps |

## Streaming & Async

| Tool | Description |
|------|-------------|
| [Server-Sent Events (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) | SSE browser API reference |
| [WebSocket (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket) | WebSocket browser API reference |
| [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse) | SSE streaming in FastAPI |
| [Celery](https://docs.celeryq.dev/) | Distributed task queue (async AI) |
| [Redis Streams](https://redis.io/docs/data-types/streams/) | Stream processing with Redis |
| [Apache Kafka](https://kafka.apache.org/) | Event streaming platform |

## Rate Limiting & Backpressure

| Tool | Description |
|------|-------------|
| [Token Bucket Algorithm](https://en.wikipedia.org/wiki/Token_bucket) | Rate limiting algorithm reference |
| [Resilience4j](https://resilience4j.readme.io/) | Java resilience library (circuit breaker, rate limiter) |
| [Hystrix](https://github.com/Netflix/Hystrix) | Netflix's latency and fault tolerance library |
| [Bottleneck (Python)](https://github.com/ialsbock/bottleneck) | Async rate limiter for Python |

## Vendor Comparison

| Provider | Models | API Type | Pricing |
|----------|--------|----------|---------|
| [OpenAI](https://platform.openai.com/docs) | GPT-4, GPT-4o, GPT-4o-mini | REST + SSE | Per token |
| [Anthropic](https://docs.anthropic.com/) | Claude Opus, Sonnet, Haiku | REST + SSE | Per token |
| [Google](https://ai.google.dev/) | Gemini 1.5 Pro, Flash | REST + SSE | Per token (free tier) |
| [Mistral](https://docs.mistral.ai/) | Mistral Large, Small | REST | Per token |
| [Cohere](https://docs.cohere.com/) | Command R, R+ | REST | Per token |
| [Together AI](https://www.together.ai/) | Various open models | REST + SSE | Per token (cheaper) |

## Tutorials & Guides

- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling) — Official guide
- [Anthropic Tool Use Documentation](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) — Claude tool use docs
- [Building Reliable LLM Applications](https://www.anyscale.com/blog/building-reliable-llm-applications) — Anyscale's reliability guide
- [LLM Caching Strategies](https://www.datastax.com/guides/llm-caching) — Datastax caching guide
- [Streaming LLM Responses with FastAPI](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse) — FastAPI streaming tutorial
- [Resilience Patterns in Microservices](https://docs.microsoft.com/en-us/azure/architecture/patterns/category/resiliency) — Azure patterns
- [Rate Limiting Strategies](https://konghq.com/blog/rate-limiting-strategies) — Kong rate limiting guide

## Books

| Title | Author | Year |
|-------|--------|------|
| Building Microservices | Sam Newman | 2021 |
| Designing Data-Intensive Applications | Martin Kleppmann | 2017 |
| Site Reliability Engineering | Beyer et al. (Google) | 2016 |
| Cloud Native Patterns | Cornelia Davis | 2019 |
