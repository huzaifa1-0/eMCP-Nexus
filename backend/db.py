from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from backend.models.db import Base
from backend.config import settings


engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=True,
    connect_args={"check_same_thread": False}  # Only for SQLite
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