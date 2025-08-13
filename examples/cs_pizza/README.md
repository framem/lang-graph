# CS Pizza Example

This example demonstrates a LangGraph workflow for a pizza ordering system with triage routing.

## Architecture

The workflow follows a simple two-agent pattern:

1. **Triage Agent**: Determines if the user wants pizza or wants to exit
2. **Pizza Agent**: Finds matching pizza based on user preferences

## Files

- `state.py`: Defines the `PizzaState` TypedDict with workflow state
- `nodes.py`: Implements the core agent logic (TriageAgent, PizzaAgent)
- `edges.py`: Contains routing logic between agents
- `agents.py`: LLM-based agents (requires Ollama setup)
- `main.py`: Main workflow setup and execution
- `test_structure.py`: Simple test without external dependencies
- `workflow_graph.mmd`: Mermaid diagram of the workflow

## Workflow Flow

1. **Start** → **Triage Agent**
2. **Triage Agent** evaluates user input:
   - If user wants pizza → route to **Pizza Agent**
   - If user doesn't want pizza → **Exit**
3. **Pizza Agent** finds matching pizza → **Exit**

## Available Pizzas

- **Margherita**: tomato, mozzarella, basil
- **Pepperoni**: tomato, mozzarella, pepperoni
- **Hawaiian**: tomato, mozzarella, ham, pineapple
- **Veggie Supreme**: tomato, mozzarella, peppers, mushrooms, onions
- **Meat Lovers**: tomato, mozzarella, pepperoni, sausage, bacon

## Usage

### Basic Test (No Dependencies)
```bash
python3 test_structure.py
```

### Full LangGraph Execution (Requires Dependencies)
```bash
# Ensure you have Ollama running with mistral:latest model
python3 main.py
```

## Example Interactions

**Scenario 1: User wants pizza**
- Input: "I want a pepperoni pizza"
- Triage: Routes to pizza_agent
- Pizza Agent: Finds "Pepperoni: Pepperoni Pizza - tomato, mozzarella, pepperoni"

**Scenario 2: User doesn't want pizza**
- Input: "No thanks, goodbye"
- Triage: Routes to exit
- Exit reason: "User doesn't want pizza"

**Scenario 3: Ambiguous request**
- Input: "I want something with vegetables"
- Triage: Routes to pizza_agent (assumes food request)
- Pizza Agent: Recommends default or matches based on keywords

## Key Features

- **Simple Triage Logic**: Keyword-based routing for demonstration
- **Pizza Matching**: Finds pizzas based on ingredients or name matching
- **Graceful Exit**: Handles users who don't want pizza
- **LangGraph Integration**: Follows standard LangGraph patterns
- **Tool Integration**: Pizza agent uses tool-like logic for matching

This example demonstrates how to create a simple but effective routing system using LangGraph's conditional edges and state management.