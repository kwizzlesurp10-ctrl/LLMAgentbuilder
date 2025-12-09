# LLM Agent Builder - Copilot Instructions

## Project Overview
LLM Agent Builder is a production-ready tool for generating custom AI agents via CLI, web UI, and Hugging Face Spaces. The architecture combines a Python backend (FastAPI), React 19 frontend, and a templating engine for code generation.

## Architecture & Core Components

### Three-Layer Architecture
1. **Core Generation Layer** (`llm_agent_builder/`)
   - `agent_builder.py`: Jinja2-based code generation engine
   - `agent_engine.py`: Headless programmatic execution of generated agents
   - `cli.py`: CLI interface with interactive and batch modes
   - `templates/`: Jinja2 templates for Anthropic and Hugging Face agent patterns

2. **API/Server Layer** (`server/`)
   - `main.py`: FastAPI endpoints with rate limiting (20/min generate, 10/min execute) and retry logic
   - `models.py`: Pydantic v2 models with multi-provider validation (Anthropic, Hugging Face, OpenAI)
   - `sandbox.py`: Resource-limited code execution (30s timeout, 100KB size limit, memory tracking)

3. **Frontend Layer** (`frontend/`)
   - React 19 with functional components and hooks
   - Stateless architecture: generated code returned as JSON, triggers browser download
   - Dark/light theme toggle persisted to localStorage
   - Tailwind CSS for styling with custom CSS variables for theming

### Data Flow: Agent Generation
```
User Input → AgentForm (Frontend) 
  → POST /api/generate (FastAPI)
  → GenerateRequest validation (Pydantic v2)
  → AgentBuilder.build_agent() (Jinja2 rendering)
  → Generated Python code (JSON response)
  → Browser download
```

### Data Flow: Agent Execution
```
User Task + Generated Code
  → POST /api/test-agent or /api/execute (FastAPI)
  → AgentEngine.execute_with_timeout() or run_in_sandbox()
  → Sandboxed subprocess with resource limits
  → ExecutionResult (structured output)
  → Frontend displays result
```

## Critical Development Patterns

### Agent Generation via Templates
Generated agents follow this pattern:
- Inherits from provider-specific base (Anthropic client or Hugging Face Hub)
- `__init__()`: Loads API key from environment, initializes model
- `chat()` or `run()`: Main interaction method with message history
- Optional: `query_database()`, `run_multi_step()`, `search_models()` based on feature flags

Key template variables passed from `GenerateRequest`:
- `agent_name`: Python class name (validated as identifier)
- `prompt`: System instructions for the agent
- `model`: Provider-specific model ID (validated allowlist)
- `provider`: "anthropic" | "huggingface" | "openai"
- `enable_multi_step`: Adds iterative task solving capability
- `tools`: List of tool definitions for function calling

### Pydantic v2 Migration Notes
- Use `@field_validator` instead of `@validator` (old v1 style deprecated)
- Use `model_validate()` instead of `parse_obj()`
- BaseModel now enforces strict mode by default in some cases
- See `server/models.py` for correct v2 patterns

### API Validation Pattern
All endpoints validate through Pydantic models:
```python
@app.post("/api/generate")
@limiter.limit("20/minute")
async def generate_agent(request: Request, generate_request: GenerateRequest):
    # Pydantic already validated input via GenerateRequest
    # Check content length limits (prompt max 10000, task max 5000)
    # Use _generate_agent_with_retry() for resilience
    # Return stateless JSON: {status, code, filename}
```

### Sandboxed Execution
- `run_in_sandbox()` creates temp files, runs via subprocess with resource limits
- Expects agent CLI to accept `--task` argument
- Unix `resource` module for CPU/memory limits (Windows compatibility handled)
- Max 30 seconds execution, 512MB memory default
- Agent must be importable and callable in a fresh Python process

## Build & Development Commands

### Backend Development
```bash
# Install dependencies (dev includes testing tools)
pip install -e ".[dev]"

# Run API locally
uvicorn server.main:app --reload  # Port 8000

# Type checking
mypy llm_agent_builder server

# Testing with coverage
pytest --cov=llm_agent_builder --cov=server
```

### Frontend Development
```bash
cd frontend

# Dev server (Vite hot reload)
npm run dev  # Port 5173

# Production build
npm run build  # Output: dist/

# Linting
npm run lint
```

### Docker Multi-Stage Build
```bash
# Multi-stage: frontend (Node) → backend (Python)
# Frontend built in stage 1, static files copied to stage 2
# Backend serves frontend from ./frontend/dist
docker build -t llm-agent-builder .
docker run -p 7860:7860 -e ANTHROPIC_API_KEY=... llm-agent-builder
```

## Project-Specific Conventions

### Directory Layout
- Generated agents saved to `generated_agents/` by CLI (not API—API returns code)
- Test outputs saved to `test_outputs/` directory
- Frontend static build goes to `frontend/dist/` (served by FastAPI StaticFiles)

### Error Handling
- FastAPI returns structured errors: `{detail: string}`
- ExecutionResult uses enum `ExecutionStatus` for consistency
- Sandbox errors wrapped in output string (never raise to user)
- Retry logic via `tenacity` library for transient failures (3 attempts, exponential backoff)

### Security
- Rate limiting: slowapi with `get_remote_address` key function
- Input validation: Content length checks (prompt 10KB, task 5KB, code 100KB)
- Sandbox isolation: subprocess with resource limits, temp files cleaned up
- API keys: Loaded from environment only (never logged or returned)

### Type Hints
- All function signatures must include parameter and return types
- Provider enums define allowed models per LLM provider
- Use `Optional[T]` for nullable types, not `T | None`

### Testing Structure
```python
# tests/ contains:
# - test_agent_builder.py: Template rendering, code generation
# - test_agent_engine.py: Programmatic execution
# - test_api.py: FastAPI endpoints, validation
# - test_cli.py: CLI commands and batch operations
# - conftest.py: Shared fixtures (mock API keys, temp agents)
```

## External Dependencies & Integration Points

### Python (Backend)
- **anthropic**: Chat completion API, streaming support
- **huggingface_hub**: Model search, inference API
- **fastapi, uvicorn**: Web server with async/await
- **pydantic**: Request/response validation (v2 required)
- **jinja2**: Agent code templating
- **tenacity**: Retry logic for API calls
- **slowapi**: Rate limiting middleware
- **prometheus-fastapi-instrumentator**: Metrics endpoint

### Frontend
- **React 19**: Latest features (hooks, concurrent rendering)
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **ESLint**: Code quality linting

### Deployment
- **Docker**: Multi-stage build for production
- **Hugging Face Spaces**: Port 7860, docker SDK runtime
- **GitHub Actions** (`.github/workflows/`): CI/CD for testing

## Common Tasks & Implementation Patterns

### Adding a New Agent Feature
1. Update `llm_agent_builder/templates/agent_template.py.j2` (add template variable)
2. Add parameter to `GenerateRequest` in `server/models.py` with validation
3. Pass parameter through `AgentBuilder.build_agent()` to template
4. Update frontend form in `frontend/src/components/AgentForm.jsx`
5. Add tests in `tests/test_agent_builder.py` with rendered code verification

### Adding a New Provider (LLM Model)
1. Add to `ProviderEnum` in `server/models.py`
2. Update `validate_model()` field_validator with new provider's allowed models
3. Create or update template for provider (e.g., `agent_template_openai.py.j2`)
4. Add client initialization in generated agent code (ApiKey handling)
5. Test end-to-end with form and API

### Debugging Agent Execution
- Check sandbox output: `ExecutionResult.to_dict()` includes status, output, error
- Use `test_agent(agent_path, task)` CLI command for local testing
- Agent code should handle `--task` CLI argument parsing
- If timeout occurs, check agent doesn't loop infinitely (30s limit)

## Key Files Reference
| File | Purpose | Key Pattern |
|------|---------|-------------|
| `agent_builder.py` | Template rendering engine | Jinja2 with feature flags |
| `agent_engine.py` | Headless execution wrapper | subprocess + resource limits |
| `server/main.py` | FastAPI endpoints | @app.post with @limiter |
| `server/models.py` | Pydantic validation | @field_validator with allowlists |
| `server/sandbox.py` | Code isolation | tempfile + subprocess.Popen |
| `frontend/src/App.jsx` | Main UI component | React hooks, localStorage |
| `templates/agent_template.py.j2` | Agent code blueprint | Conditional blocks, provider logic |

## Important Notes for AI Agents
- **Pydantic v2**: Use `@field_validator` not `@validator`; already migrated in codebase
- **Port 7860**: Required for Hugging Face Spaces (never hardcode other ports in templates)
- **Frontend-Backend Communication**: Relative URLs in production (`/api/...`), full URLs in dev
- **Stateless Design**: API returns code in response body, client handles download (supports serverless)
- **Agent CLI Args**: All generated agents must accept `--task` argument for test execution
- **Resource Limits**: Sandbox enforces 30s timeout and memory limits; agents must respect this
