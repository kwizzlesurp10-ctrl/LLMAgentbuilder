#!/usr/bin/env python3
"""
Test script for AgentEngine - demonstrates how to use the engine
to test agents programmatically without CLI output.

Usage:
    python test_engine.py <agent_path> <task>
    
Example:
    python test_engine.py generated_agents/newsbot.py "List the latest alerts"
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from llm_agent_builder.agent_engine import AgentEngine, run_agent

def main():
    """Test the AgentEngine with a provided agent and task."""
    load_dotenv()
    
    if len(sys.argv) < 3:
        print("Usage: python test_engine.py <agent_path> <task>")
        print("\nExample:")
        print('  python test_engine.py generated_agents/newsbot.py "List the latest alerts"')
        sys.exit(1)
    
    agent_path = Path(sys.argv[1])
    task = sys.argv[2]
    
    if not agent_path.exists():
        print(f"Error: Agent file not found: {agent_path}")
        sys.exit(1)
    
    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    if not api_key:
        print("Error: API key not found. Set ANTHROPIC_API_KEY or HUGGINGFACEHUB_API_TOKEN")
        sys.exit(1)
    
    print(f"Testing agent: {agent_path}")
    print(f"Task: {task}")
    print("-" * 60)
    
    # Method 1: Using the convenience function
    print("\n[Method 1: Using run_agent convenience function]")
    result = run_agent(agent_path, task, api_key=api_key, use_subprocess=True, timeout=60)
    
    print(f"\nStatus: {result['status']}")
    if result.get('execution_time'):
        print(f"Execution Time: {result['execution_time']:.2f}s")
    
    if result['status'] == 'success':
        print("\nOutput:")
        print("-" * 60)
        print(result['output'])
        print("-" * 60)
    else:
        print(f"\nError: {result.get('error', 'Unknown error')}")
        if result.get('output'):
            print(f"\nOutput:\n{result['output']}")
    
    # Method 2: Using AgentEngine directly
    print("\n\n[Method 2: Using AgentEngine directly]")
    engine = AgentEngine(api_key=api_key, timeout=60)
    result = engine.execute_with_timeout(agent_path, task)
    
    print(f"\nStatus: {result.status.value}")
    if result.execution_time:
        print(f"Execution Time: {result.execution_time:.2f}s")
    
    if result.status.value == 'success':
        print("\nOutput:")
        print("-" * 60)
        print(result.output)
        print("-" * 60)
    else:
        print(f"\nError: {result.error}")
        if result.output:
            print(f"\nOutput:\n{result.output}")

if __name__ == "__main__":
    main()
