# Data Schemas

The agent uses two MongoDB collections in the `ai_agents` database.

---

## `chunked_docs`

Documentation split into smaller pieces for targeted retrieval. Used by the vector search tool.

```json
{
  "_id": { "$oid": "67d9f3e8ce2fedc0049aa39d" },
  "updated": "2024-05-20T17:30:49.148Z",
  "metadata": {
    "contentType": null,
    "productName": "MongoDB Atlas",
    "tags": ["atlas", "docs"],
    "version": null
  },
  "action": "created",
  "sourceName": "snooty-cloud-docs",
  "body": "# View Database Access History\n\n- This feature...",  // ← content used by LLM to answer questions
  "url": "https://mongodb.com/docs/atlas/access-tracking/",
  "format": "md",
  "title": "View Database Access History",
  "embedding": [...]  // ← 512-dimensional vector (voyage-3-lite), used for vector search
}
```

**Key fields:**
- `body` — the chunk of documentation content passed to the LLM as context.
- `embedding` — vector representation of `body`, indexed with cosine similarity. Required for `$vectorSearch`.

**Vector search index** must be created on the `embedding` field:
- Model: `voyage-3-lite` (512 dimensions)
- Similarity: cosine
- Index name: `vector_index`

---

## `full_docs`

Complete, unchunked documentation pages. Used by the summarization tool. No embeddings — not intended for vector search.

```json
{
  "_id": { "$oid": "67c8999b7d94eee40b7c845d" },
  "updated": "2024-05-20T17:30:49.148Z",
  "metadata": {
    "contentType": null,
    "productName": "MongoDB Atlas",
    "tags": ["atlas", "docs"],
    "version": null
  },
  "action": "created",
  "sourceName": "snooty-cloud-docs",
  "body": "# View Database Access History\n\n- This feature is not available...",  // ← full page content
  "url": "https://mongodb.com/docs/atlas/access-tracking/",
  "format": "md",
  "title": "View Database Access History"
  // no embedding field
}
```

**Key fields:**
- `body` — the full page content sent to the LLM for summarization.
- `title` — queried with an **exact match**. Each title is unique. The tool returns "Document not found" if no match exists.

---

## Why Two Collections?

Chunking is necessary for vector search — smaller chunks give the model targeted, relevant context. But summarization requires the entire page. Combining both approaches into one collection would make one use case worse, so they're kept separate.
