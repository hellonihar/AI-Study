"""
Agent communication: structured message passing between agents.

Run: python 03-agent-communication.py

Requirements: none (stdlib only)
"""

import json
import time
import uuid
from datetime import datetime
from collections import defaultdict

print("=== Agent Communication ===\n")

class AgentMessage:
    def __init__(self, msg_type, sender, recipient, payload, correlation_id=None):
        self.id = uuid.uuid4().hex[:8]
        self.type = msg_type
        self.sender = sender
        self.recipient = recipient
        self.payload = payload
        self.correlation_id = correlation_id or self.id
        self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "sender": self.sender,
            "recipient": self.recipient,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "payload": self.payload,
        }

class MessageBus:
    def __init__(self):
        self.queues = defaultdict(list)
        self.sent_count = 0
        self.delivered_count = 0

    def send(self, message):
        self.queues[message.recipient].append(message)
        self.sent_count += 1
        return message.id

    def receive(self, agent_name):
        messages = self.queues[agent_name]
        if messages:
            self.delivered_count += 1
            return messages.pop(0)
        return None

class BaseAgent:
    def __init__(self, name, bus):
        self.name = name
        self.bus = bus
        self.processed = 0

    def send(self, recipient, msg_type, payload, correlation_id=None):
        msg = AgentMessage(msg_type, self.name, recipient, payload, correlation_id)
        self.bus.send(msg)
        return msg.id

    def receive(self):
        return self.bus.receive(self.name)

class SearchAgent(BaseAgent):
    def process(self, message):
        query = message.payload.get("query", "")
        time.sleep(0.03)
        result = {"results": [f"Doc about {query}"], "count": 1}
        self.processed += 1
        return result

class SummarizeAgent(BaseAgent):
    def process(self, message):
        docs = message.payload.get("documents", [])
        time.sleep(0.04)
        summary = f"Summary of {len(docs)} documents"
        self.processed += 1
        return {"summary": summary}

class Orchestrator(BaseAgent):
    def __init__(self, name, bus, search_agent, summarize_agent):
        super().__init__(name, bus)
        self.search = search_agent
        self.summarize = summarize_agent

    def run(self, query):
        print(f"Orchestrator: Processing query '{query}'\n")

        corr_id = uuid.uuid4().hex[:8]
        print(f"  [1] Sending search request to SearchAgent")
        self.send("search_agent", "search_request",
                  {"query": query}, correlation_id=corr_id)

        search_msg = self.bus.receive("search_agent")
        search_result = self.search.process(search_msg)
        print(f"  [2] Search result: {json.dumps(search_result)}")

        print(f"  [3] Sending summarize request to SummarizeAgent")
        self.send("summarize_agent", "summarize_request",
                  {"documents": search_result["results"]},
                  correlation_id=corr_id)

        summarize_msg = self.bus.receive("summarize_agent")
        summary_result = self.summarize.process(summarize_msg)
        print(f"  [4] Summary result: {json.dumps(summary_result)}")

        final = f"Query: {query}\nSummary: {summary_result['summary']}"
        print(f"\n  Final response:\n  {final}")

        return final

bus = MessageBus()
search_agent = SearchAgent("search_agent", bus)
summarize_agent = SummarizeAgent("summarize_agent", bus)
orchestrator = Orchestrator("orchestrator", bus, search_agent, summarize_agent)

orchestrator.run("Latest advancements in AI")

print(f"\n{'='*60}")
print("Message Bus Stats")
print(f"{'='*60}")
print(f"  Messages sent:       {bus.sent_count}")
print(f"  Messages delivered:  {bus.delivered_count}")
print(f"  Queue depth:         {sum(len(q) for q in bus.queues.values())}")
print(f"\n  Communication pattern: Orchestrator → SearchAgent → Orchestrator → SummarizeAgent → Orchestrator")
