from typing import Dict, Any, List

class StandardTool:
    def __init__(self, name: str, description: str, input_schema: Dict[str, Any], implementation: str):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.implementation = implementation

class ToolLibrary:
    """Library of standard tools that can be injected into agents."""
    
    _TOOLS = {}

    @classmethod
    def register_tool(cls, tool: StandardTool):
        cls._TOOLS[tool.name] = tool

    @classmethod
    def get_tool(cls, name: str) -> StandardTool:
        return cls._TOOLS.get(name)

    @classmethod
    def list_tools(cls) -> List[Dict[str, Any]]:
        return [
            {
                "name": tool.name, 
                "description": tool.description, 
                "input_schema": tool.input_schema
            } 
            for tool in cls._TOOLS.values()
        ]

# Define Standard Tools

# 1. Calculator
_CALCULATOR_IMPL = """
    def calculator(self, expression: str) -> str:
        \"\"\"Evaluate a mathematical expression.\"\"\"
        try:
            # Dangerous in production! Using restricted scope for demo
            allowed_names = {"abs": abs, "round": round}
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return str(result)
        except Exception as e:
            return f"Error calculating: {str(e)}"
"""

ToolLibrary.register_tool(StandardTool(
    name="calculator",
    description="Perform mathematical calculations. Supports basic arithmetic.",
    input_schema={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The mathematical expression to evaluate (e.g., '2 + 2 * 3')"
            }
        },
        "required": ["expression"]
    },
    implementation=_CALCULATOR_IMPL
))

# 2. Web Search (Mock for now, or use a real API if env var present?)
# keeping it simple for now, maybe just a placeholder or string reverse
_STRING_REVERSE_IMPL = """
    def string_reverse(self, text: str) -> str:
        \"\"\"Reverse a given string.\"\"\"
        return text[::-1]
"""

ToolLibrary.register_tool(StandardTool(
    name="string_reverse",
    description="Reverses a given string. Useful for testing tool usage.",
    input_schema={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The string to reverse"
            }
        },
        "required": ["text"]
    },
    implementation=_STRING_REVERSE_IMPL
))
