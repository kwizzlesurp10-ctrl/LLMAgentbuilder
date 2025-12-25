import os
import sys
from pathlib import Path

import pytest

from llm_agent_builder.utils import (
    API_KEY_MISSING_ERROR,
    build_agent_command,
    get_api_key,
    is_agent_file_path,
    is_copilot_token,
    temporary_python_file,
)


def test_get_api_key_with_anthropic(monkeypatch):
    """Test API key retrieval with ANTHROPIC_API_KEY set."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.delenv("HUGGINGFACEHUB_API_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_COPILOT_TOKEN", raising=False)

    assert get_api_key() == "test-anthropic-key"


def test_get_api_key_with_huggingface(monkeypatch):
    """Test API key retrieval with HUGGINGFACEHUB_API_TOKEN set."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("HUGGINGFACEHUB_API_TOKEN", "test-hf-key")
    monkeypatch.delenv("GITHUB_COPILOT_TOKEN", raising=False)

    assert get_api_key() == "test-hf-key"


def test_get_api_key_with_copilot(monkeypatch):
    """Test API key retrieval with GITHUB_COPILOT_TOKEN set."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("HUGGINGFACEHUB_API_TOKEN", raising=False)
    monkeypatch.setenv("GITHUB_COPILOT_TOKEN", "test-copilot-key")

    assert get_api_key() == "test-copilot-key"


def test_get_api_key_none(monkeypatch):
    """Test API key retrieval with no keys set."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("HUGGINGFACEHUB_API_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_COPILOT_TOKEN", raising=False)

    assert get_api_key() is None


def test_get_api_key_priority(monkeypatch):
    """Test that ANTHROPIC_API_KEY has priority."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-key")
    monkeypatch.setenv("HUGGINGFACEHUB_API_TOKEN", "hf-key")
    monkeypatch.setenv("GITHUB_COPILOT_TOKEN", "copilot-key")

    assert get_api_key() == "anthropic-key"


def test_is_copilot_token():
    """Test Copilot token detection."""
    assert is_copilot_token("ghp_abc123") is True
    assert is_copilot_token("github_pat_abc123") is True
    assert is_copilot_token("mock-copilot-token") is True
    assert is_copilot_token("sk-ant-abc123") is False
    assert is_copilot_token("hf_abc123") is False
    assert is_copilot_token(None) is False
    assert is_copilot_token("") is False


def test_temporary_python_file():
    """Test temporary Python file context manager."""
    test_code = "print('Hello, World!')"
    file_path = None

    with temporary_python_file(test_code) as temp_path:
        file_path = temp_path
        # File should exist during context
        assert os.path.exists(temp_path)
        assert temp_path.endswith(".py")

        # Read and verify content
        with open(temp_path, "r") as f:
            content = f.read()
        assert content == test_code

    # File should be cleaned up after context
    assert not os.path.exists(file_path)


def test_temporary_python_file_exception_cleanup():
    """Test that temporary file is cleaned up even on exception."""
    test_code = "print('Test')"
    file_path = None

    try:
        with temporary_python_file(test_code) as temp_path:
            file_path = temp_path
            assert os.path.exists(temp_path)
            # Simulate an exception
            raise ValueError("Test exception")
    except ValueError:
        pass

    # File should still be cleaned up
    assert not os.path.exists(file_path)


def test_is_agent_file_path_with_path_object(tmp_path):
    """Test agent source detection with Path object."""
    test_file = tmp_path / "agent.py"
    test_file.write_text("# test")

    assert is_agent_file_path(test_file) is True


def test_is_agent_file_path_with_existing_file(tmp_path):
    """Test agent source detection with existing file path string."""
    test_file = tmp_path / "agent.py"
    test_file.write_text("# test")

    assert is_agent_file_path(str(test_file)) is True


def test_is_agent_file_path_with_py_extension():
    """Test agent source detection with .py extension (non-existing)."""
    assert is_agent_file_path("nonexistent_agent.py") is True


def test_is_agent_file_path_with_code_string():
    """Test agent source detection with code containing newlines."""
    code = "import os\nprint('Hello')"
    assert is_agent_file_path(code) is False


def test_is_agent_file_path_with_single_line_code():
    """Test agent source detection with single line code."""
    code = "print('Hello')"
    # Single line without .py extension and non-existing file
    assert is_agent_file_path(code) is False


def test_build_agent_command():
    """Test agent command building."""
    cmd = build_agent_command("/path/to/agent.py", "test task")

    assert len(cmd) == 4
    assert cmd[0] == sys.executable
    assert cmd[1] == "/path/to/agent.py"
    assert cmd[2] == "--task"
    assert cmd[3] == "test task"


def test_build_agent_command_custom_python():
    """Test agent command building with custom Python executable."""
    cmd = build_agent_command("/path/to/agent.py", "test task", python_executable="python3")

    assert cmd[0] == "python3"
    assert cmd[1] == "/path/to/agent.py"
    assert cmd[2] == "--task"
    assert cmd[3] == "test task"


def test_api_key_missing_error_constant():
    """Test that API_KEY_MISSING_ERROR constant is defined."""
    assert isinstance(API_KEY_MISSING_ERROR, str)
    assert "API key" in API_KEY_MISSING_ERROR
    assert "ANTHROPIC_API_KEY" in API_KEY_MISSING_ERROR
