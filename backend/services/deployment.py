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

            return {"url": data["service"]["url"]}
    except httpx.HTTPError as e:
         raise ValueError(f"Render API error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        # Handle network-level errors
        raise ValueError(f"Failed to connect to Render API: {str(e)}")
