"""Example usage of MinimalAgents framework with basic tools."""

import os
from dotenv import load_dotenv

from minimal_agents.agent import MinimalAgent
from minimal_agents.llm.openai import OpenAIProvider
from minimal_agents.tools.code.python_repl import PythonREPL
from minimal_agents.tools.web.search import WebSearch

# Load environment variables from .env file
load_dotenv()

def main():
    """Run a simple agent example."""
    
    # Create LLM provider
    llm = OpenAIProvider(
        model="gpt-4o",  # You can change this to any OpenAI model
        temperature=0.4,
        max_tokens=1024
    )
    
    # Initialize tools
    tools = [
        PythonREPL(),  # Python code execution tool
        # Uncomment if you have a search API key
        # WebSearch(search_engine="serp")
    ]
    
    # Create agent
    agent = MinimalAgent(
        llm=llm,
        tools=tools,
        verbose=True
    )
    
    print("=" * 50)
    print("MinimalAgents Example")
    print("=" * 50)
    print("Available tools:")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
    print("\nType 'exit', 'quit', or 'bye' to end the conversation.")
    print("=" * 50)
    
    # Simple chat loop
    while True:
        # Get user input
        query = input("\nYou: ")
        
        # Check for exit command
        if query.lower() in ["exit", "quit", "bye"]:
            print("\nGoodbye!")
            break
            
        # Run the agent
        try:
            result = agent.run(query)
            print(f"\nAgent: {result}")
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()