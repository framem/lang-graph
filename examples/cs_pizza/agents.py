from abc import ABC, abstractmethod
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from state import PizzaState
import json

# Define the base class for agents
class AgentBase(ABC):
    def __init__(self, state: PizzaState):
        self.state = state

    @abstractmethod
    def get_prompt_template(self) -> str:
        pass

    def execute(self) -> PizzaState:
        # Define the prompt template
        template = self.get_prompt_template()
        prompt = PromptTemplate.from_template(template)
        llm = ChatOllama(
            model="mistral:latest",
            base_url="http://127.0.0.1:11434",
            temperature=0.1,
            timeout=60
        )
        llm_chain = prompt | llm | StrOutputParser()
        generation = llm_chain.invoke({
            "user_input": self.state["user_input"],
            "pizza_request": self.state.get("pizza_request", ""),
        })
        
        # For this simple example, we'll use the generation as-is
        # In a more complex scenario, you might parse JSON responses
        print(f"Agent response: {generation}")
        
        return self.state

# Pizza finding tool function
def find_pizza_tool(pizza_request: str) -> str:
    """Tool to find matching pizza based on user request"""
    available_pizzas = {
        'margherita': 'Classic Margherita - tomato, mozzarella, basil',
        'pepperoni': 'Pepperoni Pizza - tomato, mozzarella, pepperoni', 
        'hawaiian': 'Hawaiian Pizza - tomato, mozzarella, ham, pineapple',
        'veggie': 'Veggie Supreme - tomato, mozzarella, peppers, mushrooms, onions',
        'meat': 'Meat Lovers - tomato, mozzarella, pepperoni, sausage, bacon'
    }
    
    pizza_request_lower = pizza_request.lower()
    for pizza_name, description in available_pizzas.items():
        if pizza_name in pizza_request_lower or any(ingredient.lower() in pizza_request_lower for ingredient in description.split()):
            return f"{pizza_name.title()}: {description}"
    
    return "Margherita: Classic Margherita - tomato, mozzarella, basil (default recommendation)"

# Define the pizza finding tool
pizza_finder_tool = Tool(
    name="find_pizza",
    description="Find a matching pizza based on user preferences",
    func=find_pizza_tool
)

# Define agents
class TriageAgentLLM(AgentBase):
    def get_prompt_template(self) -> str:
        return """
        You are a triage agent for a pizza ordering system.
        User input: "{user_input}"
        
        Determine if the user wants to order pizza or wants to exit.
        Respond with JSON in this format:
        {{"wants_pizza": true/false, "reason": "explanation"}}
        
        If the user mentions pizza, food, hungry, order, or similar terms, set wants_pizza to true.
        If the user says no, exit, quit, bye, or similar terms, set wants_pizza to false.
        """

class PizzaAgentLLM(AgentBase):
    def get_prompt_template(self) -> str:
        return """
        You are a pizza recommendation agent.
        User's pizza request: "{pizza_request}"
        
        Available tools: find_pizza - finds matching pizza based on preferences
        
        Use the find_pizza tool to find the best matching pizza for the user's request.
        Then provide a friendly response recommending the pizza.
        
        Available pizzas:
        - Margherita: tomato, mozzarella, basil
        - Pepperoni: tomato, mozzarella, pepperoni
        - Hawaiian: tomato, mozzarella, ham, pineapple  
        - Veggie Supreme: tomato, mozzarella, peppers, mushrooms, onions
        - Meat Lovers: tomato, mozzarella, pepperoni, sausage, bacon
        """