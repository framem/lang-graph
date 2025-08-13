"""
Order management service.
Handles order lifecycle, validation, and persistence.
"""

from typing import List, Optional, Dict
from datetime import datetime
from state import Order, OrderItem, OrderStatus, Pizza
import uuid

class OrderValidationError(Exception):
    """Exception raised for order validation errors"""
    pass

class OrderService:
    """Service for managing order lifecycle and operations"""
    
    def __init__(self):
        self._orders: Dict[str, Order] = {}
        self._order_history: List[Order] = []
    
    def create_order(self, session_id: str) -> Order:
        """Create a new empty order"""
        order = Order(items=[], status=OrderStatus.PENDING)
        order_id = str(uuid.uuid4())
        self._orders[order_id] = order
        return order
    
    def add_pizza_to_order(self, order: Order, pizza: Pizza, quantity: int = 1, 
                          special_instructions: Optional[str] = None) -> OrderItem:
        """Add a pizza to an existing order"""
        if quantity <= 0:
            raise OrderValidationError("Quantity must be positive")
        
        if not pizza:
            raise OrderValidationError("Pizza cannot be None")
        
        order_item = OrderItem(
            pizza=pizza,
            quantity=quantity,
            special_instructions=special_instructions
        )
        
        order.add_item(order_item)
        return order_item
    
    def remove_item_from_order(self, order: Order, item_index: int) -> bool:
        """Remove an item from the order by index"""
        if 0 <= item_index < len(order.items):
            order.items.pop(item_index)
            order.calculate_total()
            return True
        return False
    
    def update_item_quantity(self, order: Order, item_index: int, new_quantity: int) -> bool:
        """Update the quantity of an order item"""
        if new_quantity <= 0:
            return self.remove_item_from_order(order, item_index)
        
        if 0 <= item_index < len(order.items):
            order.items[item_index].quantity = new_quantity
            order.calculate_total()
            return True
        return False
    
    def validate_order(self, order: Order) -> List[str]:
        """Validate an order and return list of validation errors"""
        errors = []
        
        if not order.items:
            errors.append("Order cannot be empty")
        
        for i, item in enumerate(order.items):
            if item.quantity <= 0:
                errors.append(f"Item {i+1}: Quantity must be positive")
            
            if not item.pizza:
                errors.append(f"Item {i+1}: Pizza information is missing")
            
            if item.pizza and not item.pizza.name:
                errors.append(f"Item {i+1}: Pizza name is required")
        
        if order.total_amount <= 0:
            errors.append("Order total must be greater than zero")
        
        return errors
    
    def confirm_order(self, order: Order) -> bool:
        """Confirm an order after validation"""
        validation_errors = self.validate_order(order)
        if validation_errors:
            raise OrderValidationError(f"Order validation failed: {', '.join(validation_errors)}")
        
        order.status = OrderStatus.CONFIRMED
        return True
    
    def cancel_order(self, order: Order) -> bool:
        """Cancel an order"""
        if order.status in [OrderStatus.PROCESSING, OrderStatus.COMPLETED]:
            return False  # Cannot cancel orders that are already processing or completed
        
        order.status = OrderStatus.CANCELLED
        return True
    
    def get_order_summary(self, order: Order) -> Dict:
        """Get a formatted summary of the order"""
        return {
            "order_id": id(order),  # Use object id as simple identifier
            "status": order.status.value,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "items": [
                {
                    "pizza_name": item.pizza.name.title(),
                    "description": item.pizza.description,
                    "quantity": item.quantity,
                    "unit_price": item.pizza.price,
                    "total_price": item.total_price,
                    "special_instructions": item.special_instructions
                }
                for item in order.items
            ],
            "total_amount": order.total_amount,
            "item_count": len(order.items)
        }
    
    def calculate_estimated_delivery_time(self, order: Order) -> Optional[datetime]:
        """Calculate estimated delivery time (simple implementation)"""
        if not order.items:
            return None
        
        # Base preparation time: 15 minutes + 3 minutes per pizza
        base_time = 15
        prep_time = base_time + (len(order.items) * 3)
        
        # Add delivery time: 20-30 minutes
        delivery_time = 25
        
        total_minutes = prep_time + delivery_time
        
        if order.created_at:
            from datetime import timedelta
            return order.created_at + timedelta(minutes=total_minutes)
        
        return None
    
    def get_order_history(self) -> List[Order]:
        """Get order history"""
        return self._order_history.copy()
    
    def archive_order(self, order: Order):
        """Move order to history"""
        if order not in self._order_history:
            self._order_history.append(order)

class OrderRecommendationService:
    """Service for order-based recommendations"""
    
    def __init__(self, order_service: OrderService):
        self.order_service = order_service
    
    def suggest_add_ons(self, order: Order) -> List[str]:
        """Suggest add-ons based on current order"""
        suggestions = []
        
        # Basic suggestions based on order content
        if not order.items:
            return suggestions
        
        has_meat = any('meat' in item.pizza.name.lower() or 
                      any(ingredient in ['pepperoni', 'sausage', 'bacon', 'ham'] 
                          for ingredient in item.pizza.ingredients)
                      for item in order.items)
        
        has_veggie = any('veggie' in item.pizza.name.lower() or
                        any(ingredient in ['peppers', 'mushrooms', 'onions']
                            for ingredient in item.pizza.ingredients)
                        for item in order.items)
        
        if has_meat and not has_veggie:
            suggestions.append("Add a veggie pizza for balance")
        
        if len(order.items) == 1:
            suggestions.append("Consider adding a side or drink")
        
        if order.total_amount < 20:
            suggestions.append("Add another pizza for better value")
        
        return suggestions
    
    def calculate_savings_opportunities(self, order: Order) -> Dict:
        """Calculate potential savings or deals"""
        opportunities = {
            "potential_savings": 0.0,
            "suggestions": []
        }
        
        if len(order.items) >= 2:
            opportunities["suggestions"].append("2+ pizzas qualify for 10% discount")
            opportunities["potential_savings"] = order.total_amount * 0.1
        
        if order.total_amount >= 30:
            opportunities["suggestions"].append("Orders over $30 get free delivery")
        
        return opportunities