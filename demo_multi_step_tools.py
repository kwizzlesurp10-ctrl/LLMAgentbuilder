#!/usr/bin/env python3
"""
Demonstration Script: Multi-Step Workflows and Tool Integration

This script demonstrates the complete workflow for generating and using
agents with multi-step workflows and tool integration.
"""

import os
import sys
from pathlib import Path
from llm_agent_builder.agent_builder import AgentBuilder
import json

def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def demo_multi_step_agent():
    """Demonstrate generating a multi-step workflow agent."""
    print_section("Demo 1: Multi-Step Workflow Agent")
    
    print("\n📝 Generating ResearchAgent with multi-step capabilities...")
    
    builder = AgentBuilder()
    agent_code = builder.build_agent(
        agent_name="ResearchAgent",
        prompt="You are a thorough research assistant. Break down complex questions "
               "into steps, gather information systematically, and provide comprehensive answers.",
        example_task="Research the impact of artificial intelligence on healthcare",
        model="gemini-1.5-pro",
        provider="google",
        enable_multi_step=True
    )
    
    # Save the agent
    output_dir = Path("generated_agents")
    output_dir.mkdir(exist_ok=True)
    agent_file = output_dir / "demo_research_agent.py"
    
    with open(agent_file, "w") as f:
        f.write(agent_code)
    
    print(f"✓ Agent generated: {agent_file}")
    print("\n📋 Key features in generated code:")
    print("  - run_multi_step() method for iterative refinement")
    print("  - Configurable max_steps parameter")
    print("  - Automatic completion detection")
    
    # Show code snippet
    if "run_multi_step" in agent_code:
        print("\n✨ Multi-step workflow method found in generated code!")
    
    return agent_file

def demo_tools_agent():
    """Demonstrate generating an agent with tool integration."""
    print_section("Demo 2: Tool Integration Agent")
    
    print("\n📝 Generating ToolAgent with web search and calculator tools...")
    
    # Define tools
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
    
    builder = AgentBuilder()
    agent_code = builder.build_agent(
        agent_name="ToolAgent",
        prompt="You are a helpful assistant with access to web search and calculator tools. "
               "Use these tools to help users find information and perform calculations.",
        example_task="Search for the current weather in San Francisco and calculate 15 * 23",
        model="gemini-1.5-pro",
        provider="google",
        tools=tools
    )
    
    # Save the agent
    output_dir = Path("generated_agents")
    output_dir.mkdir(exist_ok=True)
    agent_file = output_dir / "demo_tool_agent.py"
    
    with open(agent_file, "w") as f:
        f.write(agent_code)
    
    print(f"✓ Agent generated: {agent_file}")
    print("\n📋 Key features in generated code:")
    print("  - _execute_tool() method for tool execution")
    print("  - Tool definitions integrated into agent")
    print("  - Automatic tool calling by LLM")
    
    # Show code snippet
    if "_execute_tool" in agent_code:
        print("\n✨ Tool integration method found in generated code!")
    
    return agent_file

def demo_advanced_agent():
    """Demonstrate generating an advanced agent with both features."""
    print_section("Demo 3: Advanced Agent (Multi-Step + Tools)")
    
    print("\n📝 Generating AdvancedCodeReviewer with both features...")
    
    # Load tools from example file
    tools_file = Path("examples/tools_code_reviewer.json")
    if tools_file.exists():
        with open(tools_file, "r") as f:
            tools = json.load(f)
    else:
        # Fallback tools if file doesn't exist
        tools = [
            {
                "name": "analyze_code",
                "description": "Analyze code for bugs and issues",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"}
                    },
                    "required": ["code"]
                }
            }
        ]
    
    builder = AgentBuilder()
    agent_code = builder.build_agent(
        agent_name="AdvancedCodeReviewer",
        prompt="You are an expert code reviewer. Analyze code systematically using tools, "
               "identify issues, and provide comprehensive feedback through multiple iterations.",
        example_task="Review this Python function: def process(data): return data.sort()",
        model="gemini-1.5-pro",
        provider="google",
        enable_multi_step=True,
        tools=tools
    )
    
    # Save the agent
    output_dir = Path("generated_agents")
    output_dir.mkdir(exist_ok=True)
    agent_file = output_dir / "demo_advanced_agent.py"
    
    with open(agent_file, "w") as f:
        f.write(agent_code)
    
    print(f"✓ Agent generated: {agent_file}")
    print("\n📋 Key features in generated code:")
    print("  - Multi-step workflow for iterative refinement")
    print("  - Tool integration for code analysis")
    print("  - Combined capabilities for comprehensive reviews")
    
    # Verify both features
    has_multi_step = "run_multi_step" in agent_code
    has_tools = "_execute_tool" in agent_code
    
    if has_multi_step and has_tools:
        print("\n✨ Both multi-step workflow AND tool integration found!")
    
    return agent_file

def show_usage_examples():
    """Show usage examples for the generated agents."""
    print_section("Usage Examples")
    
    print("\n📖 Example 1: Using Multi-Step Agent")
    print("-" * 70)
    print("""
from generated_agents.demo_research_agent import ResearchAgent
import os

agent = ResearchAgent(api_key=os.environ['GOOGLE_GEMINI_KEY'])

# Single-step execution
result = agent.run("Research topic X")

# Multi-step execution (iterative refinement)
result = agent.run_multi_step("Research topic X", max_steps=5)
print(result)
""")
    
    print("\n📖 Example 2: Using Tool Agent")
    print("-" * 70)
    print("""
from generated_agents.demo_tool_agent import ToolAgent
import os

agent = ToolAgent(api_key=os.environ['GOOGLE_GEMINI_KEY'])

# Agent will automatically use tools when needed
result = agent.run("Search for Python tutorials and calculate 15 * 23")
print(result)

# Note: You need to implement _execute_tool() method with actual tool logic
""")
    
    print("\n📖 Example 3: Using Advanced Agent")
    print("-" * 70)
    print("""
from generated_agents.demo_advanced_agent import AdvancedCodeReviewer
import os

agent = AdvancedCodeReviewer(api_key=os.environ['GOOGLE_GEMINI_KEY'])

# Multi-step execution with tools
result = agent.run("Review this code: def add(a, b): return a + b", use_multi_step=True)
print(result)

# Or use dedicated method
result = agent.run_multi_step("Review this code...", max_steps=3)
print(result)
""")

def show_cli_examples():
    """Show CLI usage examples."""
    print_section("CLI Usage Examples")
    
    print("\n💻 Example 1: Generate Multi-Step Agent")
    print("-" * 70)
    print("""
llm-agent-builder generate \\
  --name "ResearchAgent" \\
  --prompt "You are a research assistant" \\
  --task "Research topic X" \\
  --model "gemini-1.5-pro" \\
  --provider "google" \\
  --enable-multi-step
""")
    
    print("\n💻 Example 2: Generate Agent with Tools")
    print("-" * 70)
    print("""
llm-agent-builder generate \\
  --name "ToolAgent" \\
  --prompt "You are a helpful assistant" \\
  --task "Use tools to help" \\
  --model "gemini-1.5-pro" \\
  --provider "google" \\
  --tools examples/tools_example.json
""")
    
    print("\n💻 Example 3: Generate Advanced Agent")
    print("-" * 70)
    print("""
llm-agent-builder generate \\
  --name "AdvancedAgent" \\
  --prompt "You are an expert assistant" \\
  --task "Complete complex task" \\
  --model "gemini-1.5-pro" \\
  --provider "google" \\
  --enable-multi-step \\
  --tools examples/tools_code_reviewer.json
""")

def main():
    """Run all demonstrations."""
    print("\n" + "🚀" * 35)
    print("  LLM Agent Builder - Multi-Step & Tools Demonstration")
    print("🚀" * 35)
    
    try:
        # Demo 1: Multi-step agent
        demo_multi_step_agent()
        
        # Demo 2: Tools agent
        demo_tools_agent()
        
        # Demo 3: Advanced agent
        demo_advanced_agent()
        
        # Show usage examples
        show_usage_examples()
        
        # Show CLI examples
        show_cli_examples()
        
        print_section("✅ Demonstration Complete")
        print("\n✨ Successfully generated 3 demo agents:")
        print("  1. demo_research_agent.py - Multi-step workflow")
        print("  2. demo_tool_agent.py - Tool integration")
        print("  3. demo_advanced_agent.py - Combined features")
        
        print("\n📚 Next Steps:")
        print("  1. Review generated agents in generated_agents/")
        print("  2. Implement _execute_tool() methods with actual tool logic")
        print("  3. Test agents with your API key:")
        print("     export GOOGLE_GEMINI_KEY='your-key-here'")
        print("     python generated_agents/demo_research_agent.py --task 'Your task'")
        print("  4. Read MULTI_STEP_AND_TOOLS_GUIDE.md for detailed documentation")
        
        print("\n💡 Tips:")
        print("  - Use --enable-multi-step for complex, iterative tasks")
        print("  - Use --tools for agents that need external capabilities")
        print("  - Combine both for maximum power!")
        print("  - Check provider support: Claude/OpenAI have best tool support")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
