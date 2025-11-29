import httpx
import os
from dotenv import load_dotenv

load_dotenv()

RENDER_API_KEY = os.getenv("RENDER_API_KEY")
RENDER_OWNER_ID = os.getenv("RENDER_OWNER_ID")

async def deploy_tool(repo_url: str) -> dict:
    
    if not RENDER_API_KEY or not RENDER_OWNER_ID:
        raise ValueError("Render API key or owner ID is not set in environment variables.")
    
    headers = {
        "Authentication": f"Bearer {RENDER_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    service_name = repo_url.split("/")[-1].replace(".git", "")

    payload = {
        "serviceDetails": {
            "env":"Python",
            "repo": repo_url,
            "name": service_name,
            "ownerId": RENDER_OWNER_ID,
            "autoDeploy": "yes",
            "branch": "main"
        },
        "type": "web_srv",
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.render.com/v1/services", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            return {
                        "url": data["service"]["url"],
                        "serviceId": data["service"]["id"]
            }
    except httpx.HTTPError as e:
         raise ValueError(f"Render API error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        # Handle network-level errors
        raise ValueError(f"Failed to connect to Render API: {str(e)}")
    

async def get_service_status(service_id: str) -> str:
    """
    Polls Render API to get the current status of a service.
    """
    if not RENDER_API_KEY:
        raise ValueError("Render API key is not set.")

    headers = {
        "Authorization": f"Bearer {RENDER_API_KEY}",
        "Accept": "application/json"
    }

    url = f"https://api.render.com/v1/services/{service_id}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # The status might be 'live', 'suspended', 'build_in_progress', etc.
            # You might need to adjust based on the exact Render API response structure
            # Usually it is data['service']['suspended'] or a specific status field
            # For now, let's assume Render returns a 'status' field on the service object
            # Note: Render API specifics might vary, check response if 'status' is missing.
            
            # Render often uses 'suspended' to indicate 'not live'. 
            # If the API returns a specific status field (like 'cursor'), use that.
            # For this example, we will assume data['service']['updatedAt'] changes or similar.
            
            # However, looking at standard Render API, the service object has a 'serviceDetails' 
            # but status is often inferred. 
            # Let's try to get the latest deploy status instead which is more reliable for "is it live?"
            
            # Alternative: Get latest deploy
            deploy_url = f"https://api.render.com/v1/services/{service_id}/deploys?limit=1"
            deploy_res = await client.get(deploy_url, headers=headers)
            if deploy_res.status_code == 200 and len(deploy_res.json()) > 0:
                return deploy_res.json()[0]['status'] # e.g., 'live', 'build_in_progress'
            
            return "unknown"

        except httpx.HTTPError as e:
            print(f"Error checking service status: {e}")
            return "error"
