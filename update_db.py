import asyncio
import asyncpg
import os

from backend.config import settings

async def update_schema():
    # settings.DATABASE_URL -> postgresql+asyncpg://admin:password@localhost:5432/marketplace
    # need to strip postgresql+asyncpg:// to postgres:// for asyncpg
    url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgres://")
    conn = await asyncpg.connect(url)
    try:
        await conn.execute("ALTER TABLE users ADD COLUMN api_key VARCHAR UNIQUE;")
        print("✅ api_key column added successfully!")
    except asyncpg.exceptions.DuplicateColumnError:
        print("Column might already exist.")
    except Exception as e:
        print(f"❌ Error updating database schema: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(update_schema())
