import subprocess
import tempfile
import os
import sys

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
    
    # Create a temporary file for the code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name

    try:
        # Define resource limits
        def set_limits():
            if resource:
                # CPU time limit (soft, hard)
                resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout + 5))
                
                # Memory limit (soft, hard)
                mem_limit_bytes = memory_limit_mb * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (mem_limit_bytes, mem_limit_bytes))


        # Run the script
        # We pass the task as a command line argument
        # Note: The generated agents expect --task argument
        cmd = [sys.executable, temp_file_path, "--task", task]
        
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
    finally:
        # Clean up
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
