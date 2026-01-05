"""
Agent Engine - Programmatic execution engine for testing built agents.

This module provides a headless way to execute agents without CLI output,
designed for testing agents on HuggingFace Spaces and other server
environments.
"""

import os
import sys
import importlib.util
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum

# Import configuration manager
from llm_agent_builder.config import get_config_manager

# Import GitHub Copilot client if available
try:
    from llm_agent_builder.copilot_client import CopilotClient
    COPILOT_AVAILABLE = True
except ImportError:
    COPILOT_AVAILABLE = False


class ExecutionStatus(Enum):
    """Status of agent execution."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    API_KEY_MISSING = "api_key_missing"
    AGENT_NOT_FOUND = "agent_not_found"


@dataclass
class ExecutionResult:
    """Result of agent execution."""
    status: ExecutionStatus
    output: str
    error: Optional[str] = None
    execution_time: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time
        }


class AgentEngine:
    """
    Engine for programmatically executing agents without CLI output.

    This engine can load agents from files or code strings and execute them
    in a headless manner, returning structured results suitable for testing
    and API responses.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 60,
        memory_limit_mb: int = 512
    ):
        """
        Initialize the Agent Engine.

        :param api_key: API key for the agent (if not provided, will try
            env vars)
        :param timeout: Execution timeout in seconds
        :param memory_limit_mb: Memory limit in megabytes
        """
        self.timeout = timeout
        self.memory_limit_mb = memory_limit_mb
        self.api_key = api_key or self._get_api_key()

    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment variables."""
        config_manager = get_config_manager()
        api_key = config_manager.get_any_api_key()
        if not api_key:
            # Fallback to GitHub Copilot token
            api_key = os.environ.get("GITHUB_COPILOT_TOKEN")
        return api_key

    def _is_copilot_token(self, token: Optional[str]) -> bool:
        """Check if token is a GitHub Copilot bearer token."""
        if not token:
            return False
        prefixes = ["ghp_", "github_pat_", "mock-copilot-"]
        return any(token.startswith(prefix) for prefix in prefixes)

    def _get_copilot_client(self) -> Optional[Any]:
        """Get GitHub Copilot client if available and token is present."""
        if not COPILOT_AVAILABLE:
            return None

        token = self.api_key
        if token and self._is_copilot_token(token):
            try:
                return CopilotClient(bearer_token=token)
            except Exception:
                return None
        return None

    def _load_agent_from_file(self, agent_path: Union[str, Path]) -> Any:
        """
        Load an agent class from a Python file.

        :param agent_path: Path to the agent Python file
        :return: Agent class
        """
        agent_path = Path(agent_path)
        if not agent_path.exists():
            raise FileNotFoundError(f"Agent file not found: {agent_path}")

        # Load the module dynamically
        spec = importlib.util.spec_from_file_location(
            "agent_module", agent_path
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load agent from {agent_path}")

        module = importlib.util.module_from_spec(spec)

        # Add the directory to sys.path temporarily for imports
        original_path = sys.path.copy()
        try:
            sys.path.insert(0, str(agent_path.parent))
            spec.loader.exec_module(module)
        finally:
            sys.path[:] = original_path

        # Find the agent class (first class defined in the module that's
        # not imported)
        agent_class = None
        for name, obj in module.__dict__.items():
            if (
                isinstance(obj, type) and
                name[0].isupper() and
                hasattr(obj, 'run') and
                callable(getattr(obj, 'run'))
            ):
                agent_class = obj
                break

        if agent_class is None:
            raise ValueError(f"No agent class found in {agent_path}")

        return agent_class

    def _load_agent_from_code(self, code: str) -> Any:
        """
        Load an agent class from code string.

        :param code: Python code string containing the agent class
        :return: Agent class
        """
        # Create a temporary file and load from it
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False
        ) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        try:
            return self._load_agent_from_file(temp_file_path)
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    def execute(
        self,
        agent_source: Union[str, Path],
        task: str,
        agent_name: Optional[str] = None
    ) -> ExecutionResult:
        """
        Execute an agent with a given task.

        :param agent_source: Path to agent file or code string
        :param task: Task to execute
        :param agent_name: Optional agent class name (auto-detected if not
            provided)
        :return: ExecutionResult with status and output
        """
        import time
        start_time = time.time()

        try:
            # Check API key
            if not self.api_key:
                config_manager = get_config_manager()
                status = config_manager.get_configuration_status()
                configured = [info['env_var'] for info in status.values() if info['configured']]
                
                error_msg = (
                    "API key not found. Please configure at least one provider:\n"
                    + "\n".join(f"  - {info['name']}: {info['env_var']}" 
                               for info in status.values())
                    + (f"\n\nCurrently configured: {', '.join(configured)}" if configured else "")
                )
                return ExecutionResult(
                    status=ExecutionStatus.API_KEY_MISSING,
                    output="",
                    error=error_msg,
                    execution_time=time.time() - start_time
                )

            # Check if using GitHub Copilot API
            copilot_client = self._get_copilot_client()
            if copilot_client:
                # Use GitHub Copilot API for execution
                return self._execute_with_copilot(
                    agent_source, task, copilot_client, start_time
                )

            # Determine if source is file or code
            is_file = False
            if isinstance(agent_source, Path):
                is_file = True
            elif isinstance(agent_source, str):
                if '\n' in agent_source:
                    is_file = False
                elif (os.path.exists(agent_source) or
                      agent_source.endswith('.py')):
                    is_file = True

            if is_file:
                agent_path = Path(agent_source)
                if not agent_path.exists():
                    return ExecutionResult(
                        status=ExecutionStatus.AGENT_NOT_FOUND,
                        output="",
                        error=f"Agent file not found: {agent_source}",
                        execution_time=time.time() - start_time
                    )
                agent_class = self._load_agent_from_file(agent_path)
            else:
                # Assume it's code string
                agent_class = self._load_agent_from_code(str(agent_source))

            # Instantiate agent
            agent = agent_class(api_key=self.api_key)

            # Execute agent
            result = agent.run(task)

            # Convert result to string if needed
            if not isinstance(result, str):
                result = str(result)

            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                output=result,
                execution_time=time.time() - start_time
            )

        except FileNotFoundError as e:
            return ExecutionResult(
                status=ExecutionStatus.AGENT_NOT_FOUND,
                output="",
                error=str(e),
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error=str(e),
                execution_time=time.time() - start_time
            )

    def execute_with_timeout(
        self,
        agent_source: Union[str, Path],
        task: str,
        agent_name: Optional[str] = None
    ) -> ExecutionResult:
        """
        Execute an agent with timeout protection using subprocess.

        This method uses subprocess to ensure proper timeout handling
        and resource limits, similar to the sandbox execution.

        :param agent_source: Path to agent file or code string
        :param task: Task to execute
        :param agent_name: Optional agent class name (auto-detected if not
            provided)
        :return: ExecutionResult with status and output
        """
        import subprocess
        import time
        import tempfile

        start_time = time.time()
        temp_file_created = False

        try:
            # Check API key
            if not self.api_key:
                config_manager = get_config_manager()
                status = config_manager.get_configuration_status()
                configured = [info['env_var'] for info in status.values() if info['configured']]
                
                error_msg = (
                    "API key not found. Please configure at least one provider:\n"
                    + "\n".join(f"  - {info['name']}: {info['env_var']}" 
                               for info in status.values())
                    + (f"\n\nCurrently configured: {', '.join(configured)}" if configured else "")
                )
                return ExecutionResult(
                    status=ExecutionStatus.API_KEY_MISSING,
                    output="",
                    error=error_msg,
                    execution_time=time.time() - start_time
                )

            # Check if using GitHub Copilot API
            copilot_client = self._get_copilot_client()
            if copilot_client:
                # Use GitHub Copilot API for execution
                return self._execute_with_copilot(
                    agent_source, task, copilot_client, start_time
                )

            # Determine if source is file or code
            is_file = False
            if isinstance(agent_source, Path):
                is_file = True
            elif isinstance(agent_source, str):
                if '\n' in agent_source:
                    is_file = False
                elif (os.path.exists(agent_source) or
                      agent_source.endswith('.py')):
                    is_file = True

            if is_file:
                agent_path = Path(agent_source)
                if not agent_path.exists():
                    return ExecutionResult(
                        status=ExecutionStatus.AGENT_NOT_FOUND,
                        output="",
                        error=f"Agent file not found: {agent_source}",
                        execution_time=time.time() - start_time
                    )
                agent_file = str(agent_path.absolute())
            else:
                # Create temporary file from code string
                with tempfile.NamedTemporaryFile(
                    mode='w', suffix='.py', delete=False
                ) as temp_file:
                    temp_file.write(str(agent_source))
                    agent_file = temp_file.name
                    temp_file_created = True

            # Execute via subprocess with timeout
            cmd = [sys.executable, agent_file, "--task", task]

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    env={**os.environ, **self._get_env_with_api_key()}
                )

                output = result.stdout
                if result.stderr:
                    output += f"\\n[stderr]\\n{result.stderr}"

                if result.returncode == 0:
                    return ExecutionResult(
                        status=ExecutionStatus.SUCCESS,
                        output=output,
                        execution_time=time.time() - start_time
                    )
                else:
                    return ExecutionResult(
                        status=ExecutionStatus.ERROR,
                        output=output,
                        error=f"Agent exited with code {result.returncode}",
                        execution_time=time.time() - start_time
                    )

            except subprocess.TimeoutExpired:
                return ExecutionResult(
                    status=ExecutionStatus.TIMEOUT,
                    output="",
                    error=f"Execution timed out after {self.timeout} seconds",
                    execution_time=time.time() - start_time
                )
            finally:
                # Clean up temp file if we created it
                if temp_file_created and os.path.exists(agent_file):
                    os.remove(agent_file)

        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error=str(e),
                execution_time=time.time() - start_time
            )

    def _execute_with_copilot(
        self,
        agent_source: Union[str, Path],
        task: str,
        copilot_client: Any,
        start_time: float
    ) -> ExecutionResult:
        """
        Execute agent using GitHub Copilot API.

        :param agent_source: Path to agent file or code string
        :param task: Task to execute
        :param copilot_client: GitHub Copilot client instance
        :param start_time: Start time for execution timing
        :return: ExecutionResult with status and output
        """
        import time

        try:
            # Use Copilot chat completion API
            messages = [
                {"role": "user", "content": task}
            ]

            response = copilot_client.get_chat_completion(messages=messages)

            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                output=response.content,
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error=f"GitHub Copilot API error: {str(e)}",
                execution_time=time.time() - start_time
            )

    def _get_env_with_api_key(self) -> Dict[str, str]:
        """Get environment variables with API key set."""
        env = {}
        if self.api_key:
            # Determine which key to set based on what's available
            if self._is_copilot_token(self.api_key):
                env["GITHUB_COPILOT_TOKEN"] = self.api_key
            elif os.environ.get("GOOGLE_GEMINI_KEY"):
                env["GOOGLE_GEMINI_KEY"] = self.api_key
            elif os.environ.get("HUGGINGFACEHUB_API_TOKEN"):
                env["HUGGINGFACEHUB_API_TOKEN"] = self.api_key
            else:
                # Default to Google Gemini if we can't determine
                env["GOOGLE_GEMINI_KEY"] = self.api_key
        return env


def run_agent(
    agent_path: Union[str, Path],
    task: str,
    api_key: Optional[str] = None,
    use_subprocess: bool = True,
    timeout: int = 60
) -> Dict[str, Any]:
    """
    Convenience function to run an agent and return results as dictionary.

    :param agent_path: Path to agent file
    :param task: Task to execute
    :param api_key: Optional API key (uses env vars if not provided)
    :param use_subprocess: Whether to use subprocess execution (recommended
        for timeout protection)
    :param timeout: Execution timeout in seconds
    :return: Dictionary with execution results
    """
    engine = AgentEngine(api_key=api_key, timeout=timeout)

    if use_subprocess:
        result = engine.execute_with_timeout(agent_path, task)
    else:
        result = engine.execute(agent_path, task)

    return result.to_dict()
