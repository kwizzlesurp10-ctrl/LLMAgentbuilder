#!/usr/bin/env python3
"""
Setup and Verification Script for Multi-Step Workflows and Tool Integration

This script verifies that the LLM Agent Builder is properly configured
for multi-step workflows and tool integration.
"""

import os
import sys
import json
from pathlib import Path

def check_imports():
    """Check if required modules can be imported."""
    print("✓ Checking imports...")
    try:
        from llm_agent_builder.agent_builder import AgentBuilder
        print("  ✓ AgentBuilder imported successfully")
        return True
    except ImportError as e:
        print(f"  ✗ Failed to import AgentBuilder: {e}")
        return False

def check_api_models():
    """Check if API models support tools and multi-step."""
    print("\n✓ Checking API models...")
    try:
        from server.models import GenerateRequest
        import inspect
        
        # Check model fields directly
        model_fields = GenerateRequest.model_fields
        
        has_tools = 'tools' in model_fields
        has_multi_step = 'enable_multi_step' in model_fields
        
        if has_tools and has_multi_step:
            print("  ✓ API models support tools and multi-step workflows")
            return True
        else:
            print(f"  ✗ Missing fields. Found: {list(model_fields.keys())}")
            if not has_tools:
                print("    - Missing: tools")
            if not has_multi_step:
                print("    - Missing: enable_multi_step")
            return False
    except Exception as e:
        print(f"  ✗ Error checking API models: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_examples():
    """Check if example files exist."""
    print("\n✓ Checking example files...")
    examples_dir = Path("examples")
    required_files = [
        "tools_example.json",
        "tools_code_reviewer.json",
        "multi_step_agent_example.py",
        "tools_agent_example.py",
        "advanced_agent_example.py"
    ]
    
    all_exist = True
    for file in required_files:
        file_path = examples_dir / file
        if file_path.exists():
            print(f"  ✓ {file} exists")
        else:
            print(f"  ✗ {file} not found")
            all_exist = False
    
    return all_exist

def test_tool_definition():
    """Test loading a tool definition."""
    print("\n✓ Testing tool definition loading...")
    try:
        tools_file = Path("examples/tools_example.json")
        if not tools_file.exists():
            print("  ✗ tools_example.json not found")
            return False
        
        with open(tools_file, 'r') as f:
            tools = json.load(f)
        
        if not isinstance(tools, list):
            print("  ✗ Tools should be a JSON array")
            return False
        
        if len(tools) == 0:
            print("  ✗ Tools array is empty")
            return False
        
        # Validate tool structure
        for tool in tools:
            if not all(key in tool for key in ['name', 'description', 'input_schema']):
                print(f"  ✗ Invalid tool structure: {tool}")
                return False
        
        print(f"  ✓ Successfully loaded {len(tools)} tool(s)")
        return True
    except json.JSONDecodeError as e:
        print(f"  ✗ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_agent_generation():
    """Test generating an agent with tools and multi-step."""
    print("\n✓ Testing agent generation...")
    try:
        from llm_agent_builder.agent_builder import AgentBuilder
        
        builder = AgentBuilder()
        
        # Test with multi-step
        code = builder.build_agent(
            agent_name="TestAgent",
            prompt="Test prompt",
            example_task="Test task",
            model="gemini-1.5-pro",
            provider="google",
            enable_multi_step=True
        )
        
        if "run_multi_step" in code:
            print("  ✓ Multi-step workflow code generated")
        else:
            print("  ✗ Multi-step workflow code not found")
            return False
        
        # Test with tools
        tools = [
            {
                "name": "test_tool",
                "description": "A test tool",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string"}
                    }
                }
            }
        ]
        
        code = builder.build_agent(
            agent_name="TestAgent",
            prompt="Test prompt",
            example_task="Test task",
            model="gemini-1.5-pro",
            provider="google",
            tools=tools
        )
        
        if "_execute_tool" in code:
            print("  ✓ Tool integration code generated")
        else:
            print("  ✗ Tool integration code not found")
            return False
        
        return True
    except Exception as e:
        print(f"  ✗ Error generating agent: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all checks."""
    print("=" * 60)
    print("LLM Agent Builder - Multi-Step & Tools Setup Verification")
    print("=" * 60)
    
    checks = [
        ("Imports", check_imports),
        ("API Models", check_api_models),
        ("Example Files", check_examples),
        ("Tool Definitions", test_tool_definition),
        ("Agent Generation", test_agent_generation)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} check failed with exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All checks passed! Multi-step workflows and tool integration are ready.")
        print("\nNext steps:")
        print("  1. Review examples/ directory")
        print("  2. Read MULTI_STEP_AND_TOOLS_GUIDE.md")
        print("  3. Generate your first agent with --enable-multi-step or --tools")
        return 0
    else:
        print("\n✗ Some checks failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
