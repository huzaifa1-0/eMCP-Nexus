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
            # indices[0] is the list of IDs, distances[0] is the list of scores
            for i, idx in enumerate(indices[0]):
                dist = distances[0][i]
                
                # Check if valid index AND within similarity threshold
                if idx != -1 and idx in index_to_tool_id:
                    if dist < SIMILARITY_THRESHOLD:
                        tool_id = index_to_tool_id[idx]
                        found_ids.append(tool_id)
            
            # If we found relevant semantic matches, fetch them
            if found_ids:
                # Maintain order of relevance by fetching and re-sorting in Python if necessary,
                # or just fetch where ID is in the list.
                stmt = select(DBTool).where(DBTool.id.in_(found_ids))
                result = await session.execute(stmt)
                fetched_tools = result.scalars().all()
                
                # Sortfetched tools to match the order found by FAISS (most relevant first)
                tools_map = {t.id: t for t in fetched_tools}
                tools = [tools_map[tid] for tid in found_ids if tid in tools_map]
                
        except Exception as e:
            print(f"⚠️ FAISS Error: {e}")

    # 2. Fallback SQL Search (ONLY if FAISS found nothing)
    # If FAISS returned results, we usually assume those are better than a simple text match.
    if not tools:
        print("ℹ️ Using SQL Fallback Search")
        stmt = select(DBTool).where(
            (DBTool.name.ilike(f"%{query}%")) | 
            (DBTool.description.ilike(f"%{query}%"))
        ).limit(k)
        result = await session.execute(stmt)
        tools = result.scalars().all()

    # 3. REMOVED "Last Resort" BLOCK
    # We deleted the block that returns random tools if nothing is found.
    # Now, if the query matches nothing, it correctly returns an empty list [].

    # Format for JSON response
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "cost": t.cost,
            "url": getattr(t, 'url', ''),
            "owner_id": t.owner_id
        } 
        for t in tools
    ]