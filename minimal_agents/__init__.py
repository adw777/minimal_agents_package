"""MinimalAgents: A lightweight framework for LLM-based agents with tools.

This package provides a simple way to create LLM-powered agents 
that can use various tools to complete tasks.
"""

__version__ = "0.1.0"

from minimal_agents.agent import MinimalAgent
from minimal_agents.tools.base import Tool

# Import LLM providers
from minimal_agents.llm.base import LLMProvider
from minimal_agents.llm.openai import OpenAIProvider

# Import common tools
from minimal_agents.tools.code.python_repl import PythonREPL
from minimal_agents.tools.web.search import WebSearch

__all__ = [
    "MinimalAgent",
    "Tool",
    "LLMProvider", 
    "OpenAIProvider",
    "PythonREPL",
    "WebSearch"
]