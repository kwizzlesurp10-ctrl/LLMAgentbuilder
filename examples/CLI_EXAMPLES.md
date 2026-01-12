# CLI Examples for Multi-Step Workflows and Tools

## Basic Multi-Step Workflow Agent

Generate an agent with multi-step workflow capabilities:

```bash
llm-agent-builder generate \
  --name "ResearchAgent" \
  --prompt "You are a research assistant that conducts thorough research" \
  --task "Research the impact of AI on healthcare" \
  --model "gemini-1.5-pro" \
  --provider "google" \
  --enable-multi-step
```

## Agent with Tools

Generate an agent with tool integration:

```bash
llm-agent-builder generate \
  --name "ToolAgent" \
  --prompt "You are a helpful assistant with web search and calculator tools" \
  --task "Search for current weather and calculate 15 * 23" \
  --model "gemini-1.5-pro" \
  --provider "google" \
  --tools examples/tools_example.json
```

## Advanced Agent (Multi-Step + Tools)

Generate an agent with both multi-step workflows and tools:

```bash
llm-agent-builder generate \
  --name "AdvancedCodeReviewer" \
  --prompt "You are an expert code reviewer" \
  --task "Review this code for bugs and suggest improvements" \
  --model "gemini-1.5-pro" \
  --provider "google" \
  --enable-multi-step \
  --tools examples/tools_code_reviewer.json
```

## Interactive Mode

Use interactive mode to configure everything step-by-step:

```bash
llm-agent-builder generate --interactive
```

The interactive mode will prompt you for:
- Agent name
- System prompt
- Example task
- Output directory
- Model
- Provider
- Custom template (optional)
- Database path (optional)
- **Enable multi-step workflow** (y/n)
- **Tools JSON file path** (optional)

## Tool Definition Format

Tools must be defined as a JSON array. Each tool should have:

```json
{
  "name": "tool_name",
  "description": "What the tool does",
  "input_schema": {
    "type": "object",
    "properties": {
      "param_name": {
        "type": "string",
        "description": "Parameter description"
      }
    },
    "required": ["param_name"]
  }
}
```

See `examples/tools_example.json` and `examples/tools_code_reviewer.json` for complete examples.

## Testing Generated Agents

After generating an agent, test it:

```bash
# Test with single-step execution
llm-agent-builder test generated_agents/research_agent.py --task "Research topic X"

# For multi-step agents, you can test programmatically:
python -c "
from generated_agents.research_agent import ResearchAgent
import os
agent = ResearchAgent(api_key=os.environ['GOOGLE_GEMINI_KEY'])
result = agent.run_multi_step('Research topic X', max_steps=5)
print(result)
"
```
