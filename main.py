"""
AI Agents with MongoDB — Complete Implementation
Covers: environment setup, tools, LLM tool access, LangGraph agent, memory
"""

import key_param
from pymongo import MongoClient
from langchain.agents import tool
from typing import List, Annotated
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import ToolMessage
from langgraph.graph import END, StateGraph, START
from langgraph.checkpoint.mongodb import MongoDBSaver
import voyageai


# ---------------------------------------------------------------------------
# MongoDB Initialization
# ---------------------------------------------------------------------------

def init_mongodb():
    """
    Initialize MongoDB client and collections.

    Returns:
        tuple: (mongodb_client, chunked_docs collection, full_docs collection)
    """
    mongodb_client = MongoClient(key_param.mongodb_uri)

    DB_NAME = "ai_agents"
    vs_collection = mongodb_client[DB_NAME]["chunked_docs"]
    full_collection = mongodb_client[DB_NAME]["full_docs"]

    return mongodb_client, vs_collection, full_collection


# ---------------------------------------------------------------------------
# Embedding Helper
# ---------------------------------------------------------------------------

def generate_embedding(text: str) -> List[float]:
    """
    Generate a vector embedding for a piece of text using voyage-3-lite.

    Args:
        text (str): Text to embed.

    Returns:
        List[float]: 512-dimensional embedding vector.
    """
    embedding_model = voyageai.Client(api_key=key_param.voyage_api_key)
    embedding = embedding_model.embed(
        text, model="voyage-3-lite", input_type="query"
    ).embeddings[0]
    return embedding


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool
def get_information_for_question_answering(user_query: str) -> str:
    """
    Retrieve relevant documents for a user query using vector search.

    Args:
        user_query (str): The user's question about MongoDB.

    Returns:
        str: Top 5 matching document bodies concatenated as context for the LLM.
    """
    query_embedding = generate_embedding(user_query)
    vs_collection = init_mongodb()[1]

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 150,
                "limit": 5,
            }
        },
        {
            "$project": {
                "_id": 0,
                "body": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]

    results = vs_collection.aggregate(pipeline)
    context = "\n\n".join([doc.get("body") for doc in results])
    return context


@tool
def get_page_content_for_summarization(user_query: str) -> str:
    """
    Retrieve the full content of a documentation page by exact title match for summarization.

    Args:
        user_query (str): The exact title of the documentation page.

    Returns:
        str: Full page body, or "Document not found" if no match exists.
    """
    full_collection = init_mongodb()[2]

    query = {"title": user_query}
    projection = {"_id": 0, "body": 1}
    document = full_collection.find_one(query, projection)

    if document:
        return document["body"]
    else:
        return "Document not found"


# ---------------------------------------------------------------------------
# Graph State
# ---------------------------------------------------------------------------

class GraphState(TypedDict):
    # add_messages reducer appends new messages rather than overwriting
    messages: Annotated[list, add_messages]


# ---------------------------------------------------------------------------
# Graph Nodes
# ---------------------------------------------------------------------------

def agent(state: GraphState, llm_with_tools) -> GraphState:
    """
    Agent node — the decision-maker. Invokes the LLM to either answer directly
    or decide which tool to call.
    """
    messages = state["messages"]
    result = llm_with_tools.invoke(messages)
    return {"messages": [result]}


def tool_node(state: GraphState, tools_by_name) -> GraphState:
    """
    Tool node — executes all tool calls requested by the agent node.
    """
    result = []
    tool_calls = state["messages"][-1].tool_calls

    for tool_call in tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))

    return {"messages": result}


# ---------------------------------------------------------------------------
# Router (Conditional Edge)
# ---------------------------------------------------------------------------

def route_tools(state: GraphState):
    """
    Routes to 'tools' node if the agent produced tool calls; otherwise ends.
    """
    messages = state.get("messages", [])

    if not messages:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")

    ai_message = messages[-1]

    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"

    return END


# ---------------------------------------------------------------------------
# Graph Initialization
# ---------------------------------------------------------------------------

def init_graph(llm_with_tools, tools_by_name, mongodb_client):
    """
    Build and compile the LangGraph StateGraph with MongoDB-backed checkpointing.

    Args:
        llm_with_tools: Prompt | LLM chain with tools bound.
        tools_by_name (dict): Map of tool name -> tool function.
        mongodb_client: PyMongo MongoClient for the checkpointer.

    Returns:
        Compiled StateGraph application.
    """
    graph = StateGraph(GraphState)

    graph.add_node("agent", lambda state: agent(state, llm_with_tools))
    graph.add_node("tools", lambda state: tool_node(state, tools_by_name))

    graph.add_edge(START, "agent")
    graph.add_edge("tools", "agent")
    graph.add_conditional_edges("agent", route_tools, {"tools": "tools", END: END})

    checkpointer = MongoDBSaver(mongodb_client)

    return graph.compile(checkpointer=checkpointer)


# ---------------------------------------------------------------------------
# Graph Execution
# ---------------------------------------------------------------------------

def execute_graph(app, thread_id: str, user_input: str) -> None:
    """
    Stream the graph execution for a user query, printing each node's output.

    Args:
        app: Compiled LangGraph application.
        thread_id (str): Session identifier. Same ID across calls = agent remembers prior context.
        user_input (str): The user's query.
    """
    input = {"messages": [("user", user_input)]}
    config = {"configurable": {"thread_id": thread_id}}

    for output in app.stream(input, config):
        for key, value in output.items():
            print(f"Node {key}:")
            print(value)

    print("---FINAL ANSWER---")
    print(value["messages"][-1].content)


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

def main():
    """
    Main function — initializes all components and runs the agent.
    """
    mongodb_client, vs_collection, full_collection = init_mongodb()

    tools = [
        get_information_for_question_answering,
        get_page_content_for_summarization,
    ]

    llm = ChatOpenAI(
        openai_api_key=key_param.openai_api_key,
        temperature=0,
        model="gpt-4o"
    )

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

    app = init_graph(llm_with_tools, tools_by_name, mongodb_client)

    # Test: vector search path
    execute_graph(app, "1", "What are some best practices for data backups in MongoDB?")

    # Test: memory — agent should recall the previous question
    execute_graph(app, "1", "What did I just ask you?")

    # Test: page summarization path
    execute_graph(app, "2", "Give me a summary of the page titled Create a MongoDB Deployment")


main()
