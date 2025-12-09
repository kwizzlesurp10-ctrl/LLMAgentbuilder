# Copilot Instructions for LLMAgentbuilder

## Architecture snapshot
- `llm_agent_builder/cli.py` is the primary entrypoint (`python main.py` or `llm-agent-builder`) and reuses `AgentBuilder` + Jinja templates to generate agents both interactively and via batch JSON configs.
- The FastAPI backend in `server/main.py` exposes `/api/generate`, `/api/execute`, `/api/test-agent`, health (`/health`, `/healthz`) and `/metrics` (Instrumentator) while enforcing rate limits (`slowapi`) and retries (`tenacity`).
- React frontend (`frontend/src/App.jsx`, `AgentForm.jsx`, `CodePreview.jsx`) calls `/api/generate` and `/api/execute`, downloads the generated code, and toggles themes via `data-theme`. It expects dev mode to hit `http://localhost:8000` while production uses same-origin (the backend serves `frontend/dist`).

## Critical workflows
- **CLI generation/test/list**: `python main.py generate` (with `--interactive`, `--template`, `--db-path`, `--model`, `--provider` flags), `llm-agent-builder list`, `llm-agent-builder test generated_agents/<name>.py --task <task>`, and `llm-agent-builder batch agents.json` (see example config in `README.md`).
- **Backend dev**: `uvicorn server.main:app --reload` (or `llm-agent-builder web`) to match what `frontend` expects; watch for the fallback root response when `frontend/dist` is missing.
- **Frontend dev/build**: `cd frontend && npm install && npm run dev` for live UI; `npm run build` produces the `dist` folder that `server/main.py` mounts on startup (assets live under `frontend/dist/assets`).
- **Tests & checks**: run `pytest` (all tests live under `tests/`); `mypy llm_agent_builder server`; `black --check`, `isort --check-only`, `flake8 llm_agent_builder server tests`; front-end lint `cd frontend && npm run lint` if needed.
- **Docker/Spaces**: multi-stage `Dockerfile` builds the React app, copies `frontend/dist` into the Python image, and implicitly requires `git` in the container (Hugging Face Spaces best practice).

## Patterns & conventions
- Templates under `llm_agent_builder/templates/` drive agent code; `agent_template.py.j2` is the default but CLI/backend accept a custom template path, so keep placeholders consistent with `agent_name`, `prompt`, `model`, `provider`, `tools`, `enable_multi_step`, and `db_path`.
- Generated agents expect a `--task` CLI argument and call `agent.run(task)`, so any new tooling or tests should pass that flag (see `server/sandbox.py` and `AgentEngine.execute_with_timeout`).
- `server/models.py` owns provider/model validation (Anthropic, Hugging Face, OpenAI). Mirror those lists when updating the UI dropdown (see `AgentForm.jsx`) or CLI defaults.
- `tests/test_api.py` exercises FastAPI endpoints via TestClient; align new APIs with the existing response shapes (`status`, `code`, `filename`, `output`, `detail`).

## Integration & environment specifics
- Environment variables: `ANTHROPIC_API_KEY`, `HUGGINGFACEHUB_API_TOKEN`, `ANTHROPIC_MODEL`, and optionally `GITHUB_COPILOT_TOKEN`. `dotenv` is loaded by the CLI (`load_dotenv`).
- `AgentEngine` (llm_agent_builder/agent_engine.py) tries Copilot tokens when present, falls back to env vars for Anthropic/HuggingFace, isolates execution via subprocess/timeouts, and reports structured `ExecutionResult`. Tie API tests or new features to that result schema.
- `server/sandbox.py` enforces resource limits via `resource.setrlimit`, so sandbox execution during API tests may fail if mocked agents exceed the 30‑second timeout or 512 MB limit; keep test agents simple.
- Static serving: `server/main.py` checks `frontend/dist/index.html`. When spinning up the backend without rebuilding the frontend, expect the JSON fallback response pointing to API docs `/docs`.

## Debugging & next steps
- Generated agents land in `generated_agents/`; CLI `list` and `test` commands assume files named `<agent_name>.py` lowercased. Update any automation to match that naming scheme.
- Logs from `server/main.py` already mention when the frontend bundle is served or missing; forward those logs to know if the React build is stale.
- When adjusting rate limits or retries, look at the decorators atop `/api/generate` and `/api/execute` (20/min and 10/min via `slowapi`).

Please let me know if any sections are unclear or missing context so I can refine these guidance notes.