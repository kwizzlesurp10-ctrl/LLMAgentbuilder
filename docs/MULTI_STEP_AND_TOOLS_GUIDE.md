# Multi-Step Workflows and Tool Integration Guide

## Overview

LLM Agent Builder supports two powerful features for building production-ready agents:

1. **Multi-Step Workflows**: Agents that can iterate and refine responses over multiple steps
2. **Tool Integration**: Agents that can use custom tools to extend their capabilities

## Multi-Step Workflows

### What are Multi-Step Workflows?

Multi-step workflows allow agents to break down complex tasks into multiple steps, iterating and refining their responses. This is particularly useful for:

- Research tasks that require gathering information from multiple sources
- Code generation that needs refinement
- Analysis tasks that benefit from iterative thinking
- Complex problem-solving that requires multiple passes

### How It Works

When `enable_multi_step=True`, the generated agent includes a `run_multi_step()` method that:

1. Executes the initial task
2. Evaluates if the response is complete
3. Iteratively refines the response if needed
4. Continues for up to `max_steps` iterations (default: 5)

### Usage Examples

#### CLI

```bash
llm-agent-builder generate \
  --name "ResearchAgent" \
  --prompt "You are a research assistant" \
  --task "Research AI impact on healthcare" \
  --model "gemini-1.5-pro" \
  --provider "google" \
  --enable-multi-step
```

#### Python API

```python
from llm_agent_builder.agent_builder import AgentBuilder

builder = AgentBuilder()
code = builder.build_agent(
    agent_name="ResearchAgent",
    prompt="You are a research assistant",
    example_task="Research topic X",
    model="gemini-1.5-pro",
    provider="google",
    enable_multi_step=True
)
```

#### HTTP API

```json
POST /api/generate
{
  "name": "ResearchAgent",
  "prompt": "You are a research assistant",
  "task": "Research topic X",
  "model": "gemini-1.5-pro",
  "provider": "google",
  "enable_multi_step": true
}
```

#### Using the Generated Agent

```python
from generated_agents.research_agent import ResearchAgent
import os

agent = ResearchAgent(api_key=os.environ['GOOGLE_GEMINI_KEY'])

# Option 1: Use the run method with use_multi_step flag
result = agent.run("Research topic X", use_multi_step=True)

# Option 2: Use the dedicated run_multi_step method
result = agent.run_multi_step("Research topic X", max_steps=5)
```

## Tool Integration

### What are Tools?

Tools allow agents to extend their capabilities beyond text generation. Agents can call tools to:

- Search the web
- Perform calculations
- Query databases
- Call external APIs
- Execute custom functions

### Tool Definition Format

Tools are defined as JSON Schema objects. Each tool must have:

- `name`: Unique identifier for the tool
- `description`: What the tool does (used by the LLM to decide when to call it)
- `input_schema`: JSON Schema defining the tool's parameters

### Example Tool Definition

```json
{
  "name": "search_web",
  "description": "Search the web for current information",
  "input_schema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "The search query"
      }
    },
    "required": ["query"]
  }
}
```

### Usage Examples

#### CLI

```bash
llm-agent-builder generate \
  --name "ToolAgent" \
  --prompt "You are a helpful assistant with tools" \
  --task "Search for weather and calculate 15 * 23" \
  --model "gemini-1.5-pro" \
  --provider "google" \
  --tools examples/tools_example.json
```

#### Python API

```python
from llm_agent_builder.agent_builder import AgentBuilder
import json

tools = [
    {
        "name": "search_web",
        "description": "Search the web",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    }
]

builder = AgentBuilder()
code = builder.build_agent(
    agent_name="ToolAgent",
    prompt="You are a helpful assistant",
    example_task="Search for information",
    model="gemini-1.5-pro",
    provider="google",
    tools=tools
)
```

#### HTTP API

```json
POST /api/generate
{
  "name": "ToolAgent",
  "prompt": "You are a helpful assistant",
  "task": "Search for information",
  "model": "gemini-1.5-pro",
  "provider": "google",
  "tools": [
    {
      "name": "search_web",
      "description": "Search the web",
      "input_schema": {
        "type": "object",
        "properties": {
          "query": {"type": "string"}
        },
        "required": ["query"]
      }
    }
  ]
}
```

### Implementing Tool Execution

The generated agent includes a `_execute_tool()` method stub. You need to implement it:

```python
def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool call."""
    if tool_name == "search_web":
        query = tool_input["query"]
        # Implement your web search logic
        results = your_search_function(query)
        return {"status": "success", "results": results}
    
    elif tool_name == "calculate":
        expression = tool_input["expression"]
        # Implement your calculation logic
        result = eval(expression)  # Use safe eval in production!
        return {"status": "success", "result": result}
    
    else:
        return {"status": "error", "message": f"Unknown tool: {tool_name}"}
```

**Important**: Always validate and sanitize tool inputs in production!

## Combining Multi-Step Workflows and Tools

You can combine both features for powerful agents:

```bash
llm-agent-builder generate \
  --name "AdvancedAgent" \
  --prompt "You are an expert assistant" \
  --task "Complete complex task" \
  --model "gemini-1.5-pro" \
  --provider "google" \
  --enable-multi-step \
  --tools examples/tools_example.json
```

This creates an agent that can:
- Use tools to gather information or perform actions
- Iterate over multiple steps to refine responses
- Combine tool results across multiple steps

## Provider Support

### Multi-Step Workflows

- ✅ **Google Gemini**: Full support
- ✅ **Anthropic Claude**: Full support
- ✅ **OpenAI**: Full support
- ⚠️ **HuggingFace/HuggingChat**: Basic support (may vary by model)

### Tool Integration

- ✅ **Anthropic Claude**: Full support (native tool calling)
- ✅ **OpenAI**: Full support (function calling)
- ⚠️ **Google Gemini**: Limited support (check model capabilities)
- ⚠️ **HuggingFace/HuggingChat**: Model-dependent (check model documentation)

## Best Practices

### Multi-Step Workflows

1. **Set appropriate max_steps**: More steps = more API calls = higher cost
2. **Use clear completion criteria**: Help the agent know when to stop
3. **Monitor token usage**: Multi-step workflows can consume many tokens
4. **Test completion heuristics**: The default "complete"/"finished" check may need tuning

### Tool Integration

1. **Write clear tool descriptions**: The LLM uses descriptions to decide when to call tools
2. **Validate tool inputs**: Always validate and sanitize inputs
3. **Handle errors gracefully**: Return structured error responses
4. **Limit tool scope**: Keep tools focused and specific
5. **Document tool behavior**: Include examples in descriptions when helpful

### Security

1. **Sanitize tool inputs**: Never trust user input directly
2. **Rate limit tool calls**: Prevent abuse
3. **Validate tool outputs**: Check results before returning to the LLM
4. **Use sandboxing**: For code execution tools, use sandboxed environments
5. **Monitor tool usage**: Log tool calls for security auditing

## Examples

See the `examples/` directory for complete examples:

- `multi_step_agent_example.py`: Multi-step workflow example
- `tools_agent_example.py`: Tool integration example
- `advanced_agent_example.py`: Combined features example
- `tools_example.json`: Sample tool definitions
- `tools_code_reviewer.json`: Code review tools example
- `CLI_EXAMPLES.md`: CLI usage examples

## Troubleshooting

### Multi-Step Workflows

**Issue**: Agent runs all steps even when complete
- **Solution**: Improve completion detection in your prompt or adjust the completion check logic

**Issue**: Too many API calls
- **Solution**: Reduce `max_steps` or improve initial prompt quality

### Tool Integration

**Issue**: Agent doesn't call tools
- **Solution**: Improve tool descriptions, check provider support, verify tool schema format

**Issue**: Tool execution errors
- **Solution**: Implement proper error handling in `_execute_tool()`, validate inputs

**Issue**: Invalid tool schema
- **Solution**: Validate JSON Schema format, check required fields

## Next Steps

1. Review the examples in `examples/`
2. Generate your first multi-step agent
3. Define tools for your use case
4. Test and iterate on your agent design
5. Deploy to production with proper error handling and monitoring

For more information, see:
- [README.md](README.md) - General project documentation
- [HUGGINGFACE_GUIDE.md](HUGGINGFACE_GUIDE.md) - HuggingFace-specific features
- [examples/CLI_EXAMPLES.md](examples/CLI_EXAMPLES.md) - CLI usage examples
