from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from backend.models.db import Base
from backend.config import settings

DATABASE_URL = "postgresql+asyncpg://admin:password@db:5432/marketplace"


engine = create_async_engine(
    DATABASE_URL, 
    echo=True,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
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
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)