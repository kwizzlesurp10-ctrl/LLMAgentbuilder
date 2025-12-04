"""
Tests for AgentEngine with GitHub Copilot API integration.
"""

import pytest
import os
from pathlib import Path
from llm_agent_builder.agent_engine import AgentEngine, ExecutionStatus


def test_agent_engine_with_copilot_token():
    """Test AgentEngine initialization with GitHub Copilot bearer token."""
    engine = AgentEngine(api_key="ghp_mock_token_12345")
    
    assert engine.api_key == "ghp_mock_token_12345"
    assert engine._is_copilot_token("ghp_mock_token_12345") is True


def test_agent_engine_detects_copilot_token():
    """Test that AgentEngine detects Copilot tokens correctly."""
    engine = AgentEngine()
    
    # Test various token formats
    assert engine._is_copilot_token("ghp_1234567890abcdef") is True
    assert engine._is_copilot_token("github_pat_1234567890abcdef") is True
    assert engine._is_copilot_token("mock-copilot-token") is True
    assert engine._is_copilot_token("sk-ant-api03-12345") is False  # Anthropic token
    assert engine._is_copilot_token(None) is False


def test_agent_engine_executes_with_copilot():
    """Test executing agent with GitHub Copilot API."""
    engine = AgentEngine(api_key="ghp_mock_token_12345")
    
    # Test task
    task = "Write a Python function to add two numbers"
    
    # Execute using Copilot API
    result = engine.execute("dummy_agent_path", task)
    
    # Should use Copilot API and return success
    assert result.status == ExecutionStatus.SUCCESS
    assert "Mock GitHub Copilot response" in result.output
    assert result.execution_time is not None


def test_agent_engine_copilot_from_env():
    """Test AgentEngine gets Copilot token from environment."""
    with pytest.MonkeyPatch().context() as m:
        m.setenv("GITHUB_COPILOT_TOKEN", "ghp_env_token_12345")
        engine = AgentEngine()
        
        assert engine.api_key == "ghp_env_token_12345"
        assert engine._is_copilot_token(engine.api_key) is True


def test_agent_engine_copilot_error_handling():
    """Test error handling with Copilot API."""
    engine = AgentEngine(api_key="ghp_mock_token_12345")
    
    # Test error scenario
    task = "error test"
    result = engine.execute("dummy_agent_path", task)
    
    assert result.status == ExecutionStatus.ERROR
    assert "GitHub Copilot API error" in result.error


def test_agent_engine_copilot_rate_limit():
    """Test rate limit handling with Copilot API."""
    engine = AgentEngine(api_key="ghp_mock_token_12345")
    
    # Test rate limit scenario
    task = "rate_limit test"
    result = engine.execute("dummy_agent_path", task)
    
    assert result.status == ExecutionStatus.ERROR
    assert "Rate limit" in result.error


def test_agent_engine_execute_with_timeout_copilot():
    """Test execute_with_timeout using Copilot API."""
    engine = AgentEngine(api_key="ghp_mock_token_12345", timeout=30)
    
    task = "Write a Python function"
    result = engine.execute_with_timeout("dummy_agent_path", task)
    
    assert result.status == ExecutionStatus.SUCCESS
    assert "Mock GitHub Copilot response" in result.output


def test_copilot_client_creation():
    """Test that Copilot client is created correctly."""
    engine = AgentEngine(api_key="ghp_mock_token_12345")
    copilot_client = engine._get_copilot_client()
    
    assert copilot_client is not None
    assert copilot_client.bearer_token == "ghp_mock_token_12345"
    assert copilot_client.headers["Authorization"] == "Bearer ghp_mock_token_12345"


def test_copilot_client_not_created_for_non_copilot_token():
    """Test that Copilot client is not created for non-Copilot tokens."""
    engine = AgentEngine(api_key="sk-ant-api03-12345")  # Anthropic token
    copilot_client = engine._get_copilot_client()
    
    assert copilot_client is None


def test_run_agent_convenience_with_copilot():
    """Test run_agent convenience function with Copilot token."""
    from llm_agent_builder.agent_engine import run_agent
    
    result = run_agent(
        agent_path="dummy_path",
        task="Test task",
        api_key="ghp_mock_token_12345",
        use_subprocess=False
    )
    
    assert result["status"] == "success"
    assert "Mock GitHub Copilot response" in result["output"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

