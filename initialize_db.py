import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.db import init_db

async def initialize_database():
    try:
        await init_db()
        print("✅ Database initialized successfully!")
        print("📁 SQLite database file created: marketplace.db")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")

if __name__ == "__main__":
    asyncio.run(initialize_database())