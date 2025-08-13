# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains multiple independent LangChain/LangGraph examples demonstrating different agent architectures and workflows. Each example is self-contained with its own dependencies and execution model.

## Project Structure

- **examples/**: Independent examples, each with their own virtual environment
  - **01 - langChain/**: Basic LangChain prompt-chain example using Ollama
  - **02 - langGraph/**: Simple StateGraph with two sequential nodes
  - **04 - StateGraph/**: Lottery simulation with conditional edges and loops
  - **cs airline/**: Customer service agent with triage and flight lookup
  - **cs network/**: Web-based assistant with Flask/SocketIO interface
  - **cs pizza/**: Complex pizza ordering system with multi-agent routing

## Development Commands

**Environment Setup (per example):**
```bash
cd "examples/[example-name]"
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows
pip install -r ../../requirements.txt
```

**Running Examples:**
```bash
# Basic examples
python main.py

# Pizza example with tests
python test_structure.py  # No external dependencies
python main.py            # Full workflow (requires Ollama)

# Network example web server
python web_server.py      # Starts Flask server on http://localhost:5000
```

**LLM Requirements:**
Most examples require Ollama with mistral model:
```bash
# Install Ollama: https://ollama.ai
ollama pull mistral
```

## Architecture Patterns

### State Management
Examples use TypedDict-based state with different complexity levels:
- **Simple**: Basic string fields (langChain, langGraph examples)
- **Structured**: Enums and dataclasses (cs pizza with ConversationStatus, OrderStatus)
- **Hybrid**: Mixed approaches for backward compatibility

### Workflow Patterns
1. **Linear Chain**: `01 - langChain` (prompt ’ LLM ’ parser)
2. **Sequential Nodes**: `02 - langGraph` (node_1 ’ node_2 ’ END)  
3. **Conditional Routing**: `04 - StateGraph`, `cs pizza` (conditional edges based on state)
4. **Triage Pattern**: `cs airline`, `cs pizza` (entry triage ’ specialized agents)
5. **Web Integration**: `cs network` (LangGraph + Flask/SocketIO)

### Agent Architecture
**Multi-Agent Systems**: Examples like `cs pizza` demonstrate:
- **TriageAgent**: Routes user input to appropriate handler
- **PizzaAgent**: Handles pizza-specific logic and matching
- **ContinuationAgent**: Manages conversation flow and follow-ups

### File Organization Patterns
Complex examples follow modular structure:
- `state.py`: State definitions and management utilities
- `nodes.py`: Core agent logic and node functions  
- `edges.py`: Routing logic between nodes
- `agents.py`: LLM-based agent implementations
- `services/`: Business logic services (pizza catalog, orders, etc.)
- `main.py`: Workflow assembly and execution

## Mermaid Diagram Generation

All LangGraph examples auto-generate workflow diagrams:
```python
mermaid_code = app.get_graph().draw_mermaid()
with open("workflow_graph.mmd", "w") as f:
    f.write(mermaid_code)
```

## Dependencies

Core dependencies in requirements.txt:
- **langchain==0.3.27**: Base framework
- **langgraph==0.6.4**: State graph workflows
- **langchain-ollama**: Local LLM integration
- **flask/flask_socketio**: Web interface (cs network)
- **streamlit**: Alternative web UI option
- **graphviz**: Diagram rendering support

## Key Implementation Details

### State Transitions
Use StateManager utility class for clean state transitions:
```python
StateManager.transition_to_pizza_search(state, pizza_request)
StateManager.transition_to_exit(state, reason)
```

### Error Handling
Consistent error handling with retry logic and validation_errors field in state.

### Session Management  
Advanced examples (cs pizza) include session management with ConversationService for multi-turn conversations.