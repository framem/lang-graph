from state import PizzaState, StateManager, ConversationStatus, Pizza, Order, OrderItem
from services.pizza_service import PizzaCatalogService, PizzaRecommendationService
from services.order_service import OrderService, OrderValidationError
from services.conversation_service import ConversationService
from typing import List

def TriageAgent(state: PizzaState) -> PizzaState:
    """
    Enhanced triage agent using conversation service for better context management.
    Determines if user wants pizza, wants to exit, or is continuing a conversation.
    """
    conversation_service = ConversationService()
    user_input = state.get('user_input', '').lower()
    context = state['conversation_context']
    
    # Add turn to conversation context
    context.add_turn(user_input, "triage")
    
    # Handle continuation scenarios
    if context.status == ConversationStatus.AWAITING_CONTINUATION:
        wants_to_continue = conversation_service.detect_continuation_intent(user_input, context)
        
        if wants_to_continue:
            # User wants another pizza - reset for new order
            state = StateManager.reset_for_new_order(state)
            state = StateManager.transition_to_pizza_search(state, user_input)
            print(f"Triage: User wants another pizza - starting new order: {user_input}")
        else:
            # User wants to finish
            state = StateManager.transition_to_exit(state, "User finished ordering")
            print(f"Triage: User finished ordering - ending session")
        
        return state
    
    # Initial triage logic with enhanced keywords
    pizza_keywords = [
        'pizza', 'order', 'buy', 'want', 'hungry', 'food', 'eat',
        'margherita', 'pepperoni', 'veggie', 'hawaiian', 'meat',
        'give', 'get', 'like', 'love', 'craving'
    ]
    
    exit_keywords = [
        'no thanks', 'no', 'exit', 'quit', 'bye', 'goodbye', 
        'stop', 'cancel', 'nothing', 'never mind', 'not interested'
    ]
    
    # Check for explicit exit signals first
    if (user_input.startswith('no') or 
        any(keyword in user_input for keyword in exit_keywords if keyword != 'no')):
        
        state = StateManager.transition_to_exit(state, "User declined pizza order")
        print(f"Triage: User wants to exit - {state['exit_reason']}")
    
    elif any(keyword in user_input for keyword in pizza_keywords):
        # User wants pizza
        state = StateManager.transition_to_pizza_search(state, user_input)
        print(f"Triage: User wants pizza - forwarding request: {user_input}")
    
    else:
        # Ambiguous input - default to pizza search with clarification
        state = StateManager.transition_to_pizza_search(state, user_input)
        print(f"Triage: Ambiguous input, forwarding to pizza agent for clarification: {user_input}")
    
    return state

def PizzaAgent(state: PizzaState) -> PizzaState:
    """
    Enhanced pizza agent using pizza catalog service for improved matching.
    Processes pizza requests and manages order creation.
    """
    print("PizzaAgent: Processing pizza request...")
    
    # Initialize services
    catalog_service = PizzaCatalogService()
    order_service = OrderService()
    
    pizza_request = state.get('pizza_request', '')
    context = state['conversation_context']
    
    # Add turn to conversation context
    context.add_turn(pizza_request, "pizza_agent")
    
    # Clear previous errors
    state = StateManager.clear_errors(state)
    
    try:
        # Search for matching pizzas using the enhanced service
        search_result = catalog_service.search_pizzas(pizza_request, max_results=3)
        
        if not search_result.matches:
            # No matches found - provide default recommendation
            default_pizza = catalog_service.get_pizza_by_name('margherita')
            search_result.matches = [default_pizza] if default_pizza else []
            search_result.confidence_score = 0.3
            print("PizzaAgent: No matches found, offering default recommendation")
        
        # Store search results in state
        state['matched_pizzas'] = search_result.matches
        best_match = search_result.matches[0] if search_result.matches else None
        state['selected_pizza'] = best_match
        
        # Create or get current order
        current_order = state.get('current_order')
        if not current_order:
            current_order = order_service.create_order(state.get('session_id', ''))
            state['current_order'] = current_order
        
        # Add selected pizza to order
        if best_match:
            try:
                order_item = order_service.add_pizza_to_order(current_order, best_match)
                state['found_pizza'] = str(best_match)
                
                print(f"PizzaAgent: Added {best_match.name} to order - {best_match.description}")
                
                # Provide recommendations if confidence is low
                if search_result.confidence_score < 0.7:
                    recommendation_service = PizzaRecommendationService(catalog_service)
                    similar_pizzas = recommendation_service.recommend_similar_pizzas(best_match, count=2)
                    
                    if similar_pizzas:
                        similar_names = [p.name for p in similar_pizzas]
                        print(f"PizzaAgent: Low confidence match. Consider: {', '.join(similar_names)}")
                
                # Transition to continuation state
                state = StateManager.transition_to_continuation(state)
                
            except OrderValidationError as e:
                error_msg = f"Failed to add pizza to order: {str(e)}"
                state = StateManager.add_error(state, error_msg)
                print(f"PizzaAgent: {error_msg}")
        
        else:
            error_msg = "No suitable pizza found for your request"
            state = StateManager.add_error(state, error_msg)
            print(f"PizzaAgent: {error_msg}")
    
    except Exception as e:
        error_msg = f"Error processing pizza request: {str(e)}"
        state = StateManager.add_error(state, error_msg)
        print(f"PizzaAgent: {error_msg}")
    
    return state

def ContinuationAgent(state: PizzaState) -> PizzaState:
    """
    Enhanced continuation agent with order management and proper state transitions.
    Handles order completion, continuation, and provides order summary.
    """
    print("ContinuationAgent: Pizza added to order!")
    
    # Initialize services
    order_service = OrderService()
    conversation_service = ConversationService()
    
    context = state['conversation_context']
    current_order = state.get('current_order')
    
    # Add turn to conversation context
    context.add_turn("order_processed", "continuation_agent")
    
    # Provide order summary
    if current_order:
        try:
            order_summary = order_service.get_order_summary(current_order)
            print(f"ContinuationAgent: Current order: {order_summary['item_count']} items, Total: ${order_summary['total_amount']:.2f}")
            
            # Show current items
            for i, item in enumerate(order_summary['items'], 1):
                print(f"  {i}. {item['pizza_name']} x{item['quantity']} - ${item['total_price']:.2f}")
            
            # Provide suggestions
            suggestions = order_service.OrderRecommendationService(order_service).suggest_add_ons(current_order)
            if suggestions:
                print(f"ContinuationAgent: Suggestions: {', '.join(suggestions)}")
                
        except Exception as e:
            error_msg = f"Error generating order summary: {str(e)}"
            state = StateManager.add_error(state, error_msg)
            print(f"ContinuationAgent: {error_msg}")
    
    # Set state to await user input for continuation decision
    state = StateManager.transition_to_continuation(state)
    
    print("ContinuationAgent: Would you like to add another pizza or complete your order?")
    print("  - Say 'another pizza' or 'add more' to continue ordering")  
    print("  - Say 'done', 'finish', or 'complete order' to checkout")
    
    return state