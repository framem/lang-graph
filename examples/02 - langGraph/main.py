from langgraph.graph import StateGraph, END
from typing import Dict, Any


def function_1(state: Dict[str, Any]) -> Dict[str, Any]:
    return {"text": state["text"] + " Hello "}

def function_2(state: Dict[str, Any]) -> Dict[str, Any]:
    return {"text": state["text"] + "World!"}


# StateGraph erstellen
workflow = StateGraph(dict)

workflow.add_node("node_1", function_1)
workflow.add_node("node_2", function_2)

workflow.add_edge('node_1', 'node_2')
workflow.add_edge('node_2', END)

workflow.set_entry_point("node_1")

# Compile the workflow into a runnable app
app = workflow.compile()

# Mermaid-String ausgeben
mermaid_code = app.get_graph().draw_mermaid()
print(mermaid_code)

# Optional: Mermaid-Code in Datei speichern
with open("workflow_graph.mmd", "w") as f:
    f.write(mermaid_code)



# Ausführen
result = app.invoke({"text": "langgraph: "})
print(result["text"])