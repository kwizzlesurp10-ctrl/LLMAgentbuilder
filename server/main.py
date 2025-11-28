import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Add the parent directory to sys.path to import llm_agent_builder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_agent_builder.agent_builder import AgentBuilder

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now, or specify if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    name: str
    prompt: str
    task: str
    model: str = "claude-3-5-sonnet-20241022"

@app.post("/api/generate")
async def generate_agent(request: GenerateRequest):
    try:
        builder = AgentBuilder()
        code = builder.build_agent(
            agent_name=request.name,
            prompt=request.prompt,
            example_task=request.task,
            model=request.model
        )
        
        # Stateless: Return code directly, do not save to disk
        return {
            "status": "success",
            "message": "Agent generated successfully",
            "code": code,
            "filename": f"{request.name.lower()}.py"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Serve React App
# Mount the static files from the frontend build directory
# We assume the frontend is built to 'frontend/dist'
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")

if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # If the path is a file in dist, serve it (e.g. vite.svg)
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
            
        # Otherwise serve index.html for React Router
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    print(f"Warning: Frontend build directory not found at {frontend_dist}")
