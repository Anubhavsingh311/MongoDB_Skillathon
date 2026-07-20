# Vector Search Fundamentals — Cheat Sheet

> MongoDB University · Atlas Vector Search Fundamentals

---

## Concept Map

```
Unstructured Data (text, images, audio)
        ↓
  Embedding Model  (e.g. voyage-3.5-lite)
        ↓
  Vector / Embedding  [0.02, -0.41, 0.89, ...]
        ↓
  Stored as field on MongoDB document  (plot_embedding)
        ↓
  HNSW Index  (vectorPlotIndex)
        ↓
  $vectorSearch  ← query also embedded with same model
        ↓
  Results ranked by similarity score
```

---

## Voyage AI Models

| Model | Use Case |
|---|---|
| `voyage-3.5-lite` | General-purpose (used in this course) |
| `voyage-3.5` | General-purpose, higher capacity |
| `voyage-law-2` | Legal documents |
| `voyage-code-2` | Code |
| `voyage-context-3` | RAG — chunk + global context in one pass |

`voyage-3.5-lite` dimensions: 256 / 512 / **1024** (default) / 2048

---

## Similarity Functions

| Function | Measures | Requirement | When to Use |
|---|---|---|---|
| `euclidean` | Point-to-point distance | None | General distance-based similarity |
| `cosine` | Angle only | No zero-magnitude vectors | Check model docs; MongoDB recommends using dotProduct instead |
| `dotProduct` | Angle + magnitude | Vectors must be unit-normalized | Preferred when model supports it |

**Rule:** Match the similarity function to what your embedding model was trained with.

---

## HNSW in 30 Seconds

- Multi-layer graph: layer 0 = all points + short links; top layer = few points + long links
- Search: enter top layer randomly → move toward query → drop a layer → repeat → reach bottom
- **aNN** (approximate nearest neighbor): doesn't check every point; fast but small chance of outliers
- Atlas builds and manages HNSW automatically
- Memory-intensive: use dedicated search nodes in production

---

## Index Creation

```javascript
// Basic
db.movies.createSearchIndex("vectorPlotIndex", "vectorSearch", {
  "fields": [
    { "type": "vector", "path": "plot_embedding", "numDimensions": 1024, "similarity": "cosine" }
  ]
});

// With pre-filter
db.movies.createSearchIndex("vectorPlotIndex", "vectorSearch", {
  "fields": [
    { "type": "vector", "path": "plot_embedding", "numDimensions": 1024, "similarity": "cosine" },
    { "type": "filter", "path": "year" }   // number | string | boolean only
  ]
});
```

---

## Query Templates

```python
# Basic
pipeline = [
    {"$vectorSearch": {
        "index": "vectorPlotIndex",
        "path": "plot_embedding",
        "queryVector": embedding,   # same model as index!
        "numCandidates": 100,       # 10x limit recommended
        "limit": 10
    }},
    {"$project": {"title": 1, "plot": 1, "score": {"$meta": "vectorSearchScore"}}}
]

# With pre-filter
pipeline = [
    {"$vectorSearch": {
        "index": "vectorPlotIndex",
        "path": "plot_embedding",
        "queryVector": embedding,
        "numCandidates": 100,
        "filter": {"year": {"$gt": 2010}},
        "limit": 10
    }},
    {"$project": {"title": 1, "plot": 1, "year": 1, "score": {"$meta": "vectorSearchScore"}}}
]
```

---

## Embedding Function (Python)

```python
def get_embeddings(text, model, api_key):
    import requests, json
    response = requests.post(
        'https://api.voyageai.com/v1/embeddings',
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + api_key},
        data=json.dumps({'input': text, 'model': model})
    )
    return response.json()['data'][0]['embedding']
```

---

## Critical Rules

| Rule | Why It Matters |
|---|---|
| Same model for indexing and querying | Different models produce incompatible vector spaces |
| `$vectorSearch` must be first pipeline stage | Hard requirement, same as `$search` |
| `numDimensions` must match model output | Mismatch causes index errors |
| Don't embed fields inside array subdocuments | HNSW cannot index them |
| Pre-filter fields must be declared in index | You can't filter on an un-indexed field at query time |
| More dimensions ≠ better results | Benchmark; Atlas supports up to 4096 |

---

## numCandidates Tuning

```
Start:    numCandidates = 10 × limit
Accuracy: increase numCandidates
Latency:  decrease numCandidates
```

---

## Files in This Note Set

| File | Contents |
|---|---|
| `00-cheatsheet.md` | This file — quick reference |
| `01-vectors-and-dimensions.md` | What vectors are, embedding models, similarity concepts |
| `02-store-embeddings.md` | Atlas trigger, batch job, Python embedding function |
| `03-indexing-algorithms-and-index-config.md` | HNSW deep dive, index configuration with code |
| `04-perform-vector-search.md` | `$vectorSearch` queries, pre-filtering, semantic vs. keyword |
