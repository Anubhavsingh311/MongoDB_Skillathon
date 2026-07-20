# Lesson 4 — Build the Agent's Decision-making Capabilities

## Why Graphs?

A graph structure enables agents to handle multi-step workflows that a simple linear chain cannot. Graphs support:

- Complex relationships (multiple interconnected nodes)
- Conditional logic (different paths based on state)
- Cyclical processes (loops, feedback, multi-turn reasoning)
- Visual clarity for complex workflows

LangGraph implements a **cyclical graph** where the agent can invoke a tool, receive the result, reason about it, and potentially invoke another tool — all within one conversation turn.

---

## Core Concepts

**State** — a snapshot of the application at each point in the graph's execution. Tracks the conversation and all messages flowing between nodes.

**Memory (in this context)** — storage that persists state either within a session (short-term) or across sessions (long-term). Covered in Lesson 5.

**Nodes** — processing units that receive the current state, do work, and return an updated state.

**Edges** — connections between nodes that define information flow. Can be static (always go to node X) or conditional (go to X or Y based on state).

---

## Additional Imports

```python
from typing import Annotated
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from langchain_core.messages import ToolMessage
from langgraph.graph import END, StateGraph, START
```

---

## Define State

```python
class GraphState(TypedDict):
    # Annotated with add_messages: new messages are APPENDED, not replaced
    messages: Annotated[list, add_messages]
```

`add_messages` is a reducer function. Without it, each state update would overwrite the previous messages, destroying conversation history. With it, messages accumulate across all node executions.

---

## Agent Node

The decision-maker. Receives current state, calls the LLM (with tools bound), returns the result as a new message.

```python
def agent(state: GraphState, llm_with_tools) -> GraphState:
    """
    Agent node — evaluates conversation and decides to answer directly or call a tool.
    """
    messages = state["messages"]
    result = llm_with_tools.invoke(messages)
    return {"messages": [result]}
```

Output is either:
- A **tool call** (the LLM wants to invoke a tool) → routes to the tools node.
- A **direct response** (the LLM has enough information) → routes to END.

---

## Tool Node

Executes the tools the agent node requested.

```python
def tool_node(state: GraphState, tools_by_name) -> GraphState:
    """
    Tool node — executes all tool calls pending in the latest message.
    """
    result = []
    
    tool_calls = state["messages"][-1].tool_calls
    
    for tool_call in tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    
    return {"messages": result}
```

Returns a `ToolMessage` for each tool call. These get appended to state and fed back to the agent node.

---

## Router (Conditional Edge)

Determines whether to loop back through the tools node or terminate.

```python
def route_tools(state: GraphState):
    """
    Routes to 'tools' if the latest message contains tool calls. Otherwise ends.
    """
    messages = state.get("messages", [])
    
    if len(messages) > 0:
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    
    return END
```

This is what creates the cycle: agent → tools → agent → tools → ... → END.

---

## Assemble the Graph

```python
def init_graph(llm_with_tools, tools_by_name):
    graph = StateGraph(GraphState)
    
    # Add nodes
    graph.add_node("agent", lambda state: agent(state, llm_with_tools))
    graph.add_node("tools", lambda state: tool_node(state, tools_by_name))
    
    # Static edges
    graph.add_edge(START, "agent")       # always start at agent
    graph.add_edge("tools", "agent")     # after tools, return to agent
    
    # Conditional edge: after agent, route to tools or END
    graph.add_conditional_edges(
        "agent",
        route_tools,
        {"tools": "tools", END: END}
    )
    
    return graph.compile()
```

---

## Execute the Graph

```python
def execute_graph(app, user_input: str) -> None:
    input = {"messages": [("user", user_input)]}

    for output in app.stream(input):
        for key, value in output.items():
            print(f"Node {key}:")
            print(value)
    
    print("---FINAL ANSWER---")
    print(value["messages"][-1].content)
```

`app.stream()` yields output after each node execution, giving visibility into the agent's step-by-step reasoning — useful for debugging.

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
    
    app = init_graph(llm_with_tools, tools_by_name)
    
    execute_graph(app, "What are some best practices for data backups in MongoDB?")
    execute_graph(app, "Give me a summary of the page titled Create a MongoDB Deployment")

main()
```
