import sys
import os
import uvicorn

# Ensure the project root is in sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Force reload of llm_agent_builder if it was somehow imported
if 'llm_agent_builder' in sys.modules:
    del sys.modules['llm_agent_builder']

if __name__ == "__main__":
    print(f"Starting server from {project_root}")
    # We use app_dir to tell uvicorn where to look for the app module
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True, app_dir=project_root)
