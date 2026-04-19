# testing/create_tool_simple.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from backend.models.db import DBTool, DBUser
from backend.config import settings

async def create_tool():
    DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get user
        result = await session.execute(select(DBUser).where(DBUser.email == "ans121@gmail.com"))
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ User not found!")
            return
        
        print(f"✅ Found user: {user.email} (ID: {user.id})")
        
        # Create tool using SQLAlchemy (handles JSON correctly)
        tool = DBTool(
            name="Stripe Test Tool",
            description="Test tool for Stripe payments",
            cost=4.99,
            repo_url="https://github.com/test/repo",
            branch="main",
            build_command="echo 'build complete'",
            start_command="echo 'start complete'",
            root_dir="",
            owner_id=user.id,
            url="http://localhost:8000/test-tool",
            tool_definitions=["test_subscribe", "test_payment"],  # List is fine here
            status="active",
            deploy_id="manual_001"
        )
        
        session.add(tool)
        await session.commit()
        await session.refresh(tool)
        
        print(f"\n✅ Tool created successfully!")
        print(f"   Tool ID: {tool.id}")
        print(f"   Tool Name: {tool.name}")
        print(f"   tool_definitions: {tool.tool_definitions}")
        print(f"\n📝 Use Tool ID: {tool.id} for Stripe testing")

if __name__ == "__main__":
    asyncio.run(create_tool())