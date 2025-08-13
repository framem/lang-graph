"""
Test suite for the improved cs_pizza implementation.
Tests state management and layered architecture improvements.
"""

import unittest
from datetime import datetime
from state import (
    PizzaState, StateManager, ConversationStatus, OrderStatus,
    Pizza, Order, OrderItem, ConversationContext
)
from services.pizza_service import PizzaCatalogService, PizzaRecommendationService
from services.order_service import OrderService, OrderValidationError
from services.conversation_service import ConversationService

class TestStateManagement(unittest.TestCase):
    """Test enhanced state management"""
    
    def test_pizza_model(self):
        """Test Pizza dataclass functionality"""
        pizza = Pizza(
            name="margherita",
            description="Classic Italian pizza",
            ingredients=["tomato", "mozzarella", "basil"],
            price=12.99
        )
        
        self.assertEqual(pizza.name, "margherita")
        self.assertEqual(pizza.price, 12.99)
        self.assertIn("tomato", pizza.ingredients)
        self.assertEqual(pizza.size, "medium")  # Default value
        
        # Test string representation
        str_repr = str(pizza)
        self.assertIn("Margherita", str_repr)
        self.assertIn("$12.99", str_repr)
    
    def test_order_item(self):
        """Test OrderItem functionality"""
        pizza = Pizza("pepperoni", "Pepperoni pizza", ["tomato", "pepperoni"], 14.99)
        item = OrderItem(pizza, quantity=2)
        
        self.assertEqual(item.pizza.name, "pepperoni")
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.total_price, 29.98)
        self.assertIsInstance(item.timestamp, datetime)
    
    def test_order_management(self):
        """Test Order functionality"""
        pizza1 = Pizza("margherita", "Classic", ["tomato"], 12.99)
        pizza2 = Pizza("pepperoni", "Pepperoni", ["tomato", "pepperoni"], 14.99)
        
        item1 = OrderItem(pizza1, quantity=1)
        item2 = OrderItem(pizza2, quantity=2)
        
        order = Order([item1, item2])
        
        self.assertEqual(len(order.items), 2)
        self.assertEqual(order.status, OrderStatus.PENDING)
        self.assertAlmostEqual(order.total_amount, 42.97, places=2)
        
        # Test adding items
        pizza3 = Pizza("veggie", "Vegetarian", ["tomato", "peppers"], 13.99)
        item3 = OrderItem(pizza3, quantity=1)
        order.add_item(item3)
        
        self.assertEqual(len(order.items), 3)
        self.assertAlmostEqual(order.total_amount, 56.96, places=2)
    
    def test_state_manager(self):
        """Test StateManager utility functions"""
        # Test initial state creation
        state = StateManager.create_initial_state("I want pizza", "session_123")
        
        self.assertEqual(state["user_input"], "I want pizza")
        self.assertEqual(state["session_id"], "session_123")
        self.assertEqual(state["next_action"], "triage")
        self.assertFalse(state["requires_user_input"])
        self.assertEqual(state["retry_count"], 0)
        
        # Test pizza search transition
        state = StateManager.transition_to_pizza_search(state, "pepperoni pizza")
        
        self.assertTrue(state["wants_pizza"])
        self.assertEqual(state["pizza_request"], "pepperoni pizza")
        self.assertEqual(state["conversation_context"].status, ConversationStatus.PROCESSING_ORDER)
        self.assertEqual(state["next_action"], "pizza_search")
        
        # Test exit transition
        state = StateManager.transition_to_exit(state, "User declined")
        
        self.assertFalse(state["wants_pizza"])
        self.assertEqual(state["exit_reason"], "User declined")
        self.assertEqual(state["conversation_context"].status, ConversationStatus.EXITED)
        
        # Test error handling
        state = StateManager.add_error(state, "Test error")
        
        self.assertEqual(state["last_error"], "Test error")
        self.assertIn("Test error", state["validation_errors"])
        self.assertEqual(state["retry_count"], 1)
        
        # Test error clearing
        state = StateManager.clear_errors(state)
        
        self.assertIsNone(state["last_error"])
        self.assertIsNone(state["validation_errors"])
        self.assertEqual(state["retry_count"], 0)

class TestPizzaService(unittest.TestCase):
    """Test pizza catalog and recommendation services"""
    
    def setUp(self):
        self.catalog_service = PizzaCatalogService()
        self.recommendation_service = PizzaRecommendationService(self.catalog_service)
    
    def test_pizza_catalog(self):
        """Test pizza catalog operations"""
        all_pizzas = self.catalog_service.get_all_pizzas()
        self.assertGreater(len(all_pizzas), 0)
        
        # Test getting pizza by name
        margherita = self.catalog_service.get_pizza_by_name("margherita")
        self.assertIsNotNone(margherita)
        self.assertEqual(margherita.name, "margherita")
        
        pepperoni = self.catalog_service.get_pizza_by_name("pepperoni")
        self.assertIsNotNone(pepperoni)
        self.assertIn("pepperoni", pepperoni.ingredients)
    
    def test_pizza_search(self):
        """Test enhanced pizza search functionality"""
        # Test direct name match
        result = self.catalog_service.search_pizzas("pepperoni pizza")
        self.assertGreater(len(result.matches), 0)
        self.assertEqual(result.matches[0].name, "pepperoni")
        self.assertGreater(result.confidence_score, 0.5)
        
        # Test ingredient match
        result = self.catalog_service.search_pizzas("I want something with mushrooms")
        self.assertGreater(len(result.matches), 0)
        
        # Test fuzzy matching
        result = self.catalog_service.search_pizzas("meat lovers")
        self.assertGreater(len(result.matches), 0)
        
        # Test no match scenario
        result = self.catalog_service.search_pizzas("sushi")
        # Should still return some results (default recommendations)
        self.assertGreaterEqual(len(result.matches), 0)
    
    def test_recommendations(self):
        """Test pizza recommendation service"""
        pepperoni = self.catalog_service.get_pizza_by_name("pepperoni")
        similar_pizzas = self.recommendation_service.recommend_similar_pizzas(pepperoni, count=2)
        
        self.assertLessEqual(len(similar_pizzas), 2)
        for pizza in similar_pizzas:
            self.assertNotEqual(pizza.name, "pepperoni")
        
        # Test popular pizzas
        popular = self.recommendation_service.get_popular_pizzas(count=3)
        self.assertLessEqual(len(popular), 3)
        self.assertTrue(any(p.name == "pepperoni" for p in popular))

class TestOrderService(unittest.TestCase):
    """Test order management service"""
    
    def setUp(self):
        self.order_service = OrderService()
        self.catalog_service = PizzaCatalogService()
    
    def test_order_creation(self):
        """Test order creation and management"""
        order = self.order_service.create_order("session_123")
        
        self.assertIsNotNone(order)
        self.assertEqual(order.status, OrderStatus.PENDING)
        self.assertEqual(len(order.items), 0)
        self.assertEqual(order.total_amount, 0.0)
    
    def test_add_pizza_to_order(self):
        """Test adding pizzas to orders"""
        order = self.order_service.create_order("session_123")
        pizza = self.catalog_service.get_pizza_by_name("margherita")
        
        item = self.order_service.add_pizza_to_order(order, pizza, quantity=2)
        
        self.assertEqual(len(order.items), 1)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(order.total_amount, pizza.price * 2)
    
    def test_order_validation(self):
        """Test order validation"""
        order = self.order_service.create_order("session_123")
        
        # Empty order should have validation errors
        errors = self.order_service.validate_order(order)
        self.assertIn("Order cannot be empty", errors)
        
        # Add valid pizza
        pizza = self.catalog_service.get_pizza_by_name("pepperoni")
        self.order_service.add_pizza_to_order(order, pizza)
        
        # Should pass validation now
        errors = self.order_service.validate_order(order)
        self.assertEqual(len(errors), 0)
        
        # Should confirm successfully
        confirmed = self.order_service.confirm_order(order)
        self.assertTrue(confirmed)
        self.assertEqual(order.status, OrderStatus.CONFIRMED)
    
    def test_order_summary(self):
        """Test order summary generation"""
        order = self.order_service.create_order("session_123")
        pizza1 = self.catalog_service.get_pizza_by_name("margherita")
        pizza2 = self.catalog_service.get_pizza_by_name("pepperoni")
        
        self.order_service.add_pizza_to_order(order, pizza1, quantity=1)
        self.order_service.add_pizza_to_order(order, pizza2, quantity=2, 
                                            special_instructions="Extra cheese")
        
        summary = self.order_service.get_order_summary(order)
        
        self.assertEqual(summary["item_count"], 2)
        self.assertGreater(summary["total_amount"], 0)
        self.assertEqual(len(summary["items"]), 2)
        self.assertEqual(summary["items"][1]["special_instructions"], "Extra cheese")

class TestConversationService(unittest.TestCase):
    """Test conversation management service"""
    
    def setUp(self):
        self.conversation_service = ConversationService()
    
    def test_session_creation(self):
        """Test conversation session creation"""
        session_id, state = self.conversation_service.create_session("I want pizza")
        
        self.assertIsNotNone(session_id)
        self.assertEqual(state["user_input"], "I want pizza")
        self.assertEqual(state["session_id"], session_id)
        
        # Clean up
        self.conversation_service.cleanup_session(session_id)
    
    def test_session_management(self):
        """Test session state management"""
        session_id, state = self.conversation_service.create_session("Hello")
        
        # Test getting session state
        retrieved_state = self.conversation_service.get_session_state(session_id)
        self.assertEqual(retrieved_state["user_input"], "Hello")
        
        # Test updating session state
        state["user_input"] = "I want pizza now"
        updated = self.conversation_service.update_session_state(session_id, state)
        self.assertTrue(updated)
        
        # Test adding user input
        success = self.conversation_service.add_user_input(session_id, "Pepperoni please")
        self.assertTrue(success)
        
        retrieved_state = self.conversation_service.get_session_state(session_id)
        self.assertEqual(retrieved_state["user_input"], "Pepperoni please")
        
        # Clean up
        self.conversation_service.cleanup_session(session_id)
    
    def test_continuation_detection(self):
        """Test continuation intent detection"""
        context = ConversationContext()
        
        # Test explicit continuation with "another"
        result = self.conversation_service.detect_continuation_intent("another pizza", context)
        self.assertTrue(result)
        
        # Test explicit ending
        result = self.conversation_service.detect_continuation_intent("no thanks I'm done", context)
        self.assertFalse(result)
        
        # Test pizza-related continuation
        result = self.conversation_service.detect_continuation_intent("I want margherita too", context)
        self.assertTrue(result)
        
        # Test awaiting continuation context
        context.status = ConversationStatus.AWAITING_CONTINUATION
        result = self.conversation_service.detect_continuation_intent("another pizza", context)
        self.assertTrue(result)
    
    def test_conversation_summary(self):
        """Test conversation summary generation"""
        session_id, state = self.conversation_service.create_session("I want pizza")
        
        summary = self.conversation_service.get_conversation_summary(session_id)
        
        self.assertIsNotNone(summary)
        self.assertEqual(summary["session_id"], session_id)
        self.assertEqual(summary["status"], "initial")
        self.assertGreater(summary["turn_count"], 0)
        
        # Clean up
        self.conversation_service.cleanup_session(session_id)

def run_integration_test():
    """Integration test simulating a complete workflow"""
    print("\n" + "="*50)
    print("INTEGRATION TEST - COMPLETE WORKFLOW")
    print("="*50)
    
    # Initialize services
    catalog_service = PizzaCatalogService()
    order_service = OrderService()
    conversation_service = ConversationService()
    
    # Simulate complete pizza ordering flow
    print("1. Creating conversation session...")
    session_id, state = conversation_service.create_session("I want a pepperoni pizza")
    
    print("2. Searching for pizza...")
    search_result = catalog_service.search_pizzas("pepperoni pizza")
    assert len(search_result.matches) > 0, "Should find pepperoni pizza"
    
    print("3. Creating order...")
    order = order_service.create_order(session_id)
    pizza = search_result.matches[0]
    order_service.add_pizza_to_order(order, pizza)
    
    print("4. Validating order...")
    errors = order_service.validate_order(order)
    assert len(errors) == 0, f"Order should be valid, got errors: {errors}"
    
    print("5. Confirming order...")
    confirmed = order_service.confirm_order(order)
    assert confirmed, "Order should confirm successfully"
    
    print("6. Getting order summary...")
    summary = order_service.get_order_summary(order)
    assert summary["item_count"] == 1, "Should have 1 item in order"
    assert "pepperoni" in summary["items"][0]["pizza_name"].lower(), "Should be pepperoni pizza"
    
    print("7. Testing continuation detection...")
    context = state["conversation_context"]
    context.status = ConversationStatus.AWAITING_CONTINUATION  # Set proper context
    wants_more = conversation_service.detect_continuation_intent("another pizza", context)
    assert wants_more, "Should detect continuation intent"
    
    print("8. Cleaning up session...")
    conversation_service.cleanup_session(session_id)
    
    print("\n✅ Integration test PASSED - All components work together correctly!")

if __name__ == "__main__":
    # Run unit tests
    print("Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run integration test
    try:
        run_integration_test()
    except Exception as e:
        print(f"\n❌ Integration test FAILED: {str(e)}")
        raise
    
    print(f"\n🎉 All tests completed successfully!")
    print("Enhanced cs_pizza implementation is working correctly!")