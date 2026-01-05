# HuggingFace Integration Guide

## Overview

LLM Agent Builder now features comprehensive HuggingFace integration, including support for:

- **HuggingChat**: Conversational AI using open-source models
- **HuggingFace Inference API**: Direct access to thousands of models
- **Model Context Protocol (MCP)**: Standardized interface for HuggingFace resources
- **Safety Features**: Built-in content moderation and safety checks
- **Dataset Integration**: Easy access to HuggingFace datasets

## Quick Start

### 1. Set Up Your API Token

```bash
export HUGGINGFACEHUB_API_TOKEN="your_token_here"
```

Or add it to your `.env` file:

```
HUGGINGFACEHUB_API_TOKEN=hf_...
```

Get your token from: https://huggingface.co/settings/tokens

### 2. Generate a HuggingChat Agent

```bash
llm-agent-builder generate \
  --name "ChatAssistant" \
  --prompt "You are a helpful AI assistant" \
  --task "Help users with coding questions" \
  --provider huggingchat \
  --model "meta-llama/Meta-Llama-3.1-70B-Instruct"
```

### 3. Run Your Agent

```bash
python generated_agents/chatassistant.py --task "Explain Python decorators"
```

## HuggingChat Features

### Supported Models

HuggingChat provides access to powerful open-source models:

- **Meta-Llama 3.1 70B Instruct** (Default, best performance)
- **Meta-Llama 3.1 8B Instruct** (Faster, good for most tasks)
- **Mistral 7B Instruct v0.3** (Efficient, great for general use)
- **Mixtral 8x7B Instruct** (Mixture of experts, high quality)
- **CodeLlama 34B Instruct** (Specialized for coding tasks)
- **Zephyr 7B Beta** (Optimized for chat)

### Using HuggingChat API Directly

```python
from llm_agent_builder.huggingchat_client import HuggingChatClient

# Initialize client
client = HuggingChatClient(model="meta-llama/Meta-Llama-3.1-70B-Instruct")

# Simple chat
response = client.chat("What is machine learning?")
print(response)

# With system prompt
response = client.chat(
    "Write a Python function to sort a list",
    system_prompt="You are an expert Python developer"
)

# Streaming response
response = client.chat(
    "Explain neural networks",
    stream=True  # Prints as it generates
)
```

### Conversation History

HuggingChat agents maintain conversation history automatically:

```python
agent = ChatAssistant()

# First message
response1 = agent.run("My name is Alice")

# Context is maintained
response2 = agent.run("What's my name?")
# -> "Your name is Alice"

# Clear history when needed
agent.clear_history()
```

### Advanced Features

#### Search for Models

```python
from llm_agent_builder.huggingchat_client import HuggingChatClient

client = HuggingChatClient()
models = client.search_models("code generation", task="text-generation")

for model in models:
    print(f"{model['id']}: {model['downloads']} downloads")
```

#### Command-Line Model Search

```bash
python generated_agents/chatassistant.py \
  --search-model "sentiment analysis"
```

## HuggingFace MCP Integration

Model Context Protocol (MCP) provides a standardized way to interact with HuggingFace resources.

### Using MCP Client

```python
from llm_agent_builder.hf_mcp_integration import HuggingFaceMCPClient

# Initialize MCP client
mcp = HuggingFaceMCPClient()

# List available tools
tools = mcp.get_available_tools()
for tool in tools:
    print(f"{tool.name}: {tool.description}")

# Search models with safety info
result = mcp.call_tool("search_models", {
    "query": "text generation",
    "limit": 5
})

# Get model safety information
safety = mcp.call_tool("get_model_safety", {
    "model_id": "meta-llama/Meta-Llama-3.1-70B-Instruct"
})
print(f"Has safety features: {safety['has_safety_features']}")
print(f"License: {safety['license']}")

# Run inference safely
result = mcp.call_tool("inference", {
    "model_id": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "inputs": "Hello, how are you?",
    "parameters": {"max_new_tokens": 50}
})
```

### Available MCP Tools

1. **search_models** - Find models on HuggingFace Hub
2. **search_datasets** - Find datasets on HuggingFace Hub
3. **search_spaces** - Find Spaces on HuggingFace Hub
4. **get_model_info** - Get detailed model information
5. **get_model_safety** - Check safety features and licensing
6. **inference** - Run model inference

### MCP-Enabled Agent

Generate an agent with full MCP capabilities:

```python
from llm_agent_builder.hf_mcp_integration import create_mcp_agent_template

# Get the template code
code = create_mcp_agent_template()

# Save to file
with open("mcp_agent.py", "w") as f:
    f.write(code)

# Run it
# python mcp_agent.py --search "sentiment analysis" --task "text-classification"
```

### Export MCP Configuration

```python
from llm_agent_builder.hf_mcp_integration import HuggingFaceMCPClient

client = HuggingFaceMCPClient()
client.export_mcp_config("hf_mcp_config.json")
```

This creates a configuration file that can be used with MCP-compatible tools.

## Safety Features

### Content Moderation

All HuggingChat agents include built-in safety features:

```python
# Check model safety before use
agent = ChatAssistant()
safety_info = agent.get_model_safety_info("meta-llama/Meta-Llama-3.1-70B-Instruct")

if safety_info['has_safety_checker']:
    print("✓ Model has safety features enabled")
else:
    print("⚠ Model may not have safety features")
```

### Gated Models

Some models require additional approval:

```python
# MCP client automatically checks for gated models
mcp = HuggingFaceMCPClient()
info = mcp.call_tool("get_model_info", {"model_id": "some-gated-model"})

if info.get('gated'):
    print("This model requires acceptance of terms")
```

## Dataset Integration

Access HuggingFace datasets in your agents:

```python
from llm_agent_builder.huggingchat_client import HuggingChatClient

client = HuggingChatClient()

# Search for datasets
datasets = client.search_datasets("sentiment analysis", limit=5)
for dataset in datasets:
    print(f"Dataset: {dataset}")

# Use in agent
agent = ChatAssistant()
result = agent.run("Analyze the IMDB movie review dataset")
```

## Inference Endpoints

### Using Inference API

HuggingFace Inference API is automatically used by HuggingChat agents:

```python
from huggingface_hub import InferenceClient

client = InferenceClient(token="your_token")

# Text generation
response = client.text_generation(
    "Once upon a time",
    model="meta-llama/Meta-Llama-3.1-8B-Instruct",
    max_new_tokens=100
)

# Chat completion
messages = [
    {"role": "user", "content": "What is AI?"}
]
response = client.chat_completion(
    messages=messages,
    model="meta-llama/Meta-Llama-3.1-70B-Instruct"
)
```

### Dedicated Inference Endpoints

For production use, consider using Dedicated Inference Endpoints for:
- Lower latency
- Higher throughput
- Custom configurations
- Better security

Learn more: https://huggingface.co/inference-endpoints

## API Reference

### HuggingChatClient

```python
class HuggingChatClient:
    def __init__(
        self,
        token: Optional[str] = None,
        model: Optional[str] = None,
        base_url: str = "https://huggingface.co/chat"
    )
    
    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False
    ) -> str
    
    def clear_history(self) -> None
    
    def get_available_models(self) -> List[str]
    
    def search_models(
        self,
        query: str,
        task: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]
```

### HuggingFaceMCPClient

```python
class HuggingFaceMCPClient:
    def __init__(self, token: Optional[str] = None)
    
    def get_available_tools(self) -> List[MCPTool]
    
    def get_resources(
        self,
        resource_type: Optional[MCPResourceType] = None,
        limit: int = 10
    ) -> List[MCPResource]
    
    def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]
    
    def export_mcp_config(
        self,
        output_path: str = "hf_mcp_config.json"
    ) -> None
```

## Examples

### Example 1: Code Generation Agent

```bash
llm-agent-builder generate \
  --name "CodeGenerator" \
  --prompt "You are an expert programmer specializing in Python" \
  --task "Generate efficient, well-documented code" \
  --provider huggingchat \
  --model "codellama/CodeLlama-34b-Instruct-hf"
```

### Example 2: Data Analysis Agent

```bash
llm-agent-builder generate \
  --name "DataAnalyst" \
  --prompt "You are a data scientist expert in pandas and visualization" \
  --task "Analyze datasets and provide insights" \
  --provider huggingchat \
  --model "meta-llama/Meta-Llama-3.1-70B-Instruct"
```

### Example 3: Safety-First Agent

```python
from llm_agent_builder.hf_mcp_integration import HuggingFaceMCPClient

class SafetyFirstAgent:
    def __init__(self):
        self.mcp = HuggingFaceMCPClient()
    
    def run_with_safety_check(self, model_id: str, prompt: str):
        # Check safety first
        safety = self.mcp.call_tool("get_model_safety", {"model_id": model_id})
        
        if not safety.get("has_safety_features"):
            print("⚠ Warning: Model lacks safety features")
            return None
        
        # Run inference
        result = self.mcp.call_tool("inference", {
            "model_id": model_id,
            "inputs": prompt
        })
        
        return result
```

## Troubleshooting

### API Token Issues

**Problem**: `HUGGINGFACEHUB_API_TOKEN not set`

**Solution**:
```bash
export HUGGINGFACEHUB_API_TOKEN="hf_your_token_here"
```

### Rate Limiting

**Problem**: Too many requests error

**Solution**: 
- Use HuggingFace Pro for higher limits
- Implement exponential backoff
- Cache results when possible

### Model Not Found

**Problem**: Model ID not recognized

**Solution**:
```python
# Search for similar models
from llm_agent_builder.huggingchat_client import HuggingChatClient

client = HuggingChatClient()
models = client.search_models("your search term")
print("Available models:", [m['id'] for m in models])
```

### Gated Model Access

**Problem**: Cannot access gated model

**Solution**:
1. Visit the model page on HuggingFace
2. Accept the model's terms and conditions
3. Wait for approval (usually instant)
4. Retry with your token

## Best Practices

### 1. Always Check Safety

```python
# Before using any model
safety_info = mcp.call_tool("get_model_safety", {"model_id": model_id})
if safety_info['has_safety_features']:
    # Proceed
    pass
```

### 2. Use Appropriate Models

- **Chat/General**: Meta-Llama 3.1 70B
- **Code**: CodeLlama 34B
- **Speed**: Meta-Llama 3.1 8B or Mistral 7B
- **Efficiency**: Zephyr 7B

### 3. Implement Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_model_info(model_id: str):
    return mcp.call_tool("get_model_info", {"model_id": model_id})
```

### 4. Handle Errors Gracefully

```python
try:
    result = agent.run(task)
except RuntimeError as e:
    if "rate limit" in str(e).lower():
        time.sleep(60)  # Wait and retry
    else:
        raise
```

### 5. Clear History for New Topics

```python
# When switching topics
agent.clear_history()
new_result = agent.run("New topic...")
```

## Additional Resources

- [HuggingFace Documentation](https://huggingface.co/docs)
- [HuggingChat Models](https://huggingface.co/chat/models)
- [Inference API Docs](https://huggingface.co/docs/api-inference/)
- [Model Cards](https://huggingface.co/docs/hub/model-cards)
- [Dataset Library](https://huggingface.co/docs/datasets/)
- [Safety Guidelines](https://huggingface.co/blog/content-moderation)

## Contributing

We welcome contributions to improve HuggingFace integration! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This integration is part of LLM Agent Builder, licensed under MIT License.
