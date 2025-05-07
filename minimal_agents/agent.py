"""Core agent implementation for MinimalAgents framework."""

import datetime
import re
from typing import List, Dict, Tuple, Any, Optional, Union
from pydantic import BaseModel, Field

from minimal_agents.llm.base import LLMProvider
from minimal_agents.tools.base import Tool
from minimal_agents.utils.parsing import extract_tool_calls, extract_final_answer
from minimal_agents.utils.prompts import DEFAULT_SYSTEM_PROMPT, DEFAULT_PROMPT_TEMPLATE

# Response parsing tokens
FINAL_ANSWER_TOKEN = "Final Answer:"
OBSERVATION_TOKEN = "Observation:"
THOUGHT_TOKEN = "Thought:"
PLAN_TOKEN = "Plan:"
ACTION_TOKEN = "Action:"
ACTION_INPUT_TOKEN = "Action Input:"
CHAT_RESPONSE_TOKEN = "Chat Response:"

class MinimalAgent(BaseModel):
    """Agent that orchestrates LLM interactions with tools.
    
    This agent manages the conversation flow, determines when to use tools,
    and processes responses to achieve the user's goals.
    """
    
    llm: LLMProvider
    tools: List[Tool] = Field(default_factory=list)
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    prompt_template: str = DEFAULT_PROMPT_TEMPLATE
    max_iterations: int = 10
    verbose: bool = False
    stop_patterns: List[str] = Field(
        default_factory=lambda: [f'\n{OBSERVATION_TOKEN}', f'\n\t{OBSERVATION_TOKEN}']
    )
    
    class Config:
        arbitrary_types_allowed = True
    
    @property
    def tool_descriptions(self) -> str:
        """Get formatted tool descriptions for prompt inclusion."""
        return "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])

    @property
    def tool_names(self) -> str:
        """Get comma-separated list of tool names."""
        return ", ".join([tool.name for tool in self.tools])

    @property
    def tool_by_name(self) -> Dict[str, Tool]:
        """Get dictionary mapping tool names to tool instances."""
        return {tool.name: tool for tool in self.tools}
    
    def run(self, query: str) -> str:
        """Process a query and return the final response.
        
        Args:
            query: The user's question or request
            
        Returns:
            The agent's final answer
        """
        context = []  # Store conversation history
        iterations = 0
        
        # Format the initial prompt
        formatted_prompt = self._format_prompt(query, context)
        
        # First check if this is a direct chat response that doesn't need tools
        if self.verbose:
            print(f"Running agent with query: {query}")
            print(f"Available tools: {self.tool_names}")
            
        # Generate initial response
        response = self.llm.generate(formatted_prompt, stop=self.stop_patterns)
        
        # Check if the model decided to give a direct chat response
        if CHAT_RESPONSE_TOKEN in response:
            chat_response = response.split(CHAT_RESPONSE_TOKEN)[1].strip()
            if self.verbose:
                print(f"Direct chat response: {chat_response}")
            return chat_response
            
        # If we're here, we're in tool-using mode
        context.append(response)
        
        while iterations < self.max_iterations:
            iterations += 1
            
            if self.verbose:
                print(f"\n--- Iteration {iterations} ---")
            
            if iterations > 1:  # We already have the first response
                # Format the prompt with the updated context
                formatted_prompt = self._format_prompt(query, context)
                response = self.llm.generate(formatted_prompt, stop=self.stop_patterns)
                
            # Extract tool name and input from response
            tool_name, tool_input = self._extract_tool_call(response)
            
            # Check if we've reached a final answer
            if tool_name == "Final Answer":
                if self.verbose:
                    print(f"Final Answer: {tool_input}")
                return tool_input
                
            # Check for direct chat response (though this should be caught earlier)
            if tool_name == "Chat Response":
                if self.verbose:
                    print(f"Chat Response: {tool_input}")
                return tool_input
            
            # Execute the tool if found
            if tool_name not in self.tool_by_name:
                error_msg = f"Unknown tool: {tool_name}. Available tools: {self.tool_names}"
                if self.verbose:
                    print(f"Error: {error_msg}")
                tool_result = f"Error: {error_msg}"
            else:
                try:
                    if self.verbose:
                        print(f"Using tool: {tool_name}")
                        print(f"Tool input: {tool_input}")
                    
                    # Execute the tool and get result
                    tool = self.tool_by_name[tool_name]
                    tool_result = tool.run(tool_input)
                    
                    if self.verbose:
                        # Truncate long results for display
                        display_result = (
                            f"{tool_result[:500]}..." if len(tool_result) > 500 else tool_result
                        )
                        print(f"Tool result: {display_result}")
                except Exception as e:
                    tool_result = f"Error: {str(e)}"
                    if self.verbose:
                        print(f"Tool execution error: {str(e)}")
            
            # Add the observation and prepare for next iteration
            response += f"\n{OBSERVATION_TOKEN} {tool_result}\n{THOUGHT_TOKEN}"
            context.append(response)
        
        # If we reach max iterations without a final answer
        if self.verbose:
            print("\nReached maximum iterations without final answer")
            
        # Extract insights from all collected observations
        insights = self._extract_insights(context)
        return f"I wasn't able to reach a definite conclusion after multiple attempts. Here's what I found: {insights}"
    
    def _format_prompt(self, query: str, context: List[str] = None) -> str:
        """Format the prompt with query and context.
        
        Args:
            query: The user's question
            context: List of previous responses/context
            
        Returns:
            Formatted prompt string
        """
        if context is None:
            context = []
            
        # Format the prompt template with today's date, tool descriptions, etc.
        prompt = self.prompt_template.format(
            today=datetime.date.today(),
            tool_description=self.tool_descriptions,
            tool_names=self.tool_names,
            question=query,
            previous_responses="\n".join(context)
        )
        
        return prompt
    
    def _extract_tool_call(self, response: str) -> Tuple[str, str]:
        """Extract the tool call and input from LLM response.
        
        Args:
            response: The raw LLM response text
            
        Returns:
            Tuple of (tool_name, tool_input)
        """
        # Check for final answer
        if FINAL_ANSWER_TOKEN in response:
            final_answer = response.split(FINAL_ANSWER_TOKEN)[1].strip()
            return "Final Answer", final_answer
            
        # Check for chat response
        if CHAT_RESPONSE_TOKEN in response:
            chat_response = response.split(CHAT_RESPONSE_TOKEN)[1].strip()
            return "Chat Response", chat_response
            
        # Extract action and action input with regex
        action_regex = r"Action: [\[]?(.*?)[\]]?[\n]*Action Input:[\s]*(.*)"
        match = re.search(action_regex, response, re.DOTALL)
        
        if not match:
            # If no clear action is detected, try alternative parsing
            if ACTION_TOKEN in response and ACTION_INPUT_TOKEN in response:
                try:
                    action_part = response.split(ACTION_TOKEN)[1].split("\n")[0].strip()
                    if OBSERVATION_TOKEN in response:
                        input_part = response.split(ACTION_INPUT_TOKEN)[1].split(OBSERVATION_TOKEN)[0].strip()
                    else:
                        input_part = response.split(ACTION_INPUT_TOKEN)[1].strip()
                    return action_part, input_part
                except Exception:
                    pass
            
            # If parsing fails, raise error
            raise ValueError(f"Could not parse tool call from response: {response}")
        
        tool_name = match.group(1).strip()
        tool_input = match.group(2).strip(" \n\"'")
        return tool_name, tool_input
    
    def _extract_insights(self, context: List[str]) -> str:
        """Extract key insights from observations when no final answer is reached.
        
        Args:
            context: List of all previous responses
            
        Returns:
            String with extracted insights
        """
        combined = "\n".join(context)
        observations = []
        
        # Extract all observations using regex
        observation_pattern = f"{OBSERVATION_TOKEN}(.*?)(?={THOUGHT_TOKEN}|$)"
        matches = re.findall(observation_pattern, combined, re.DOTALL)
        
        # Get the most important observations (last 3)
        for match in matches[-3:]:
            observations.append(match.strip())
        
        return "\n\n".join(observations)
    
    def add_tool(self, tool: Tool) -> None:
        """Add a new tool to the agent.
        
        Args:
            tool: The tool to add
        """
        self.tools.append(tool)
    
    def remove_tool(self, tool_name: str) -> bool:
        """Remove a tool by name.
        
        Args:
            tool_name: Name of the tool to remove
            
        Returns:
            True if tool was removed, False if not found
        """
        original_count = len(self.tools)
        self.tools = [tool for tool in self.tools if tool.name != tool_name]
        return len(self.tools) < original_count
    
    @classmethod
    def create(
        cls,
        llm: LLMProvider,
        tools: Optional[List[Tool]] = None,
        system_prompt: Optional[str] = None,
        verbose: bool = False
    ) -> 'MinimalAgent':
        """Factory method to create a MinimalAgent with common defaults.
        
        Args:
            llm: LLM provider instance
            tools: Optional list of tools (defaults to empty list)
            system_prompt: Optional custom system prompt
            verbose: Whether to print verbose output
            
        Returns:
            Configured MinimalAgent instance
        """
        return cls(
            llm=llm,
            tools=tools or [],
            system_prompt=system_prompt or DEFAULT_SYSTEM_PROMPT,
            verbose=verbose
        )