"""
Shared utility functions for LLM Agent Builder.

This module provides common functionality used across different components
to avoid code duplication.
"""

import os
import tempfile
from typing import Optional, List
from contextlib import contextmanager
from pathlib import Path


# Constants
API_KEY_MISSING_ERROR = "API key not found. Set ANTHROPIC_API_KEY, HUGGINGFACEHUB_API_TOKEN, or GITHUB_COPILOT_TOKEN"


def get_api_key() -> Optional[str]:
    """
    Get API key from environment variables.
    
    Checks for API keys in the following order:
    1. ANTHROPIC_API_KEY
    2. HUGGINGFACEHUB_API_TOKEN
    3. GITHUB_COPILOT_TOKEN
    
    :return: API key if found, None otherwise
    """
    return (
        os.environ.get("ANTHROPIC_API_KEY") or 
        os.environ.get("HUGGINGFACEHUB_API_TOKEN") or
        os.environ.get("GITHUB_COPILOT_TOKEN")
    )


def is_copilot_token(token: Optional[str]) -> bool:
    """
    Check if token is a GitHub Copilot bearer token.
    
    :param token: Token to check
    :return: True if token is a Copilot token, False otherwise
    """
    if not token:
        return False
    return any(token.startswith(prefix) for prefix in ["ghp_", "github_pat_", "mock-copilot-"])


@contextmanager
def temporary_python_file(code: str):
    """
    Context manager for creating and cleaning up temporary Python files.
    
    :param code: Python code to write to the temporary file
    :yields: Path to the temporary file
    """
    temp_file = None
    temp_file_path = None
    
    try:
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        temp_file.write(code)
        temp_file_path = temp_file.name
        temp_file.close()
        
        yield temp_file_path
    finally:
        # Clean up the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


def is_agent_file_path(agent_source: object) -> bool:
    """
    Determine if agent_source is a file path or code string.
    
    :param agent_source: Either a Path object, file path string, or code string
    :return: True if it's a file path, False if it's code
    """
    if isinstance(agent_source, Path):
        return True
    
    if isinstance(agent_source, str):
        # If it contains newlines, it's likely code
        if '\n' in agent_source:
            return False
        # If it exists as a file or has .py extension, treat as path
        if os.path.exists(agent_source) or agent_source.endswith('.py'):
            return True
    
    return False


def build_agent_command(script_path: str, task: str, python_executable: Optional[str] = None) -> List[str]:
    """
    Build a command list for executing an agent script.
    
    :param script_path: Path to the agent Python script
    :param task: Task to pass to the agent
    :param python_executable: Python executable to use (defaults to sys.executable)
    :return: Command list suitable for subprocess execution
    """
    import sys
    
    if python_executable is None:
        python_executable = sys.executable
    
    return [python_executable, script_path, "--task", task]
