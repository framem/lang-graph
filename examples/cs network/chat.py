from langchain_core.messages import HumanMessage
from langgraph.constants import END
from langgraph.graph import StateGraph
from state import GraphState
from node import triage_agent, triage_router, jira_node, confluence_node, status_node, product_agent, product_router

def create_workflow():
    """Create and compile the workflow graph."""
    workflow = StateGraph(GraphState)
    workflow.add_node("triage", triage_agent)
    workflow.add_node("product_agent", product_agent)
    workflow.add_node("jira_agent", jira_node)
    workflow.add_node("confluence_agent", confluence_node)
    workflow.add_node("status_agent", status_node)

    workflow.set_entry_point("triage")
    workflow.add_edge("jira_agent", END)
    workflow.add_edge("confluence_agent", END)
    workflow.add_edge("status_agent", END)
    workflow.add_conditional_edges("triage", triage_router, {
        "product": "product_agent",
        "jira": "jira_agent",
        "confluence": "confluence_agent",
        "status": "status_agent",
        "end": END
    })
    workflow.add_conditional_edges("product_agent", product_router)

    return workflow.compile()

def chat_loop():
    """Interactive chat loop with the cs network graph."""
    app = create_workflow()

    print("🤖 CS Network Assistant gestartet!")
    print("Verfügbare Bereiche: Product, Jira, Confluence, Status")
    print("Tippe 'exit' oder 'quit' zum Beenden.\n")

    while True:
        try:
            # Get user input
            user_input = input("Sie: ").strip()

            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'bye', 'tschüss']:
                print("👋 Auf Wiedersehen!")
                break

            if not user_input:
                continue

            # Create input message
            input_message = {
                "messages": [HumanMessage(content=user_input)]
            }

            # Process through the graph
            print("🔄 Verarbeitung...")
            result = app.invoke(input_message)

            # Display results
            print("\n" + "="*50)
            for msg in result["messages"]:
                if msg.type == "ai":
                    print(f"🤖 Assistant: {msg.content}")
                elif msg.type == "human":
                    print(f"👤 Sie: {msg.content}")
            print("="*50 + "\n")

        except KeyboardInterrupt:
            print("\n👋 Chat beendet!")
            break
        except Exception as e:
            print(f"❌ Fehler: {e}")
            print("Bitte versuchen Sie es erneut.\n")

if __name__ == "__main__":
    chat_loop()
