"""
Tests for the unified entry point system.
"""
import subprocess
import sys


def test_main_help():
    """Test main.py --help works."""
    result = subprocess.run(
        [sys.executable, "main.py", "--help"],
        capture_output=True,
        text=True,
        cwd="/home/runner/work/LLMAgentbuilder/LLMAgentbuilder"
    )
    assert result.returncode == 0
    assert "llm-agent-builder" in result.stdout


def test_main_routes_to_cli_list():
    """Test main.py routes 'list' command to CLI."""
    result = subprocess.run(
        [sys.executable, "main.py", "list"],
        capture_output=True,
        text=True,
        cwd="/home/runner/work/LLMAgentbuilder/LLMAgentbuilder"
    )
    assert result.returncode == 0
    assert "agent" in result.stdout.lower()


def test_cli_generate_help():
    """Test CLI generate command help."""
    result = subprocess.run(
        [sys.executable, "main.py", "generate", "--help"],
        capture_output=True,
        text=True,
        cwd="/home/runner/work/LLMAgentbuilder/LLMAgentbuilder"
    )
    assert result.returncode == 0
    assert "Name of the agent" in result.stdout


def test_cli_module_list():
    """Test CLI module can be invoked directly."""
    result = subprocess.run(
        [sys.executable, "-m", "llm_agent_builder.cli", "list"],
        capture_output=True,
        text=True,
        cwd="/home/runner/work/LLMAgentbuilder/LLMAgentbuilder"
    )
    assert result.returncode == 0
    assert "agent" in result.stdout.lower()


def test_cli_with_flag():
    """Test --cli flag works."""
    result = subprocess.run(
        [sys.executable, "main.py", "--cli", "list"],
        capture_output=True,
        text=True,
        cwd="/home/runner/work/LLMAgentbuilder/LLMAgentbuilder"
    )
    assert result.returncode == 0
    assert "agent" in result.stdout.lower()
