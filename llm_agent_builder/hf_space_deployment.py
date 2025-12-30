"""
HuggingFace Spaces Deployment Helper

This module provides utilities for deploying LLM agents to HuggingFace Spaces.
"""

import os
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass


@dataclass
class SpaceConfig:
    """Configuration for a HuggingFace Space."""
    space_name: str
    sdk: str = "docker"  # docker, gradio, streamlit, static
    app_port: int = 7860
    title: Optional[str] = None
    emoji: str = "🤖"
    color_from: str = "blue"
    color_to: str = "indigo"
    python_version: str = "3.9"
    
    def to_readme_header(self) -> str:
        """Generate README header for Space."""
        return f"""---
title: {self.title or self.space_name}
emoji: {self.emoji}
colorFrom: {self.color_from}
colorTo: {self.color_to}
sdk: {self.sdk}
app_port: {self.app_port}
python_version: "{self.python_version}"
---
"""


class SpaceDeploymentHelper:
    """
    Helper class for deploying agents to HuggingFace Spaces.
    
    This class generates all necessary files for deploying an agent
    to HuggingFace Spaces, including Dockerfile, requirements, and config.
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize deployment helper.
        
        :param token: HuggingFace API token
        """
        self.token = token or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
        if self.token:
            from huggingface_hub import HfApi
            self.api = HfApi(token=self.token)
        else:
            self.api = None
    
    def create_space_files(
        self,
        agent_path: str,
        output_dir: str,
        config: SpaceConfig,
        include_web_ui: bool = True
    ) -> Dict[str, str]:
        """
        Create all files needed for Space deployment.
        
        :param agent_path: Path to agent Python file
        :param output_dir: Directory to create Space files
        :param config: Space configuration
        :param include_web_ui: Whether to include web UI
        :return: Dictionary of created file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        created_files = {}
        
        # 1. Create README.md with metadata
        readme_path = output_path / "README.md"
        readme_content = self._generate_readme(config, Path(agent_path).stem)
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        created_files['README.md'] = str(readme_path)
        
        # 2. Create Dockerfile
        dockerfile_path = output_path / "Dockerfile"
        dockerfile_content = self._generate_dockerfile(config, include_web_ui)
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        created_files['Dockerfile'] = str(dockerfile_path)
        
        # 3. Create requirements.txt
        requirements_path = output_path / "requirements.txt"
        requirements_content = self._generate_requirements(include_web_ui)
        with open(requirements_path, 'w') as f:
            f.write(requirements_content)
        created_files['requirements.txt'] = str(requirements_path)
        
        # 4. Copy agent file
        agent_dest = output_path / "agent.py"
        with open(agent_path, 'r') as src, open(agent_dest, 'w') as dst:
            dst.write(src.read())
        created_files['agent.py'] = str(agent_dest)
        
        # 5. Create app.py (FastAPI server)
        app_path = output_path / "app.py"
        app_content = self._generate_app(config, include_web_ui)
        with open(app_path, 'w') as f:
            f.write(app_content)
        created_files['app.py'] = str(app_path)
        
        # 6. Create .env.example
        env_example_path = output_path / ".env.example"
        with open(env_example_path, 'w') as f:
            f.write("HUGGINGFACEHUB_API_TOKEN=your_token_here\n")
        created_files['.env.example'] = str(env_example_path)
        
        # 7. Create .gitignore
        gitignore_path = output_path / ".gitignore"
        with open(gitignore_path, 'w') as f:
            f.write(".env\n__pycache__/\n*.pyc\n.DS_Store\n")
        created_files['.gitignore'] = str(gitignore_path)
        
        return created_files
    
    def _generate_readme(self, config: SpaceConfig, agent_name: str) -> str:
        """Generate README for Space."""
        header = config.to_readme_header()
        content = f"""
# {config.title or config.space_name}

This Space hosts an AI agent built with [LLM Agent Builder](https://github.com/kwizzlesurp10-ctrl/LLMAgentbuilder).

## Agent: {agent_name}

This agent uses HuggingFace models to perform various tasks.

## Usage

1. Set your HuggingFace API token in the Space settings (Settings → Repository secrets → New secret)
   - Name: `HUGGINGFACEHUB_API_TOKEN`
   - Value: Your token from https://huggingface.co/settings/tokens

2. The Space will automatically start and be accessible via the web interface.

## API Endpoints

- `POST /api/chat` - Send a message to the agent
- `GET /health` - Health check
- `GET /` - Web interface

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export HUGGINGFACEHUB_API_TOKEN=your_token

# Run the app
python app.py
```

## About

Built with ❤️ using [LLM Agent Builder](https://github.com/kwizzlesurp10-ctrl/LLMAgentbuilder)
"""
        return header + content
    
    def _generate_dockerfile(self, config: SpaceConfig, include_web_ui: bool) -> str:
        """Generate Dockerfile for Space."""
        return f"""FROM python:{config.python_version}-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE {config.app_port}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{config.app_port}/health || exit 1

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "{config.app_port}"]
"""
    
    def _generate_requirements(self, include_web_ui: bool) -> str:
        """Generate requirements.txt."""
        requirements = [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "pydantic>=2.0.0",
            "huggingface_hub>=0.19.0",
            "python-dotenv>=1.0.0",
            "requests>=2.31.0",
        ]
        
        if include_web_ui:
            requirements.extend([
                "jinja2>=3.1.0",
                "slowapi>=0.1.9",
            ])
        
        return "\\n".join(requirements) + "\\n"
    
    def _generate_app(self, config: SpaceConfig, include_web_ui: bool) -> str:
        """Generate app.py FastAPI application."""
        return '''"""
FastAPI application for HuggingFace Space deployment.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the agent
from agent import *

app = FastAPI(
    title="AI Agent API",
    description="AI agent powered by HuggingFace",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1024

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

# Initialize agent
try:
    # Find the agent class (first class that has a run method)
    agent_class = None
    for name, obj in globals().items():
        if isinstance(obj, type) and hasattr(obj, 'run') and name[0].isupper():
            agent_class = obj
            break
    
    if agent_class is None:
        raise ValueError("No agent class found")
    
    agent = agent_class()
    print(f"✓ Agent initialized: {agent_class.__name__}")
except Exception as e:
    print(f"✗ Error initializing agent: {e}")
    agent = None

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Agent API",
        "status": "running" if agent else "error",
        "endpoints": {
            "chat": "POST /api/chat",
            "health": "GET /health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy" if agent else "unhealthy",
        "agent_loaded": agent is not None
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the agent."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        response = agent.run(
            request.message,
            max_tokens=request.max_tokens
        )
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
'''
    
    def create_space(
        self,
        space_name: str,
        agent_path: str,
        private: bool = False,
        space_sdk: str = "docker"
    ) -> Dict[str, Any]:
        """
        Create a new Space on HuggingFace Hub.
        
        :param space_name: Name of the Space
        :param agent_path: Path to agent file
        :param private: Whether Space should be private
        :param space_sdk: SDK to use (docker, gradio, streamlit)
        :return: Space creation result
        """
        if not self.api:
            return {
                "error": "HuggingFace API token not provided",
                "success": False
            }
        
        try:
            # Create Space
            repo_id = f"{self.api.whoami()['name']}/{space_name}"
            
            space_url = self.api.create_repo(
                repo_id=repo_id,
                repo_type="space",
                private=private,
                space_sdk=space_sdk
            )
            
            return {
                "success": True,
                "space_url": space_url,
                "repo_id": repo_id,
                "message": f"Space created successfully at {space_url}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def upload_to_space(
        self,
        space_name: str,
        local_dir: str,
        commit_message: str = "Deploy agent to Space"
    ) -> Dict[str, Any]:
        """
        Upload files to an existing Space.
        
        :param space_name: Name of the Space
        :param local_dir: Local directory with Space files
        :param commit_message: Commit message
        :return: Upload result
        """
        if not self.api:
            return {
                "error": "HuggingFace API token not provided",
                "success": False
            }
        
        try:
            repo_id = f"{self.api.whoami()['name']}/{space_name}"
            
            self.api.upload_folder(
                folder_path=local_dir,
                repo_id=repo_id,
                repo_type="space",
                commit_message=commit_message
            )
            
            space_url = f"https://huggingface.co/spaces/{repo_id}"
            
            return {
                "success": True,
                "space_url": space_url,
                "message": f"Files uploaded successfully to {space_url}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def deploy_agent_to_space(
        self,
        agent_path: str,
        space_name: str,
        config: Optional[SpaceConfig] = None,
        private: bool = False
    ) -> Dict[str, Any]:
        """
        Complete deployment: create Space, generate files, and upload.
        
        :param agent_path: Path to agent file
        :param space_name: Name for the Space
        :param config: Space configuration
        :param private: Whether Space should be private
        :return: Deployment result
        """
        if config is None:
            config = SpaceConfig(space_name=space_name)
        
        # Create temporary directory for Space files
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate Space files
            files = self.create_space_files(
                agent_path=agent_path,
                output_dir=temp_dir,
                config=config,
                include_web_ui=True
            )
            
            print(f"✓ Generated {len(files)} Space files")
            
            # Create Space if it doesn't exist
            create_result = self.create_space(
                space_name=space_name,
                agent_path=agent_path,
                private=private,
                space_sdk=config.sdk
            )
            
            if not create_result.get("success"):
                # Space might already exist, try uploading anyway
                print(f"Note: {create_result.get('error', 'Unknown error')}")
            
            # Upload files
            upload_result = self.upload_to_space(
                space_name=space_name,
                local_dir=temp_dir,
                commit_message=f"Deploy {Path(agent_path).stem} agent"
            )
            
            return upload_result


if __name__ == "__main__":
    # Example usage
    print("HuggingFace Spaces Deployment Helper")
    print("=" * 60)
    
    # Create a test configuration
    config = SpaceConfig(
        space_name="test-agent-space",
        title="Test AI Agent",
        emoji="🤖",
        sdk="docker"
    )
    
    print(f"\\nSpace Configuration:")
    print(f"  Name: {config.space_name}")
    print(f"  SDK: {config.sdk}")
    print(f"  Port: {config.app_port}")
    
    # Test file generation (without actual deployment)
    helper = SpaceDeploymentHelper()
    print("\\n✓ Deployment helper initialized")
    print("\\nTo deploy an agent:")
    print("  1. Set HUGGINGFACEHUB_API_TOKEN environment variable")
    print("  2. Use: helper.deploy_agent_to_space(agent_path, space_name)")
