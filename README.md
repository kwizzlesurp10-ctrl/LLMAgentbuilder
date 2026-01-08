---
title: LLM Agent Builder
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---

# LLM Agent Builder

> **A powerful, production-ready tool for generating custom LLM agents via CLI, web UI, and Hugging Face Spaces**

LLM Agent Builder is a comprehensive Python application that enables developers to quickly scaffold and generate AI agents using Anthropic's Claude models or Hugging Face models. Built with FastAPI, React 19, and modern Python tooling.

## ✨ Features

- 🚀 **Multi-Provider Support**: Generate agents for Google Gemini, Anthropic Claude, OpenAI, HuggingFace, and HuggingChat models
- 💬 **HuggingChat Integration**: Full support for HuggingChat's open-source conversational models
- 🔒 **Advanced Safety**: Built-in content moderation and safety checking with HuggingFace models
- 🌐 **MCP Integration**: Model Context Protocol support for standardized HuggingFace resource access
- 🎨 **Modern Web UI**: Beautiful React 19 interface with dark/light theme toggle
- 💻 **Powerful CLI**: Interactive mode, batch generation, agent testing, and listing
- 🔧 **Tool Integration**: Built-in support for tool calling and multi-step workflows
- 🛡️ **Production Ready**: Rate limiting, retry logic, input validation, and sandboxed execution
- 📦 **Easy Deployment**: Docker-ready for Hugging Face Spaces with one-command deployment
- 🧪 **Comprehensive Testing**: Full test coverage with pytest and CI/CD

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Node.js 18+ (for web UI)
- pip

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/kwizzlesurp10-ctrl/LLMAgentbuilder.git
   cd LLMAgentbuilder
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the package:**

   ```bash
   pip install -e .
   ```

   Or install dependencies directly:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key:**

   Create a `.env` file:

   ```bash
   # For Google Gemini
   GOOGLE_GEMINI_KEY="your-google-gemini-api-key-here"
   ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"

   # For Hugging Face (optional)
   HUGGINGFACEHUB_API_TOKEN="your-hf-token-here"
   ```

## 📖 Usage

### Web Interface (Default)

The easiest way to use LLM Agent Builder is via the web interface.

1. **Launch the application:**

   ```bash
   python main.py
   # or
   llm-agent-builder
   ```

2. **Access the UI:**

   Open your browser to `http://localhost:7860`.

   The web interface allows you to:
   - Generate agents using a simple form
   - Preview and copy generated code
   - Test agents directly in the browser
   - Switch between dark and light themes

### Command Line Interface

You can still use the CLI for scripting or if you prefer the terminal.

#### Generate an Agent

**Interactive Mode:**

```bash
llm-agent-builder generate --interactive
```

**Command-Line Mode:**

```bash
llm-agent-builder generate \
  --name "CodeReviewer" \
  --prompt "You are an expert code reviewer specializing in Python." \
  --task "Review this function for bugs and suggest improvements." \
  --model "claude-3-5-sonnet-20241022" \
  --provider "anthropic" \
  --template "path/to/your/template.j2"
```

#### List Generated Agents

```bash
llm-agent-builder list
# or specify custom output directory
llm-agent-builder list --output ./my_agents
```

#### Test an Agent

```bash
llm-agent-builder test generated_agents/codereviewer.py --task "Review this code: def add(a, b): return a + b"
```

#### Batch Generation

Create a JSON config file (`agents.json`):

```json
[
  {
    "name": "DataAnalyst",
    "prompt": "You are a data analyst expert in Pandas and NumPy.",
    "task": "Analyze this CSV file and provide summary statistics.",
    "model": "claude-3-5-sonnet-20241022",
    "provider": "anthropic"
  },
  {
    "name": "CodeWriter",
    "prompt": "You are a Python programming assistant.",
    "task": "Write a function to calculate fibonacci numbers.",
    "model": "claude-3-5-sonnet-20241022",
    "provider": "anthropic"
  }
]
```

Then run:

```bash
llm-agent-builder batch agents.json
```

### Web Interface

1. **Start the Backend Server:**

   ```bash
   uvicorn server.main:app --reload
   ```

   The API will be available at `http://localhost:8000`.

2. **Start the Frontend:**

   Open a new terminal:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Open your browser to `http://localhost:5173`.

### Features in Web UI

- ✨ **Live Code Preview**: See generated code in real-time
- 🎨 **Theme Toggle**: Switch between dark and light themes
- 📋 **Copy to Clipboard**: One-click code copying
- 🧪 **Test Agent**: Execute agents directly in the browser (sandboxed)
- 📥 **Auto-Download**: Generated agents automatically download

## ⚙️ Configuration

LLM Agent Builder supports comprehensive YAML-based configuration with environment-specific settings and environment variable overrides.

### Quick Configuration

```bash
# View current configuration
llm-agent-builder config show

# Validate a configuration file
llm-agent-builder config validate --file config/production.yaml

# Generate a configuration template
llm-agent-builder config generate --output my-config.yaml

# Use a custom configuration
llm-agent-builder --config my-config.yaml web
```

### Configuration Files

Configuration files are located in the `config/` directory:

- `config/default.yaml` - Default settings for all environments
- `config/development.yaml` - Development overrides
- `config/production.yaml` - Production settings
- `config/test.yaml` - Test environment settings

### Environment Variable Overrides

Override any configuration value using environment variables:

```bash
# Server settings
SERVER__PORT=8080
SERVER__HOST="localhost"

# Provider settings
PROVIDERS__GOOGLE__RATE_LIMIT=50

# Enable/disable features
ENABLE_RATE_LIMITING=false
ENVIRONMENT=development
```

### Configuration Priority

1. Environment variables (highest priority)
2. Environment-specific config file (`config/{ENV}.yaml`)
3. Default config file (`config/default.yaml`)
4. Built-in defaults

### Example Configuration

```yaml
server:
  host: "0.0.0.0"
  port: 7860
  workers: 4
  reload: false

providers:
  google:
    api_key_env: GOOGLE_GEMINI_KEY
    default_model: gemini-1.5-pro
    rate_limit: 20

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: null

environment: production
enable_metrics: true
enable_rate_limiting: true
```

For complete configuration documentation, see [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

## 🏗️ Architecture

### Project Structure

```
LLMAgentbuilder/
├── llm_agent_builder/      # Core package
│   ├── agent_builder.py    # AgentBuilder class with multi-step & tool support
│   ├── cli.py               # CLI with subcommands (generate, list, test, batch)
│   └── templates/           # Jinja2 templates for agent generation
│       ├── agent_template.py.j2
│       └── agent_template_hf.py.j2
├── server/                  # FastAPI backend
│   ├── main.py             # API endpoints with rate limiting & retries
│   ├── models.py           # Pydantic models for validation
│   └── sandbox.py          # Sandboxed code execution
├── frontend/                # React 19 frontend
│   ├── src/
│   │   ├── App.jsx          # Main app with theme toggle
│   │   └── components/
│   │       ├── AgentForm.jsx    # Agent configuration form
│   │       └── CodePreview.jsx  # Code preview with copy button
│   └── tailwind.config.js   # Tailwind CSS configuration
├── tests/                   # Comprehensive test suite
│   ├── test_agent_builder.py
│   ├── test_cli.py
│   └── test_api.py
├── .github/workflows/       # CI/CD workflows
│   └── ci.yml              # GitHub Actions for testing & linting
├── pyproject.toml          # Modern Python project configuration
├── requirements.txt        # Python dependencies
└── Dockerfile              # Docker configuration for deployment
```

## 🔧 Advanced Features

### Multi-Step Workflows

Agents can be generated with multi-step workflow capabilities that allow iterative refinement:

**CLI:**

```bash
llm-agent-builder generate \
  --name "ResearchAgent" \
  --prompt "You are a research assistant" \
  --task "Research topic X" \
  --enable-multi-step
```

**Python:**

```python
from llm_agent_builder.agent_builder import AgentBuilder

builder = AgentBuilder()
code = builder.build_agent(
    agent_name="ResearchAgent",
    prompt="You are a research assistant",
    example_task="Research topic X",
    enable_multi_step=True
)

# In your generated agent
agent = ResearchAgent(api_key="your-key")
result = agent.run_multi_step("Complete this complex task", max_steps=5)
```

### Tool Integration

Generate agents with tool calling support to extend capabilities:

**CLI:**

```bash
llm-agent-builder generate \
  --name "ToolAgent" \
  --prompt "You are an agent with tools" \
  --task "Use tools to complete tasks" \
  --tools examples/tools_example.json
```

**Python:**

```python
builder = AgentBuilder()
code = builder.build_agent(
    agent_name="ToolAgent",
    prompt="You are an agent with tools",
    example_task="Use tools to complete tasks",
    tools=[
        {
            "name": "search_web",
            "description": "Search the web",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                }
            }
        }
    ],
    enable_multi_step=True  # Can combine with multi-step!
)
```

**📖 See [MULTI_STEP_AND_TOOLS_GUIDE.md](docs/MULTI_STEP_AND_TOOLS_GUIDE.md) for comprehensive documentation and examples.**

### API Endpoints

The FastAPI backend provides:

- `POST /api/generate` - Generate a new agent (rate limited: 20/min)
- `POST /api/execute` - Execute agent code in sandbox (rate limited: 10/min)
- `GET /health` - Health check endpoint
- `GET /healthz` - Kubernetes health check
- `GET /metrics` - Prometheus metrics

## 🧪 Testing

Run the test suite:

```bash
# All tests
pytest

# With coverage
pytest --cov=llm_agent_builder --cov=server --cov-report=html

# Specific test file
pytest tests/test_cli.py -v
```

### Type Checking

```bash
mypy llm_agent_builder server
```

### Linting

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run linters
flake8 llm_agent_builder server tests
black --check llm_agent_builder server tests
isort --check-only llm_agent_builder server tests
```

## 🚢 Deployment

### Hugging Face Spaces

1. Create a new Space on Hugging Face
2. Select **Docker** as the SDK
3. Push the repository:

   ```bash
   git push https://huggingface.co/spaces/your-username/your-space
   ```

   The `Dockerfile` automatically builds the React frontend and serves it via FastAPI.

### Docker

Build and run locally:

```bash
docker build -t llm-agent-builder .
docker run -p 8000:8000 -e GOOGLE_GEMINI_KEY=your-key llm-agent-builder
```

## 📊 Supported Models

### Anthropic Claude

- `claude-3-5-sonnet-20241022` (Default)
- `claude-3-5-haiku-20241022`
- `claude-3-opus-20240229`
- `claude-3-haiku-20240307`

### HuggingFace Inference API

- `meta-llama/Meta-Llama-3-8B-Instruct`
- `mistralai/Mistral-7B-Instruct-v0.3`

### HuggingChat (Conversational)

- `meta-llama/Meta-Llama-3.1-70B-Instruct` (Default, best performance)
- `meta-llama/Meta-Llama-3.1-8B-Instruct` (Faster)
- `mistralai/Mistral-7B-Instruct-v0.3` (Efficient)
- `mistralai/Mixtral-8x7B-Instruct-v0.1` (High quality)
- `codellama/CodeLlama-34b-Instruct-hf` (Specialized for code)
- `HuggingFaceH4/zephyr-7b-beta` (Optimized for chat)

## 🔒 Safety & Content Moderation

LLM Agent Builder includes comprehensive safety features powered by HuggingFace:

- **Content Safety Checking**: Automatic toxicity and hate speech detection
- **Model Safety Validation**: Verify models have safety features before use
- **Safe Agent Wrapper**: Add safety checking to any agent
- **Gated Model Support**: Handle models that require approval

See [HUGGINGFACE_GUIDE.md](docs/HUGGINGFACE_GUIDE.md) for detailed safety documentation.

## 🌐 HuggingFace MCP Integration

Model Context Protocol (MCP) provides standardized access to HuggingFace resources:

- **Model Search & Discovery**: Find and analyze models
- **Dataset Integration**: Access HuggingFace datasets
- **Space Discovery**: Find and explore Spaces
- **Safety Validation**: Check model safety features
- **Inference API**: Run models via standardized interface

```python
from llm_agent_builder.hf_mcp_integration import HuggingFaceMCPClient

mcp = HuggingFaceMCPClient()
models = mcp.call_tool("search_models", {"query": "sentiment", "limit": 5})
```

See [HUGGINGFACE_GUIDE.md](docs/HUGGINGFACE_GUIDE.md) for complete MCP documentation.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Run linting (`black`, `isort`, `flake8`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### Development Setup

```bash
# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Install frontend dependencies
cd frontend && npm install

# Run pre-commit hooks (if configured)
pre-commit install
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Anthropic Claude](https://www.anthropic.com/)
- Powered by [FastAPI](https://fastapi.tiangolo.com/) and [React](https://react.dev/)
- Deployed on [Hugging Face Spaces](https://huggingface.co/spaces)

## 📚 Additional Resources

- [HuggingFace Integration Guide](docs/HUGGINGFACE_GUIDE.md) - **Complete guide to HuggingChat, MCP, and safety features**
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Hugging Face Hub Documentation](https://huggingface.co/docs/hub/)
- [HuggingChat Models](https://huggingface.co/chat/models)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

## 🔌 Extending with Custom Providers

LLM Agent Builder uses a provider registry pattern that makes it easy to add support for new LLM providers without modifying core code.

### Provider Architecture

The system uses an abstract base class `LLMProvider` that defines the interface all providers must implement:

- `get_template_name()` - Returns the Jinja2 template file for generating agents
- `validate_config(config)` - Validates provider-specific configuration
- `get_env_var_name()` - Returns the environment variable name for API keys
- `get_default_model()` - Returns the default model for the provider
- `get_supported_models()` - Returns list of supported models

### Adding a New Provider

To add a new LLM provider, follow these steps:

#### 1. Create a Provider Class

Create a new file `llm_agent_builder/providers/your_provider.py`:

```python
from typing import Dict, List
from .base import LLMProvider, register_provider


@register_provider("your_provider")
class YourProvider(LLMProvider):
    """Provider for Your LLM Service."""
    
    def get_template_name(self) -> str:
        """Return the template file for this provider."""
        return "agent_template_your_provider.py.j2"
    
    def validate_config(self, config: Dict) -> bool:
        """Validate provider-specific configuration."""
        model = config.get("model")
        if model and model not in self.get_supported_models():
            return False
        return True
    
    def get_env_var_name(self) -> str:
        """Return the environment variable name for API key."""
        return "YOUR_PROVIDER_API_KEY"
    
    def get_default_model(self) -> str:
        """Return the default model."""
        return "your-default-model"
    
    def get_supported_models(self) -> List[str]:
        """Return list of supported models."""
        return [
            "your-default-model",
            "your-other-model",
        ]
```

#### 2. Create a Template

Create a Jinja2 template file `llm_agent_builder/templates/agent_template_your_provider.py.j2`:

```python
import os
from typing import Optional

class {{ agent_name }}:
    def __init__(self, api_key: str):
        # Initialize your provider's client
        self.api_key = api_key
        self.model = "{{ model }}"
        self.prompt = "{{ prompt }}"
    
    def run(self, task: str) -> str:
        # Implement your provider's API call
        # Return the response text
        pass

if __name__ == '__main__':
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.environ.get("YOUR_PROVIDER_API_KEY")
    if not api_key:
        raise ValueError("YOUR_PROVIDER_API_KEY not found")
    
    agent = {{ agent_name }}(api_key=api_key)
    result = agent.run("{{ example_task }}")
    print(result)
```

#### 3. Register the Provider

Add the import to `llm_agent_builder/providers/__init__.py`:

```python
from .your_provider import YourProvider

__all__ = [
    # ... existing exports
    'YourProvider',
]
```

#### 4. Test Your Provider

Create tests in `tests/test_your_provider.py`:

```python
from llm_agent_builder.providers import ProviderRegistry
from llm_agent_builder.agent_builder import AgentBuilder

def test_your_provider_registered():
    assert ProviderRegistry.is_registered("your_provider")

def test_your_provider_template():
    provider = ProviderRegistry.get("your_provider")
    assert provider.get_template_name() == "agent_template_your_provider.py.j2"

def test_build_agent_with_your_provider():
    builder = AgentBuilder()
    code = builder.build_agent(
        agent_name="TestAgent",
        prompt="Test prompt",
        example_task="Test task",
        model="your-default-model",
        provider="your_provider"
    )
    assert "class TestAgent:" in code
```

### Benefits of the Provider Pattern

- ✅ **Open/Closed Principle**: Add new providers without modifying existing code
- ✅ **Standardized Interface**: All providers implement the same interface
- ✅ **Automatic Discovery**: Providers are automatically registered via decorator
- ✅ **Easy Testing**: Each provider can be tested independently
- ✅ **Plugin Architecture**: Providers can be developed as separate plugins

### Current Providers

The following providers are currently available:

| Provider | Models | Template | API Key Env Var |
|----------|--------|----------|-----------------|
| **google** | gemini-1.5-pro, gemini-1.5-flash | agent_template.py.j2 | GOOGLE_GEMINI_KEY |
| **anthropic** | claude-3-5-sonnet, claude-3-opus | agent_template.py.j2 | ANTHROPIC_API_KEY |
| **openai** | gpt-4o, gpt-4-turbo, gpt-4 | agent_template_openai.py.j2 | OPENAI_API_KEY |
| **huggingface** | Meta-Llama-3-8B-Instruct | agent_template_hf.py.j2 | HUGGINGFACEHUB_API_TOKEN |
| **huggingchat** | Meta-Llama-3.1-70B-Instruct | agent_template_huggingchat.py.j2 | HUGGINGCHAT_EMAIL |

## 🐛 Troubleshooting

### Common Issues

**Issue**: `GOOGLE_GEMINI_KEY not found`

- **Solution**: Ensure your `.env` file is in the project root and contains `GOOGLE_GEMINI_KEY=your-key`

**Issue**: Frontend build fails

- **Solution**: Ensure Node.js 18+ is installed and run `npm install` in the `frontend/` directory

**Issue**: Rate limit errors

- **Solution**: The API has rate limiting (20 requests/min for generation, 10/min for execution). Wait a moment and retry.

**Issue**: Agent execution times out

- **Solution**: Check that your agent code is valid Python and doesn't have infinite loops. The sandbox has a 30-second timeout.

**Issue**: Hugging Face Spaces build fails with "openvscode-server" download error

- **Cause**: This is a known issue with Hugging Face Spaces' dev-mode feature. The injected vscode stage tries to download openvscode-server from GitHub, which can fail due to network issues.
- **Solutions**:
  1. **Disable dev-mode** (recommended): In your Space settings, disable "Dev Mode" if you don't need the VS Code interface
  2. **Retry the build**: This is often a temporary network issue on HF Spaces' side
  3. **Wait and retry**: HF Spaces infrastructure issues are usually resolved within a few hours
- **Note**: Our Dockerfile includes all necessary tools (`wget`, `tar`, `git`) for dev-mode compatibility, but we cannot control the injected stages that HF Spaces adds.

## 📈 Roadmap

- [x] Support for OpenAI models (✅ Completed)
- [x] Provider registry pattern for easy extensibility (✅ Completed)
- [ ] Agent marketplace/sharing
- [ ] Visual workflow builder
- [ ] Agent versioning
- [ ] Advanced tool library
- [ ] Multi-agent orchestration

---

**Made with ❤️ by the LLM Agent Builder Team**
