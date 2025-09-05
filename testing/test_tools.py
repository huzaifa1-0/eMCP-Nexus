# testing/test_tools.py
import pytest
from httpx import AsyncClient
from fastapi import status

pytestmark = pytest.mark.asyncio

async def get_auth_token(async_client: AsyncClient, username: str, email: str) -> str:
    await async_client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": "password123"},
    )
    response = await async_client.post(
        "/auth/login",
        json={"email": email, "password": "password123"},
    )
    return response.json()["access_token"]

async def test_create_tool(async_client: AsyncClient):
    token = await get_auth_token(async_client, "tool_creator", "creator@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    tool_data = {"name": "My New Tool", "description": "A great new tool", "cost": 10.0, "url": "http://example.com"}
    
    response = await async_client.post("/tools/", json=tool_data, headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == tool_data["name"]
    assert "id" in data

async def test_get_tool(async_client: AsyncClient):
    # First, create a tool
    token = await get_auth_token(async_client, "tool_owner", "owner@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    tool_data = {"name": "Another Tool", "description": "Another great tool", "cost": 5.0, "url": "http://example.com/another"}
    create_response = await async_client.post("/tools/", json=tool_data, headers=headers)
    tool_id = create_response.json()["id"]
    
    # Now, get the tool
    response = await async_client.get(f"/tools/{tool_id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == tool_data["name"]
    assert data["id"] == tool_id

async def test_get_non_existent_tool(async_client: AsyncClient):
    response = await async_client.get("/tools/999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND