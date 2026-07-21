# Answer Generation — Assembling the Full RAG System

The **generator** takes the retrieved chunks and the user's query, builds a prompt, and sends it to the generative model to produce a response.

---

## Generator Components

| Component | Role |
|-----------|------|
| **Prompt Template** | Instructs the LLM on tone, scope, format, and what to do when context is absent |
| **Generative Model** | Produces the human-readable response (different from the embedding model) |

---

## Prompt Template

The template controls LLM behavior. Key directives used in this course:

```python
template = """
Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Do not answer the question if there is no given context.
Do not answer the question if it is not related to the context.
Do not give recommendations to anything other than MongoDB.
Context:
{context}
Question: {question}
"""
```

You can extend the template to specify: tone, output format, verbosity, domain restrictions, and more.

---

## Assembling the Chain (LCEL)

```python
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

custom_rag_prompt = PromptTemplate.from_template(template)

retrieve = {
    "context": retriever | (lambda docs: "\n\n".join([d.page_content for d in docs])),
    "question": RunnablePassthrough()
}

llm = ChatOpenAI(openai_api_key=key_param.LLM_API_KEY, temperature=0)
response_parser = StrOutputParser()

rag_chain = (
    retrieve
    | custom_rag_prompt
    | llm
    | response_parser
)
```

**Pipeline stages:**

```
retrieve (chunks + query)
    → custom_rag_prompt (assembled prompt string)
    → llm (raw model output)
    → response_parser (clean string)
```

- `RunnablePassthrough` passes the user query through unchanged to the prompt's `{question}` slot
- The lambda joins the list of chunk objects into a single newline-separated string for the prompt's `{context}` slot
- `StrOutputParser` converts the LLM's raw output object to a plain string

---

## Full `rag.py`

```python
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import ChatOpenAI
from langchain_voyageai import VoyageAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
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

    template = """
    Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Do not answer the question if there is no given context.
    Do not answer the question if it is not related to the context.
    Do not give recommendations to anything other than MongoDB.
    Context:
    {context}
    Question: {question}
    """

    custom_rag_prompt = PromptTemplate.from_template(template)

    retrieve = {
        "context": retriever | (lambda docs: "\n\n".join([d.page_content for d in docs])),
        "question": RunnablePassthrough(),
    }

    llm = ChatOpenAI(openai_api_key=key_param.LLM_API_KEY, temperature=0)
    response_parser = StrOutputParser()

    rag_chain = (
        retrieve
        | custom_rag_prompt
        | llm
        | response_parser
    )

    answer = rag_chain.invoke(query)
    return answer

print(query_data("What is the difference between a database and collection in MongoDB?"))
```

Run:

```bash
python rag.py
```

---

## Behavior Verification

Ask a question in scope:
> "What is the difference between a collection and database in MongoDB?"
→ Returns a grounded answer from the chunks.

Ask an out-of-scope question:
> "Why is the sky blue?"
→ Returns "I don't know" — correct behavior given the prompt constraint.

---

## Key Takeaways

- The generator's quality is heavily influenced by **prompt engineering**. Spend time here.
- The generative model and embedding model are different and serve different roles.
- The LCEL pipe operator (`|`) makes the chain readable and composable.
- Experiment with your own data and prompts — results vary significantly with different chunking strategies, models, and prompt templates.
