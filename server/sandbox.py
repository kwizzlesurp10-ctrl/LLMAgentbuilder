import subprocess
import os
import sys

# Import shared utilities
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_agent_builder.utils import temporary_python_file, build_agent_command

try:
    import resource
except ImportError:
    resource = None


def run_in_sandbox(code: str, task: str, timeout: int = 30, memory_limit_mb: int = 512) -> str:
    """
    Executes the provided Python code in a sandboxed environment.
    
    :param code: The Python code to execute.
    :param task: The task argument to pass to the script.
    :param timeout: Execution timeout in seconds.
    :param memory_limit_mb: Memory limit in megabytes.
    :return: The stdout and stderr output.
    """
    try:
        with temporary_python_file(code) as temp_file_path:
            # Define resource limits
            def set_limits():
                if resource:
                    # CPU time limit (soft, hard)
                    resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout + 5))

                    # Memory limit (soft, hard)
                    mem_limit_bytes = memory_limit_mb * 1024 * 1024
                    resource.setrlimit(resource.RLIMIT_AS, (mem_limit_bytes, mem_limit_bytes))

            # Build command
            cmd = build_agent_command(temp_file_path, task)

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=set_limits
            )

            try:
                stdout, stderr = process.communicate(timeout=timeout)
                output = stdout
                if stderr:
                    output += f"\nErrors:\n{stderr}"
                return output
            except subprocess.TimeoutExpired:
                process.kill()
                return f"Execution timed out after {timeout} seconds."

    except Exception as e:
        return f"Sandbox error: {str(e)}"
