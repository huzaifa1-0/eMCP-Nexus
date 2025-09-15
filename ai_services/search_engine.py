from typing import List, Dict
import os
import faiss
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.db import DBTool
from .embeddings import get_embedding
import asyncio


DIMENSION = 384
FAISS_INDEX_PATH = "faiss_index.bin"

index = faiss.IndexFlatL2(DIMENSION)

index_to_tool_id = {}

def save_faiss_index():
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open("index_to_tool_id.json", "w") as f:
        import json
        json.dump(index_to_tool_id, f)

def load_faiss_index():
    global index, index_to_tool_id
    if os.path.exists(FAISS_INDEX_PATH):
        index = faiss.read_index(FAISS_INDEX_PATH)
        with open("index_to_tool_id.json", "r") as f:
            import json
            index_to_tool_id = {int(k): v for k, v in json.load(f).items()}
        print("Faiss index json successfully")
    else:
        print("Faiss index file not found, starting with an empty index")

faiss_lock = asyncio.Lock()

async def add_tool_to_faiss(tool_id: int, name: str, description: str):
    embedding = get_embedding(f"{name}. {description}")

    embedding_np = np.array([embedding]).astype('float32')
    async with faiss_lock:
        index.add(embedding_np)
        new_index_position = index.ntotal - 1
        index_to_tool_id[new_index_position] = tool_id
        save_faiss_index()
        print(f"Tool {tool_id} added to Faiss index at position {new_index_position}")

async def search_tools(session: AsyncSession, query: str, k: int = 5) -> List[Dict]:
    if index.ntotal == 0:
        return []
    
    query_embedding = get_embedding(query)
    query_embedding_np = np.array([query_embedding]).astype('float32')

    distances, indices = index.search(query_embedding_np, k)

    tool_ids = [index_to_tool_id[i] for i in indices[0]]

    result = await session.execute(
        select(DBTool).where(DBTool.id.in_(tool_ids))
    )

    tools = []
    for tool in result.scalars().all():
        tools.append({
            "id": tool.id,
            "name": tool.name,
            "description": tool.description,
            "cost": tool.cost,
            "url": tool.url,
            "owner_id": tool.owner_id
        })
    return tools
