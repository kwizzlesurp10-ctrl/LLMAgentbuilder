import pytest
import subprocess
import sys
import os

def test_cli_help():
    result = subprocess.run([sys.executable, "main.py", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Generate an LLM agent using Anthropic API" in result.stdout

def test_cli_generate_agent(temp_output_dir):
    agent_name = "CLITestAgent"
    
    result = subprocess.run([
        sys.executable, "main.py",
        "--name", agent_name,
        "--output", temp_output_dir,
        "--model", "claude-3-test"
    ], capture_output=True, text=True)
    
    assert result.returncode == 0
    assert f"Agent '{agent_name}' has been created" in result.stdout
    
    output_file = os.path.join(temp_output_dir, f"{agent_name.lower()}.py")
    assert os.path.exists(output_file)
    
    with open(output_file, "r") as f:
        content = f.read()
        assert f"class {agent_name}:" in content
        assert 'model=os.environ.get("ANTHROPIC_MODEL", "claude-3-test")' in content
