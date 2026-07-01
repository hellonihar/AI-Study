"""
Debate agents: two agents argue positions, judge decides.

Run: python 06-debate-agent.py

Requirements: none (stdlib only)
"""

import json
import time

print("=== Debate System ===\n")

class DebateAgent:
    def __init__(self, name, position):
        self.name = name
        self.position = position
        self.arguments = []

    def argue(self, topic, opposing_argument=None):
        time.sleep(0.03)
        if not opposing_argument:
            argument = f"I support {self.position} because the evidence "
            argument += "clearly shows this is the optimal approach. "
            argument += f"Multiple studies confirm that {topic} benefits from this direction."
        else:
            argument = f"My opponent claims \"{opposing_argument[:40]}...\" "
            argument += f"but this overlooks the key fact that {self.position} "
            argument += "has been proven more effective in comparable scenarios."

        self.arguments.append(argument)
        return argument

class Judge:
    def __init__(self):
        self.name = "judge"
        self.decisions = []

    def evaluate(self, topic, pro_agent, con_agent):
        print(f"  Judge evaluating debate on: {topic}")
        print(f"  Pro ({pro_agent.name}): {len(pro_agent.arguments)} arguments")
        print(f"  Con ({con_agent.name}): {len(con_agent.arguments)} arguments")

        pro_strength = sum(len(a) for a in pro_agent.arguments)
        con_strength = sum(len(a) for a in con_agent.arguments)

        if pro_strength > con_strength:
            winner = pro_agent.name
            reasoning = "Pro position had more detailed and substantiated arguments."
        else:
            winner = con_agent.name
            reasoning = "Con position presented stronger counterarguments."

        decision = {
            "topic": topic,
            "winner": winner,
            "reasoning": reasoning,
            "pro_arguments": len(pro_agent.arguments),
            "con_arguments": len(con_agent.arguments),
        }
        self.decisions.append(decision)
        return decision

def run_debate(topic):
    print(f"\n{'='*60}")
    print(f"Debate Topic: {topic}")
    print(f"{'='*60}")

    pro = DebateAgent("proponent", "in favor")
    con = DebateAgent("opponent", "against")
    judge = Judge()

    print(f"\nRound 1 — Opening Statements:")
    pro_arg = pro.argue(topic)
    print(f"  Pro: {pro_arg}")
    con_arg = con.argue(topic)
    print(f"  Con: {con_arg}")

    print(f"\nRound 2 — Rebuttals:")
    pro_rebuttal = pro.argue(topic, con_arg)
    print(f"  Pro: {pro_rebuttal}")
    con_rebuttal = con.argue(topic, pro_arg)
    print(f"  Con: {con_rebuttal}")

    print(f"\nRound 3 — Closing Statements:")
    pro_closing = pro.argue(topic, con_rebuttal)
    print(f"  Pro: {pro_closing[:60]}...")
    con_closing = con.argue(topic, pro_rebuttal)
    print(f"  Con: {con_closing[:60]}...")

    decision = judge.evaluate(topic, pro, con)
    print(f"\n  ⚖ Judge's Decision:")
    print(f"     Winner: {decision['winner']}")
    print(f"     Reasoning: {decision['reasoning']}")

    return decision

topics = [
    "Should AI development be regulated?",
    "Should companies open-source their AI models?",
]

for topic in topics:
    run_debate(topic)

print(f"\n{'='*60}")
print("Debate System Summary")
print(f"{'='*60}")
print("  Pattern: Pro → Con → Rebuttal → Rebuttal → Closing → Judge")
print("  Each agent makes evidence-based arguments")
print("  Judge evaluates argument quality, not quantity")
