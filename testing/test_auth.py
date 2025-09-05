import pytest
from httpx import AsyncClient
from fastapi import status

# Mark all tests in this file as asyncio tests
pytestmark = pytest.mark.asyncio

async def test_register_user(async_client: AsyncClient):
    """Test user registration."""
    response = await async_client.post(
        "/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data

async def test_login_for_access_token(async_client: AsyncClient):
    """Test user login and token generation."""
    # First, register a user to ensure the user exists
    await async_client.post(
        "/auth/register",
        json={"username": "loginuser", "email": "login@example.com", "password": "password123"},
    )

    # Now, attempt to log in using the correct form data format
    response = await async_client.post(
        "/auth/token",
        data={"username": "loginuser", "password": "password123"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

async def test_create_tool_with_auth(async_client: AsyncClient):
    """Test creating a tool with a valid authentication token."""
    # Register and log in to get a token
    await async_client.post(
        "/auth/register",
        json={"username": "tooluser", "email": "tool@example.com", "password": "password123"},
    )
    login_response = await async_client.post(
        "/auth/token",
        data={"username": "tooluser", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Use the token to create a tool
    tool_data = {"name": "Test Tool", "description": "A tool for testing", "cost": 9.99, "url": "http://example.com/tool"}
    response = await async_client.post("/tools/", json=tool_data, headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Test Tool"
    assert "owner_id" in data

async def test_create_tool_without_auth(async_client: AsyncClient):
    """Test that creating a tool without a token fails."""
    tool_data = {"name": "Unauthorized Tool", "description": "This should fail", "cost": 1.00, "url": "http://example.com/fail"}
    response = await async_client.post("/tools/", json=tool_data)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

