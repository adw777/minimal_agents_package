# MinimalAgents Framework: Usage Guide

This guide covers how to use the MinimalAgents framework to build and run LLM-powered agents with custom tools.

## Table of Contents
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Creating Custom Tools](#creating-custom-tools)
- [LLM Providers](#llm-providers)
- [Advanced Usage](#advanced-usage)
- [Environment Setup](#environment-setup)
- [Examples](#examples)

## Installation

### From PyPI (Once Published)
```bash
pip install minimal-agents
```

### From Source
```bash
# Clone the repository
git clone https://github.com/yourusername/minimal_agents.git
cd minimal_agents

# Install in development mode
pip install -e .

# Install extras (optional)
pip install -e ".[google,tools,development]"
```

## Basic Usage

Here's a simple example of creating and running an agent:

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
    verbose=True  # Set to True for detailed logs
)

# Run a query
result = agent.run("Calculate the factorial of 5 using Python")
print(result)
```

## Creating Custom Tools

Creating your own tools is straightforward:

```python
from minimal_agents.tools.base import Tool

class WeatherTool(Tool):
    """Tool for getting weather information."""
    
    name: str = "Weather Tool"
    description: str = "Get current weather for a location. Input should be a city name."
    
    def run(self, input_text: str) -> str:
        """Get weather for the specified location."""
        location = input_text.strip()
        
        # In a real implementation, you would call a weather API here
        # This is just a placeholder example
        return f"Weather for {location}: 72°F, Partly Cloudy"

# Usage:
weather_tool = WeatherTool()
agent.tools.append(weather_tool)
```

## LLM Providers

### OpenAI

```python
from minimal_agents.llm.openai import OpenAIProvider

openai_llm = OpenAIProvider(
    model="gpt-4o",        # Model name
    temperature=0.4,       # Creativity (0.0 to 1.0)
    max_tokens=1024,       # Max output tokens (optional)
    api_key="your_api_key" # Alternatively, set OPENAI_API_KEY env var
)
```

### Implementing a Gemini Provider

Here's how you could implement a Google Gemini provider:

```python
import os
from typing import List, Optional
from google import genai

from minimal_agents.llm.base import LLMProvider

class GeminiProvider(LLMProvider):
    """Google Gemini API provider for language models."""
    
    model: str = "gemini-1.5-pro"
    temperature: float = 0.4
    max_tokens: Optional[int] = None
    api_key: Optional[str] = None
    client: Optional[Any] = None
    
    def __init__(
        self,
        model: str = "gemini-1.5-pro",
        temperature: float = 0.4,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """Initialize the Gemini provider."""
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("Gemini API key is required.")
        
        # Initialize the client
        genai.configure(api_key=self.api_key)
    
    def generate(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Generate text using Gemini API."""
        model = genai.GenerativeModel(self.model)
        
        generation_config = {
            "temperature": self.temperature,
        }
        
        if self.max_tokens:
            generation_config["max_output_tokens"] = self.max_tokens
        
        if stop:
            generation_config["stop_sequences"] = stop
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text
    
    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "gemini"
    
    @property
    def model_name(self) -> str:
        """Get the model name."""
        return self.model
```

## Advanced Usage

### Adding Multiple Tools

```python
from minimal_agents.tools.code.python_repl import PythonREPL
from minimal_agents.tools.web.search import WebSearch
from your_custom_tools import CustomTool1, CustomTool2

# Create tools
tools = [
    PythonREPL(),
    WebSearch(api_key="your_search_api_key"),
    CustomTool1(),
    CustomTool2()
]

# Create agent with multiple tools
agent = MinimalAgent(llm=llm, tools=tools)
```

### Customizing System Prompts

You can customize how the agent behaves by modifying its system prompt:

```python
custom_system_prompt = """
You are an AI assistant specialized in data analysis.
When you receive input, first determine if it's a data analysis task.
If it is, use the appropriate tools to analyze the data.
Otherwise, respond conversationally.
"""

agent = MinimalAgent(
    llm=llm,
    tools=tools,
    system_prompt=custom_system_prompt
)
```

## Environment Setup

Create a `.env` file in your project root with your API keys:

```
# .env file
OPENAI_API_KEY=sk-your-openai-key
SEARCH_API_KEY=your-search-api-key
GEMINI_API_KEY=your-gemini-key
```

Then load it in your code:

```python
from dotenv import load_dotenv
load_dotenv()
```

## Examples

### Interactive Chat Agent

```python
from minimal_agents.agent import MinimalAgent
from minimal_agents.llm.openai import OpenAIProvider
from minimal_agents.tools.code.python_repl import PythonREPL

# Initialize agent
llm = OpenAIProvider(model="gpt-4o")
agent = MinimalAgent(llm=llm, tools=[PythonREPL()], verbose=True)

# Interactive chat loop
print("Chat with the agent (type 'exit' to quit)")
while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ["exit", "quit", "bye"]:
        break
    
    response = agent.run(user_input)
    print(f"\nAgent: {response}")
```

### File Processing Agent

```python
from minimal_agents.agent import MinimalAgent
from minimal_agents.llm.openai import OpenAIProvider
from minimal_agents.tools.code.python_repl import PythonREPL
from minimal_agents.tools.data.file_reader import FileReader

# Initialize agent with file processing tools
llm = OpenAIProvider(model="gpt-4o")
tools = [PythonREPL(), FileReader()]
agent = MinimalAgent(llm=llm, tools=tools)

# Process a file
query = "Read data.csv and calculate the average of the 'Price' column"
result = agent.run(query)
print(result)
```

For more examples, see the `examples/` directory in the repository.