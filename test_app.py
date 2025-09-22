import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.db import engine

async def test_database():
    try:
        async with engine.connect() as conn:
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing application setup...")
    asyncio.run(test_database())