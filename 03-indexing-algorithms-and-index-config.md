# Module 3: Indexing Algorithms & Configuring a Vector Index

> **Course:** MongoDB Atlas Vector Search Fundamentals  
> **Sections:** Perform a Vector Search → Video: Indexing Algorithms / Video: Configure a Vector Index

---

## How Atlas Indexes Vectors: HNSW

Atlas Vector Search uses **Hierarchical Navigable Small World (HNSW)** graphs to index embeddings. Understanding how HNSW works explains why vector search is fast and why results are "approximate."

### The Two Ideas HNSW is Built On

#### Skip Lists

A skip list is a sorted linked list with multiple layers. Search starts at the top layer (fewest nodes, greatest gaps between them) and works downward, narrowing the target range layer by layer until it lands on the exact value.

It's faster than a flat linked list but still too slow for high-dimensional data at scale.

#### NSW Graphs (Navigable Small World, 2011)

An NSW graph places data points as nodes with edges representing similarity between them. Searching means traversing edges from a random entry point toward the query point.

**Problem:** If the random entry point is already near the query, the algorithm may stop prematurely — concluding it has found the nearest neighbor when a better one exists elsewhere. This produces subpar results.

---

### HNSW: The Synthesis

HNSW solves the NSW early-stopping problem by adding layers (like a skip list) on top of an NSW graph.

```
Layer 3:   *           *                    *
           |           |                    |
Layer 2:   *     *     *         *          *
           |     |     |         |          |
Layer 1:   * *   * *   * *   *   * *   *   * *
           | |   | |   | |   |   | |   |   | |
Layer 0:   * * * * * * * * * * * * * * * * * *   (all points, shortest links)
```

- **Layer 0** contains every point with short-range links.
- Higher layers contain progressively fewer points with longer-range links.
- Analogy: zooming out on a GPS map. Higher layers are the highway-level view; layer 0 is street level.

### aNN Search (Approximate Nearest Neighbor)

HNSW is queried using the **approximate nearest neighbor (aNN)** algorithm:

1. Enter at a random point on the topmost layer.
2. Move to the closest vertex to the query point at that layer.
3. Drop down one layer and repeat from that position.
4. Continue until reaching layer 0, where the query point is surrounded by its nearest neighbors.

aNN does **not** exhaustively search every point. This makes it fast enough for production but means there is a small probability of outliers in results. The tradeoff is intentional and generally acceptable.

> Atlas builds and manages the HNSW graph automatically. You don't write any graph code.

> **Memory constraint:** HNSW is memory-intensive. MongoDB recommends **dedicated search nodes** for vector workloads to isolate memory from your main cluster operations.

---

## Configuring a Vector Search Index

### Constraints to Know Before You Start

1. The `vector` field type can only be applied to fields that actually contain embeddings.
2. You cannot index a field inside a subdocument that lives inside an **array field**. Don't nest your embedding field inside an array of documents.

---

### Similarity Functions

The similarity function you choose when creating the index determines how the HNSW graph measures proximity. Always check your embedding model's documentation first — use whatever the model was trained with.

| Function | Measures | Notes |
|---|---|---|
| `euclidean` | Straight-line distance between vectors | Derived from the Pythagorean theorem, generalized to N dimensions |
| `cosine` | Angle between vectors | Ignores magnitude; zero-magnitude vectors not allowed; MongoDB recommends normalizing and using `dotProduct` instead |
| `dotProduct` | Angle + magnitude | Vectors must be normalized to unit length at both index time and query time |

`voyage-3.5-lite` was trained with **cosine** similarity.

---

### Basic Vector Index

```javascript
db.movies.createSearchIndex(
  "vectorPlotIndex",       // index name
  "vectorSearch",          // must specify; omitting defaults to regular search index
  {
    "fields": [
      {
        "type": "vector",
        "path": "plot_embedding",    // field containing the embeddings
        "numDimensions": 1024,       // must match your model's output dimension
        "similarity": "cosine"
      }
    ]
  }
);
```

**How to find numDimensions if you don't know it:**
- Check your embedding model's documentation.
- Count the elements in any already-generated embedding array — each element is one dimension.

`voyage-3.5-lite` options: 256, 512, **1024** (default), 2048.

---

### Vector Index with Pre-filter Field

Pre-filtering narrows the search space *before* the aNN traversal begins, removing irrelevant documents upfront. This improves both performance and result relevance.

```javascript
db.movies.createSearchIndex(
  "vectorPlotIndex",
  "vectorSearch",
  {
    "fields": [
      {
        "type": "vector",
        "path": "plot_embedding",
        "numDimensions": 1024,
        "similarity": "cosine"
      },
      {
        "type": "filter",
        "path": "year"            // filter fields: numbers, strings, or booleans only
      }
    ]
  }
);
```

> Filter fields currently support numbers, strings, and booleans. Check MongoDB docs for any expansion to additional types.

---

## Key Takeaways

- HNSW = skip list layering + NSW graph traversal. Atlas manages it; you just configure the index.
- aNN is approximate by design — fast but not guaranteed to return the single closest vector.
- Always match `numDimensions` exactly to your embedding model's output.
- Pick `similarity` based on the model's training; when in doubt, experiment.
- Pre-filter fields must be declared at index time, then used at query time (covered in Module 4).
- Use dedicated search nodes in production to avoid memory contention with your primary cluster.
