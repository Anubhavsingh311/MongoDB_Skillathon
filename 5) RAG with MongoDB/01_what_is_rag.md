# What is RAG?

**RAG** = Retrieval Augmented Generation

A technique that extends LLM knowledge by retrieving relevant data from an external source and injecting it into the prompt at inference time.

---

## Why RAG Exists — LLM Limitations

### 1. Insufficient / Private Data
LLMs train on public data. They cannot accurately answer questions about internal company data, proprietary systems, or domain-specific corpora.

### 2. Stale Data
Models have a training cutoff. They cannot answer accurately about developments after that date. RAG allows injecting current data without retraining.

### 3. Context Window Overload (Token Limit)
The context window is the maximum number of tokens the LLM can consider at once. A **token ≈ 1 word**. When the limit is hit, the model drops earlier tokens, degrading response quality. RAG mitigates this by sending only the most relevant chunks.

---

## How RAG Solves These Problems

| Problem | RAG Solution |
|---------|-------------|
| Private data | Inject proprietary data as context in the prompt |
| Stale data | Inject recent data without waiting for model updates |
| Token overflow | Retrieve only the most relevant chunks — efficient token use |

---

## RAG Architecture (High Level)

### Ingestion Pipeline (one-time / scheduled)
```
Raw Data (PDF, HTML, JSON, etc.)
    → Sanitize
    → Chunk
    → Generate Embeddings (Embedding Model)
    → Store chunks + embeddings in Atlas
```

### Query Pipeline (per request)
```
User Query
    → Vectorize query (same Embedding Model)
    → Atlas Vector Search → retrieve top-k relevant chunks
    → Build prompt: chunks + query (natural language)
    → Send prompt to Generative Model
    → Return answer to user
```

---

## Two Models — Important Distinction

| Model Type | Purpose |
|------------|---------|
| **Embedding Model** | Converts text → dense vector. Used during ingestion AND retrieval. Must be the same model for both. |
| **Generative Model** | Produces human-like text responses. Receives the assembled prompt and generates the answer. |

These are **different models** serving different roles. Do not conflate them.
