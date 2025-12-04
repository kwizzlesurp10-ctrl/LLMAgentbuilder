# Agent Engine Usage Guide

The `AgentEngine` provides a programmatic way to execute built agents without CLI output, making it ideal for testing agents on HuggingFace Spaces and in automated environments.

## Features

- **Headless Execution**: Run agents without CLI display/output
- **Structured Results**: Get execution results as structured data
- **Timeout Protection**: Built-in timeout and resource limits
- **Multiple Input Methods**: Load agents from files or code strings
- **Error Handling**: Comprehensive error handling and status reporting

## Basic Usage

### Method 1: Using the Convenience Function

```python
from llm_agent_builder import run_agent

# Execute an agent from file
result = run_agent(
    agent_path="generated_agents/newsbot.py",
    task="List the latest alerts",
    api_key="your-api-key",  # Optional, uses env vars if not provided
    use_subprocess=True,     # Recommended for timeout protection
    timeout=60
)

print(f"Status: {result['status']}")
print(f"Output: {result['output']}")
print(f"Execution Time: {result['execution_time']:.2f}s")
```

### Method 2: Using AgentEngine Directly

```python
from llm_agent_builder import AgentEngine, ExecutionStatus

# Create engine instance
engine = AgentEngine(
    api_key="your-api-key",  # Optional, uses env vars if not provided
    timeout=60,
    memory_limit_mb=512
)

# Execute agent
result = engine.execute_with_timeout(
    agent_source="generated_agents/newsbot.py",
    task="List the latest alerts"
)

# Check result
if result.status == ExecutionStatus.SUCCESS:
    print(f"Success: {result.output}")
else:
    print(f"Error: {result.error}")
```

### Method 3: Execute from Code String

```python
from llm_agent_builder import AgentEngine

agent_code = """
class MyAgent:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def run(self, task):
        return f"Processed: {task}"
"""

engine = AgentEngine(api_key="your-api-key")
result = engine.execute_with_timeout(agent_code, "test task")
print(result.output)
```

## API Endpoint Usage

The engine is also available via the FastAPI server at `/api/test-agent`:

```bash
# Test an agent from file path
curl -X POST http://localhost:8000/api/test-agent \
  -H "Content-Type: application/json" \
  -d '{
    "agent_path": "generated_agents/newsbot.py",
    "task": "List the latest alerts",
    "timeout": 60
  }'

# Test an agent from code string
curl -X POST http://localhost:8000/api/test-agent \
  -H "Content-Type: application/json" \
  -d '{
    "agent_code": "class MyAgent:\n    def __init__(self, api_key):\n        self.api_key = api_key\n    def run(self, task):\n        return f\"Processed: {task}\"",
    "task": "test task"
  }'
```

## Response Format

All execution results follow this structure:

```python
{
    "status": "success" | "error" | "timeout" | "api_key_missing" | "agent_not_found",
    "output": "Agent output string",
    "error": "Error message (if status != success)",
    "execution_time": 1.23  # seconds
}
```

## Status Values

- `success`: Agent executed successfully
- `error`: Agent execution failed with an error
- `timeout`: Agent execution exceeded the timeout limit
- `api_key_missing`: No API key found in environment or provided
- `agent_not_found`: Agent file not found

## Command Line Testing

Use the provided test script:

```bash
python scripts/test_engine.py generated_agents/newsbot.py "List the latest alerts"
```

## HuggingFace Spaces Integration

For HuggingFace Spaces, you can use the engine in your Space's app:

```python
from llm_agent_builder import AgentEngine
import gradio as gr

engine = AgentEngine()

def test_agent(agent_code, task):
    result = engine.execute_with_timeout(agent_code, task)
    return result.output if result.status.value == "success" else f"Error: {result.error}"

iface = gr.Interface(
    fn=test_agent,
    inputs=[
        gr.Textbox(label="Agent Code", lines=20),
        gr.Textbox(label="Task")
    ],
    outputs=gr.Textbox(label="Result")
)

iface.launch()
```

## Error Handling

The engine handles various error scenarios:

- **Missing API Key**: Returns `api_key_missing` status
- **File Not Found**: Returns `agent_not_found` status
- **Execution Errors**: Returns `error` status with error message
- **Timeouts**: Returns `timeout` status

Always check the `status` field before using the `output`:

```python
result = engine.execute_with_timeout(agent_path, task)

if result.status == ExecutionStatus.SUCCESS:
    # Safe to use result.output
    process_output(result.output)
else:
    # Handle error
    log_error(result.error)
```

## Best Practices

1. **Use `execute_with_timeout`**: Provides better timeout protection and resource limits
2. **Set Appropriate Timeouts**: Adjust timeout based on expected agent execution time
3. **Handle Errors**: Always check status before using output
4. **Use Environment Variables**: Store API keys in environment variables for security
5. **Test Locally First**: Test agents locally before deploying to production
