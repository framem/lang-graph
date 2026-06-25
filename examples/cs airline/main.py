from langgraph.graph import StateGraph, END

from edges import checking_required_data
from nodes import Triage, AskForFlightNumber, GetFlightDetails
from state import CustomerState


workflow = StateGraph(CustomerState)


workflow.add_node("triage", Triage)
workflow.add_node("askForFlightNumber", AskForFlightNumber)
workflow.add_node("getFlightDetails", GetFlightDetails)


workflow.add_edge('triage', 'askForFlightNumber')
workflow.add_edge('getFlightDetails', END)


# Set the entry point of the workflow
workflow.set_entry_point("triage")

# Add conditional edges: branch on whether a valid flight number is present
workflow.add_conditional_edges(
    "askForFlightNumber",
    checking_required_data,
    {
        "try_again": END,
        "got_flight_number": 'getFlightDetails',
    },
)


# Compile the workflow into a runnable app
app = workflow.compile()

# Mermaid-String ausgeben
mermaid_code = app.get_graph().draw_mermaid()
# print(mermaid_code)

# Optional: Mermaid-Code in Datei speichern
with open("workflow_graph.mmd", "w") as f:
    f.write(mermaid_code)

# Initialize the state
initial_state = CustomerState(
    flight_number = "A-123",
)

for s in app.stream(initial_state):
    # Print the current state
    print("for s in app.stream(initial_state):")
    print(s)

