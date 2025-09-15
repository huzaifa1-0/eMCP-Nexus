from typing import List, Dict
import os
import faiss
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.db import DBTool
from .embeddings import get_embedding


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

    
def add_tool_to_faiss(tool_id: int, name: str, description: str):
    embedding = get_embedding(f"{name}. {description}")

    embedding_np = np.array([embedding]).astype('float32')

    index.add(embedding_np)
    
