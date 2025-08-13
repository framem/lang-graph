from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from langgraph.constants import END

from state import GraphState
from tools import fetch_product, search_products, get_product_categories


def triage_agent(state: GraphState) -> GraphState:
    user_message = state["messages"][-1].content
    llm = ChatOllama(
        model="mistral:latest",
        base_url="http://127.0.0.1:11434",
        temperature=0.1,
        timeout=10
    )
    system_prompt = (
        "Du bist ein Routing-Agent. Ordne die folgende Nutzeranfrage einer Kategorie zu: \n"
        "Mögliche Kategorien: Product, Jira, Confluence, Status\n"
        "Gib nur eine dieser Kategorien als Antwort zurück. Wenn keine passt, gibt 'end' zurück."
    )
    prompt = f"System:{system_prompt}\nNutzeranfrage: {HumanMessage(content=user_message).content}"
    response = llm.invoke(prompt)
    category = response.content.strip().lower()
    if category not in ["product", "jira", "confluence", "status"]:
        category = "end"

    # Store the routing decision in state and return state
    state["routing_decision"] = category
    return state

def triage_router(state: GraphState) -> str:
    # Return the routing decision for conditional edges
    return state.get("routing_decision", "end")

def product_router(state: GraphState) -> str:
    # Check if we need to route back to triage or end
    routing_decision = state.get("routing_decision", "end")
    if routing_decision in ["product_ask_id", "triage"]:
        return "triage"

    return END

def product_agent(state: GraphState) -> GraphState:
    user_message = state["messages"][-1].content

    # Create ReAct agent with tools
    llm = ChatOllama(
        model="mistral:latest",
        base_url="http://127.0.0.1:11434",
        temperature=0.1,
        timeout=10
    )

    tools = [fetch_product, search_products, get_product_categories]

    # ReAct prompt template
    react_prompt = PromptTemplate.from_template("""
    You are a product assistant helping customers with product inquiries.
    You have access to the following tools:

    {tools}

    Use the following format:

    Question: the input question you need to answer
    Thought: you should always think about what to do
    Important Rules:
    - In the `Action:` line, write only the exact tool name (from [{tool_names}]), without parentheses or additions.
    - In the `Action Input:` line, write only the input for the tool.
    - If you no longer need any tools, write:
        Action: none
        Action Input: none
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can be repeated N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Always respond in German in the `Final Answer`. When retrieving product information, summarize it clearly. Use the tool names exactly as defined.

    Question: {input}
    {agent_scratchpad}
    """)

    try:
        # Create and execute ReAct agent
        agent = create_react_agent(llm, tools, react_prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=5,handle_parsing_errors=True)

        result = agent_executor.invoke({"input": user_message})
        response_content = result.get("output", "Entschuldigung, ich konnte Ihre Anfrage nicht bearbeiten.")

        return {"messages": state["messages"] + [AIMessage(content=response_content)]}

    except Exception as e:
        print(f"Error in product ReAct agent: {e}")
        state["routing_decision"] = "triage"
        return {"messages": state["messages"] + [AIMessage(content="Fehler beim Verarbeiten Ihrer Produktanfrage. Wie kann ich Ihnen sonst helfen?")]}

def jira_tool(state: GraphState) -> GraphState:
    query = state["messages"][-1].content
    answer = query
    return {"messages": state["messages"] + [AIMessage(content=answer)]}

def confluence_tool(state: GraphState) -> GraphState:
    query = state["messages"][-1].content
    answer = query
    return {"messages": state["messages"] + [AIMessage(content=answer)]}

def status_tool(state: GraphState) -> GraphState:
    query = state["messages"][-1].content
    answer = "All good"
    return {"messages": state["messages"] + [AIMessage(content=answer)]}
