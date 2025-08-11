# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a minimal Docker-based development environment configured for a project named "langGraph". The repository contains:

- `docker-compose.yml`: Defines a Docker service using the `nordwind/claude:latest` image
- `langGraph.iml`: IntelliJ IDEA module configuration file

## Docker Environment

The project is configured to run within a Docker container:

- **Service name**: `coding-agent`
- **Container name**: `langGraph_code_assistant`
- **Image**: `nordwind/claude:latest`
- **Volume mapping**: Current directory mounted to `/app` in container

## Development Commands

**Requirements**: Python 3.9 or 3.10 (recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your OpenAI API key OR configure Ollama

# For Ollama setup:
# 1. Install Ollama: https://ollama.ai
# 2. Pull a model: ollama pull llama3.1:8b
# 3. Set LLM_PROVIDER=ollama in .env

# Run the airline support assistant
python main.py
```

## Project Structure

- `main.py`: Core LangChain agent with flight status and policy tools
- `data/flights.json`: Sample flight data
- `data/policies.txt`: Airline policy knowledge base
- `requirements.txt`: Python dependencies

## Architecture

Simple LangChain agent setup with:
- **Agent**: ZERO_SHOT_REACT_DESCRIPTION for reasoning
- **Tools**: Flight status lookup, policy information retrieval
- **LLM**: GPT-3.5-turbo for conversation and reasoning
- **Data**: JSON-based flight database and text-based policies