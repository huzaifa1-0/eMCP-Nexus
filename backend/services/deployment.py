import os
import httpx
from dotenv import load_dotenv  # Import dotenv

# Load environment variables from .env file
load_dotenv()

async def deploy_tool(repo_url: str):
    api_key = os.getenv("RENDER_API_KEY")
    owner_id = os.getenv("RENDER_OWNER_ID")
    
    if not api_key or not owner_id:
        # Debug print to help you see if it failed
        print(f"DEBUG: API Key present? {bool(api_key)}, Owner ID present? {bool(owner_id)}")
        raise ValueError("Missing RENDER_API_KEY or RENDER_OWNER_ID in .env file")

    url = "https://api.render.com/v1/services"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Simple payload to deploy a Node/Python service from a public repo
    payload = {
        "serviceDetails": {
            "env": "node", # Defaulting to node for MCP quickstarts
            "envSpecificDetails": {
                "buildCommand": "npm install && npm run build", # Standard build command
                "startCommand": "node build/index.js" # Standard start command
            }
        },
        "type": "web_service",
        "name": repo_url.split("/")[-1], 
        "ownerId": owner_id,
        "repo": repo_url,
        "autoDeploy": "yes",
        "branch": "main"
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
    # FIX: Get the key inside this function too
    api_key = os.getenv("RENDER_API_KEY")
    
    if not api_key:
        print("❌ Error: RENDER_API_KEY missing during status check")
        return "error"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }

    url = f"https://api.render.com/v1/services/{service_id}/deploys?limit=1"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                deploys = response.json()
                if len(deploys) > 0:
                    return deploys[0]['status'] # e.g., 'live', 'build_in_progress'
            return "unknown"

        except Exception as e:
            print(f"Error checking service status: {e}")
            return "error"