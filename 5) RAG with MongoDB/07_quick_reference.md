# Quick Reference — RAG with MongoDB

## End-to-End Data Flow

```
[Source PDF]
    ↓  PyPDFLoader
[Pages array]
    ↓  Filter (>20 words)
[cleaned_pages]
    ↓  create_metadata_tagger (GPT extracts title, keywords, hasCode)
[docs with metadata]
    ↓  RecursiveCharacterTextSplitter (500 tokens, 150 overlap)
[split_docs (173 chunks)]
    ↓  VoyageAIEmbeddings (voyage-3.5-lite)
[MongoDB Atlas — chunked_data collection]

         ↕  At query time:

[User Query]
    ↓  VoyageAIEmbeddings (same model)
[Query vector]
    ↓  Atlas $vectorSearch (pre-filter: hasCode=false, k=3)
[Top-3 relevant chunks]
    ↓  PromptTemplate.from_template(template)
[Assembled prompt: context + question]
    ↓  ChatOpenAI (temperature=0)
[Raw LLM output]
    ↓  StrOutputParser
[Answer string]
```

---

## Atlas Vector Search Index Definition

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

---

## Key Parameters to Tune

| Parameter | Default | Effect |
|-----------|---------|--------|
| `chunk_size` | 500 | Larger = more context per chunk, fewer chunks |
| `chunk_overlap` | 150 | Larger = better cross-boundary continuity, more storage |
| `k` (retriever) | 3 | More chunks = more context, more tokens consumed |
| `score_threshold` | 0.01 | Higher = stricter relevance filter (LangChain-normalized scores) |
| `numDimensions` | 1024 | voyage-3.5-lite supports 256/512/1024/2048 |
| `temperature` (LLM) | 0 | 0 = deterministic; increase for more creative responses |

---

## Chunking Strategy Decision Checklist

- [ ] What is the LLM's token limit?
- [ ] What is the natural granularity of my source data (sentence, paragraph, section)?
- [ ] Do I need overlap? (Usually yes for prose, maybe not for structured data)
- [ ] Would summarizing chunks improve retrieval? (Advanced — useful for code)
- [ ] Is the data multi-modal? (Images/video need different handling)
- [ ] How frequently does the data change? (Informs refresh strategy)

---

## Common Pitfalls

| Mistake | Consequence |
|---------|-------------|
| Different embedding model at ingestion vs. query time | Meaningless similarity scores, garbage retrieval |
| No pre-filtering on large collections | Slower queries, higher latency |
| `score_threshold` tuned against raw Atlas scores | LangChain normalizes scores — they will be much lower |
| Chunks too large | Irrelevant context bleeds into the prompt |
| Chunks too small | Insufficient context for the LLM to generate a good answer |
| No metadata on chunks | Can't pre-filter; must scan all vectors |

---

## File Structure

```
project/
├── key_param.py          # API keys and connection string
├── sample_files/
│   └── mongodb.pdf       # Source document
├── load_data.py          # Ingestion pipeline
└── rag.py                # Retriever + generator (query interface)
```

---

## GitHub Reference

Course code: https://github.com/mongodb-university/curriculum/tree/main/Atlas-Vector-Search/U3-Using-Atlas-Vector-Search-for-RAG/
