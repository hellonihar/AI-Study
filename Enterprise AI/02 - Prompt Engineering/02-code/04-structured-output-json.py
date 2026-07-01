"""
Compare methods for reliably extracting structured JSON from LLM output.

Run: python 04-structured-output-json.py

Requirements: pip install ollama
"""

import ollama
import json
import re

MODEL = "llama3.2:3b"

# ─── Method 1: Prompt-only JSON extraction ───
def extract_json_prompt(text):
    prompt = f"""Extract the following information as JSON:
- name (string)
- age (number)
- occupation (string)
- skills (array of strings)

Text: {text}

Output ONLY valid JSON, no other text:"""
    resp = ollama.chat(model=MODEL, messages=[
        {"role": "user", "content": prompt},
    ])
    content = resp["message"]["content"]
    # Try to parse JSON
    try:
        # Find JSON block if wrapped in code fences
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        pass
    return {"error": "parse_failed", "raw": content}

# ─── Method 2: JSON mode with function calling simulation ───
def extract_json_function(text):
    prompt = f"""You are a data extraction system. Your output must be valid JSON matching this schema:
{{
    "name": "string",
    "age": "number",
    "occupation": "string",
    "skills": ["string"]
}}

Text: {text}

JSON output:"""
    resp = ollama.chat(model=MODEL, messages=[
        {"role": "user", "content": prompt},
    ])
    content = resp["message"]["content"]
    try:
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        pass
    return {"error": "parse_failed", "raw": content}

# ─── Method 3: Prompt + retry pattern ───
def extract_json_with_retry(text, max_retries=2):
    for attempt in range(max_retries + 1):
        prompt = f"""Extract JSON from this text. Valid JSON only.
Schema: {{"name": "string", "age": "number", "occupation": "string", "skills": ["string"]}}

Text: {text}"""

        if attempt > 0:
            prompt = f"""Previous attempt failed with error: {last_error}
Fix the JSON. Schema: {{"name": "string", "age": "number", "occupation": "string", "skills": ["string"]}}

Text: {text}"""

        resp = ollama.chat(model=MODEL, messages=[
            {"role": "user", "content": prompt},
        ])
        content = resp["message"]["content"]
        try:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError as e:
            last_error = str(e)
            continue
    return {"error": "all_retries_failed", "raw": content}

# ─── Test ───
TEXTS = [
    "Alice Johnson is a 32-year-old software engineer. She knows Python, Go, and Kubernetes.",
    "Bob Smith, age 45, works as a data scientist. Skills: SQL, Python, machine learning, statistics.",
    "Carol is 28 and a product manager. She specializes in user research and agile methodology.",
]

print("=== Structured JSON Extraction Comparison ===\n")

for text in TEXTS:
    print(f"Text: {text[:60]}...")
    r1 = extract_json_prompt(text)
    r2 = extract_json_function(text)
    r3 = extract_json_with_retry(text)
    print(f"  Prompt-only:    {'✅' if 'error' not in r1 else '❌ ' + str(r1.get('error', ''))}")
    print(f"  Function-style: {'✅' if 'error' not in r2 else '❌ ' + str(r2.get('error', ''))}")
    print(f"  Retry:          {'✅' if 'error' not in r3 else '❌ ' + str(r3.get('error', ''))}")
    if 'error' not in r1:
        print(f"    → {json.dumps(r1)}")
    print()
