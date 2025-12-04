"""
Tests for AgentEngine - programmatic agent execution.
"""

import os
import tempfile
from pathlib import Path
import pytest
from llm_agent_builder.agent_engine import AgentEngine, ExecutionStatus, run_agent


# Simple test agent code
TEST_AGENT_CODE = '''
import os
import argparse

class TestAgent:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def run(self, task):
        return f"Processed task: {task}"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", default="default task")
    args = parser.parse_args()
    
    agent = TestAgent(api_key="test-key")
    result = agent.run(args.task)
    print(result)
'''

# Test agent with error
TEST_AGENT_ERROR_CODE = '''
class TestAgentError:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def run(self, task):
        raise ValueError("Test error")
'''


@pytest.fixture
def temp_agent_file(tmp_path):
    """Create a temporary agent file for testing."""
    agent_file = tmp_path / "test_agent.py"
    agent_file.write_text(TEST_AGENT_CODE)
    return agent_file


@pytest.fixture
def engine():
    """Create an AgentEngine instance for testing."""
    # Use a dummy API key for testing
    return AgentEngine(api_key="test-key", timeout=10)


def test_engine_initialization():
    """Test AgentEngine initialization."""
    engine = AgentEngine(api_key="test-key", timeout=30)
    assert engine.api_key == "test-key"
    assert engine.timeout == 30
    assert engine.memory_limit_mb == 512


def test_engine_get_api_key_from_env(monkeypatch):
    """Test that engine gets API key from environment."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "env-key")
    engine = AgentEngine()
    assert engine.api_key == "env-key"


def test_load_agent_from_file(temp_agent_file, engine):
    """Test loading an agent from a file."""
    agent_class = engine._load_agent_from_file(temp_agent_file)
    assert agent_class is not None
    assert agent_class.__name__ == "TestAgent"


def test_load_agent_from_code(engine):
    """Test loading an agent from code string."""
    agent_class = engine._load_agent_from_code(TEST_AGENT_CODE)
    assert agent_class is not None
    assert agent_class.__name__ == "TestAgent"


def test_execute_agent_direct(temp_agent_file, engine):
    """Test executing an agent directly (without subprocess)."""
    result = engine.execute(temp_agent_file, "test task")
    
    assert result.status == ExecutionStatus.SUCCESS
    assert "test task" in result.output
    assert result.execution_time is not None


def test_execute_agent_with_subprocess(temp_agent_file, engine):
    """Test executing an agent with subprocess."""
    result = engine.execute_with_timeout(temp_agent_file, "test task")
    
    assert result.status == ExecutionStatus.SUCCESS
    assert "test task" in result.output
    assert result.execution_time is not None


def test_execute_agent_error(engine):
    """Test executing an agent that raises an error."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(TEST_AGENT_ERROR_CODE)
        temp_file = Path(f.name)
    
    try:
        result = engine.execute(temp_file, "test task")
        assert result.status == ExecutionStatus.ERROR
        assert result.error is not None
    finally:
        if temp_file.exists():
            temp_file.unlink()


def test_execute_agent_file_not_found(engine):
    """Test executing a non-existent agent file."""
    # Use a path that definitely doesn't exist
    nonexistent_path = Path("/tmp/nonexistent_agent_12345.py")
    result = engine.execute(nonexistent_path, "test task")
    assert result.status == ExecutionStatus.AGENT_NOT_FOUND
    assert result.error is not None


def test_execute_agent_no_api_key():
    """Test executing an agent without API key."""
    engine = AgentEngine(api_key=None)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(TEST_AGENT_CODE)
        temp_file = Path(f.name)
    
    try:
        result = engine.execute(temp_file, "test task")
        assert result.status == ExecutionStatus.API_KEY_MISSING
    finally:
        if temp_file.exists():
            temp_file.unlink()


def test_run_agent_convenience_function(temp_agent_file):
    """Test the run_agent convenience function."""
    result = run_agent(temp_agent_file, "test task", api_key="test-key", use_subprocess=False)
    
    assert result["status"] == "success"
    assert "test task" in result["output"]
    assert result["execution_time"] is not None


def test_execution_result_to_dict():
    """Test ExecutionResult.to_dict() method."""
    from llm_agent_builder.agent_engine import ExecutionResult
    
    result = ExecutionResult(
        status=ExecutionStatus.SUCCESS,
        output="test output",
        execution_time=1.5
    )
    
    result_dict = result.to_dict()
    assert result_dict["status"] == "success"
    assert result_dict["output"] == "test output"
    assert result_dict["execution_time"] == 1.5
    assert result_dict["error"] is None
