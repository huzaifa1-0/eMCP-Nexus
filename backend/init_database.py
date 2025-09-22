import asyncio
import os
import sys

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from backend.db import init_db

async def initialize():
    try:
        await init_db()
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")

if __name__ == "__main__":
    asyncio.run(initialize())