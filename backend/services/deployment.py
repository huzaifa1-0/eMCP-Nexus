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

    async with httpx.AsyncClient() as client:
        