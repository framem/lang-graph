from typing import TypedDict, Optional, List, Dict, Any, Literal
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ConversationStatus(Enum):
    """Enum for conversation states"""
    INITIAL = "initial"
    PROCESSING_ORDER = "processing_order"
    AWAITING_CONTINUATION = "awaiting_continuation"
    COMPLETED = "completed"
    EXITED = "exited"

class OrderStatus(Enum):
    """Enum for order states"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class Pizza:
    """Pizza data model"""
    name: str
    description: str
    ingredients: List[str]
    price: float
    size: str = "medium"
    
    def __str__(self) -> str:
        return f"{self.name.title()} ({self.size}): {self.description} - ${self.price}"
    
    def __hash__(self) -> int:
        """Make Pizza hashable for use in sets and dict keys"""
        return hash((self.name, tuple(self.ingredients), self.price, self.size))
    
    def __eq__(self, other) -> bool:
        """Define equality for Pizza objects"""
        if not isinstance(other, Pizza):
            return False
        return (self.name == other.name and 
                self.ingredients == other.ingredients and
                self.price == other.price and
                self.size == other.size)

@dataclass 
class OrderItem:
    """Individual order item"""
    pizza: Pizza
    quantity: int = 1
    special_instructions: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    @property
    def total_price(self) -> float:
        return self.pizza.price * self.quantity

@dataclass
class Order:
    """Complete order information"""
    items: List[OrderItem]
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = None
    total_amount: float = 0.0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        self.calculate_total()
    
    def calculate_total(self):
        """Calculate total order amount"""
        self.total_amount = sum(item.total_price for item in self.items)
    
    def add_item(self, item: OrderItem):
        """Add item to order"""
        self.items.append(item)
        self.calculate_total()

@dataclass
class ConversationContext:
    """Context for the current conversation"""
    turn_count: int = 0
    status: ConversationStatus = ConversationStatus.INITIAL
    last_agent: Optional[str] = None
    conversation_history: List[str] = None
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
    
    def add_turn(self, user_input: str, agent_name: str):
        """Add a conversation turn"""
        self.turn_count += 1
        self.last_agent = agent_name
        self.conversation_history.append(f"Turn {self.turn_count} ({agent_name}): {user_input}")

class PizzaState(TypedDict):
    """Enhanced state management for pizza ordering workflow"""
    # Core conversation state
    user_input: str
    conversation_context: ConversationContext
    
    # Legacy fields for backward compatibility  
    wants_pizza: Optional[bool]
    pizza_request: Optional[str]
    found_pizza: Optional[str]
    exit_reason: Optional[str]
    continue_ordering: Optional[bool]
    
    # Enhanced state fields
    current_order: Optional[Order]
    matched_pizzas: Optional[List[Pizza]]
    selected_pizza: Optional[Pizza]
    validation_errors: Optional[List[str]]
    
    # Session management
    session_id: Optional[str]
    user_preferences: Optional[Dict[str, Any]]
    
    # Workflow control
    next_action: Optional[Literal["triage", "pizza_search", "order_confirmation", "continuation", "exit"]]
    requires_user_input: bool
    
    # Error handling
    last_error: Optional[str]
    retry_count: int

class StateManager:
    """State management utility class"""
    
    @staticmethod
    def create_initial_state(user_input: str, session_id: str = None) -> PizzaState:
        """Create initial state for a new conversation"""
        return {
            "user_input": user_input,
            "conversation_context": ConversationContext(),
            "wants_pizza": None,
            "pizza_request": None,
            "found_pizza": None,
            "exit_reason": None,
            "continue_ordering": None,
            "current_order": None,
            "matched_pizzas": None,
            "selected_pizza": None,
            "validation_errors": None,
            "session_id": session_id,
            "user_preferences": {},
            "next_action": "triage",
            "requires_user_input": False,
            "last_error": None,
            "retry_count": 0
        }
    
    @staticmethod
    def transition_to_pizza_search(state: PizzaState, pizza_request: str) -> PizzaState:
        """Transition state to pizza search mode"""
        state["wants_pizza"] = True
        state["pizza_request"] = pizza_request
        state["conversation_context"].status = ConversationStatus.PROCESSING_ORDER
        state["next_action"] = "pizza_search"
        return state
    
    @staticmethod
    def transition_to_continuation(state: PizzaState) -> PizzaState:
        """Transition state to continuation mode"""
        state["conversation_context"].status = ConversationStatus.AWAITING_CONTINUATION
        state["next_action"] = "continuation"
        state["requires_user_input"] = True
        return state
    
    @staticmethod
    def transition_to_exit(state: PizzaState, reason: str) -> PizzaState:
        """Transition state to exit mode"""
        state["wants_pizza"] = False
        state["exit_reason"] = reason
        state["conversation_context"].status = ConversationStatus.EXITED
        state["next_action"] = "exit"
        return state
    
    @staticmethod
    def add_error(state: PizzaState, error: str) -> PizzaState:
        """Add an error to the state"""
        if state["validation_errors"] is None:
            state["validation_errors"] = []
        state["validation_errors"].append(error)
        state["last_error"] = error
        state["retry_count"] += 1
        return state
    
    @staticmethod
    def clear_errors(state: PizzaState) -> PizzaState:
        """Clear errors from state"""
        state["validation_errors"] = None
        state["last_error"] = None
        state["retry_count"] = 0
        return state
    
    @staticmethod
    def reset_for_new_order(state: PizzaState) -> PizzaState:
        """Reset state fields for a new pizza order while preserving context"""
        state["pizza_request"] = None
        state["found_pizza"] = None
        state["matched_pizzas"] = None
        state["selected_pizza"] = None
        state["continue_ordering"] = None
        state["next_action"] = "triage"
        state["requires_user_input"] = True
        StateManager.clear_errors(state)
        return state

# Type aliases for better readability
AgentResponse = Dict[str, Any]
WorkflowResult = Dict[str, Any]