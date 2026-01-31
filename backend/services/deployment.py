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

    async with httpx.AsyncClient() as client:
        try:
            print(f"🚀 Deploying to Render: {repo_url}")
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            return {
                "url": data["service"]["serviceDetails"]["url"],
                "serviceId": data["service"]["id"]
            }
            
        except httpx.HTTPError as e:
            error_msg = e.response.text if e.response else str(e)
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