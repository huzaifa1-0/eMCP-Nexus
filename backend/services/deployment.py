import os
import httpx
import uuid
from dotenv import load_dotenv  # Import dotenv

# Load environment variables from .env file
load_dotenv()

async def deploy_tool(repo_url: str, branch: str, build_command: str, start_command: str, root_dir: str):
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

    # Use a longer timeout (30s) to prevent premature timeouts
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, headers=headers)
            
            # 1. Log non-200 responses to see if Render is rejecting us
            if response.status_code != 200:
                print(f"⚠️ Render API Warning: Received {response.status_code}")
                print(f"   Response: {response.text}")
                return "unknown"

            deploys = response.json()
            if len(deploys) > 0:
                status = deploys[0]['status']
                # Map Render statuses to our internal statuses if needed
                return status 
            
            return "unknown"

        except httpx.TimeoutException:
            print(f"❌ Error: Connection timed out checking status for {service_id}")
            return "error"
        except Exception as e:
            # 2. Print the FULL error so we can fix it
            print(f"❌ CRITICAL Error checking service status: {type(e).__name__} - {e}")
            return "error"