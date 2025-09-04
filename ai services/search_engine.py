from typing import List,Dict
import os
from .embeddings import get_embedding


USE_BIGQUERY = os.getenv("USE_BIGQUERY", "false").lower() == "true"



async def search_tools(query: str, k: int = 5) -> List[Dict]:
     """
    Searches tools based on semantic similarity.
    Uses BigQuery if available, else falls back to FAISS.
    """
     query_embedding = get_embedding(query)

     if USE_BIGQUERY:
          # TODO: Replace with actual BigQuery Vector Search
        return [{"id": 1, "name": "BigQuery Search Stub", "score": 0.95}]
     else:
         import faiss
         import numpy as np

         tools_db = {
            1: ("AI Summarizer", get_embedding("summarize documents")),
            2: ("Image Classifier", get_embedding("classify pictures")),
            3: ("Speech-to-Text", get_embedding("convert audio to text"))
        }
        
         d = len(query_embedding)
         index = faiss.IndexFlatL2(d)
         vectors = np.array([v for _, v in tools_db.values()]).astype("float32")
         
     