# Retriever — Retrieving the Data

The retriever takes a user query, vectorizes it, and uses Atlas Vector Search to find the most relevant chunks.

---

## Atlas Vector Search Index

Create a vector search index named `vector_index` on the `chunked_data` collection:

```json
{
  "fields": [
    {
      "numDimensions": 1024,
      "path": "embedding",
      "similarity": "cosine",
      "type": "vector"
    },
    {
      "path": "hasCode",
      "type": "filter"
    }
  ]
}
```

**Notes:**
- `voyage-3.5-lite` default dimension is **1024**. Can also use 256, 512, or 2048.
- The `hasCode` field is indexed as a `filter` type to support pre-filtering.
- The `path` field must match the field name where embeddings are stored in your documents.

---

## Setting Up the VectorStore

```python
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_voyageai import VoyageAIEmbeddings
import key_param

dbName = "book_mongodb_chunks"
collectionName = "chunked_data"
index = "vector_index"

vectorStore = MongoDBAtlasVectorSearch.from_connection_string(
    key_param.MONGODB_URI,
    dbName + "." + collectionName,
    VoyageAIEmbeddings(voyage_api_key=key_param.VOYAGE_API_KEY, model="voyage-3.5-lite"),
    index_name=index,
)
```

**Critical:** Use the **same embedding model** here as during ingestion. Mismatched models produce meaningless similarity scores.

---

## Basic Retriever

```python
def query_data(query):
    retriever = vectorStore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3},
    )
    results = retriever.invoke(query)
    print(results)
```

| Parameter | Description |
|-----------|-------------|
| `search_type` | `"similarity"`, `"similarity_score_threshold"`, or `"mmr"` (maximal marginal relevance) |
| `k` | Number of chunks to return |

---

## Pre-filtering on Metadata

Pre-filtering reduces the vector search space before computing similarities. This lowers computational cost and latency. The field must be indexed as `"type": "filter"` in the vector index.

```python
retriever = vectorStore.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 3,
        "pre_filter": {"hasCode": {"$eq": False}},
    },
)
```

---

## Score Threshold Filtering

LangChain normalizes Atlas Vector Search scores, resulting in lower values than raw Atlas scores. Experiment to find the right threshold.

```python
retriever = vectorStore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "k": 3,
        "pre_filter": {"hasCode": {"$eq": False}},
        "score_threshold": 0.01,
    },
)
```

**Why 0.01?** LangChain's `similarity_score_threshold` normalizes scores and uses a slightly different similarity function than raw Atlas. Start low and tune upward based on observed result quality.

---

## Full `rag.py` (Retriever Only)

```python
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_voyageai import VoyageAIEmbeddings
import key_param

dbName = "book_mongodb_chunks"
collectionName = "chunked_data"
index = "vector_index"

vectorStore = MongoDBAtlasVectorSearch.from_connection_string(
    key_param.MONGODB_URI,
    dbName + "." + collectionName,
    VoyageAIEmbeddings(voyage_api_key=key_param.VOYAGE_API_KEY, model="voyage-3.5-lite"),
    index_name=index,
)

def query_data(query):
    retriever = vectorStore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 3,
            "pre_filter": {"hasCode": {"$eq": False}},
            "score_threshold": 0.01,
        },
    )
    results = retriever.invoke(query)
    print(results)

query_data("When did MongoDB begin supporting multi-document transactions?")
```

Run:

```bash
python rag.py
```
