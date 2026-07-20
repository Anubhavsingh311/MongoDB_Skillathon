# Lesson 2 — Create Tools for the Agent

## What Are Tools?

Specialized functions that extend agent capabilities beyond what the LLM knows on its own. LLMs can't access real-time data, private databases, or perform operations outside their training. Tools bridge that gap.

When an agent uses a tool it:
1. Determines which tool (if any) is appropriate.
2. Formats the input.
3. Calls the tool.
4. Incorporates the response into its reasoning to generate a final answer.

Tool types include: API calls, database queries, plugins, web search — any callable that returns useful data.

---

## The `@tool` Decorator

LangChain's `@tool` decorator registers a regular Python function as a tool. It automatically surfaces the function's name, description, and parameter schema to the model. **Good names, clear descriptions, and proper schema definitions directly improve the model's ability to select and invoke tools correctly.**

---

## Additional Imports

```python
from langchain.agents import tool
from typing import List
import voyageai
```

---

## Helper: Generate Embeddings

Not exposed to the LLM directly — used internally by the vector search tool to embed the user query before searching.

```python
def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for a piece of text.

    Args:
        text (str): The text to embed.
        embedding_model (voyage-3-lite): The embedding model.

    Returns:
        List[float]: The embedding of the text.
    """
    embedding_model = voyageai.Client(api_key=key_param.voyage_api_key)

    embedding = embedding_model.embed(
        text, model="voyage-3-lite", input_type="query"
    ).embeddings[0]
    
    return embedding
```

---

## Tool 1 — Vector Search (Question Answering)

Embeds the user query, runs a `$vectorSearch` aggregation against `chunked_docs`, and returns the top 5 matching document bodies concatenated as a single string. The LLM uses this context to generate an answer.

```python
@tool 
def get_information_for_question_answering(user_query: str) -> str:
    """
    Retrieve relevant documents for a user query using vector search.

    Args:
        user_query (str): The user's query.

    Returns:
        str: The retrieved documents as a string.
    """
    query_embedding = generate_embedding(user_query)

    vs_collection = init_mongodb()[1]
    
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 150,  # wider candidate pool for better recall
                "limit": 5,            # return top 5 by similarity
            }
        },
        {
            "$project": {
                "_id": 0,
                "body": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]
    
    results = vs_collection.aggregate(pipeline)
    
    context = "\n\n".join([doc.get("body") for doc in results])
    
    return context
```

---

## Tool 2 — Document Lookup (Summarization)

Finds a single document by exact title match in `full_docs` and returns the full page body. The LLM then summarizes it.

> **Note:** This is an exact string match. The query must match the `title` field precisely. Plan for this constraint if titles are user-supplied.

```python
@tool 
def get_page_content_for_summarization(user_query: str) -> str:
    """
    Retrieve the content of a documentation page for summarization.

    Args:
        user_query (str): The user's query (title of the documentation page).

    Returns:
        str: The content of the documentation page.
    """
    full_collection = init_mongodb()[2]

    query = {"title": user_query}
    
    projection = {"_id": 0, "body": 1}
    
    document = full_collection.find_one(query, projection)
    
    if document:
        return document["body"]
    else:
        return "Document not found"
```

---

## Testing Tools Directly

Before wiring tools into the agent, test them in isolation:

```python
tools = [
    get_information_for_question_answering,
    get_page_content_for_summarization
]

answer = get_information_for_question_answering.invoke(
    "What are some best practices for data backups in MongoDB?"
)
print("answer:" + answer)

summary = get_page_content_for_summarization.invoke("Create a MongoDB Deployment")
print("Summary:" + summary)
```

Remove these test calls before moving to the next lesson — they run the tools outside the agent's decision loop.
