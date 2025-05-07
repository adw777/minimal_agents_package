# MinimalAgents

A lightweight framework for building LLM-powered agents with tools.

## Overview

MinimalAgents provides a simple, flexible way to create AI agents that can use various tools to solve problems. The framework focuses on:

- **Minimalism**: Clean interfaces with minimal abstractions
- **Flexibility**: Easy to extend with new LLMs and tools
- **Pragmatism**: Built for practical use cases

## Features

- 🔄 **Unified Tool Interface**: Consistent API for all tools
- 🧠 **Multiple LLM Support**: Works with various language model providers
- 🛠️ **Built-in Tools**: Comes with several useful tools ready to use
- 🧩 **Extensible**: Easy to create custom tools and LLM providers
- 📝 **Conversation Management**: Handles context and multi-step reasoning

## Installation

```bash
# Basic installation
pip install minimal-agents

# With all dependencies
pip install minimal-agents[all]
```

## Quick Start

```python
from minimal_agents.agent import MinimalAgent
from minimal_agents.llm.openai import OpenAIProvider
from minimal_agents.tools.code.python_repl import PythonREPL

# Initialize an LLM provider
llm = OpenAIProvider(
    model="gpt-4o",
    temperature=0.4
)

# Create tools
tools = [PythonREPL()]

# Create the agent
agent = MinimalAgent(
    llm=llm,
    tools=tools,
    verbose=True
)

# Run a query
result = agent.run("Calculate the factorial of 5 using Python")
print(result)
```

## Creating Custom Tools

```python
from minimal_agents.tools.base import Tool

class WeatherTool(Tool):
    """Tool for getting weather information."""
    
    name: str = "Weather Tool"
    description: str = "Get current weather for a location. Input should be a city name."
    
    def run(self, input_text: str) -> str:
        """Get weather for the specified location."""
        location = input_text.strip()
        
        # Implement your weather API call here
        return f"Weather for {location}: 72°F, Partly Cloudy"
```

## Documentation

For more detailed documentation, see the [Usage Guide](docs/usage_guide.md) and [API Reference](docs/api_reference.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.