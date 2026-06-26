# QA/Testing → AI Evals

## The Traditional Skill

You designed test strategies: unit tests, integration tests, end-to-end tests, regression suites, smoke tests, and performance tests. You measured code coverage, tracked bug rates, and automated test execution in CI/CD pipelines.

## The AI Equivalent

AI evaluation (evals) is the same discipline applied to LLM outputs. The difference: instead of asserting `response.status == 200`, you assert the *quality* of generated text — is it faithful to the source? Does it contain hallucinations? Is the tone appropriate? Is the format valid JSON?

The testing mindset is identical:
- **Unit tests** → test individual prompts against example inputs
- **Regression tests** → run a fixed eval set before every prompt deployment
- **Integration tests** → test the full RAG pipeline end-to-end
- **Performance tests** → measure latency and token cost per query
- **A/B tests** → compare prompt versions or model versions in production

## New Concepts to Learn

- **LLM-as-judge:** Using a strong LLM (GPT-4, Claude) to score another model's outputs — replaces human judgment for large-scale evaluation
- **Eval sets:** Curated test cases with expected outputs — your new regression suite
- **Hallucination detection:** Automated checks that the model's output is grounded in the provided context (RAGAS faithfulness metric)
- **Cost monitoring:** Testing for token efficiency — is the model using 200 tokens when 50 would do?
- **Golden datasets:** A fixed set of inputs with human-verified ideal outputs — the gold standard for eval
- **Prompt regression:** When a prompt change improves accuracy on task A but hurts on task B — you need a comprehensive eval set to catch regressions

## A Concrete Translation Example

**Traditional QA:** 100 test cases → run against API → assert exact output → pass/fail

**AI eval:** 100 eval examples (prompt + expected output pattern) → run LLM → compare with LLM-as-judge on a rubric → score 0–100

Same process. The comparison method changes from exact match to semantic/quality scoring, but the testing discipline — write tests, run them, track results, catch regressions — is the same.

## Key Resources

- RAGAS framework — evaluation metrics for RAG pipelines
- LangSmith — eval set management and tracking
- DeepEval — unit testing framework for LLM outputs
- "Evaluating LLM Systems" (Anthropic guide)
