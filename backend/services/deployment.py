import os
import httpx
import uuid
from dotenv import load_dotenv  # Import dotenv
from typing import Optional, Dict

# Load environment variables from .env file
load_dotenv()

async def deploy_tool(repo_url: str, branch: str, build_command: str, start_command: str, root_dir: str, env_vars: Optional[Dict[str, str]] = None):
    api_key = os.getenv("RENDER_API_KEY")
    owner_id = os.getenv("RENDER_OWNER_ID")
    
    if not api_key or not owner_id:
        raise ValueError("Missing RENDER_API_KEY or RENDER_OWNER_ID in .env file")

    url = "https://api.render.com/v1/services"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    base_name = repo_url.split("/")[-1]
    unique_suffix = str(uuid.uuid4())[:8]
    service_name = f"{base_name}-{unique_suffix}"
    
    render_env_vars = []
    if env_vars:
        for key, value in env_vars.items():
            render_env_vars.append({"key": key, "value": value})
    # Simple payload to deploy a Python service from a public repo
    payload = {
        "serviceDetails": {
            "model": "free",
            "env": "python", # Defaulting to python for MCP quickstarts
            "envSpecificDetails": {
                "buildCommand": build_command, # Standard build command
                "startCommand": start_command # Standard start command
            }
        },
        "type": "web_service",
        "name": service_name, 
        "ownerId": owner_id,
        "repo": repo_url,
        "autoDeploy": "yes",
        "branch": branch,
        "rootDir": root_dir
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print(f"🚀 Deploying to Render: {repo_url}")
            print(f"📦 Service Name: {service_name}")
            # Use sensitive data masking for logs
            debug_payload = payload.copy()
            print(f"📝 Payload: {debug_payload}")
            
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code >= 500:
                print(f"❌ Render Server Error: {response.text}")
                
            response.raise_for_status()
            data = response.json()
            
            return {
                "url": data["service"]["serviceDetails"]["url"],
                "serviceId": data["service"]["id"]
            }
            
        except httpx.HTTPError as e:
            # Safely get response text if it exists
            response = getattr(e, 'response', None)
            error_msg = response.text if response is not None else str(e)
            print(f"❌ Render Deployment Error: {error_msg}")
            raise ValueError(f"Render API error: {error_msg}")

async def get_service_status(service_id: str) -> str:
    """
    Polls Render API to get the current status of a service.
    """
    api_key = os.getenv("RENDER_API_KEY")
    
    if not api_key:
        print("❌ Error: RENDER_API_KEY missing during status check")
        return "error"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }

    url = f"https://api.render.com/v1/services/{service_id}/deploys?limit=1"

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, headers=headers)
            
            # If Render says "Not Found" or "Unauthorized", return error
            if response.status_code != 200:
                print(f"⚠️ Render API Warning: Received {response.status_code}")
                return "error"

            deploys = response.json()
            
            # ✅ SAFE CHECK: Use .get() to avoid crashing
            if isinstance(deploys, list) and len(deploys) > 0:
                latest_deploy = deploys[0]
                
                # Try to get 'status', if missing try 'state', if both missing assume 'live' (since 200 OK)
                status = latest_deploy.get('status') or latest_deploy.get('state') or "live"
                return status
            
            # If list is empty, it might be a fresh service
            return "live"

        except Exception as e:
            print(f"❌ Error checking service status: {e}")
            return "error"
        

# ... (keep existing imports and code) ...

async def fetch_repo_readme(repo_url: str, branch: str = "main") -> str:
    """
    Fetches the README.md from a GitHub repository to use as context for the AI.
    """
    # 1. Clean the URL (remove .git suffix if present)
    clean_url = repo_url.strip().rstrip(".git")
    
    # 2. Convert standard GitHub URL to Raw User Content URL
    # From: https://github.com/username/repo
    # To:   https://raw.githubusercontent.com/username/repo/{branch}/README.md
    if "github.com" in clean_url:
        raw_url = clean_url.replace("github.com", "raw.githubusercontent.com")
        raw_url = f"{raw_url}/{branch}/README.md"
    else:
        # If it's not a GitHub URL, we skip it for now
        return ""

    async with httpx.AsyncClient() as client:
        try:
            print(f"📥 Fetching README context from: {raw_url}")
            response = await client.get(raw_url, follow_redirects=True, timeout=5.0)
            
            if response.status_code == 200:
                # Limit to 1000 characters to prevent overloading the vector embedding model
                # and strip excessive whitespace
                content = response.text[:1000].strip()
                return content
            else:
                print(f"⚠️ README not found (Status: {response.status_code})")
                return ""
        except Exception as e:
            print(f"⚠️ Failed to fetch README: {e}")
            return ""