from typing import List, Dict, Any
import os
import json
import asyncio
import numpy as np
import faiss
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.db import DBTool
from backend.ai_services.embeddings import get_embedding

# --- Configuration ---
DIMENSION = 384
FAISS_INDEX_PATH = "faiss_index.bin"
MAP_PATH = "index_to_tool_id.json"

# --- Global State ---
index = faiss.IndexFlatL2(DIMENSION)
index_to_tool_id = {}
faiss_lock = asyncio.Lock()

# --- Helpers ---
def save_faiss_index():
    try:
        faiss.write_index(index, FAISS_INDEX_PATH)
        with open(MAP_PATH, "w") as f:
            json.dump(index_to_tool_id, f)
    except Exception as e:
        print(f"Error saving FAISS index: {e}")

def load_faiss_index():
    global index, index_to_tool_id
    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(MAP_PATH):
        try:
            index = faiss.read_index(FAISS_INDEX_PATH)
            with open(MAP_PATH, "r") as f:
                data = json.load(f)
                index_to_tool_id = {int(k): v for k, v in data.items()}
            print(f"✅ FAISS index loaded with {index.ntotal} vectors.")
        except Exception as e:
            print(f"⚠️ Failed to load FAISS index: {e}")
            index = faiss.IndexFlatL2(DIMENSION)
            index_to_tool_id = {}
    else:
        print("ℹ️ No existing FAISS index found. Starting fresh.")

# Load immediately
load_faiss_index()

# --- Core Functions ---

async def add_tool_to_faiss(tool_id: int, name: str, description: str):
    """
    Adds a tool to the FAISS index.
    """
    try:
        text = f"{name}. {description}"
        embedding = get_embedding(text)
        embedding_np = np.array([embedding]).astype('float32')

        async with faiss_lock:
            index.add(embedding_np)
            new_position = index.ntotal - 1
            index_to_tool_id[new_position] = tool_id
            save_faiss_index()
            print(f"✅ Tool {tool_id} added to Semantic Search.")
    except Exception as e:
        print(f"❌ Error adding tool to FAISS: {e}")

# --- THE CRITICAL FUNCTION FIX ---
async def search_tools(session: AsyncSession, query: str, k: int = 5) -> List[Dict[str, Any]]:
    """
    Hybrid Search: FAISS -> SQL Fallback
    CRITICAL: This function MUST accept 'k' as an argument.
    """
    tools = []
    
    # 1. Try Semantic Search (FAISS)
    if index.ntotal > 0:
        try:
            query_embedding = get_embedding(query)
            query_np = np.array([query_embedding]).astype('float32')
            distances, indices = index.search(query_np, k)
            
            found_ids = [index_to_tool_id.get(i) for i in indices[0] if i != -1 and i in index_to_tool_id]
            
            if found_ids:
                stmt = select(DBTool).where(DBTool.id.in_(found_ids))
                result = await session.execute(stmt)
                tools = result.scalars().all()
        except Exception as e:
            print(f"⚠️ FAISS Error: {e}")

    # 2. Fallback SQL Search (If FAISS failed or empty)
    if not tools:
        print("ℹ️ Using SQL Fallback Search")
        stmt = select(DBTool).where(
            (DBTool.name.ilike(f"%{query}%")) | 
            (DBTool.description.ilike(f"%{query}%"))
        ).limit(k)
        result = await session.execute(stmt)
        tools = result.scalars().all()

    # 3. Last Resort (Show anything)
    if not tools:
        stmt = select(DBTool).order_by(DBTool.id.desc()).limit(k)
        result = await session.execute(stmt)
        tools = result.scalars().all()

    # Format for JSON response
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "cost": t.cost,
            "url": getattr(t, 'url', ''), # Safe access
            "owner_id": t.owner_id
        } 
        for t in tools
    ]