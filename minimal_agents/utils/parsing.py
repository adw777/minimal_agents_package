"""Utility functions for parsing LLM responses."""

import re
from typing import Tuple, Optional

# Token constants used for parsing
FINAL_ANSWER_TOKEN = "Final Answer:"
OBSERVATION_TOKEN = "Observation:"
THOUGHT_TOKEN = "Thought:"
PLAN_TOKEN = "Plan:"
ACTION_TOKEN = "Action:"
ACTION_INPUT_TOKEN = "Action Input:"
CHAT_RESPONSE_TOKEN = "Chat Response:"

def extract_tool_calls(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract tool name and input from LLM response.
    
    Args:
        text: The raw LLM response text
        
    Returns:
        Tuple of (tool_name, tool_input) or (None, None) if not found
    """
    # Regular expression to extract action and action input
    action_regex = r"Action: [\[]?(.*?)[\]]?[\n]*Action Input:[\s]*(.*?)(?=\n\s*Observation:|\Z)"
    match = re.search(action_regex, text, re.DOTALL)
    
    if not match:
        return None, None
        
    tool_name = match.group(1).strip()
    tool_input = match.group(2).strip(" \n\"'")
    return tool_name, tool_input

def extract_final_answer(text: str) -> Optional[str]:
    """Extract final answer from LLM response.
    
    Args:
        text: The raw LLM response text
        
    Returns:
        The extracted final answer or None if not found
    """
    if FINAL_ANSWER_TOKEN not in text:
        return None
        
    final_answer = text.split(FINAL_ANSWER_TOKEN)[1].strip()
    return final_answer

def extract_chat_response(text: str) -> Optional[str]:
    """Extract direct chat response from LLM response.
    
    Args:
        text: The raw LLM response text
        
    Returns:
        The extracted chat response or None if not found
    """
    if CHAT_RESPONSE_TOKEN not in text:
        return None
        
    chat_response = text.split(CHAT_RESPONSE_TOKEN)[1].strip()
    return chat_response

def extract_observations(text: str) -> list[str]:
    """Extract all observations from a response with multiple tool calls.
    
    Args:
        text: The combined LLM response text
        
    Returns:
        List of observation strings
    """
    observation_pattern = f"{OBSERVATION_TOKEN}(.*?)(?={THOUGHT_TOKEN}|$)"
    observations = re.findall(observation_pattern, text, re.DOTALL)
    return [obs.strip() for obs in observations]

def extract_thoughts(text: str) -> list[str]:
    """Extract all thought sections from a response.
    
    Args:
        text: The combined LLM response text
        
    Returns:
        List of thought strings
    """
    thought_pattern = f"{THOUGHT_TOKEN}(.*?)(?={ACTION_TOKEN}|{PLAN_TOKEN}|{FINAL_ANSWER_TOKEN}|$)"
    thoughts = re.findall(thought_pattern, text, re.DOTALL)
    return [thought.strip() for thought in thoughts]