from langchain_core.messages import HumanMessage
from langgraph.constants import END
from langgraph.graph import StateGraph
from state import GraphState
from node import Triage, jira_agent, confluence_agent, status_agent

workflow = StateGraph(GraphState)


workflow.add_node("triage", Triage)
workflow.add_node("jira_agent", jira_agent)
workflow.add_node("confluence_agent", confluence_agent)
workflow.add_node("status_agent", status_agent)

workflow.set_entry_point("triage")
workflow.add_edge("jira_agent", END)
workflow.add_edge("confluence_agent", END)
workflow.add_edge("status_agent", END)

workflow.add_conditional_edges("triage", Triage, {
    "jira": "jira_agent",
    "confluence": "confluence_agent",
    "status": "status_agent",
    "__end__": END
})

app = workflow.compile()


mermaid_code = app.get_graph().draw_mermaid()
with open("workflow_graph.mmd", "w") as f:
    f.write(mermaid_code)

if __name__ == "__main__":
    input_message = {
        "messages": [HumanMessage(content="Gibt es aktuell Systemprobleme?")]
    }
    result = app.invoke(input_message)
    for msg in result["messages"]:
        print(f"{msg.type}: {msg.content}")
