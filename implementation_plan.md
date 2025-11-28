# Implementation Plan - Hugging Face Spaces Deployment

## Goal Description

Prepare the LLMAgentBuilder for deployment to **Hugging Face Spaces** (Docker). This involves making the application stateless (serverless-friendly) and packaging both the React frontend and FastAPI backend into a single Docker container.

## User Review Required
>
> [!IMPORTANT]
> **File Saving Change**: The application will no longer save files to the *server's* `generated_agents/` directory. Instead, it will trigger a **file download** in the user's browser. This is necessary because Hugging Face Spaces have ephemeral storage (files are lost on restart).

## Proposed Changes

### 1. Make Application Stateless

#### [MODIFY] [server/main.py](file:///wsl.localhost/Ubuntu/root/LLMAgentBuilder/server/main.py)

- Remove `os.makedirs` and file writing logic.
- Keep the return of the `code` string.

#### [MODIFY] [frontend/src/App.jsx](file:///wsl.localhost/Ubuntu/root/LLMAgentBuilder/frontend/src/App.jsx)

- Update `handleGenerate` to receive the code and trigger a browser download of the `.py` file.
- Remove "Saved to path" message.

### 2. Single-Container Setup (FastAPI + React)

#### [MODIFY] [server/main.py](file:///wsl.localhost/Ubuntu/root/LLMAgentBuilder/server/main.py)

- Mount `StaticFiles` to serve the React `dist/` folder.
- Add a catch-all route to serve `index.html` for React routing.

### 3. Docker Configuration

#### [NEW] [Dockerfile](file:///wsl.localhost/Ubuntu/root/LLMAgentBuilder/Dockerfile)

- **Stage 1 (Frontend)**: Node.js image -> `npm run build`.
- **Stage 2 (Backend)**: Python image -> Install requirements -> Copy React build -> Run Uvicorn.

## Verification Plan

### Manual Verification

1. **Local Docker Test**:
    - Build image: `docker build -t llm-agent-builder .`
    - Run: `docker run -p 7860:7860 llm-agent-builder`
    - Access `http://localhost:7860`.
    - Generate an agent -> Confirm file downloads to local computer.
2. **Hugging Face Deployment** (User Action):
    - User pushes `Dockerfile` to their Space.
