# RAG with MongoDB — Course Overview

**Platform:** MongoDB University  
**Course:** RAG with MongoDB  

## Module Structure

| # | Module | Topics |
|---|--------|--------|
| 1 | Identify RAG Architecture | What is RAG?, AI Integrations & Frameworks |
| 2 | Describe Chunking Strategies | Preparing the Data, Chunking Strategies |
| 3 | Create a RAG Application | Retrieving the Data, Answer Generation, Lab |
| 4 | Conclusion | Skill Check |

## Prerequisites

- Atlas Cluster Connection String
- OpenAI API Key
- Voyage AI API Key

## Stack Used

| Layer | Tool |
|-------|------|
| Vector Store | MongoDB Atlas Vector Search |
| Embedding Model | Voyage AI (`voyage-3.5-lite`) |
| Generative Model | OpenAI GPT (`gpt-3.5-turbo` / `ChatOpenAI`) |
| Framework | LangChain (Python) |
| PDF Parsing | PyPDF / `PyPDFLoader` |

## Install Dependencies

```bash
pip3 install langchain langchain_community langchain_core langchain_voyageai \
             langchain_openai langchain_mongodb pymongo pypdf
```

## Environment Setup (`key_param.py`)

```python
MONGODB_URI = "<your_atlas_connection_string>"
VOYAGE_API_KEY = "<your_voyageai_api_key>"
LLM_API_KEY = "<your_llm_api_key>"
```
