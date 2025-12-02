# Stage 1: Build Frontend
FROM node:22-alpine as frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Base Python image with git (for Hugging Face Spaces dev-mode compatibility)
# Using python:3.10 (not slim) which includes git by default
FROM python:3.10 as base
# Ensure git and build tools are available
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Stage 3: Build Backend & Serve
FROM base
WORKDIR /app

# Ensure git is available for Hugging Face Spaces dev-mode stages
# (git is already in base, but this ensures it's present when HF Spaces wraps this stage)
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY llm_agent_builder/ ./llm_agent_builder/
COPY server/ ./server/
COPY main.py .
# Create empty init for server if not exists (though we have it)
# COPY server/__init__.py ./server/ 

# Copy frontend build from stage 1
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Expose port 7860 (Hugging Face Spaces default)
EXPOSE 7860

# Run the application
# Host 0.0.0.0 is required for Docker
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "7860"]
