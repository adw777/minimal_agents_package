"""OpenAI LLM provider implementation."""

import os
from typing import List, Optional, Dict, Any

from openai import OpenAI
from pydantic import Field

from minimal_agents.llm.base import LLMProvider

class OpenAIProvider(LLMProvider):
    """OpenAI API provider for language models."""
    
    model: str = "gpt-4o"
    temperature: float = 0.4
    max_tokens: Optional[int] = None
    api_key: Optional[str] = None
    client: Optional[Any] = None
    
    def __init__(
        self,
        model: str = "gpt-4o",
        temperature: float = 0.4,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """Initialize the OpenAI provider.
        
        Args:
            model: The OpenAI model name to use
            temperature: Temperature setting for generation (0.0 to 1.0)
            max_tokens: Maximum tokens to generate (optional)
            api_key: OpenAI API key (will use OPENAI_API_KEY env var if not provided)
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key.")
        
        # Initialize the client
        self.client = OpenAI(api_key=self.api_key)
    
    def generate(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Generate text using OpenAI API.
        
        Args:
            prompt: The prompt to send to the model
            stop: Optional list of strings that will stop generation
            
        Returns:
            Generated text response
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stop=stop
        )
        
        return response.choices[0].message.content
    
    @property
    def provider_name(self) -> str:
        """Get the provider name.
        
        Returns:
            String "openai"
        """
        return "openai"
    
    @property
    def model_name(self) -> str:
        """Get the model name.
        
        Returns:
            The name of the model being used
        """
        return self.model