# Preparing the Data (Ingestion Pipeline)

Data ingestion = **3 steps**: Identify → Prepare → Store

---

## Step 1: Identify Data Sources

RAG can use any data format: PDFs, HTML, JSON, MongoDB documents, video, images, tabular data.

**This course uses:** `mongodb.pdf` (The Little Book of MongoDB)  
**Parser:** `PyPDFLoader` from LangChain — splits by page, returns each page as a list element with metadata.

```python
loader = PyPDFLoader("./sample_files/mongodb.pdf")
pages = loader.load()
```

---

## Step 2: Prepare the Data

### 2a. Sanitize
Remove empty or low-signal pages to avoid wasting tokens on embedding generation.

```python
cleaned_pages = []
for page in pages:
    if len(page.page_content.split(" ")) > 20:
        cleaned_pages.append(page)
```

**Rule of thumb:** Filter pages with fewer than 20 words. Cover pages, blank pages, etc. get dropped.

### 2b. Chunk
Break large texts into smaller pieces so the retriever can index and search efficiently, and so individual chunks fit in the LLM context window.

**Splitter used:** `RecursiveCharacterTextSplitter`  
**Strategy:** Paragraph-level chunking (each chunk focuses on one topic)

```python
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=150)
```

| Parameter | Value | Why |
|-----------|-------|-----|
| `chunk_size` | 500 tokens | Approx. paragraph size |
| `chunk_overlap` | 150 tokens | Preserve context across chunk boundaries |

**Chunk overlap** creates duplicate tokens between adjacent chunks. Looks redundant to humans but prevents incomplete context being sent to the LLM.

### 2c. Generate Metadata
Metadata enables **pre-filtering** in Atlas Vector Search, which narrows the search space before vector similarity is computed.

Use an LLM to auto-generate metadata from each page:

```python
schema = {
    "properties": {
        "title": {"type": "string"},
        "keywords": {"type": "array", "items": {"type": "string"}},
        "hasCode": {"type": "boolean"},
    },
    "required": ["title", "keywords", "hasCode"],
}

llm = ChatOpenAI(openai_api_key=key_param.LLM_API_KEY, temperature=0, model="gpt-3.5-turbo")
document_transformer = create_metadata_tagger(metadata_schema=schema, llm=llm)
docs = document_transformer.transform_documents(cleaned_pages)
split_docs = text_splitter.split_documents(docs)
```

---

## Step 3: Store — Generate Embeddings and Insert into Atlas

**Embedding model:** `voyage-3.5-lite` (Voyage AI)  
Supports dimensions: 256, 512, 1024 (default), 2048. Suitable for technical docs, code, law, finance, etc.

```python
embeddings = VoyageAIEmbeddings(voyage_api_key=key_param.VOYAGE_API_KEY, model="voyage-3.5-lite")

vectorStore = MongoDBAtlasVectorSearch.from_documents(
    split_docs, embeddings, collection=collection
)
```

This single call generates embeddings for every chunk and inserts them into Atlas. Result: 173 documents (chunks) for the sample PDF.

---

## Keeping Data Fresh

For frequently updated sources, use a **scheduled Atlas Trigger** or **cron job** to:
1. Pull new/updated data from the source
2. Chunk, generate metadata, create embeddings
3. Upsert into Atlas

---

## Full `load_data.py`

```python
from pymongo import MongoClient
from langchain_openai import ChatOpenAI
from langchain_voyageai import VoyageAIEmbeddings
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_transformers.openai_functions import create_metadata_tagger
import key_param

client = MongoClient(key_param.MONGODB_URI)
dbName = "book_mongodb_chunks"
collectionName = "chunked_data"
collection = client[dbName][collectionName]

# Load and sanitize
loader = PyPDFLoader("./sample_files/mongodb.pdf")
pages = loader.load()
cleaned_pages = [p for p in pages if len(p.page_content.split(" ")) > 20]

# Chunk config
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=150)

# Metadata schema
schema = {
    "properties": {
        "title": {"type": "string"},
        "keywords": {"type": "array", "items": {"type": "string"}},
        "hasCode": {"type": "boolean"},
    },
    "required": ["title", "keywords", "hasCode"],
}

# Generate metadata with LLM
llm = ChatOpenAI(openai_api_key=key_param.LLM_API_KEY, temperature=0, model="gpt-3.5-turbo")
document_transformer = create_metadata_tagger(metadata_schema=schema, llm=llm)
docs = document_transformer.transform_documents(cleaned_pages)
split_docs = text_splitter.split_documents(docs)

# Embed and store
embeddings = VoyageAIEmbeddings(voyage_api_key=key_param.VOYAGE_API_KEY, model="voyage-3.5-lite")
vectorStore = MongoDBAtlasVectorSearch.from_documents(split_docs, embeddings, collection=collection)
```

Run:

```bash
python load_data.py
```
