# Lesson 3 — Give the LLM Access to Tools

## Function Calling

Function calling lets an LLM interact with external tools by generating **structured outputs** (function name + formatted arguments) rather than free text. The model analyzes the user's request, decides which function to invoke, and formats the input accordingly.

Most major models support this — OpenAI, Anthropic, Google — but implementation details vary. Check your model's documentation for specifics.

---

## Additional Imports

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
```

---

## Updated `main()` — Prompt, Tool Binding, Chain

```python
def main():
    mongodb_client, vs_collection, full_collection = init_mongodb()
    
    tools = [
        get_information_for_question_answering,
        get_page_content_for_summarization
    ]
    
    llm = ChatOpenAI(openai_api_key=key_param.openai_api_key, temperature=0, model="gpt-4o")
    
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "You are a helpful AI assistant."
                " You are provided with tools to answer questions and summarize technical documentation related to MongoDB."
                " Think step-by-step and use these tools to get the information required to answer the user query."
                " Do not re-run tools unless absolutely necessary."
                " If you are not able to get enough information using the tools, reply with I DON'T KNOW."
                " You have access to the following tools: {tool_names}."
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    
    # Pre-fill {tool_names} placeholder using partials
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
    
    # Attach tools to the LLM so it knows what's available
    bind_tools = llm.bind_tools(tools)
    
    # Chain: format prompt → pass to LLM with tools
    llm_with_tools = prompt | bind_tools
```

### Key Concepts

**Partials** — pre-fill specific placeholder values in a prompt template without providing a full input. Here, `{tool_names}` is filled once at setup time so it doesn't need to be supplied on every invocation.

**`bind_tools`** — registers the tool schemas with the LLM so the model knows what functions are available and how to call them.

**Chain (`|` operator)** — composes the prompt formatting step and the LLM call into a single pipeline. Calling `.invoke()` on the chain runs both in sequence.

---

## Verifying Tool Selection (Testing Only)

```python
# Verify the LLM picks the right tool for each query type
tool_call_check = llm_with_tools.invoke(
    ["What are some best practices for data backups in MongoDB?"]
).tool_calls
print("Tool call check:", tool_call_check)
# Expected: get_information_for_question_answering

tool_call_check = llm_with_tools.invoke(
    ["Give me a summary of the page titled Create a MongoDB Deployment"]
).tool_calls
print("Tool call check:", tool_call_check)
# Expected: get_page_content_for_summarization
```

The `.tool_calls` property on the response shows which tool the model selected and what arguments it formatted. Remove these checks before proceeding — the graph handles invocation in the next lesson.
