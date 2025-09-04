from typing import List, Dict
import os
import numpy as np
import faiss
from .embeddings import get_embedding

USE_BIGQUERY = os.getenv("USE_BIGQUERY", "false").lower() == "true"


async def search_tools(query: str, k: int = 5) -> List[Dict]:
    """
    Semantic search for tools.
    Uses BigQuery if enabled, else falls back to FAISS local index.
    """

    
    query_embedding = get_embedding(query)

    if USE_BIGQUERY:
        # 🚀 TODO: Replace with real BigQuery Vector Search logic
        return [{"id": 1, "name": "BigQuery Search Stub", "score": 0.95}]

    
    tools_db = {
        1: ("AI Summarizer", get_embedding("summarize documents")),
        2: ("Image Classifier", get_embedding("classify pictures")),
        3: ("Speech-to-Text", get_embedding("convert audio to text")),
        4: ("Chatbot Assistant", get_embedding("conversational AI chatbot")),
        5: ("Code Generator", get_embedding("generate source code from text"))
    }

    
    vectors = np.array([v for _, v in tools_db.values()]).astype("float32")
    d = vectors.shape[1]

    
    index = faiss.IndexFlatIP(d)
    faiss.normalize_L2(vectors)
    index.add(vectors)

    
    query_vec = np.array(query_embedding).astype("float32").reshape(1, -1)
    faiss.normalize_L2(query_vec)

    
    distances, indices = index.search(query_vec, min(k, len(tools_db)))

    results = []
    for idx, score in zip(indices[0], distances[0]):
        tool_id = list(tools_db.keys())[idx]
        tool_name = tools_db[tool_id][0]
        results.append({
            "id": tool_id,
            "name": tool_name,
            "score": float(score)  
        })

    
    results.sort(key=lambda x: x["score"], reverse=True)

    return results
