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

def product_router(state: GraphState) -> str:
    # Check if we need to route back to triage or end
    routing_decision = state.get("routing_decision", "end")
    if routing_decision in ["product_ask_id", "triage"]:
        return "triage"

    return "end"

def product_agent(state: GraphState) -> GraphState:
    user_message = state["messages"][-1].content

    # Extract product ID from user message using regex
    import re
    product_id_match = re.search(r'\b(\d+)\b', user_message)

    if product_id_match:
        product_id = product_id_match.group(1)

        try:
            # Fetch product data from API
            response = requests.get(f'https://fakestoreapi.com/products/{product_id}')
            product_data = response.json()

            # Convert JSON to readable string format
            product_text = f"""
            Produkt (ID: {product_id}):
            - Name: {product_data.get('title', 'N/A')}
            - Preis: ${product_data.get('price', 'N/A')}
            - Kategorie: {product_data.get('category', 'N/A')}
            - Bewertung: {product_data.get('rating', {}).get('rate', 'N/A')}/5 ({product_data.get('rating', {}).get('count', 0)} Bewertungen)
            - Beschreibung: {product_data.get('description', 'N/A')}
            """.strip()

            llm = ChatOllama(
                model="mistral:latest",
                base_url="http://127.0.0.1:11434",
                temperature=0.1,
                timeout=10
            )
            system_prompt = (
                "Du bist ein Produkt-Agent. Fasse die folgende Produktbeschreibung zusammen. \n"
                "Zeige dabei IMMER auch die ID.\n"
                "Übersetze Texte IMMER in deutsche Sprache."
            )
            prompt = f"System:{system_prompt}\nProduktbeschreibung: {product_text}"
            response = llm.invoke(prompt)

            return {"messages": state["messages"] + [AIMessage(content=response.content)]}

        except Exception as e:
            print(f"Error fetching product: {e}")
            # Error fetching product, route back to triage
            state["routing_decision"] = "triage"
            return {"messages": state["messages"] + [AIMessage(content="Fehler beim Abrufen der Produktdaten. Wie kann ich Ihnen sonst helfen?")]}

    else:
        # No product ID found, ask for one and route back to triage
        state["routing_decision"] = "product_ask_id"
        return {"messages": state["messages"] + [AIMessage(content="Bitte geben Sie eine Produkt-ID (1-20) an, um Produktinformationen zu erhalten.")]}

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
