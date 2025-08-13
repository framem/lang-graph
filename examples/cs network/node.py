from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage
from state import GraphState
import requests

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
        prompt = f"System:{system_prompt}\nNutzeranfrage: {user_message}"
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

def product_agent(state: GraphState) -> GraphState:
    response = requests.get('https://fakestoreapi.com/products/1')
    return {"messages": state["messages"] + [AIMessage(content=response.json())]}

def jira_agent(state: GraphState) -> GraphState:
    query = state["messages"][-1].content
    answer = query
    return {"messages": state["messages"] + [AIMessage(content=answer)]}

def confluence_agent(state: GraphState) -> GraphState:
    query = state["messages"][-1].content
    answer = query
    return {"messages": state["messages"] + [AIMessage(content=answer)]}

def status_agent(state: GraphState) -> GraphState:
    query = state["messages"][-1].content
    answer = "All good"
    return {"messages": state["messages"] + [AIMessage(content=answer)]}