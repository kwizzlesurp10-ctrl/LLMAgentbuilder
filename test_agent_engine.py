#!/usr/bin/env python3
"""
Test script for AgentEngine - demonstrates usage and tests functionality.
"""
import os
import sys
from llm_agent_builder.agent_engine import AgentEngine, ExecutionStatus, run_agent

def main():
    """Run AgentEngine tests."""
    print("=" * 70)
    print("AgentEngine Test Script")
    print("=" * 70)
    
    # Set test token
    os.environ['GITHUB_COPILOT_TOKEN'] = 'mock-copilot-token-for-testing'
    
    # Test agent code
    agent_code = '''import os
import sys
from typing import Optional, List, Dict, Any
try:
    from llm_agent_builder.copilot_client import CopilotClient
    COPILOT_AVAILABLE = True
except ImportError:
    COPILOT_AVAILABLE = False

class TestAgent:
    def __init__(self, api_key):
        if not COPILOT_AVAILABLE:
            raise ImportError("CopilotClient not available")
        self.client = CopilotClient(bearer_token=api_key)
        self.prompt = "You are a helpful assistant"
    
    def run(self, task: str):
        messages = [{"role": "user", "content": f"{self.prompt}\\n\\nTask: {task}"}]
        response = self.client.get_chat_completion(messages=messages)
        return response.content

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    args = parser.parse_args()
    
    api_key = os.environ.get("GITHUB_COPILOT_TOKEN")
    if not api_key:
        print("Error: GITHUB_COPILOT_TOKEN not found")
        sys.exit(1)
    
    try:
        agent = TestAgent(api_key=api_key)
        print(f"Running TestAgent with task: {args.task}\\n")
        result = agent.run(args.task)
        print("Response:")
        print("-" * 50)
        print(result)
        print("-" * 50)
    except Exception as e:
        print(f"Error running agent: {e}")
        sys.exit(1)
'''
    
    print("\n1. Testing AgentEngine initialization...")
    engine = AgentEngine(timeout=30)
    print(f"   ✓ Engine initialized")
    print(f"   - Timeout: {engine.timeout}s")
    print(f"   - API key available: {engine.api_key is not None}")
    
    print("\n2. Testing agent execution...")
    result = engine.execute_with_timeout(agent_code, "Say hello and introduce yourself")
    
    print(f"   Status: {result.status}")
    print(f"   Execution time: {result.execution_time:.3f}s")
    
    if result.status == ExecutionStatus.SUCCESS:
        print(f"   ✓ Agent executed successfully!")
        print(f"\n   Output:")
        print("   " + "-" * 66)
        for line in result.output.split('\n')[:10]:
            print(f"   {line}")
        print("   " + "-" * 66)
    else:
        print(f"   ✗ Execution failed")
        print(f"   Error: {result.error}")
        if result.output:
            print(f"   Output: {result.output[:200]}")
    
    print("\n3. Testing convenience function...")
    result_dict = run_agent(
        agent_path=agent_code,
        task="What is Python?",
        api_key=os.environ.get('GITHUB_COPILOT_TOKEN'),
        use_subprocess=True,
        timeout=30
    )
    
    print(f"   Status: {result_dict.get('status')}")
    print(f"   Execution time: {result_dict.get('execution_time', 0):.3f}s")
    if result_dict.get('status') == 'success':
        print(f"   ✓ Convenience function works!")
    
    print("\n" + "=" * 70)
    print("All tests completed!")
    print("=" * 70)

if __name__ == '__main__':
    main()

