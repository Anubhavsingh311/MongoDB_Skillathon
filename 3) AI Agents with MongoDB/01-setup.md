# Lesson 1 — Set Up the Environment

## Planning Before Writing Code

Before any implementation, define three things:

1. **Tasks** — what the agent will do.
2. **Data** — type, sources, how it will be processed.
3. **Decision logic** — the agent's reasoning process and what data it uses to decide.

For this agent: answer MongoDB questions (vector search over `chunked_docs`) and summarize pages (find by title in `full_docs`).

---

## Dependencies (`pyproject.toml`)

| Package | Purpose |
|---|---|
| `langchain` | Core framework — backbone for LLM capabilities |
| `langchain-openai` | LangChain integration with OpenAI LLMs |
| `langgraph` | Workflow/graph engine for agent decision-making |
| `langgraph-checkpoint-mongodb` | Persists agent state in MongoDB across sessions |
| `pymongo` | Official MongoDB Python driver |
| `voyageai` | Embedding model to convert text → vectors for semantic search |

You're not locked to these packages. MongoDB works with most agent frameworks, or you can build your own solution on top of PyMongo directly.

---

## Code

### Imports

```python
import key_param
from pymongo import MongoClient
from langchain_openai import ChatOpenAI
```

### MongoDB Initialization

```python
def init_mongodb():
    """
    Initialize MongoDB client and collections.

    Returns:
        tuple: MongoDB client, vector search collection, full documents collection.
    """
    mongodb_client = MongoClient(key_param.mongodb_uri)
    
    DB_NAME = "ai_agents"
    
    vs_collection = mongodb_client[DB_NAME]["chunked_docs"]
    
    full_collection = mongodb_client[DB_NAME]["full_docs"]
    
    return mongodb_client, vs_collection, full_collection
```

### Entry Point

```python
def main():
    """
    Main function to initialize and execute the graph.
    """
    mongodb_client, vs_collection, full_collection = init_mongodb()
    
    llm = ChatOpenAI(openai_api_key=key_param.openai_api_key, temperature=0, model="gpt-4o")
    
    # More functionality added in subsequent lessons

main()
```

`temperature=0` produces deterministic responses — important for tool selection reliability.
