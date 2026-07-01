# Prompts and Templates

## Prompt Primitives

Prompts are pre-defined templates that the host can use to guide the LLM's behavior. They are reusable, parameterized, and server-defined.

## Prompt Definition

```python
@server.prompt()
def code_review(language: str, code_snippet: str) -> str:
    """
    Review code for bugs, security issues, and best practices.

    Args:
        language: Programming language (python, javascript, rust, etc.)
        code_snippet: The code to review
    """
    return f"""
    Please review the following {language} code:

    ```{language}
    {code_snippet}
    ```

    Focus on:
    1. **Security vulnerabilities** (injection, XSS, path traversal)
    2. **Performance issues** (N+1 queries, memory leaks)
    3. **Best practices** (error handling, logging, type safety)
    4. **Potential bugs** (off-by-one, race conditions, edge cases)

    Format your response as:
    - **Critical issues** (must fix)
    - **Warnings** (should fix)
    - **Suggestions** (nice to have)
    """
```

## Prompt Parameters

Prompts support named parameters with types:

```python
@server.prompt()
def meeting_summary(
    transcript: str,
    max_length: int = 200,
    include_action_items: bool = True,
) -> str:
    """
    Summarize a meeting transcript.

    Args:
        transcript: Full meeting transcript text
        max_length: Maximum summary length in words
        include_action_items: Whether to extract action items
    """
    template = f"""Summarize this meeting transcript in at most {max_length} words.

    Transcript:
    {transcript}

    """
    if include_action_items:
        template += "\nInclude action items with assignees."
    else:
        template += "\nFocus on key decisions and outcomes only."

    return template
```

## Prompt Templates

Template patterns for common use cases:

### Document Analysis
```
Analyze the following document:
{document_content}

Provide:
- Main topics (3-5 bullet points)
- Key findings
- Recommendations
```

### Data Extraction
```
Extract structured information from the following text:

Text: {input_text}

Fields to extract:
{fields}

Format as JSON.
```

### Translation
```
Translate the following text from {source_language} to {target_language}.

Text: {text}

Maintain the original tone and style.
```

## Dynamic Prompts

Prompts can depend on resources or server state:

```python
@server.prompt()
def analyze_document(uri: str) -> str:
    """Analyze a document by its URI."""
    content = read_resource(uri)  # Fetch resource content
    if content is None:
        return "Error: Document not found."
    return f"""
    Analyze the following document:

    {content}

    Provide analysis including: structure, key arguments,
    data quality, and recommendations.
    """
```

## Prompt Composition

Prompts can reference other prompts or resources:

```python
@server.prompt()
def comprehensive_review(code_uri: str, requirements_uri: str) -> str:
    """Compare code against requirements."""
    code = read_resource(code_uri)
    requirements = read_resource(requirements_uri)

    review_prompt = server.get_prompt("code_review",
                                       language="python",
                                       code_snippet=code)

    return f"""
    {review_prompt}

    Additional context - requirements:
    {requirements}

    Verify the code meets all requirements.
    """
```

## Best Practices for Prompts

1. **Clear instructions**: Be explicit about what the LLM should do
2. **Structured output**: Specify format (JSON, bullet points, etc.)
3. **Constraints**: Include length limits, style guides, tone requirements
4. **Examples**: Include few-shot examples for complex tasks
5. **Fallback**: Provide default behavior if parameters are missing
