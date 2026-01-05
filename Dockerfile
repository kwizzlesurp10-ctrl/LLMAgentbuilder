# Stage 1: Build Frontend
FROM node:22-alpine as frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Base Python image with dependencies
# Using python:3.10 (matches project requirements: >=3.9)
FROM python:3.10-slim as base

# Install system dependencies needed for HF Spaces dev-mode and runtime
# git: Required for HF Spaces dev-mode (runs git config commands)
# build-essential: Needed for compiling Python packages
# ca-certificates: Required for HTTPS API calls (Google Gemini, Hugging Face Hub)
# wget, tar: Needed for injected vscode stage in HF Spaces dev-mode
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    ca-certificates \
    wget \
    tar \
    && rm -rf /var/lib/apt/lists/* \
    && git --version

# Stage 3: Build Backend & Serve
FROM base
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY llm_agent_builder/ ./llm_agent_builder/
COPY server/ ./server/
COPY main.py .

# Copy optional workflow files (comment out if not present)
COPY workflow_impl.py ./
COPY workflow.db ./

# Copy frontend build from stage 1
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Create generated_agents directory with proper permissions
# Critical for HF Spaces which runs as arbitrary user
RUN mkdir -p generated_agents && \
    chmod -R 777 /app

# Add healthcheck for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:7860/health')" || exit 1

# Expose port 7860 (Hugging Face Spaces default)
EXPOSE 7860

# Add labels for better image metadata
LABEL maintainer="LLMAgentBuilder Team" \
      description="LLM Agent Builder - Generate and test AI agents" \
      version="1.0.0"

# Run the application
# Host 0.0.0.0 is required for Docker and HF Spaces
# Use unified entry point with --serve flag
CMD ["python", "main.py", "--serve"]
