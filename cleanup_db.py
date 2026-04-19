import asyncio
from sqlalchemy import text
from backend.db import engine

async def cleanup():
    print("🧹 Cleaning up production database...")
    try:
        async with engine.begin() as conn:
            # Delete tools and related data
            # Order matters because of Foreign Keys
            await conn.execute(text("DELETE FROM ratings;"))
            await conn.execute(text("DELETE FROM tools;"))
            print("✅ All test tools and reviews have been deleted.")
            print("🚀 Your marketplace is now a clean slate for real users!")
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")

if __name__ == "__main__":
    asyncio.run(cleanup())
