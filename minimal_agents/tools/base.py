"""Base tool interface for all tools in the MinimalAgents framework."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class Tool(BaseModel, ABC):
    """Base class for all MinimalAgents tools.
    
    Every tool must implement:
    1. A name (displayed to the LLM)
    2. A description (helping the LLM understand when to use the tool)
    3. A run method that executes the tool functionality
    """
    
    name: str = Field(..., description="The name of the tool")
    description: str = Field(..., description="A description of what the tool does and when to use it")
    
    @abstractmethod
    def run(self, input_text: str) -> str:
        """Execute the tool with the given input.
        
        Args:
            input_text: The text input to the tool
            
        Returns:
            The tool's output as a string
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the tool to a dictionary format for agent consumption.
        
        Returns:
            A dictionary with the tool's name and description
        """
        return {
            "name": self.name,
            "description": self.description
        }