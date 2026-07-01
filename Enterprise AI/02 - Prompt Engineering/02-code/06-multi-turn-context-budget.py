"""
Simulate a long multi-turn conversation and measure context growth.
Demonstrate summarization-based compression.

Run: python 06-multi-turn-context-budget.py

Requirements: pip install ollama
"""

import ollama
import tiktoken  # pip install tiktoken

MODEL = "llama3.2:3b"

# Use tiktoken for token counting (approximate)
enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    return len(enc.encode(text))

def simulate_conversation(turns=10):
    history = []
    system = "You are a helpful travel agent. Help the user plan a trip."
    
    questions = [
        "I want to visit Japan in Spring.",
        "What are the best cities to visit?",
        "How many days should I spend in Tokyo?",
        "What's the budget for a 2-week trip?",
        "Should I get a JR Pass?",
        "What's the best time to see cherry blossoms?",
        "Recommend some hotels in Kyoto.",
        "What foods should I try?",
        "Do I need a visa?",
        "Can you create a day-by-day itinerary?",
    ]
    
    for i in range(min(turns, len(questions))):
        # Build the conversation messages
        messages = [{"role": "system", "content": system}]
        messages.extend(history)
        messages.append({"role": "user", "content": questions[i]})
        
        # Count tokens before response
        prompt_text = str(messages)
        prompt_tokens = count_tokens(prompt_text)
        
        # Get response
        resp = ollama.chat(model=MODEL, messages=messages)
        response_text = resp["message"]["content"]
        response_tokens = count_tokens(response_text)
        
        print(f"Turn {i+1}: Context before = {prompt_tokens:5d} tokens, "
              f"Response = {response_tokens:3d} tokens, "
              f"Total history turns = {len(history)//2 + 1}")
        
        history.append({"role": "user", "content": questions[i]})
        history.append({"role": "assistant", "content": response_text})
    
    return history

# ─── Run without compression ───
print("=== Uncompressed Conversation ===")
history = simulate_conversation(turns=10)
print(f"\nFinal context size: ~{sum(count_tokens(str(h)) for h in history)} tokens")

# ─── Now with summarization ───
print("\n\n=== With Summarization Compression ===")

def compress_history(history, max_turns=4):
    """Compress old turns into a summary, keep last N turns full."""
    if len(history) <= max_turns * 2:
        return history
    
    # Extract old turns (everything before the last max_turns)
    old_turns = history[:-(max_turns * 2)]
    recent_turns = history[-(max_turns * 2):]
    
    # Summarize old turns
    old_text = "\n".join(
        f"{'User' if t['role'] == 'user' else 'Assistant'}: {t['content'][:200]}"
        for t in old_turns
    )
    
    summary_prompt = f"Summarize this conversation, preserving all user preferences, decisions, and unresolved questions:\n\n{old_text}"
    resp = ollama.chat(model=MODEL, messages=[{"role": "user", "content": summary_prompt}])
    summary = resp["message"]["content"]
    
    print(f"\nCompression: {count_tokens(str(old_turns))} tokens → {count_tokens(summary)} tokens "
          f"({count_tokens(str(old_turns)) / max(1, count_tokens(summary)):.1f}× compression)")
    
    # Rebuild history with summary + recent turns
    return [
        {"role": "system", "content": f"Previous conversation summary: {summary}"}
    ] + recent_turns

compressed_history = simulate_conversation(turns=10)
for i in range(3):
    compressed_history = compress_history(compressed_history, max_turns=4)

print(f"\nFinal compressed context: ~{sum(count_tokens(str(h)) for h in compressed_history)} tokens")
print(f"Without compression it would have been: ~{sum(count_tokens(str(h)) for h in history)} tokens")
