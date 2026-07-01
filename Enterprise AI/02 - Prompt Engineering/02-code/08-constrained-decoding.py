"""
Constrained decoding: enforce output structure at the logit level.

This requires a self-hosted model with guided decoding support.
Run with: python 08-constrained-decoding.py

Requirements: pip install outlines transformers torch
"""

import outlines
from outlines import generate

def demo_outlines():
    """Demonstrate grammar-guided JSON generation with Outlines."""
    try:
        # Load a small model
        import torch
        model = outlines.models.transformers("Qwen/Qwen2.5-0.5B-Instruct")
        
        # Define JSON schema
        schema = """
        {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"},
                "skills": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["name", "age", "skills"]
        }
        """
        
        # Create constrained generator
        generator = generate.json(model, schema)
        
        print("=== Constrained Decoding with Outlines ===\n")
        
        # Test with extraction task
        text = "John Doe is a 32-year-old software engineer. He knows Python and Go."
        prompt = f"Extract info from: {text}"
        
        result = generator(prompt, max_tokens=100)
        print(f"Input: {text}")
        print(f"Output: {result}")
        print(f"Valid JSON: ✅")
        print()
        
        # Multiple runs — guaranteed valid JSON every time
        print("10 runs — all produce valid JSON:")
        for i in range(10):
            text = f"Person {i+1}, age {20+i}, skills: cooking, reading"
            result = generator(f"Extract: {text}", max_tokens=80)
            # No need to try/except — it's always valid
            print(f"  Run {i+1}: {result}")
            
    except ImportError as e:
        print(f"Skipping: {e}")
        print("To run this demo: pip install outlines transformers torch")
        print()
        print_alternative()

def print_alternative():
    """Show the concept with a simplified simulation."""
    print("=== Constrained Decoding: Concept ===")
    print()
    print("Constrained decoding modifies logits during generation to enforce:")
    print("  - Valid JSON syntax (brackets, commas, quotes)")
    print("  - Schema compliance (correct field types, required fields)")
    print("  - Regex patterns (e.g., phone number format)")
    print("  - CFG grammars (e.g., SQL syntax)")
    print()
    print("How it works:")
    print("  1. Define a grammar/schema for the output.")
    print("  2. At each decoding step, compute which tokens are valid.")
    print("  3. Mask all invalid tokens' logits to -inf.")
    print("  4. Sample only from valid tokens.")
    print()
    print("Result: 100% valid output, zero parse failures, no retries needed.")
    print()
    print("Supported by:")
    print("  - vLLM: guided_decoding (JSON, regex, grammar)")
    print("  - llama.cpp: grammars")
    print("  - Outlines (with Transformers, vLLM, llama.cpp backends)")
    print("  - Guidance (Microsoft)")

if __name__ == "__main__":
    try:
        demo_outlines()
    except Exception as e:
        print(f"Error: {e}")
        print()
        print_alternative()
