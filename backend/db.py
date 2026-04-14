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
    import asyncio
    
    # Redact password for logging but show host/port/db
    try:
        if "@" in settings.DATABASE_URL:
            # Format: protocol://user:pass@host:port/db
            prefix_part, rest_part = settings.DATABASE_URL.split("@", 1)
            protocol_user = prefix_part.split(":", 1)[0] + "://***"
            print(f"Connecting to database: {protocol_user}@{rest_part}")
        else:
            print(f"Connecting to database: {settings.DATABASE_URL}")
    except Exception:
        # Fallback if parsing fails
        print("Connecting to database: [Hidden URL]")
    
    max_retries = 10
    retry_delay = 2
    
    for attempt in range(1, max_retries + 1):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print(f"✅ Database tables created/verified on attempt {attempt}.")
            return
        except Exception as e:
            if attempt == max_retries:
                print(f"❌ Could not connect to database after {max_retries} attempts: {e}")
                raise e
            print(f"⚠️ Connection attempt {attempt}/{max_retries} failed. Retrying in {retry_delay}s...")
            await asyncio.sleep(retry_delay)