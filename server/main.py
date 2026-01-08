import os
import subprocess
import sys
from pathlib import Path
import subprocess
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

# Add the parent directory to sys.path to import llm_agent_builder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prometheus_fastapi_instrumentator import Instrumentator

from llm_agent_builder.agent_builder import AgentBuilder
from llm_agent_builder.agent_engine import AgentEngine
from llm_agent_builder.config import get_config, AppConfig
from server.models import GenerateRequest, ProviderEnum, TestAgentRequest
from server.sandbox import run_in_sandbox

# Load configuration
app_config: AppConfig = get_config()
print(f"✓ Configuration loaded: environment={app_config.environment}, port={app_config.server.port}")

app = FastAPI(title="LLM Agent Builder API", version="1.0.0")

# Rate limiting (use config)
if app_config.enable_rate_limiting:
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    print("✓ Rate limiting enabled")
else:
    limiter = None
    print("✗ Rate limiting disabled")

# Instrumentator (use config)
if app_config.enable_metrics:
    Instrumentator().instrument(app).expose(app)
    print("✓ Metrics enabled")

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

# Helper to apply rate limit only if enabled
def rate_limit_if_enabled(limit: str):
    """Decorator to apply rate limiting only if enabled in config."""
    def decorator(func):
        if app_config.enable_rate_limiting and limiter:
            return limiter.limit(limit)(func)
        return func
    return decorator

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
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
        stream=request.stream,
        db_path=request.db_path,
        enable_multi_step=request.enable_multi_step,
        tools=request.tools
    )


@app.post("/api/execute")
@rate_limit_if_enabled("10/minute")
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
    except HTTPException:  # Re-raise HTTPException directly
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")


@app.post("/api/generate")
@rate_limit_if_enabled("20/minute")
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
            "filename": f"{generate_request.name.lower()}.py",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:  # Re-raise HTTPException directly
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")


@app.post("/api/test-agent")
@rate_limit_if_enabled("10/minute")
async def test_agent(request: Request, test_request: TestAgentRequest):
    """
    Test a built agent using the AgentEngine.

    This endpoint allows testing agents programmatically without CLI output,
    suitable for HuggingFace Spaces and automated testing.

    Either agent_code or agent_path must be provided.
    """
    try:
        # Validate that at least one source is provided
        if not test_request.agent_code and not test_request.agent_path:
            raise HTTPException(status_code=400, detail="Either agent_code or agent_path must be provided")

        # Validate code length if provided
        if test_request.agent_code and len(test_request.agent_code) > 100000:
            raise HTTPException(status_code=400, detail="Agent code exceeds maximum size limit (100KB)")

        # Validate task length
        if len(test_request.task) > 5000:
            raise HTTPException(status_code=400, detail="Task exceeds maximum length (5000 characters)")

        # Create engine
        engine = AgentEngine(timeout=test_request.timeout or 60)

        # Determine agent source
        if test_request.agent_code:
            agent_source = test_request.agent_code
        elif test_request.agent_path:
            # Validate path exists
            agent_path = Path(test_request.agent_path)
            if not agent_path.exists():
                raise HTTPException(status_code=404, detail=f"Agent file not found: {test_request.agent_path}")
            agent_source = str(agent_path)

        # Execute agent
        result = engine.execute_with_timeout(agent_source, test_request.task)

        # Return structured result
        return result.to_dict()

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test execution error: {str(e)}")

@app.get("/api/config")
async def get_config_info():
    """
    Get current configuration (sanitized).
    Note: API keys and sensitive info are not exposed.
    """
    config_dict = app_config.model_dump()
    
    # Remove sensitive data
    if "providers" in config_dict:
        for provider in config_dict["providers"].values():
            if isinstance(provider, dict) and "api_key_env" in provider:
                # Just show that it's configured, don't show the actual env var name
                provider["api_key_configured"] = bool(os.environ.get(provider["api_key_env"]))
                provider.pop("api_key_env", None)
    
    return {
        "status": "ok",
        "config": config_dict
    }

@app.get("/health")
@app.get("/healthz")
async def health_check():
    return {"status": "ok", "version": "1.1.0"}


# Serve React App
# Mount the static files from the frontend build directory
# We assume the frontend is built to 'frontend/dist'
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")
_index_html_path = os.path.join(frontend_dist, "index.html")

if os.path.exists(frontend_dist) and os.path.exists(_index_html_path):
    print(f"✓ Serving frontend from: {frontend_dist}")

    # Mount static assets (must be before catch-all route)
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # Serve root
    @app.get("/")
    async def serve_root():
        return FileResponse(_index_html_path, media_type="text/html")

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
        return FileResponse(_index_html_path, media_type="text/html")

else:
    # Fallback if frontend is not built
    @app.get("/")
    async def serve_root_fallback():
        return {
            "message": "LLM Agent Builder API",
            "status": "Frontend not built. Please build the frontend or use API endpoints.",
            "api_docs": "/docs",
            "endpoints": {"generate": "POST /api/generate", "execute": "POST /api/execute", "health": "GET /health"},
        }

    print(f"⚠ Warning: Frontend build directory not found at {frontend_dist}")
    print(f"   Expected path: {frontend_dist}")
    print("   Serving API only. Access API docs at /docs")
