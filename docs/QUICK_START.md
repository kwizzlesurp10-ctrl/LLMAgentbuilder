# Quick Start: Multi-Step Workflows & Tool Integration

## 🚀 Get Started in 3 Steps

### Step 1: Verify Setup

```bash
python setup_multi_step_tools.py
```

All checks should pass ✅

### Step 2: Generate Your First Agent

**Option A: Multi-Step Workflow Agent**

```bash
llm-agent-builder generate \
  --name "MyResearchAgent" \
  --prompt "You are a research assistant" \
  --task "Research topic X" \
  --model "gemini-1.5-pro" \
  --provider "google" \
  --enable-multi-step
```

**Option B: Agent with Tools**

```bash
llm-agent-builder generate \
  --name "MyToolAgent" \
  --prompt "You are a helpful assistant" \
  --task "Use tools to help users" \
  --model "gemini-1.5-pro" \
  --provider "google" \
  --tools examples/tools_example.json
```

**Option C: Advanced Agent (Both Features)**

```bash
llm-agent-builder generate \
  --name "MyAdvancedAgent" \
  --prompt "You are an expert assistant" \
  --task "Complete complex task" \
  --model "gemini-1.5-pro" \
  --provider "google" \
  --enable-multi-step \
  --tools examples/tools_example.json
```

### Step 3: Use Your Agent

```python
from generated_agents.my_research_agent import MyResearchAgent
import os

# Set your API key
os.environ['GOOGLE_GEMINI_KEY'] = 'your-key-here'

# Create agent
agent = MyResearchAgent(api_key=os.environ['GOOGLE_GEMINI_KEY'])

# Use it!
result = agent.run("Research AI trends in 2024")
print(result)

# For multi-step agents:
result = agent.run_multi_step("Research AI trends", max_steps=5)
print(result)
```

## 📋 Common Use Cases

### Research & Analysis

```bash
llm-agent-builder generate \
  --name "ResearchAgent" \
  --prompt "You are a thorough researcher" \
  --task "Research and analyze topic X" \
  --enable-multi-step
```

### Code Review

```bash
llm-agent-builder generate \
  --name "CodeReviewer" \
  --prompt "You are an expert code reviewer" \
  --task "Review code for bugs and improvements" \
  --enable-multi-step \
  --tools examples/tools_code_reviewer.json
```

### Data Analysis

```bash
llm-agent-builder generate \
  --name "DataAnalyst" \
  --prompt "You are a data analyst" \
  --task "Analyze data and provide insights" \
  --enable-multi-step
```

## 🎯 When to Use Each Feature

### Use Multi-Step Workflows When

- ✅ Task requires iterative refinement
- ✅ Complex problem-solving needed
- ✅ Research or analysis tasks
- ✅ Code generation that needs refinement

### Use Tool Integration When

- ✅ Need external data (web search, APIs)
- ✅ Mathematical calculations
- ✅ Database queries
- ✅ Custom functionality required

### Use Both When

- ✅ Complex tasks requiring both iteration and external tools
- ✅ Production-ready agents
- ✅ Maximum capability needed

## 🔧 Tool Definition Format

Create a JSON file with your tools:

```json
[
  {
    "name": "tool_name",
    "description": "What the tool does",
    "input_schema": {
      "type": "object",
      "properties": {
        "param": {
          "type": "string",
          "description": "Parameter description"
        }
      },
      "required": ["param"]
    }
  }
]
```

See `examples/tools_example.json` for complete examples.

## 🌐 Provider Support

| Feature | Google Gemini | Anthropic Claude | OpenAI | HuggingFace |
|---------|--------------|------------------|--------|-------------|
| Multi-Step | ✅ | ✅ | ✅ | ⚠️ |
| Tools | ⚠️ | ✅ | ✅ | ⚠️ |

✅ = Full support | ⚠️ = Model-dependent

## 📚 More Resources

- **Full Guide**: [MULTI_STEP_AND_TOOLS_GUIDE.md](MULTI_STEP_AND_TOOLS_GUIDE.md)
- **CLI Examples**: [examples/CLI_EXAMPLES.md](../examples/CLI_EXAMPLES.md)
- **Setup Summary**: [SETUP_SUMMARY.md](SETUP_SUMMARY.md)
- **Demo Script**: `python demo_multi_step_tools.py`

## 🐛 Troubleshooting

**Agent doesn't use tools?**

- Check tool descriptions are clear
- Verify provider supports tool calling
- Ensure tool schema is valid JSON

**Multi-step runs too many steps?**

- Reduce `max_steps` parameter
- Improve completion detection in prompt

**Need help?**

- Check [MULTI_STEP_AND_TOOLS_GUIDE.md](MULTI_STEP_AND_TOOLS_GUIDE.md)
- Review examples in `examples/`
- Run `python setup_multi_step_tools.py` to verify setup

---

**Ready to build powerful agents!** 🚀
