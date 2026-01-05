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

- 🚀 **Multi-Provider Support**: Generate agents for Anthropic Claude, HuggingFace, and HuggingChat models
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

### Quick Start

The easiest way to use LLM Agent Builder is to simply run it without any arguments - it will launch the web interface by default:

```bash
python main.py
# or if installed via pip:
llm-agent-builder
```

This will start the web interface at `http://localhost:7860`.

### Modes of Operation

LLM Agent Builder supports two modes:

1. **Web Mode (Default)**: User-friendly web interface
2. **CLI Mode**: Command-line interface for automation and scripting

#### Web Mode

Launch the web interface:

```bash
# Default (launches web interface)
llm-agent-builder

# Explicit web mode with custom host/port
llm-agent-builder --serve --host 127.0.0.1 --port 8080

# Or use the dedicated serve command
llm-agent-builder-serve
```

The web interface provides:
- Interactive agent generation form
- Live code preview
- Direct agent testing in browser
- Copy-to-clipboard functionality
- Dark/light theme toggle

#### CLI Mode

Use CLI commands for automation and batch operations:

**Generate an Agent:**

Interactive Mode:

```bash
# Force CLI mode for interactive generation
llm-agent-builder --cli generate
# or use the dedicated CLI command
llm-agent-builder-cli generate
```

Command-Line Mode:

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

### Available Commands

LLM Agent Builder provides three entry point commands:

1. **`llm-agent-builder`** - Unified entry point (defaults to web mode)
   - Run without args: Launches web interface
   - Run with CLI commands: Routes to CLI mode
   - Use `--serve` to explicitly launch web mode
   - Use `--cli` to force CLI mode

2. **`llm-agent-builder-cli`** - Direct CLI access
   - Always uses CLI mode
   - Useful for scripts and automation

3. **`llm-agent-builder-serve`** - Direct web server access
   - Always launches web interface
   - Useful for server deployments

### Web Interface (Deprecated Direct Access)

**Note:** The standalone backend/frontend setup is now unified. Simply run `llm-agent-builder` to access the web interface.

For development with separate frontend/backend:

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

### Docker Deployment

The Docker image now uses the unified entry point and defaults to web mode:

```bash
# Build the image
docker build -t llm-agent-builder .

# Run with default web mode
docker run -p 7860:7860 -e GOOGLE_GEMINI_KEY="your-key" llm-agent-builder

# Run with CLI mode (example: list agents)
docker run llm-agent-builder python main.py --cli list
```

The container exposes port 7860 for the web interface.

### Features in Web UI

- ✨ **Live Code Preview**: See generated code in real-time
- 🎨 **Theme Toggle**: Switch between dark and light themes
- 📋 **Copy to Clipboard**: One-click code copying
- 🧪 **Test Agent**: Execute agents directly in the browser (sandboxed)
- 📥 **Auto-Download**: Generated agents automatically download

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

Agents can be generated with multi-step workflow capabilities:

```python
# In your generated agent
agent = MyAgent(api_key="your-key")
result = agent.run_multi_step("Complete this complex task", max_steps=5)
```

### Tool Integration

Generate agents with tool calling support:

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
    enable_multi_step=True
)
```

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

See [HUGGINGFACE_GUIDE.md](HUGGINGFACE_GUIDE.md) for detailed safety documentation.

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

See [HUGGINGFACE_GUIDE.md](HUGGINGFACE_GUIDE.md) for complete MCP documentation.

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

- [HuggingFace Integration Guide](HUGGINGFACE_GUIDE.md) - **Complete guide to HuggingChat, MCP, and safety features**
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Hugging Face Hub Documentation](https://huggingface.co/docs/hub/)
- [HuggingChat Models](https://huggingface.co/chat/models)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

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

- [ ] Support for OpenAI models
- [ ] Agent marketplace/sharing
- [ ] Visual workflow builder
- [ ] Agent versioning
- [ ] Advanced tool library
- [ ] Multi-agent orchestration

---

**Made with ❤️ by the LLM Agent Builder Team**
