"""Base LLM provider interface for the MinimalAgents framework."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class LLMProvider(ABC):
    """Abstract base class for LLM providers.
    
    This interface should be implemented by all language model providers
    in the MinimalAgents framework.
    """
    
    @abstractmethod
    def generate(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Generate text from a prompt.
        
        Args:
            prompt: The prompt to send to the language model
            stop: Optional list of strings that will stop generation if encountered
            
        Returns:
            The generated text as a string
        """
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the LLM provider."""
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the name of the specific model being used."""
        pass