# Stage 1: Build Frontend
FROM node:22-alpine as frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Base Python image with git (for Hugging Face Spaces dev-mode compatibility)
# Using python:3.11 (not slim) which includes git by default
FROM python:3.11 as base
# Ensure git, build tools, and utilities needed for HF Spaces dev-mode are available
# wget and tar are needed for the injected vscode stage in dev-mode
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    ca-certificates \
    wget \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Stage 3: Build Backend & Serve
FROM base
WORKDIR /app

# Ensure git, ca-certificates, and utilities are explicitly available in final stage
# Critical for Hugging Face Spaces dev-mode which wraps this stage
# HF Spaces runs git config commands in wrapped stages, so git must be present
# ca-certificates needed for HTTPS API calls (Anthropic, Hugging Face Hub)
# wget and tar needed for injected vscode stage in dev-mode
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    wget \
    tar \
    && rm -rf /var/lib/apt/lists/* \
    && git --version

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY llm_agent_builder/ ./llm_agent_builder/
COPY server/ ./server/
COPY main.py .
COPY workflow.db .
COPY workflow_impl.py .

# Copy frontend build from stage 1
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Expose port 7860 (Hugging Face Spaces default)
EXPOSE 7860

# Run the application
# Host 0.0.0.0 is required for Docker
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "7860"]
