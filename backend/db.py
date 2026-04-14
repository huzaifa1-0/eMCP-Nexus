from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from backend.models.db import Base
from backend.config import settings


engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=True, 
)
async_session_factory = async_sessionmaker(
    bind=engine, 
    expire_on_commit=False, 
    class_=AsyncSession
)
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
            


async def init_db():
    from backend.config import settings
    # Redact password for logging
    redacted_url = settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL
    print(f"Connecting to database: ...@{redacted_url}")
    
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
            print("Database tables created/verified.")
        except Exception as e:
            print(f"Error during database initialization: {e}")
            raise e