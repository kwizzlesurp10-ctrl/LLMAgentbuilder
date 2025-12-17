import os
import time
from dotenv import load_dotenv
from huggingface_hub import HfApi, create_repo, upload_folder
from huggingface_hub.utils import HfHubHTTPError

def main():
    load_dotenv()
    token = os.getenv("HUGGINGFACEHUB_API_TOKEN") or os.getenv("HF_TOKEN")

    if not token:
        print("Error: HF Token not found in .env (HUGGINGFACEHUB_API_TOKEN or HF_TOKEN)")
        return

    api = HfApi(token=token)
    try:
        user_info = api.whoami()
        user = user_info["name"]
        print(f"Authenticated as: {user}")
    except Exception as e:
        print(f"Authentication failed: {e}")
        return

    import sys
    
    if len(sys.argv) > 1:
        repo_name = sys.argv[1]
    else:
        repo_name = input(f"Enter Space name (default: LLMAgentBuilder): ").strip() or "LLMAgentBuilder"
    # Append timestamp if default to ensure uniqueness implies user might want new one
    # But user input overrides.
    
    repo_id = f"{user}/{repo_name}"

    print(f"Target Space: {repo_id}")

    try:
        # Check if exists
        api.repo_info(repo_id=repo_id, repo_type="space")
        print(f"Space {repo_id} already exists. Uploading to it...")
    except HfHubHTTPError:
        print(f"Space {repo_id} not found. Creating...")
        try:
            create_repo(repo_id=repo_id, repo_type="space", space_sdk="docker", private=False, token=token)
            print("Space created successfully.")
        except Exception as e:
            print(f"Failed to create space: {e}")
            return

    print("Uploading files... This may take a minute.")
    try:
        upload_url = upload_folder(
            folder_path=".",
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
                "setup_hf_space.py"
            ]
        )
        print(f"Successfully uploaded to {upload_url}")
        print(f"Your Space is building at: https://huggingface.co/spaces/{repo_id}")
    except Exception as e:
        print(f"Upload failed: {e}")

if __name__ == "__main__":
    main()
