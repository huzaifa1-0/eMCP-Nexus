from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from backend.models.db import Base
from backend.config import settings


engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=True, 
    pool_pre_ping=True, # Verify connection liveness
    pool_recycle=300,   # Refresh connections every 5 minutes
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
                from sqlalchemy import text
                await conn.run_sync(Base.metadata.create_all)
                
                # Manual migration for new columns
                try:
                    # PostgreSQL supports 'ADD COLUMN IF NOT EXISTS'
                    if "postgresql" in settings.DATABASE_URL:
                        await conn.execute(text("ALTER TABLE ratings ADD COLUMN IF NOT EXISTS comment TEXT;"))
                        await conn.execute(text("ALTER TABLE tools ADD COLUMN IF NOT EXISTS readme TEXT;"))
                        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS api_key VARCHAR;"))
                    else:
                        # SQLite (Local) fallback
                        try:
                            await conn.execute(text("ALTER TABLE ratings ADD COLUMN comment TEXT;"))
                        except Exception: pass
                        try:
                            await conn.execute(text("ALTER TABLE tools ADD COLUMN readme TEXT;"))
                        except Exception: pass
                        try:
                            await conn.execute(text("ALTER TABLE users ADD COLUMN api_key VARCHAR;"))
                        except Exception: pass
                except Exception as me:
                    print(f"Migration info: {me}")
            
            print(f"✅ Database tables created/verified/migrated on attempt {attempt}.")
            return
        except Exception as e:
            if attempt == max_retries:
                print(f"❌ Could not connect to database after {max_retries} attempts.")
                print(f"Error details: {str(e)}")
                if "SSL" in str(e):
                    print("TIP: This looks like an SSL error. Check if your DATABASE_URL needs 'ssl=require'.")
                raise e
            print(f"⚠️ Connection attempt {attempt}/{max_retries} failed: {str(e)[:100]}...")
            print(f"Retrying in {retry_delay}s...")
            await asyncio.sleep(retry_delay)