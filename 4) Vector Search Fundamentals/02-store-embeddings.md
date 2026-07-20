# Module 2: Store Embeddings for Your Data

> **Course:** MongoDB Atlas Vector Search Fundamentals  
> **Section:** Store Embeddings

---

## Overview

To use vector search, every document that you want to be searchable needs an embedding stored on it. Atlas stores embeddings as a regular field on the document — no separate vector database required.

The challenge: you need embeddings for existing documents AND for all future documents as the collection grows. The recommended approach uses two complementary patterns.

---

## Two-Phase Strategy

| Phase | What it does | When it runs |
|---|---|---|
| **Event Trigger** | Generates and stores an embedding whenever a document is inserted, updated, or replaced | Continuously, going forward |
| **Batch Job** | Backfills embeddings for all documents that existed before the trigger | Run once on the existing corpus |

This combination means you're covered from the moment you deploy, while historical data catches up in the background.

---

## The Embedding Function

Both phases share the same core logic: send a field's text to the embedding API, receive a vector, write it back to the document.

### Python (used for batch jobs and application code)

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

> **Security:** Never hardcode or expose your API key. Store it in environment variables or Atlas App Services secrets.

> **Performance:** The example above sends one document per request. For large datasets, batch multiple documents per API call — it's significantly more efficient.

---

## Atlas Event Trigger (JavaScript)

Configure the trigger in the Atlas dashboard under **Triggers → Add Trigger → Database Trigger**:

- **Type:** Database trigger
- **Watch level:** Collection
- **Cluster:** Cluster0
- **Database / Collection:** `sample_mflix` / `movies`
- **Operation types:** Insert, Update, Replace
- **Full document:** Yes (required so the function can access the field to embed)
- **Function name:** `embeddings`

### Trigger Function

```javascript
exports = async function(changeEvent) {
    const doc = changeEvent.fullDocument;
    const url = 'https://api.voyageai.com/v1/embeddings';
    const voyageai_key = context.values.get("VoyageAI_secret");

    try {
        console.log(`Processing document with id: ${doc._id}`);

        let response = await context.http.post({
            url: url,
            headers: {
                'Authorization': [`Bearer ${voyageai_key}`],
                'Content-Type': ['application/json']
            },
            body: JSON.stringify({
                input: doc.plot,                          // field to embed
                model: context.values.get("model")        // model name stored as secret
            })
        });

        let responseData = EJSON.parse(response.body.text());

        if (response.statusCode === 200) {
            console.log("Successfully received embedding.");

            const embedding = responseData.data[0].embedding;

            const collection = context.services
                .get("cluster0")
                .db("sample_mflix")
                .collection("movies");

            const result = await collection.updateOne(
                { _id: doc._id },
                { $set: { plot_embedding: embedding } }
            );

            if (result.modifiedCount === 1) {
                console.log("Successfully updated the document.");
            } else {
                console.log("Failed to update the document.");
            }
        } else {
            console.log(`Failed to receive embedding. Status code: ${response.statusCode}`);
        }

    } catch(err) {
        console.error(err);
    }
};
```

---

## Batch Backfill (Python)

Loop through existing documents and call `get_embeddings()` for each one, then update the document with the result.

```python
# Pseudocode structure — adapt to your collection size and rate limits
for doc in collection.find({"plot_embedding": {"$exists": False}}):
    embedding = get_embeddings(doc["plot"], model, api_key)
    collection.update_one(
        {"_id": doc["_id"]},
        {"$set": {"plot_embedding": embedding}}
    )
```

> Filter on `$exists: False` so you only process documents that don't already have an embedding, making the job resumable.

---

## Embedding Model: `voyage-3.5-lite`

| Property | Value |
|---|---|
| Provider | Voyage AI |
| Dimension options | 256, 512, **1024** (default), 2048 |
| Quantization | int8, binary |
| Use cases | General retrieval, technical docs, code, law, finance, long documents, conversations |
| API endpoint | `https://api.voyageai.com/v1/embeddings` |

---

## Key Takeaways

- Embeddings live on the document as a regular field — no secondary database needed.
- Use a trigger for ongoing freshness; use a batch job to seed existing data.
- The `plot_embedding` field written here is what the vector index (Module 3) will index.
- Keep API keys out of source code — use Atlas App Services secrets or environment variables.
