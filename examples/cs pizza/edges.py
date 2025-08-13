from typing import Literal
from state import PizzaState

def route_after_triage(state: PizzaState) -> Literal["pizza_agent", "__end__"]:
    """
    Routing function that determines next step after triage.
    Routes to pizza_agent if user wants pizza, otherwise exits.
    """
    wants_pizza = state.get('wants_pizza', False)
    
    if wants_pizza:
        print("Routing: User wants pizza -> pizza_agent")
        return "pizza_agent"
    else:
        print("Routing: User doesn't want pizza -> __end__")
        return "__end__"

def route_after_pizza(state: PizzaState) -> Literal["continuation_agent"]:
    """
    Routing function after pizza agent - always goes to continuation.
    """
    print("Routing: Pizza processed -> continuation_agent")
    return "continuation_agent"

def route_after_continuation(state: PizzaState) -> Literal["triage", "__end__"]:
    """
    Routing function after continuation agent.
    Routes back to triage if user wants another pizza, otherwise ends.
    """
    continue_ordering = state.get('continue_ordering', False)
    
    if continue_ordering:
        print("Routing: User wants another pizza -> triage")
        return "triage"
    else:
        print("Routing: Order complete -> __end__")
        return "__end__"