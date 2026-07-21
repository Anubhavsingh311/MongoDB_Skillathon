# Chunking Strategies

Chunking = breaking source data into smaller pieces for indexing, retrieval, and context window management.

---

## Why Chunk?

**Reason 1 — Context Window Limits**  
LLMs can only process a fixed number of tokens at once. Instead of sending a 50,000-token document to an LLM with a 32,000-token limit, break it into ~50 chunks of ~1,000 tokens and send only the relevant ones.

If a model hits its token limit it either:
- Drops earlier tokens (loses context), or
- Stops mid-sentence

**Reason 2 — Accuracy, Relevancy, Precision**  
Even as context windows grow (some LLMs now handle 100k+ tokens), chunking still improves quality:
- LLMs are slow to ingest large token sets
- Large inputs cause "forgetting" of less-prominent tokens
- Focused chunks give more precise retrieval ("needle in a haystack" test)

---

## Three Components of a Chunking Strategy

### 1. Chunk Size
Maximum number of tokens per chunk. Must be comfortably less than the LLM's token limit, since you'll also include metadata and the query in the same context window.

**Rule of thumb:** If the LLM has a 2,048-token window, keep chunks at 200–300 tokens.  
Smaller chunk size → more chunks → more storage/memory needed.

### 2. Chunk Overlap
Number of tokens shared between adjacent chunks. Prevents important context from being lost at chunk boundaries.

- Larger overlap → more shared tokens → better context continuity, more storage
- Smaller overlap → less duplication

Some use cases (e.g., structured data with natural boundaries) may not need overlap at all.

### 3. Splitting Technique
Determines where chunk boundaries fall. Ranges from naive to complex:

| Technique | Description |
|-----------|-------------|
| By character | Split every N characters |
| By token | Split every N tokens |
| By sentence | Split at sentence boundaries |
| By paragraph | Split at paragraph/section breaks |
| By page | One chunk per page |
| Semantic | Use an LLM to identify topically coherent boundaries |

**There is no universal best strategy.** Experiment with your specific data and representative queries.

---

## Advanced: Chunk Summarization

Chunks don't have to be raw source text. For code-heavy sources, you can:
1. Chunk the raw code
2. Use an LLM to summarize each code chunk in natural language
3. Store the summary as the embedding source, with the raw code alongside it

This improves semantic search because natural language queries match summaries more effectively than raw code.

---

## Chunking vs. Modern Large Context Windows

Even at 100k+ token windows, chunking is still valuable:
- Reduces computational cost (you only process relevant data)
- Avoids "lost in the middle" degradation (LLMs attend poorly to tokens far from the edges of long inputs)
- Keeps latency low

---

## This Course's Strategy

| Parameter | Value |
|-----------|-------|
| Splitter | `RecursiveCharacterTextSplitter` |
| Chunk size | 500 tokens |
| Chunk overlap | 150 tokens |
| Rationale | Each PDF page has multiple paragraphs; paragraph-level chunks keep each chunk topically focused |
