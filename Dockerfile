# Stage 1: Build Frontend
FROM node:18-alpine as frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build Backend & Serve
FROM python:3.9-slim
WORKDIR /app

# Install system dependencies if needed (e.g. for some python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY llm_agent_builder/ ./llm_agent_builder/
COPY server/ ./server/
# Create empty init for server if not exists (though we have it)
# COPY server/__init__.py ./server/ 

# Copy frontend build from stage 1
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Expose port 7860 (Hugging Face Spaces default)
EXPOSE 7860

# Run the application
# Host 0.0.0.0 is required for Docker
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "7860"]
