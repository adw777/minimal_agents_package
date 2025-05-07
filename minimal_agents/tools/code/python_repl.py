"""Python REPL tool for executing Python code."""

import sys
from io import StringIO
from typing import Dict, Optional

from minimal_agents.tools.base import Tool

class PythonREPL(Tool):
    """Tool for executing Python code in a REPL environment."""
    
    name: str = "Python REPL"
    description: str = (
        "A Python shell. Use this to execute Python commands. "
        "Input should be a valid Python command. "
        "If you want to see the output of a value, you should print it out "
        "with print()."
    )
    globals_dict: Dict = None
    locals_dict: Dict = None
    
    def __init__(self, **data):
        """Initialize the Python REPL tool.
        
        You can optionally provide globals_dict and locals_dict to maintain state
        between executions.
        """
        super().__init__(**data)
        self.globals_dict = self.globals_dict or globals().copy()
        self.locals_dict = self.locals_dict or locals().copy()
    
    def run(self, input_text: str) -> str:
        """Execute Python code and return the output.
        
        Args:
            input_text: Valid Python code to execute
            
        Returns:
            String output from code execution, or error message
        """
        # Clean the input
        code = input_text.strip()
        
        # Remove Markdown code fences if present
        if code.startswith("```python"):
            code = code[9:]
        elif code.startswith("```"):
            code = code[3:]
            
        if code.endswith("```"):
            code = code[:-3]
        
        # Redirect stdout to capture output
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        
        try:
            # Execute the code
            exec(code, self.globals_dict, self.locals_dict)
            sys.stdout = old_stdout
            output = mystdout.getvalue()
            
            # Return output if any, or success message
            if output.strip():
                return output
            else:
                return "Code executed successfully (no output)."
        except Exception as e:
            sys.stdout = old_stdout
            return f"Error: {str(e)}"
        finally:
            # Ensure stdout is restored even if there's an error
            sys.stdout = old_stdout