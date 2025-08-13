#!/usr/bin/env python3
"""
Simple test of the pizza workflow without external dependencies.
This simulates the workflow execution to demonstrate the continuation logic.
"""

from state import PizzaState
from nodes import TriageAgent, PizzaAgent, ContinuationAgent
from edges import route_after_triage, route_after_pizza, route_after_continuation

def simulate_workflow(initial_input: str):
    """Simulate the workflow execution step by step."""
    print(f"\n{'='*50}")
    print(f"STARTING WORKFLOW WITH INPUT: '{initial_input}'")
    print(f"{'='*50}")
    
    # Initialize state
    state = PizzaState(
        user_input=initial_input,
        wants_pizza=False,
        pizza_request="",
        found_pizza=None,
        exit_reason=None,
        continue_ordering=None,
    )
    
    current_node = "triage"
    step = 1
    
    while current_node != "__end__":
        print(f"\n--- Step {step}: {current_node} ---")
        
        if current_node == "triage":
            state = TriageAgent(state)
            next_node = route_after_triage(state)
            
        elif current_node == "pizza_agent":
            state = PizzaAgent(state)
            next_node = route_after_pizza(state)
            
        elif current_node == "continuation_agent":
            state = ContinuationAgent(state)
            next_node = route_after_continuation(state)
        
        print(f"Current state: {dict(state)}")
        print(f"Next node: {next_node}")
        
        current_node = next_node
        step += 1
        
        # Safety check to avoid infinite loops
        if step > 10:
            print("Too many steps, ending simulation")
            break
    
    print(f"\n--- WORKFLOW ENDED ---")
    print(f"Final state: {dict(state)}")

if __name__ == "__main__":
    # Test scenarios
    test_cases = [
        "I want a pepperoni pizza",
        "No thanks, I don't want anything", 
        "I want margherita pizza and then another one",
        "Give me a veggie pizza done"
    ]
    
    for test_input in test_cases:
        simulate_workflow(test_input)
        print("\n" + "="*70)