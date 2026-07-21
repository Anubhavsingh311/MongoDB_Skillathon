# AI Integrations and Frameworks

Atlas Vector Search is highly extensible. You can integrate it with managed services, popular frameworks, or build a custom solution.

---

## Option 1: Fully Managed — Amazon Bedrock

- Skip infrastructure setup entirely
- Set up Atlas as a **Knowledge Base** in Bedrock (a repository that stores and organizes data for retrieval)
- Point Bedrock at your data sources (e.g., S3 bucket of PDFs)
- Bedrock handles: chunking, embeddings, and storing everything in Atlas
- Then create a **Bedrock Agent** that uses the knowledge base for specific tasks

**Ref:** [MongoDB + Amazon Bedrock Docs](https://www.mongodb.com/docs/)

---

## Option 2: Frameworks

All three have official Atlas Vector Search integrations:

| Framework | Notes |
|-----------|-------|
| **LangChain** | Used in this course. Chains retriever + generator via LCEL. |
| **LlamaIndex** | Good for document-heavy pipelines. |
| **Microsoft Semantic Kernel** | Microsoft ecosystem integration. |

---

## Option 3: Custom / Homegrown

Build your own retrieval + generation pipeline without a framework. Atlas Vector Search supports this via the `$vectorSearch` aggregation stage.

---

## LangChain Concepts Used in This Course

**Chains** — series of interconnected tasks, similar to MongoDB aggregation pipelines. Each stage processes data and passes it to the next.

**LCEL (LangChain Expression Language)** — declarative pipe (`|`) syntax for assembling chains:

```python
chain = retrieve | prompt | llm | output_parser
```

**Key LangChain packages:**

| Package | Purpose |
|---------|---------|
| `langchain` | Core framework |
| `langchain_community` | Community integrations (loaders, transformers) |
| `langchain_core` | Runnables, output parsers |
| `langchain_openai` | OpenAI LLM + embeddings |
| `langchain_voyageai` | Voyage AI embeddings |
| `langchain_mongodb` | MongoDB Atlas Vector Search integration |
| `pymongo` | Raw MongoDB driver |
| `pypdf` | PDF parsing |
