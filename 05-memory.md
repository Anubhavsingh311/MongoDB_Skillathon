# Lesson 5 — Add Memory to the Agent

## State vs. Memory

These are related but distinct:

- **State** — the current workflow snapshot: what's happening right now in this graph execution.
- **Memory** — storage that persists state so the agent can recall it later. Works alongside state to create continuity.

Analogy: state is what you're actively thinking about; memory is what you've stored and can retrieve when needed.

---

## Types of Agent Memory

**Short-term memory** — context within a single interaction or session. Lets the agent understand follow-up questions like "What about the first option?" by knowing what "first option" refers to.

**Long-term memory** — persistent storage across multiple sessions. Enables the agent to recall user preferences, summarized conversation history, or actions taken weeks ago.

This lesson implements **short-term memory** using MongoDB as the storage layer, via LangGraph's checkpointer API.

---

## How the Checkpointer Works

LangGraph's checkpointer captures graph state at each node execution. When a thread ID is supplied at invocation time, LangGraph automatically saves that snapshot to MongoDB and loads the prior snapshot from the same thread on subsequent calls.

LangGraph creates and manages the required collections automatically:
- Database: `checkpointing_db`
- Collections: `checkpoints`, `checkpoint_writes`

Each document is keyed by thread ID, which is how the agent associates a new message with the right conversation history.

---

## Additional Import

```python
from langgraph.checkpoint.mongodb import MongoDBSaver
```

---

## Updated `init_graph` — Add Checkpointer

```python
def init_graph(llm_with_tools, tools_by_name, mongodb_client):
    graph = StateGraph(GraphState)
    
    graph.add_node("agent", lambda state: agent(state, llm_with_tools))
    graph.add_node("tools", lambda state: tool_node(state, tools_by_name))
    
    graph.add_edge(START, "agent")
    graph.add_edge("tools", "agent")
    graph.add_conditional_edges("agent", route_tools, {"tools": "tools", END: END})
    
    checkpointer = MongoDBSaver(mongodb_client)
    
    return graph.compile(checkpointer=checkpointer)
```

`mongodb_client` is now a required parameter — pass it in from `main()`.

---

## Updated `execute_graph` — Add Thread ID

```python
def execute_graph(app, thread_id: str, user_input: str) -> None:
    input = {"messages": [("user", user_input)]}
    
    config = {"configurable": {"thread_id": thread_id}}
    
    for output in app.stream(input, config):
        for key, value in output.items():
            print(f"Node {key}:")
            print(value)
    
    print("---FINAL ANSWER---")
    print(value["messages"][-1].content)
```

`config` carries the `thread_id` into the graph execution. LangGraph uses it to fetch the matching checkpoint from MongoDB before running the agent node.

**In production:** use a session ID generated when the user starts a chat session. The same thread ID across multiple `execute_graph` calls means the agent remembers earlier turns. A new thread ID starts a fresh conversation.

---

## Updated `main()`

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
    
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
    bind_tools = llm.bind_tools(tools)
    llm_with_tools = prompt | bind_tools
    
    tools_by_name = {tool.name: tool for tool in tools}
    
    app = init_graph(llm_with_tools, tools_by_name, mongodb_client)  # now passes mongodb_client
    
    # Same thread_id "1" across both calls — agent remembers the first question
    execute_graph(app, "1", "What are some best practices for data backups in MongoDB?")
    execute_graph(app, "1", "What did I just ask you?")

main()
```

The second query confirms memory is working: the agent responds that you asked about MongoDB backup best practices, retrieved from the `checkpointing_db` checkpoint for thread `"1"`.

---

## What's Stored in MongoDB

After running the agent, `checkpointing_db` will contain:

- **`checkpoints`** — full graph state snapshots per thread ID per step.
- **`checkpoint_writes`** — individual write operations that compose each checkpoint.

These are managed entirely by LangGraph. You don't write to these collections directly.

---

## What's Next

Short-term memory within a session is just the foundation. Possible extensions:

- **Long-term memory** — summarize and persist conversations across sessions.
- **Additional tools** — database metrics monitoring, write operations, external API calls.
- **Human-in-the-loop** — pause graph execution for user confirmation before taking actions.
