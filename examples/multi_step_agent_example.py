"""
Example: Generating an agent with multi-step workflow capabilities

This example demonstrates how to generate an agent that can iterate
and refine its responses over multiple steps.
"""

from llm_agent_builder.agent_builder import AgentBuilder

# Initialize the builder
builder = AgentBuilder()

# Generate an agent with multi-step workflow enabled
agent_code = builder.build_agent(
    agent_name="ResearchAgent",
    prompt="You are a research assistant that conducts thorough research on topics. "
           "You break down complex questions into steps, gather information, "
           "and synthesize comprehensive answers.",
    example_task="Research the impact of artificial intelligence on healthcare",
    model="gemini-1.5-pro",
    provider="google",
    enable_multi_step=True  # Enable multi-step workflow
)

# Save the generated agent
with open("generated_agents/research_agent.py", "w") as f:
    f.write(agent_code)

print("✓ Multi-step agent generated successfully!")
print("\nUsage:")
print("  agent = ResearchAgent(api_key='your-key')")
print("  result = agent.run('Research topic X', use_multi_step=True)")
print("  # Or use the dedicated method:")
print("  result = agent.run_multi_step('Research topic X', max_steps=5)")
