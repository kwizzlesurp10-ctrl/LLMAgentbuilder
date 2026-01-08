"""
Example: Generating an agent with tool integration

This example demonstrates how to generate an agent that can use
custom tools to extend its capabilities.
"""

from llm_agent_builder.agent_builder import AgentBuilder
import json

# Define tools for the agent
tools = [
    {
        "name": "search_web",
        "description": "Search the web for current information",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "calculate",
        "description": "Perform mathematical calculations",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression (e.g., '2 + 2', 'sqrt(16)')"
                }
            },
            "required": ["expression"]
        }
    }
]

# Initialize the builder
builder = AgentBuilder()

# Generate an agent with tools
agent_code = builder.build_agent(
    agent_name="ToolAgent",
    prompt="You are a helpful assistant that can search the web and perform calculations. "
           "Use the available tools to help users with their requests.",
    example_task="What is the current weather in San Francisco? Also calculate 15 * 23.",
    model="gemini-1.5-pro",
    provider="google",
    tools=tools  # Pass tools to the agent
)

# Save the generated agent
with open("generated_agents/tool_agent.py", "w") as f:
    f.write(agent_code)

print("✓ Tool-enabled agent generated successfully!")
print("\nNote: You'll need to implement the _execute_tool method in the generated agent")
print("to actually execute the tool calls. The template provides a stub implementation.")
