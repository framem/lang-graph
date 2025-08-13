from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage
from state import GraphState

def Triage(state: GraphState) -> GraphState:
        user_message = state["messages"][-1].content
        llm = ChatOllama(
            model="mistral:latest",
            base_url="http://127.0.0.1:11434",
            temperature=0.1,
            timeout=60
        )
        system_prompt = (
            "Du bist ein Routing-Agent. Ordne die folgende Nutzeranfrage einer Kategorie zu: \n"
            "Mögliche Kategorien: Jira, Confluence, Status\n"
            "Gib nur eine dieser Kategorien als Antwort zurück. Wenn keine passt, gibt 'end' zurück."
        )
        prompt = f"System:{system_prompt}\nNutzeranfrage: {user_message}"
        response = llm.invoke(prompt)
        category = response.content.strip().lower()
        if category not in ["jira", "confluence", "status"]:
            category = "end"
        return category

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