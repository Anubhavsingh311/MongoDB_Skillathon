# AI Agents with MongoDB — Overview

## What Is an AI Agent?

A software system that can **perceive its environment, make decisions, and take actions** to achieve specific goals. Three capabilities distinguish agents from simpler software:

- **Reasoning** — analyzes situations, evaluates options, determines best course of action rather than following predefined steps.
- **Tool usage** — calls external functions: database queries, APIs, content generation, web search.
- **Memory** — maintains context over time, remembers past interactions, improves performance.

## When to Use an Agent

Agents are a good fit for:

- Complex tasks with no structured, predetermined workflow
- Processes with high latency tolerance (immediate response not required)
- Non-deterministic scenarios where multiple valid solutions exist
- Applications requiring personalization that adapts to individual users over time

Agents are **not** always the right answer. They add complexity unjustified for simple or well-defined tasks. If a straightforward algorithm or classic ML model handles the job, prefer that.

**Example distinction:**
- Basic code completion suggesting the next characters → not an agent
- Coding assistant that understands your project, suggests preferred libraries, generates style-consistent code, remembers your feedback, and explains its logic → agent

## MongoDB's Role in an Agent Architecture

LLMs have no way to permanently store information outside their training data. MongoDB bridges this gap with two roles:

1. **Knowledge base** — stores domain-specific data (documentation, product info) the agent can query to answer questions.
2. **Agent memory** — persists user preferences, past conversations, and results of previous actions across sessions.

The agent supplies reasoning and decision-making; MongoDB supplies the persistent storage that makes those capabilities useful over time.

## What This Course Builds

An agent that does two things:

1. **Answers questions about MongoDB** using vector search over chunked documentation (`chunked_docs` collection).
2. **Summarizes specific documentation pages** using a direct `find` query by title (`full_docs` collection).

The agent decides which tool to call based on the user's query — vector search for general questions, find query for summarization requests.

This is intentionally scoped as a foundation. More complex future capabilities — memory, human-in-the-loop controls, additional tools — can be layered on top.
