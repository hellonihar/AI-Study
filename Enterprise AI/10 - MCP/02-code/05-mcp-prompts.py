"""
MCP prompts: defining prompt templates with parameter substitution.

Run: python 05-mcp-prompts.py

Requirements: none (stdlib only)
"""

import json
import re
from datetime import datetime

print("=== MCP Prompts ===\n")

class Prompt:
    def __init__(self, name, description, arguments, template):
        self.name = name
        self.description = description
        self.arguments = arguments
        self.template = template

    def render(self, args):
        validated = {}
        for arg in self.arguments:
            name = arg["name"]
            if name in args:
                validated[name] = args[name]
            elif arg.get("required", True):
                if "default" in arg:
                    validated[name] = arg["default"]
                else:
                    return {"error": f"Missing required argument: {name}"}
            else:
                validated[name] = arg.get("default", "")

        try:
            content = self.template.format(**validated)
            return {"content": [{"type": "text", "text": content}]}
        except KeyError as e:
            return {"error": f"Template rendering error: missing {e}"}

PROMPTS = [
    Prompt(
        name="code_review",
        description="Review source code for bugs, security issues, and best practices",
        arguments=[
            {"name": "language", "description": "Programming language", "required": True},
            {"name": "code", "description": "Source code to review", "required": True},
            {"name": "style", "description": "Review style (brief/detailed)", "default": "detailed"},
        ],
        template="""Review the following {language} code:

```{language}
{code}
```

Style: {style}

Please analyze for:
1. Security vulnerabilities
2. Performance issues
3. Best practices violations
4. Potential bugs

Format as:
- Critical (must fix)
- Warnings (should fix)
- Suggestions (nice to have)""",
    ),
    Prompt(
        name="meeting_summary",
        description="Summarize a meeting transcript with action items",
        arguments=[
            {"name": "transcript", "description": "Meeting transcript", "required": True},
            {"name": "max_words", "description": "Maximum summary length", "default": "200"},
            {"name": "include_actions", "description": "Include action items", "default": "true"},
        ],
        template="""Summarize this meeting transcript in at most {max_words} words:

Transcript:
{transcript}

{f"Extract action items with assignees." if include_actions == "true" else "Focus on key decisions and outcomes only."}

Format:
- Key decisions
- Discussion points
{f"- Action items" if include_actions == "true" else ""}""",
    ),
    Prompt(
        name="translate",
        description="Translate text between languages maintaining tone and style",
        arguments=[
            {"name": "text", "description": "Text to translate", "required": True},
            {"name": "source_lang", "description": "Source language", "default": "auto"},
            {"name": "target_lang", "description": "Target language", "required": True},
        ],
        template="""Translate the following text from {source_lang} to {target_lang}.

Original text:
{text}

Requirements:
- Maintain the original tone and style
- Preserve formatting (lists, headings, emphasis)
- Keep technical terms accurate
- Adapt idioms appropriately

Return only the translated text, no explanations.""",
    ),
]

print("Available Prompts:\n")
for prompt in PROMPTS:
    print(f"  {prompt.name}")
    print(f"    {prompt.description}")
    for arg in prompt.arguments:
        req = " (required)" if arg.get("required", True) else f" (default: {arg.get('default', 'none')})"
        print(f"    • {arg['name']}: {arg['description']}{req}")
    print(f"    Template preview: {prompt.template[:60]}...")
    print()

print(f"{'='*60}")
print("Rendering Prompts")
print(f"{'='*60}")

test_cases = [
    ("code_review", {"language": "python", "code": "def add(a, b):\n    return a + b", "style": "brief"}),
    ("code_review", {"language": "python", "code": "import os\ndef run(cmd):\n    os.system(cmd)"}),
    ("meeting_summary", {"transcript": "Alice: Let's discuss Q1 goals. Bob: Focus on AI features.", "max_words": "100"}),
    ("translate", {"text": "Hello, how are you?", "target_lang": "Spanish"}),
]

for name, args in test_cases:
    print(f"\n  Prompt: {name}")
    print(f"  Args:   {args}")

    prompt = next((p for p in PROMPTS if p.name == name), None)
    if prompt:
        result = prompt.render(args)
        if "error" in result:
            print(f"  Error: {result['error']}")
        else:
            text = result["content"][0]["text"]
            lines = text.split("\n")
            print(f"  Rendered ({len(lines)} lines):")
            for line in lines[:5]:
                print(f"    {line[:70]}")
            if len(lines) > 5:
                print(f"    ... ({len(lines) - 5} more lines)")
    print()
