#!/usr/bin/env python3
"""
Simple test to verify the cs_pizza example structure works without external dependencies.
"""

from state import PizzaState
from nodes import TriageAgent, PizzaAgent
from edges import route_after_triage

def test_structure():
    print("Testing cs_pizza example structure...")
    
    # Test case 1: User wants pizza
    print("\n--- Test 1: User wants pizza ---")
    state1 = PizzaState(
        user_input="I want a pepperoni pizza",
        wants_pizza=False,
        pizza_request="",
        found_pizza=None,
        exit_reason=None,
    )
    
    # Run triage
    state1 = TriageAgent(state1)
    route1 = route_after_triage(state1)
    print(f"Triage result: wants_pizza={state1['wants_pizza']}, route={route1}")
    
    if route1 == "pizza_agent":
        state1 = PizzaAgent(state1)
        print(f"Pizza found: {state1['found_pizza']}")
    
    # Test case 2: User doesn't want pizza
    print("\n--- Test 2: User doesn't want pizza ---")
    state2 = PizzaState(
        user_input="No thanks, goodbye",
        wants_pizza=False,
        pizza_request="",
        found_pizza=None,
        exit_reason=None,
    )
    
    # Run triage
    state2 = TriageAgent(state2)
    route2 = route_after_triage(state2)
    print(f"Triage result: wants_pizza={state2['wants_pizza']}, route={route2}")
    print(f"Exit reason: {state2.get('exit_reason')}")
    
    # Test case 3: Veggie pizza request
    print("\n--- Test 3: Veggie pizza request ---")
    state3 = PizzaState(
        user_input="I want something with vegetables and mushrooms",
        wants_pizza=False,
        pizza_request="",
        found_pizza=None,
        exit_reason=None,
    )
    
    # Run triage
    state3 = TriageAgent(state3)
    route3 = route_after_triage(state3)
    print(f"Triage result: wants_pizza={state3['wants_pizza']}, route={route3}")
    
    if route3 == "pizza_agent":
        state3 = PizzaAgent(state3)
        print(f"Pizza found: {state3['found_pizza']}")
    
    print("\nStructure test completed successfully!")

if __name__ == "__main__":
    test_structure()