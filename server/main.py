import os
import sys
import time
from typing import Dict
import subprocess
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Add the parent directory to sys.path to import llm_agent_builder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_agent_builder.agent_builder import AgentBuilder
from server.models import GenerateRequest, ProviderEnum
from server.sandbox import run_in_sandbox
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="LLM Agent Builder API", version="1.0.0")

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Instrumentator
Instrumentator().instrument(app).expose(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now, or specify if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExecuteRequest(BaseModel):
    code: str
    task: str

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError))
)
def _generate_agent_with_retry(request: GenerateRequest) -> str:
    """Generate agent code with retry logic."""
    builder = AgentBuilder()
    return builder.build_agent(
        agent_name=request.name,
        prompt=request.prompt,
        example_task=request.task,
        model=request.model,
        provider=request.provider,
        stream=request.stream
    )

@app.post("/api/execute")
@limiter.limit("10/minute")
async def execute_agent(request: Request, execute_request: ExecuteRequest):
    """Execute agent code in a sandboxed environment."""
    try:
        # Validate code length
        if len(execute_request.code) > 100000:  # 100KB limit
            raise HTTPException(status_code=400, detail="Code exceeds maximum size limit (100KB)")
        
        output = run_in_sandbox(execute_request.code, execute_request.task)
        return {"status": "success", "output": output}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Execution timed out")
    except HTTPException: # Re-raise HTTPException directly
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")

@app.post("/api/generate")
@limiter.limit("20/minute")
async def generate_agent(request: Request, generate_request: GenerateRequest):
    """Generate a new agent with retry logic and rate limiting."""
    try:
        # Validate input lengths
        if len(generate_request.prompt) > 10000:
            raise HTTPException(status_code=400, detail="Prompt exceeds maximum length (10000 characters)")
        if len(generate_request.task) > 5000:
            raise HTTPException(status_code=400, detail="Task exceeds maximum length (5000 characters)")
        
        code = _generate_agent_with_retry(generate_request)
        
        # Stateless: Return code directly, do not save to disk
        return {
            "status": "success",
            "message": "Agent generated successfully",
            "code": code,
            "filename": f"{generate_request.name.lower()}.py"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException: # Re-raise HTTPException directly
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")

@app.get("/health")
@app.get("/healthz")
async def health_check():
    return {"status": "ok"}

# Serve React App
# Mount the static files from the frontend build directory
# We assume the frontend is built to 'frontend/dist'
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")
index_html_path = os.path.join(frontend_dist, "index.html") if os.path.exists(frontend_dist) else None

if os.path.exists(frontend_dist) and os.path.exists(index_html_path):
    print(f"✓ Serving frontend from: {frontend_dist}")
    
    # Mount static assets (must be before catch-all route)
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    
    # Serve root
    @app.get("/")
    async def serve_root():
        return FileResponse(index_html_path, media_type="text/html")

    # Catch-all route for React Router (must be last, excludes API routes)
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # Skip API routes and other special paths - let FastAPI handle these
        if full_path.startswith(("api/", "docs", "redoc", "openapi.json", "metrics", "health")):
            raise HTTPException(status_code=404, detail="Not found")
        
        # If the path is a file in dist, serve it (e.g. vite.svg, favicon.ico)
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
            
        # Otherwise serve index.html for React Router
        return FileResponse(index_html_path, media_type="text/html")
else:
    # Fallback if frontend is not built
    @app.get("/")
    async def serve_root_fallback():
        return {
            "message": "LLM Agent Builder API",
            "status": "Frontend not built. Please build the frontend or use API endpoints.",
            "api_docs": "/docs",
            "endpoints": {
                "generate": "POST /api/generate",
                "execute": "POST /api/execute",
                "health": "GET /health"
            }
        }
    print(f"⚠ Warning: Frontend build directory not found at {frontend_dist}")
    print(f"   Expected path: {frontend_dist}")
    print(f"   Serving API only. Access API docs at /docs")
