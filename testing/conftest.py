import sys
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Add the project's root directory to the Python path
# This allows pytest to find the 'backend' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.main import app
from backend.db import get_async_session, Base


TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_db

@pytest_asyncio.fixture(scope="module")
async def async_client():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
