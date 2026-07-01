# Advanced RAG Patterns

Beyond naive RAG: techniques that improve reliability, handle complex queries, and reduce hallucination.

## Taxonomy

```
                      ┌─────────────────┐
                      │  Advanced RAG    │
                      └────────┬────────┘
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
   ┌─────────────┐    ┌─────────────────┐   ┌──────────────┐
   │ Corrective   │    │   Self-RAG      │   │  Agentic RAG │
   │ RAG (CRAG)   │    │   (Self-RAG)    │   │  (Agentic)   │
   └─────────────┘    └─────────────────┘   └──────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
   Retry/refine        Self-critique         Tool use, multi-step
   retrieval           + reflection          decision-making
```

## 1. Corrective RAG (CRAG)

When retrieval quality is uncertain, correct rather than fail.

```python
def corrective_rag(query):
    chunks = retrieve(query, top_k=5)
    relevance = compute_relevance_scores(query, chunks)

    if relevance < LOW_THRESHOLD:
        # Retrieval failed — try alternative
        new_query = rewrite_query(query)
        return corrective_rag(new_query)

    elif relevance < MEDIUM_THRESHOLD:
        # Partial retrieval — keep good chunks, search more
        good_chunks = [c for c in chunks if c.score > MEDIUM_THRESHOLD]
        new_chunks = expand_search(query, exclude=good_chunks_ids)
        return generate(query, good_chunks + new_chunks)

    else:
        # High quality — generate normally
        return generate(query, chunks)
```

**Key mechanism:** A lightweight relevance classifier scores each retrieved chunk. Low scores trigger correction.

**Relevance classifier:** Train a binary classifier (relevant / not relevant) on (query, passage) pairs. A cross-encoder fine-tuned on 1K labeled examples achieves 0.90+ accuracy.

## 2. Self-RAG

The LLM reflects on its own retrieval and generation quality, deciding when to retrieve and when to trust its own knowledge.

```python
def self_rag(query):
    # Step 1: Does the query require retrieval?
    if not should_retrieve(query):
        return llm.generate(query)  # use parametric knowledge

    # Step 2: Retrieve and generate with critique
    chunks = retrieve(query, top_k=5)
    draft = llm.generate(query, chunks)

    # Step 3: Self-critique
    critique = llm.evaluate(
        f"Does the answer address the query? "
        f"Are all claims supported by the passages?"
    )

    if critique.passes:
        return draft
    else:
        return self_rag(rewrite_query(query))
```

**Key mechanisms:**
1. **Retrieval token** — special token `<retrieve>` that the LLM can emit when it decides to search
2. **Critique tokens** — after generation, the model emits `<relevant>`, `<supported>`, `<useful>` tokens to self-evaluate
3. **Reflection** — if critique fails, iterate

**Training:** The model is fine-tuned on a dataset of (query, retrieved, response, critique) examples. Requires ~10K labeled examples.

## 3. Agentic RAG

The LLM uses tools (search, code execution, database queries) to dynamically decide how to gather information.

```python
def agentic_rag(query, max_steps=5):
    context = []
    for step in range(max_steps):
        action = llm.decide_next_action(
            query=query,
            context=context,
            tools=["vector_search", "web_search", "sql_query", "python"]
        )

        if action.type == "answer":
            return action.response

        elif action.type == "vector_search":
            chunks = vector_search(action.params)
            context.extend(chunks)

        elif action.type == "web_search":
            results = web_search(action.params)
            context.extend(results)

        elif action.type == "sql_query":
            rows = execute_sql(action.params)
            context.append(format_rows(rows))

    return generate(query, context)
```

**Framework support:** LangChain, LlamaIndex, AutoGen, CrewAI all support tool-using agents that can perform multi-step retrieval.

## 4. Graph RAG

Combine knowledge graph structure with vector search for multi-hop reasoning over entities.

```
Query: "Which drugs interact with Aspirin?"
    ↓
Step 1: Extract entity: "Aspirin" → node ID: drug/aspirin
Step 2: Vector search: [embedding of "Aspirin"] → find related entities
Step 3: Graph traversal: Aspirin → interacts_with → [list of drugs]
Step 4: Retrieve text for each drug node
Step 5: Generate answer with graph context
```

Microsoft's GraphRAG (2024) builds a hierarchical graph of entities and communities from document corpora, enabling:
- Multi-hop reasoning over entity relationships
- Community-level summarization ("what is the overall theme of this document set?")
- 20-40% better recall on multi-hop questions vs. naive RAG

## 5. Fusion RAG / Multi-Query RAG

Generate multiple query variations, retrieve for each, merge results.

```python
def fusion_rag(query):
    variations = llm.generate(
        f"Generate 5 different phrasings of: {query}"
    )
    all_chunks = []
    for v in variations:
        chunks = retrieve(v, top_k=5)
        all_chunks.extend(chunks)

    # Deduplicate and re-rank
    deduped = deduplicate(all_chunks)
    ranked = re_rank(query, deduped)
    return generate(query, ranked[:10])
```

**Benefit:** Captures diverse aspects of a query. Improves recall by 10-20% on ambiguous queries.

## 6. RAPTOR (Recursive Abstractive Processing)

Build a hierarchical tree of document summaries for efficient retrieval.

```
Level 0: Raw chunks (512 tokens each)
Level 1: Summarize 5 chunks → summary node (256 tokens)
Level 2: Summarize 5 level-1 summaries → higher summary
Level 3: ... (recursive)

Retrieval: Search all levels → return most relevant + their children
```

**Benefit:** Captures both high-level themes and supporting details. Effective for book-length documents.

## Comparison

| Pattern | Complexity | Retrieval Quality | Latency | When to Use |
|---|---|---|---|---|
| Corrective RAG | Medium | High | +50-200ms | Retrieval is unreliable |
| Self-RAG | Very high | Very high | +200-500ms | Need self-reflection |
| Agentic RAG | High | Very high | +500ms-several s | Multi-step reasoning |
| Graph RAG | High | Very high | +100-500ms | Entity-heavy domains |
| Fusion RAG | Low | High | +50-100ms | Ambiguous queries |
| RAPTOR | Medium | High | +50-100ms | Long documents |

## Production Recommendation

Start with **Corrective RAG** — it provides the most quality improvement for the least complexity. Add **Agentic RAG** only when you need multi-step tool use. **Self-RAG** requires model fine-tuning — only worth it for very high-stakes applications.
