# Module 4: Perform a Vector Search

> **Course:** MongoDB Atlas Vector Search Fundamentals  
> **Section:** Perform a Vector Search → Video: Create a Search Query Using Vector Search

---

## Core Principle: Vectorize Your Query

You cannot compare a text string against numeric vectors directly. Before running a search, you must embed your query using **the same model used to index the data**. Using a different model produces vectors in an incompatible space — results will be meaningless.

```python
# Generate the query embedding (same model as used during indexing)
query = "A movie about people who are trying to escape from a maximum security facility"
embedding = get_embeddings(query, model="voyage-3.5-lite", api_key=api_key)
```

---

## The `$vectorSearch` Aggregation Stage

`$vectorSearch` performs an approximate nearest neighbor (aNN) search on the HNSW graph built by your index.

**Rules:**
- Must be the **first stage** in the aggregation pipeline (same constraint as `$search`).
- Driver support: PyMongo, Node.js, Java, C# (check MongoDB docs for additions).

---

## Basic Vector Search Query

```python
pipeline = [
    {
        "$vectorSearch": {
            "index": "vectorPlotIndex",      # name of your vector search index
            "path": "plot_embedding",         # field containing the stored embeddings
            "queryVector": embedding,         # your query embedded with the same model
            "numCandidates": 100,             # number of aNN traversal restarts
            "limit": 10                       # number of results to return
        }
    },
    {
        "$project": {
            "title": 1,
            "plot": 1,
            "score": {"$meta": "vectorSearchScore"}   # similarity score
        }
    }
]

results = collection.aggregate(pipeline)
```

---

## Understanding `numCandidates`

`numCandidates` controls how many times the aNN algorithm restarts from a different random entry point on the top HNSW layer before returning results.

- **Higher numCandidates** → searches more of the graph → higher accuracy → higher latency.
- **Lower numCandidates** → faster but more likely to miss the true nearest neighbors.

**Recommended starting ratio: 10:1** (numCandidates to limit).

```
numCandidates: 100
limit: 10
→ ratio: 10:1  ✓
```

Adjust based on your latency vs. accuracy requirements.

---

## Vector Search with Pre-filter

If you declared a `filter` field in your index (Module 3), you can use it at query time to narrow the search space before aNN traversal. This is more efficient than post-filtering because irrelevant documents are excluded before the graph search begins.

```python
pipeline = [
    {
        "$vectorSearch": {
            "index": "vectorPlotIndex",
            "path": "plot_embedding",
            "queryVector": embedding,
            "numCandidates": 100,
            "filter": {"year": {"$gt": 2010}},   # pre-filter applied before aNN search
            "limit": 10
        }
    },
    {
        "$project": {
            "title": 1,
            "plot": 1,
            "year": 1,
            "score": {"$meta": "vectorSearchScore"}
        }
    }
]

results = collection.aggregate(pipeline)
```

> Always use pre-filtering when possible. Searching an entire HNSW graph with thousands of dimensions is resource-intensive — filtering up front reduces that cost significantly.

---

## Semantic Search vs. Keyword Search

This is the key practical difference between vector search and traditional text search:

| | Keyword Search | Vector Search |
|---|---|---|
| Query type | Exact terms | Natural language description |
| Matches on | Literal string presence | Semantic meaning |
| Example query | `"prison escape"` | `"people trying to get out of a high-security facility"` |
| Returns | Documents containing those words | Documents about that concept |

A vector search for *"inmate leading a rebellion"* can return a movie whose plot says *"prisoners organize an uprising"* — no keyword overlap required.

---

## `get_embeddings` Function (Reusable)

```python
import requests
import json

def get_embeddings(text, model, api_key):
    url = 'https://api.voyageai.com/v1/embeddings'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + api_key
    }
    data = {
        'input': text,
        'model': model
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()['data'][0]['embedding']
```

Use this same function for both indexing (Module 2) and querying — the model must be identical in both contexts.

---

## Key Takeaways

- Embed your query with the same model used at index time. This is non-negotiable.
- `$vectorSearch` must be the first pipeline stage.
- Start with `numCandidates` at 10x your `limit`; tune from there based on latency needs.
- Pre-filtering is declared in the index and applied in the query via the `filter` key.
- Vector search returns results by semantic meaning, not keyword presence — write queries as descriptions, not search terms.
- Use `{"$meta": "vectorSearchScore"}` in `$project` to surface the similarity score for debugging or ranking UI.
