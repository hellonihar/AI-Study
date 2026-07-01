# 05 - RAG Application: ChatGPT-Over-Your-Notes

## Overview

Build a retrieval-augmented generation (RAG) system that ingests a set of markdown notes, chunks them by semantic boundaries, embeds each chunk into a vector database (ChromaDB), and answers questions about the notes using GPT-4o-mini (or any cheap LLM) with source citations.

## Tech Stack

- **Embeddings** — `text-embedding-3-small` (OpenAI) or `all-MiniLM-L6-v2` (local)
- **Vector store** — ChromaDB (runs embedded, no separate server)
- **LLM** — OpenAI GPT-4o-mini (cheap, fast) or a local model via Ollama
- **Orchestration** — LangChain or pure Python
- **Data** — Markdown notes in a local directory

## Architecture & Design

```
                    INGESTION                               QUERY
┌──────────────────────────┐          ┌──────────────────────────┐
│  markdown/               │          │  user question           │
│  ├── notes.md            │          │       │                  │
│  └── references.md       │          │       ▼                  │
│         │                │          │  embed question          │
│         ▼                │          │       │                  │
│  chunk by paragraphs     │          │       ▼                  │
│  (256-512 tokens, 10%    │          │  ChromaDB similarity     │
│   overlap)               │          │  search (top-k=5)        │
│         │                │          │       │                  │
│         ▼                │          │       ▼                  │
│  embed each chunk        │          │  build prompt:           │
│         │                │          │  "Context: {chunks}      │
│         ▼                │          │   Question: {q}          │
│  store in ChromaDB        │          │   Cite sources."        │
│  (metadata: source file,  │          │       │                  │
│   chunk index)            │          │       ▼                  │
│                          │          │  GPT-4o-mini             │
│                          │          │       │                  │
│                          │          │       ▼                  │
│                          │          │  answer + citations      │
└──────────────────────────┘          └──────────────────────────┘
```

**Design decisions:**

- **Chunk by semantic boundaries** (paragraphs, sections) rather than fixed token counts. Fixed chunks often split sentences mid-thought, destroying meaning and reducing retrieval quality.
- **10% overlap** between chunks ensures that a question spanning a chunk boundary still retrieves the relevant context.
- **ChromaDB** instead of Pinecone/Qdrant because it runs embedded (no infrastructure) and is ideal for a single-user learning project. The API is the same, so migrating later is trivial.
- **Source citation in the prompt** — the LLM is instructed to cite which file and section each part of the answer comes from. This grounds the response and lets the user verify.

## Setup & Run

1. Install dependencies:
   ```bash
   pip install chromadb openai langchain langchain-openai
   ```
2. Ingest your markdown notes:
   ```python
   # ingest.py
   import os
   from langchain.text_splitter import RecursiveCharacterTextSplitter
   from langchain_community.vectorstores import Chroma
   from langchain_openai import OpenAIEmbeddings

   splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
   docs = []
   for fname in os.listdir("notes/"):
       with open(f"notes/{fname}") as f:
           chunks = splitter.split_text(f.read())
           for i, chunk in enumerate(chunks):
               docs.append({"text": chunk, "source": fname, "chunk": i})

   embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
   vectorstore = Chroma.from_texts(
       texts=[d["text"] for d in docs],
       embedding=embeddings,
       metadatas=[{"source": d["source"], "chunk": d["chunk"]} for d in docs],
       persist_directory="./chroma_db")
   vectorstore.persist()
   ```
   ```bash
   python ingest.py
   ```
3. Query the RAG system:
   ```python
   # query.py
   from langchain_openai import ChatOpenAI, OpenAIEmbeddings
   from langchain_community.vectorstores import Chroma
   from langchain.prompts import ChatPromptTemplate

   vectorstore = Chroma(persist_directory="./chroma_db",
                        embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"))
   retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
   llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
   prompt = ChatPromptTemplate.from_template(
       "Answer the question using ONLY the context below. "
       "Cite the source file for each claim.\n\nContext: {context}\n\nQuestion: {question}")

   def answer(question):
       context = "\n\n".join(
           f"[{d.metadata['source']}] {d.page_content}"
           for d in retriever.get_relevant_documents(question))
       return llm.invoke(prompt.format(context=context, question=question))

   print(answer("What did I learn about transformers?"))
   ```
   ```bash
   python query.py
   ```

## What You Learn

- The full RAG cycle: chunk → embed → store → retrieve → augment → generate
- Chunking strategies and why they matter for retrieval quality
- Embedding models and vector similarity search
- Prompt engineering for grounded generation with source citations
- The difference between open-book (RAG) and closed-book (pure LLM) question answering
- Debugging retrieval failures: is the chunk not in the DB? Is the embedding not capturing the semantics? Is the prompt confusing the LLM?
