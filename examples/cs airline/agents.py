from abc import ABC, abstractmethod

from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from state import CustomerState
import inspect
import json
import random


# Define the base class for tasks
class AgentBase(ABC):
    def __init__(self, state: CustomerState):
        self.state = state

    @abstractmethod
    def get_prompt_template(self) -> str:
        pass

    def execute(self) -> CustomerState:

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
            "flight_number": self.state["flight_number"],
            # "use_tool": self.state["use_tool"],
            # "tools_list": self.state["tools_list"]
        })
        data = json.loads(generation)
        # self.state["use_tool"] = data.get("use_tool", False)
        # self.state["tool_exec"] = generation

        # self.state["history"] += "\n" + generation
        # self.state["history"] = clip_history(self.state["history"])

        return self.state


# Define agents
class ChatAgent(AgentBase):
    def get_prompt_template(self) -> str:
        return """
            Available tools: 
            Question: 
            As ChatAgent, decide if we need to use a tool or not.
            If we don't need a tool, just reply; otherwise, let the ToolAgent handle it.
        """

class ToolAgent(AgentBase):
    def get_prompt_template(self) -> str:
        return """
            History: 
            Available tools: 
            Based on the history, choose the appropriate tool and arguments in the format:
            {{"function": "<function>", "args": [<arg1>,<arg2>, ...]}}
        """
