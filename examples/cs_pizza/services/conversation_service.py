"""
Conversation management service.
Handles conversation flow, context management, and session state.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from state import ConversationContext, ConversationStatus, PizzaState, StateManager
import uuid

class ConversationService:
    """Service for managing conversation state and flow"""
    
    def __init__(self):
        self._sessions: Dict[str, PizzaState] = {}
        self._conversation_history: Dict[str, List[Dict]] = {}
    
    def create_session(self, initial_input: str) -> tuple[str, PizzaState]:
        """Create a new conversation session"""
        session_id = str(uuid.uuid4())
        state = StateManager.create_initial_state(initial_input, session_id)
        
        # Initialize conversation context with first turn
        state["conversation_context"].add_turn(initial_input, "user")
        
        self._sessions[session_id] = state
        self._conversation_history[session_id] = []
        
        self._log_conversation_turn(session_id, initial_input, "user", "session_start")
        
        return session_id, state
    
    def get_session_state(self, session_id: str) -> Optional[PizzaState]:
        """Get the current state for a session"""
        return self._sessions.get(session_id)
    
    def update_session_state(self, session_id: str, state: PizzaState) -> bool:
        """Update the session state"""
        if session_id in self._sessions:
            self._sessions[session_id] = state
            return True
        return False
    
    def add_user_input(self, session_id: str, user_input: str) -> bool:
        """Add new user input to existing session"""
        if session_id not in self._sessions:
            return False
        
        state = self._sessions[session_id]
        state["user_input"] = user_input
        state["conversation_context"].add_turn(user_input, "user")
        
        self._log_conversation_turn(session_id, user_input, "user", 
                                  state["conversation_context"].status.value)
        
        return True
    
    def transition_conversation_status(self, session_id: str, new_status: ConversationStatus) -> bool:
        """Transition conversation to new status"""
        if session_id not in self._sessions:
            return False
        
        state = self._sessions[session_id]
        old_status = state["conversation_context"].status
        state["conversation_context"].status = new_status
        
        self._log_status_transition(session_id, old_status, new_status)
        
        return True
    
    def should_continue_conversation(self, session_id: str) -> bool:
        """Determine if conversation should continue based on state"""
        if session_id not in self._sessions:
            return False
        
        state = self._sessions[session_id]
        context = state["conversation_context"]
        
        # Don't continue if explicitly exited
        if context.status == ConversationStatus.EXITED:
            return False
        
        # Don't continue if too many turns (prevent infinite loops)
        if context.turn_count > 20:
            self.transition_conversation_status(session_id, ConversationStatus.EXITED)
            return False
        
        # Continue if requires user input or is processing
        if state.get("requires_user_input", False):
            return True
        
        if context.status in [ConversationStatus.PROCESSING_ORDER, 
                             ConversationStatus.AWAITING_CONTINUATION]:
            return True
        
        return False
    
    def get_conversation_summary(self, session_id: str) -> Optional[Dict]:
        """Get a summary of the conversation"""
        if session_id not in self._sessions:
            return None
        
        state = self._sessions[session_id]
        context = state["conversation_context"]
        history = self._conversation_history.get(session_id, [])
        
        return {
            "session_id": session_id,
            "status": context.status.value,
            "turn_count": context.turn_count,
            "last_agent": context.last_agent,
            "has_order": state.get("current_order") is not None,
            "conversation_length": len(history),
            "started_at": history[0]["timestamp"] if history else None,
            "last_activity": history[-1]["timestamp"] if history else None
        }
    
    def get_context_for_agent(self, session_id: str, agent_name: str) -> Dict[str, Any]:
        """Get relevant context for a specific agent"""
        if session_id not in self._sessions:
            return {}
        
        state = self._sessions[session_id]
        context = state["conversation_context"]
        
        base_context = {
            "session_id": session_id,
            "turn_count": context.turn_count,
            "conversation_status": context.status.value,
            "user_input": state["user_input"],
            "last_agent": context.last_agent
        }
        
        # Add agent-specific context
        if agent_name.lower() == "triage":
            base_context.update({
                "is_new_session": context.turn_count <= 1,
                "previous_exit_reason": state.get("exit_reason")
            })
        
        elif agent_name.lower() == "pizza":
            base_context.update({
                "pizza_request": state.get("pizza_request"),
                "current_order": state.get("current_order"),
                "previous_matches": state.get("matched_pizzas"),
                "validation_errors": state.get("validation_errors")
            })
        
        elif agent_name.lower() == "continuation":
            base_context.update({
                "current_order": state.get("current_order"),
                "found_pizza": state.get("found_pizza"),
                "order_history": self._get_order_history_for_session(session_id)
            })
        
        return base_context
    
    def _log_conversation_turn(self, session_id: str, content: str, 
                              speaker: str, status: str):
        """Log a conversation turn"""
        if session_id not in self._conversation_history:
            self._conversation_history[session_id] = []
        
        self._conversation_history[session_id].append({
            "timestamp": datetime.now().isoformat(),
            "speaker": speaker,
            "content": content,
            "status": status,
            "turn": len(self._conversation_history[session_id]) + 1
        })
    
    def _log_status_transition(self, session_id: str, old_status: ConversationStatus, 
                              new_status: ConversationStatus):
        """Log status transitions"""
        self._log_conversation_turn(
            session_id,
            f"Status transition: {old_status.value} -> {new_status.value}",
            "system",
            new_status.value
        )
    
    def _get_order_history_for_session(self, session_id: str) -> List[str]:
        """Get order history for a session"""
        if session_id not in self._conversation_history:
            return []
        
        history = self._conversation_history[session_id]
        orders = []
        
        for entry in history:
            if "found_pizza" in entry.get("content", "") or "order" in entry.get("content", "").lower():
                orders.append(entry["content"])
        
        return orders
    
    def cleanup_session(self, session_id: str) -> bool:
        """Clean up session data"""
        removed = False
        
        if session_id in self._sessions:
            del self._sessions[session_id]
            removed = True
        
        if session_id in self._conversation_history:
            del self._conversation_history[session_id]
        
        return removed
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        active_sessions = []
        
        for session_id, state in self._sessions.items():
            if state["conversation_context"].status != ConversationStatus.EXITED:
                active_sessions.append(session_id)
        
        return active_sessions
    
    def detect_continuation_intent(self, user_input: str, context: ConversationContext) -> bool:
        """Detect if user wants to continue ordering based on context"""
        import re
        
        input_lower = user_input.lower()
        words = input_lower.split()
        
        # Explicit continuation keywords (use word boundaries)
        continue_keywords = ['another', 'more', 'yes', 'continue', 'again', 'next', 'add', 'also']
        end_keywords = ['no', 'done', 'finish', 'complete', 'stop', 'thanks']
        
        # Check for explicit end signals first (using word boundaries)
        for keyword in end_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', input_lower):
                return False
        
        # Special case for "that's all"
        if "that's all" in input_lower:
            return False
        
        # Check for continuation signals (using word boundaries)
        for keyword in continue_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', input_lower):
                return True
        
        # Context-based detection
        if context.status == ConversationStatus.AWAITING_CONTINUATION:
            # If we're specifically waiting for continuation input
            # Check for pizza-related keywords that suggest continuation
            pizza_keywords = ['pizza', 'margherita', 'pepperoni', 'hawaiian', 'veggie', 'meat']
            if any(keyword in input_lower for keyword in pizza_keywords):
                return True
            # Default to ending unless explicit continuation
            return False
        
        # If user mentions specific pizza items, likely wants to continue
        pizza_keywords = ['pizza', 'margherita', 'pepperoni', 'hawaiian', 'veggie', 'meat']
        if any(keyword in input_lower for keyword in pizza_keywords):
            return True
        
        # Default to not continuing for ambiguous input
        return False