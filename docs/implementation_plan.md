# Configure Model Options

## Goal Description

Update the agent generation form to include the latest Anthropic models and add support for Hugging Face models. Additionally, implement backend validation, streaming support, security measures, a sandbox executor, and observability.

## User Review Required
>
> [!NOTE]
> I am adding `claude-3-5-haiku-20241022` to the list.
> I am also adding support for Hugging Face models (via `huggingface_hub`).
> I am adding backend validation using Pydantic.
> I am adding a streaming response toggle.
> I am adding security measures (pre-commit hook).
> I am adding a Sandbox Executor for safe agent execution.
> I am adding Prometheus metrics and a `/healthz` endpoint.

## Proposed Changes

### Frontend

#### [MODIFY] [AgentForm.jsx](file:///wsl.localhost/Ubuntu/root/LLMAgentBuilder/frontend/src/components/AgentForm.jsx)

- Add a "Provider" dropdown (Anthropic, Hugging Face).
- Update "Model" dropdown options based on the selected provider.
- Add `claude-3-5-haiku-20241022` for Anthropic.
- Add `meta-llama/Meta-Llama-3-8B-Instruct` and `mistralai/Mistral-7B-Instruct-v0.3` for Hugging Face.
- Add a "Stream Response" checkbox (default: false).
- Add a "Test Agent" button to execute the generated code in the sandbox.
- Display execution results (output/errors) in the UI.

### Backend

#### [NEW] [models.py](file:///wsl.localhost/Ubuntu/root/LLMAgentBuilder/server/models.py)

- Define `ProviderEnum` (Anthropic, HuggingFace).
- Define `GenerateRequest` Pydantic model with validation:
  - `provider`: ProviderEnum
  - `model`: Validated against an allowlist per provider.
  - `stream`: bool (default: False)

#### [MODIFY] [main.py](file:///wsl.localhost/Ubuntu/root/LLMAgentBuilder/server/main.py)

- Import `GenerateRequest` from `models.py`.
- Update `generate_agent` endpoint to use the new validation model.
- Add `/api/execute` endpoint.
- Add `prometheus-fastapi-instrumentator`.
- Add `/metrics` and `/healthz` endpoints.

#### [MODIFY] [agent_builder.py](file:///wsl.localhost/Ubuntu/root/LLMAgentBuilder/llm_agent_builder/agent_builder.py)

- Update `build_agent` to accept `provider` and `stream` arguments.
- Select the appropriate template (`agent_template.py.j2` or `agent_template_hf.py.j2`) based on the provider.
- Pass `stream` to the template context.

#### [NEW] [agent_template_hf.py.j2](file:///wsl.localhost/Ubuntu/root/LLMAgentBuilder/llm_agent_builder/templates/agent_template_hf.py.j2)

- Create a new Jinja2 template for agents using `huggingface_hub.InferenceClient`.
- Use `HUGGINGFACEHUB_API_TOKEN` for authentication.
- Implement conditional logic for `stream=True` vs `stream=False`.

#### [MODIFY] [agent_template.py.j2](file:///wsl.localhost/Ubuntu/root/LLMAgentBuilder/llm_agent_builder/templates/agent_template.py.j2)

- Fix the environment variable name from `GEMINI_API_KEY` to `ANTHROPIC_API_KEY`.

### Sandbox Executor

#### [NEW] [sandbox.py](file:///wsl.localhost/Ubuntu/root/LLMAgentBuilder/server/sandbox.py)

- Implement `run_in_sandbox(code: str, task: str) -> str`:
  - Write code to a temporary file.
  - Use `subprocess.Popen` to execute the file.
  - Use `preexec_fn` to set `resource.setrlimit`:
    - `RLIMIT_CPU`: Limit CPU time (e.g., 30 seconds).
    - `RLIMIT_AS`: Limit address space (memory) (e.g., 512MB).
  - Capture `stdout` and `stderr`.
  - Handle timeouts and errors.

### Security & Misc

#### [NEW] [.env.example](file:///wsl.localhost/Ubuntu/root/LLMAgentBuilder/.env.example)

- Add `ANTHROPIC_API_KEY` and `HUGGINGFACEHUB_API_TOKEN` placeholders.

#### [NEW] [pre-commit-check.sh](file:///wsl.localhost/Ubuntu/root/LLMAgentBuilder/pre-commit-check.sh)

- Simple script to grep for potential API keys in staged files.

#### [MODIFY] [requirements.txt](file:///wsl.localhost/Ubuntu/root/LLMAgentBuilder/requirements.txt)

- Add `prometheus-fastapi-instrumentator`.

## Verification Plan

### Automated Tests

- Run `pytest` to ensure no regressions in `agent_builder`.

### Manual Verification

- Start the frontend (`npm run dev` in `frontend/`).
- Verify the new provider and model options.
- Verify the stream toggle works.
- Generate an agent with streaming enabled and check the code.
- Test the "Test Agent" button with a simple task.
- Verify `/metrics` and `/healthz` endpoints.
- Try to commit a file with a fake API key to test the hook.
