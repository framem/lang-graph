from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END

from nodes import TriageAgent, PizzaAgent, ContinuationAgent
from state import PizzaState, StateManager, ConversationContext
from edges import route_after_triage, route_after_pizza, route_after_continuation
from agents import TriageAgentLLM, PizzaAgentLLM
from services.conversation_service import ConversationService
from services.pizza_service import PizzaCatalogService
from services.order_service import OrderService

# Initialize agent nodes
def triage_agent_node(state: PizzaState) -> PizzaState:
    return TriageAgent(state)

def pizza_agent_node(state: PizzaState) -> PizzaState:
    return PizzaAgent(state)

def continuation_agent_node(state: PizzaState) -> PizzaState:
    return ContinuationAgent(state)

# Create the workflow
workflow = StateGraph(PizzaState)

# Add nodes
workflow.add_node("triage", triage_agent_node)
workflow.add_node("pizza_agent", pizza_agent_node)
workflow.add_node("continuation_agent", continuation_agent_node)

# Set entry point
workflow.set_entry_point("triage")

# Add conditional edges
workflow.add_conditional_edges(
    "triage",
    route_after_triage,
    {
        "pizza_agent": "pizza_agent",
        "__end__": END,
    },
)

# Pizza agent goes to continuation
workflow.add_conditional_edges(
    "pizza_agent",
    route_after_pizza,
    {
        "continuation_agent": "continuation_agent",
    },
)

# Continuation agent can loop back to triage or end
workflow.add_conditional_edges(
    "continuation_agent",
    route_after_continuation,
    {
        "triage": "triage",
        "__end__": END,
    },
)

# Compile the workflow into a runnable app
app = workflow.compile()

# Generate Mermaid diagram
mermaid_code = app.get_graph().draw_mermaid()

# Save Mermaid code to file
with open("workflow_graph.mmd", "w") as f:
    f.write(mermaid_code)

print("Pizza ordering workflow created successfully!")
print("Mermaid diagram saved to workflow_graph.mmd")

# Enhanced test scenarios with new architecture
def test_pizza_workflow():
    print("\n" + "="*50)
    print("TESTING ENHANCED PIZZA WORKFLOW")
    print("="*50)
    
    conversation_service = ConversationService()
    
    test_cases = [
        {
            "name": "User wants pepperoni pizza",
            "input": "I want to order a pepperoni pizza",
        },
        {
            "name": "User doesn't want pizza", 
            "input": "No thanks, I don't want anything",
        },
        {
            "name": "User wants veggie pizza",
            "input": "I'm hungry and want something with vegetables",
        },
        {
            "name": "User asks for meat lovers",
            "input": "Give me a meat lovers pizza",
        },
        {
            "name": "Ambiguous request",
            "input": "I'm really hungry right now",
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- Test: {test_case['name']} ---")
        print(f"Input: {test_case['input']}")
        
        # Create session and initial state using new state manager
        session_id, initial_state = conversation_service.create_session(test_case["input"])
        
        try:
            # Run workflow
            final_result = None
            step_count = 0
            max_steps = 10  # Prevent infinite loops
            
            for step in app.stream(initial_state):
                step_count += 1
                if step_count > max_steps:
                    print("  Max steps reached - stopping to prevent infinite loop")
                    break
                    
                final_result = step
                # Print step info
                for node_name, node_state in step.items():
                    print(f"  Step {step_count} - {node_name}:")
                    if node_state.get('found_pizza'):
                        print(f"    Found pizza: {node_state['found_pizza']}")
                    if node_state.get('exit_reason'):
                        print(f"    Exit reason: {node_state['exit_reason']}")
                    if node_state.get('last_error'):
                        print(f"    Error: {node_state['last_error']}")
            
            # Show final conversation summary
            summary = conversation_service.get_conversation_summary(session_id)
            if summary:
                print(f"  Final status: {summary['status']}")
                print(f"  Total turns: {summary['turn_count']}")
                
        except Exception as e:
            print(f"  Test failed with error: {str(e)}")
        finally:
            # Cleanup session
            conversation_service.cleanup_session(session_id)
        
        print("-" * 50)

def interactive_pizza_session():
    """Interactive session for testing the enhanced workflow"""
    print("\n" + "="*50)
    print("INTERACTIVE PIZZA ORDERING SESSION")
    print("="*50)
    print("Type 'quit' to exit the session")
    
    conversation_service = ConversationService()
    
    # Get initial user input
    initial_input = input("\nWhat would you like to order today? ")
    if initial_input.lower() == 'quit':
        return
    
    # Create session
    session_id, state = conversation_service.create_session(initial_input)
    
    try:
        while conversation_service.should_continue_conversation(session_id):
            # Run one iteration of the workflow
            step_count = 0
            for step in app.stream(state):
                step_count += 1
                if step_count > 5:  # Prevent runaway
                    break
                    
                # Update state with latest step
                for node_name, node_state in step.items():
                    state = node_state
            
            # Check if we need user input
            if state.get('requires_user_input', False):
                # Get next user input
                next_input = input("\nYour response: ")
                if next_input.lower() == 'quit':
                    break
                    
                # Add input to session
                conversation_service.add_user_input(session_id, next_input)
                state["user_input"] = next_input
                state["requires_user_input"] = False
            else:
                break
    
    except KeyboardInterrupt:
        print("\n\nSession interrupted by user")
    except Exception as e:
        print(f"\nSession error: {str(e)}")
    finally:
        # Show final summary
        summary = conversation_service.get_conversation_summary(session_id)
        if summary:
            print(f"\n--- Session Summary ---")
            print(f"Status: {summary['status']}")
            print(f"Total turns: {summary['turn_count']}")
            if summary.get('has_order'):
                print("Order was created during session")
        
        conversation_service.cleanup_session(session_id)
        print("Session ended. Thanks for testing!")

if __name__ == "__main__":
    # Run automated tests
    test_pizza_workflow()
    
    # Offer interactive session
    user_choice = input("\nWould you like to try the interactive session? (y/n): ")
    if user_choice.lower() in ['y', 'yes']:
        interactive_pizza_session()