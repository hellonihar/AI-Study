"""
Batch ingestion pipeline: process documents in batches with checkpointing.

Run: python 06-batch-ingestion.py

Requirements: pip install numpy
"""

import time
import json
import hashlib
from datetime import datetime

print("=== Batch Ingestion Pipeline ===\n")

DOCUMENTS = [
    {"id": 1, "source": "confluence", "title": "API Design Guide", "text": "REST APIs should use consistent naming conventions. Use nouns for resources and HTTP methods for actions."},
    {"id": 2, "source": "confluence", "title": "Deployment Guide", "text": "Deployments use Kubernetes with Helm charts. Each service has its own values.yaml."},
    {"id": 3, "source": "sharepoint", "title": "Q3 Report", "text": "Q3 2024 financial performance exceeded targets. Revenue grew 15% YoY to $12.4M."},
    {"id": 4, "source": "sharepoint", "title": "Engineering Roadmap", "text": "H1 2025 priorities: AI integration (Q1), platform migration (Q2), and security hardening."},
    {"id": 5, "source": "email", "title": "Meeting Notes", "text": "Dec 1 standup: Alice working on RAG pipeline. Bob reviewing PR #234. CI/CD pipeline flaky."},
    {"id": 6, "source": "confluence", "title": "Database Schema", "text": "Customers table (id, name, email, phone, status, created_at, updated_at). Index on email."},
    {"id": 7, "source": "email", "title": "Customer Feedback", "text": "Several customers reported slow search times. Need to investigate vector DB query performance."},
    {"id": 8, "source": "email", "title": "Fwd: Meeting Notes", "text": "Fwd: Dec 1 standup: Alice working on RAG pipeline. Bob reviewing PR #234."},
]

CHUNK_SIZE = 100
CHUNK_OVERLAP = 20

class BatchPipeline:
    def __init__(self, batch_size=3):
        self.batch_size = batch_size
        self.checkpoint_file = None
        self.processed_ids = set()
        self.stats = {"total": 0, "succeeded": 0, "failed": 0, "skipped": 0}

    def load_checkpoint(self):
        self.processed_ids = set()
        return len(self.processed_ids)

    def save_checkpoint(self):
        pass

    def chunk_text(self, text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            if end < len(text):
                end = text.rfind(" ", start, end + 1)
                if end == -1 or end - start < chunk_size // 2:
                    end = min(start + chunk_size, len(text))
            chunks.append(text[start:end].strip())
            start = end - overlap if end - overlap > start else end
        return chunks

    def process_document(self, doc):
        doc_id = doc["id"]
        if doc_id in self.processed_ids:
            self.stats["skipped"] += 1
            return {"status": "skipped", "reason": "already processed"}

        try:
            text = doc.get("text", "")
            if not text:
                raise ValueError("Empty text")

            chunks = self.chunk_text(text)
            metadata = {
                "doc_id": f"DOC-{doc_id}",
                "source": doc["source"],
                "title": doc.get("title", ""),
                "chunk_count": len(chunks),
                "processed_at": datetime.utcnow().isoformat(),
                "content_hash": hashlib.md5(text.encode()).hexdigest(),
            }

            self.stats["succeeded"] += len(chunks)
            self.processed_ids.add(doc_id)
            return {"status": "success", "chunks": len(chunks), "metadata": metadata}

        except Exception as e:
            self.stats["failed"] += 1
            return {"status": "failed", "error": str(e)}

    def run(self, documents):
        self.stats["total"] = len(documents)
        batches = [documents[i:i + self.batch_size]
                   for i in range(0, len(documents), self.batch_size)]

        print(f"Processing {len(documents)} documents in {len(batches)} batches "
              f"(batch_size={self.batch_size})...\n")

        for batch_idx, batch in enumerate(batches, 1):
            print(f"  Batch {batch_idx}/{len(batches)}:")

            for doc in batch:
                time.sleep(0.05)
                result = self.process_document(doc)

                status_icon = {"success": "✓", "skipped": "→", "failed": "✗"}
                icon = status_icon.get(result["status"], "?")

                if result["status"] == "success":
                    print(f"    {icon} {doc['title'][:30]:<30} "
                          f"({result['chunks']} chunks)")
                elif result["status"] == "skipped":
                    print(f"    {icon} {doc['title'][:30]:<30} "
                          f"(already processed)")
                else:
                    print(f"    {icon} {doc['title'][:30]:<30} "
                          f"(error: {result.get('error', 'unknown')})")

        self.save_checkpoint()

pipeline = BatchPipeline(batch_size=3)
pipeline.load_checkpoint()
pipeline.run(DOCUMENTS)

print(f"\n{'='*50}")
print("Pipeline Summary")
print(f"{'='*50}")
print(f"  Total documents:  {pipeline.stats['total']}")
print(f"  Chunks created:   {pipeline.stats['succeeded']}")
print(f"  Failed:           {pipeline.stats['failed']}")
print(f"  Skipped (dupes):  {pipeline.stats['skipped']}")
print(f"\nChunking stats (avg chunks/doc): "
      f"{pipeline.stats['succeeded'] / max(pipeline.stats['total'], 1):.1f}")

print(f"\n{'='*50}")
print("Sample Chunk Output")
print(f"{'='*50}")
for doc in DOCUMENTS[:2]:
    chunks = pipeline.chunk_text(doc["text"])
    print(f"\n{doc['title']} ({len(chunks)} chunks):")
    for i, chunk in enumerate(chunks):
        print(f"  [{i+1}] {chunk[:60]}...")
