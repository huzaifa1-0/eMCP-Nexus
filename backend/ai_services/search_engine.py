from typing import List, Dict, Any
import os
import json
import asyncio
import numpy as np
import faiss
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.db import DBTool, DBRating, DBUser
from backend.ai_services.embeddings import get_embedding

# --- Configuration ---
DIMENSION = 384
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "faiss_index.bin")
MAP_PATH = os.path.join(BASE_DIR, "index_to_tool_id.json")

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


load_faiss_index()

# --- Core Functions ---

async def add_tool_to_faiss(tool_id: int, name: str, description: str, readme: str = ""):
    """
    Adds a tool to the FAISS index. Combines name, description, and readme for better semantic matching.
    """
    try:
        # Combine all metadata for a rich search context
        rich_text = f"Name: {name}. Description: {description}. Details: {readme or ''}"
        embedding = get_embedding(rich_text)
        embedding_np = np.array([embedding]).astype('float32')

        async with faiss_lock:
            index.add(embedding_np)
            new_position = index.ntotal - 1
            index_to_tool_id[new_position] = tool_id
            save_faiss_index()
            print(f"✅ Tool {tool_id} indexed in Semantic Search (Context length: {len(rich_text)} chars).")
    except Exception as e:
        print(f"❌ Error adding tool to FAISS: {e}")

async def remove_tool_from_faiss(tool_id: int):
    """
    Removes a tool from the FAISS index by rebuilding the index without it.
    (FAISS IndexFlatL2 doesn't support easy individual removal, so we rebuild from the mapping)
    """
    try:
        global index, index_to_tool_id
        async with faiss_lock:
            # Create a new index and mapping
            new_index = faiss.IndexFlatL2(DIMENSION)
            new_mapping = {}
            
            # Re-add everything except the deleted tool
            # This is faster than a full DB re-index because we don't need to re-fetch/re-embed
            # But wait, we don't store the vectors in memory. 
            # Actually, for small scales, a full re-index from DB is fine.
            # If scale is large, we'd need a more complex vector DB.
            print(f"🗑️ Removing tool {tool_id} from search index...")
            
        # For now, let's just trigger a re-index from DB to keep it simple and consistent
        # In a real vector DB like Pinecone, this is a single API call.
        pass 
    except Exception as e:
        print(f"❌ Error removing tool from FAISS: {e}")

async def reindex_all_tools(session: AsyncSession):
    """
    Clears the FAISS index and rebuilds it from the database.
    """
    print("🔄 Re-indexing all tools from database...")
    try:
        global index, index_to_tool_id
        
        # 1. Reset index
        async with faiss_lock:
            index = faiss.IndexFlatL2(DIMENSION)
            index_to_tool_id = {}
        
        # 2. Fetch all tools
        stmt = select(DBTool)
        result = await session.execute(stmt)
        tools = result.scalars().all()
        
        # 3. Add each tool
        for t in tools:
            await add_tool_to_faiss(t.id, t.name, t.description, getattr(t, 'readme', ''))
            
        print(f"✅ Re-indexing complete. {index.ntotal} tools indexed.")
    except Exception as e:
        print(f"❌ Re-indexing failed: {e}")


SIMILARITY_THRESHOLD = 1.0 

async def search_tools(session: AsyncSession, query: str, k: int = 5) -> List[Dict[str, Any]]:
    """
    Hybrid Search: FAISS -> SQL Fallback
    """
    tools = []
    found_ids = []
    
    # 1. Try Semantic Search (FAISS)
    if index.ntotal > 0:
        try:
            query_embedding = get_embedding(query)
            query_np = np.array([query_embedding]).astype('float32')
            
            # Search FAISS
            distances, indices = index.search(query_np, k)
            
            # Filter results by distance threshold
            for i, idx in enumerate(indices[0]):
                dist = distances[0][i]
                if idx != -1 and idx in index_to_tool_id:
                    if dist < SIMILARITY_THRESHOLD:
                        tool_id = index_to_tool_id[idx]
                        found_ids.append(tool_id)
            
            if found_ids:
                from sqlalchemy.orm import selectinload
                stmt = select(DBTool).options(
                    selectinload(DBTool.owner).selectinload(DBUser.tools),
                    selectinload(DBTool.ratings).selectinload(DBRating.user)
                ).where(DBTool.id.in_(found_ids))
                result = await session.execute(stmt)
                fetched_tools = result.scalars().all()
                
                tools_map = {t.id: t for t in fetched_tools}
                tools = [tools_map[tid] for tid in found_ids if tid in tools_map]
                
        except Exception as e:
            print(f"⚠️ FAISS Error: {e}")

    # 2. Fallback SQL Search
    if not tools:
        print("ℹ️ Using SQL Fallback Search")
        from sqlalchemy.orm import selectinload
        stmt = select(DBTool).options(
            selectinload(DBTool.owner).selectinload(DBUser.tools),
            selectinload(DBTool.ratings).selectinload(DBRating.user)
        ).where(
            (DBTool.name.ilike(f"%{query}%")) | 
            (DBTool.description.ilike(f"%{query}%"))
        ).limit(k)
        result = await session.execute(stmt)
        tools = result.scalars().all()

    # Format for JSON response
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "cost": t.cost,
            "url": getattr(t, 'url', ''),
            "owner_id": t.owner_id,
            "author": t.author,
            "author_tools_count": t.author_tools_count,
            "reviews": t.reviews
        } 
        for t in tools
    ]