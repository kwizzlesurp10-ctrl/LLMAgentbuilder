"""
Example: Generating an advanced agent with both multi-step workflows and tools

This example demonstrates how to combine multi-step workflows with tool integration
for powerful, production-ready agents.
"""

from llm_agent_builder.agent_builder import AgentBuilder
import json

# Load tools from JSON file
with open("examples/tools_code_reviewer.json", "r") as f:
    tools = json.load(f)

# Initialize the builder
builder = AgentBuilder()

# Generate an advanced agent with both features
agent_code = builder.build_agent(
    agent_name="AdvancedCodeReviewer",
    prompt="You are an expert code reviewer. Analyze code systematically, "
           "identify issues, and provide comprehensive feedback. Use tools "
           "to analyze code and suggest improvements.",
    example_task="Review this Python function for bugs and suggest improvements: "
                 "def process_data(data): return data.sort()",
    model="gemini-1.5-pro",
    provider="google",
    enable_multi_step=True,  # Enable multi-step workflow
    tools=tools  # Enable tool integration
)

# Save the generated agent
with open("generated_agents/advanced_code_reviewer.py", "w") as f:
    f.write(agent_code)

print("✓ Advanced agent generated successfully!")
print("\nThis agent has:")
print("  - Multi-step workflow capabilities (can iterate and refine)")
print("  - Tool integration (can use analyze_code and suggest_improvements)")
print("\nUsage:")
print("  agent = AdvancedCodeReviewer(api_key='your-key')")
print("  # Single-step execution with tools")
print("  result = agent.run('Review this code: ...')")
print("  # Multi-step execution with tools")
print("  result = agent.run('Review this code: ...', use_multi_step=True)")
