import os
from typing import Optional
from huggingface_hub import HfApi, create_repo, upload_folder
from huggingface_hub.utils import HfHubHTTPError

def deploy_to_hf(
    repo_id: str,
    token: Optional[str] = None,
    private: bool = False,
    space_sdk: str = "docker",
    project_root: Optional[str] = None
) -> str:
    """
    Create a Hugging Face Space and upload the project files.
    """
    if not token:
        token = os.getenv("HUGGINGFACEHUB_API_TOKEN") or os.getenv("HF_TOKEN")
    
    if not token:
        raise ValueError("Hugging Face token not found. Please set HUGGINGFACEHUB_API_TOKEN or HF_TOKEN.")

    api = HfApi(token=token)
    
    # Verify authentication
    try:
        user_info = api.whoami()
        print(f"Authenticated as: {user_info['name']}")
    except Exception as e:
        raise RuntimeError(f"Authentication failed: {e}")

    # Ensure repo_id has the username/org if not provided
    if "/" not in repo_id:
        repo_id = f"{user_info['name']}/{repo_id}"

    print(f"Target Space: {repo_id}")

    try:
        # Check if exists
        api.repo_info(repo_id=repo_id, repo_type="space")
        print(f"Space {repo_id} already exists. Uploading to it...")
    except HfHubHTTPError:
        print(f"Space {repo_id} not found. Creating...")
        try:
            create_repo(
                repo_id=repo_id, 
                repo_type="space", 
                space_sdk=space_sdk, 
                private=private, 
                token=token
            )
            print("Space created successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to create space: {e}")

    if not project_root:
        # Assume project root is the parent of the package
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"Uploading files from {project_root}... This may take a minute.")
    try:
        upload_url = upload_folder(
            folder_path=project_root,
            repo_id=repo_id,
            repo_type="space",
            token=token,
            ignore_patterns=[
                ".git*", 
                "venv*", 
                ".venv*", 
                "__pycache__*", 
                "frontend/node_modules*", 
                "*.pyc", 
                "*.ds_store", 
                ".env*",
                "generated_agents*",
                "test_outputs*",
                "logs*",
                "scripts/setup_hf_space.py"
            ]
        )
        return upload_url
    except Exception as e:
        raise RuntimeError(f"Upload failed: {e}")
