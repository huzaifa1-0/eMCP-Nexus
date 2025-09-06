from typing import List, Dict
import os
from google.cloud import bigquery
from .embeddings import get_embedding


project_id = os.getenv("GOOGLE_PROJECT")
dataset_id = os.getenv("GOOGLE_DATASET")
table_id = "tools_with_embeddings"
client = bigquery.Client(project=project_id)



async def search_tools(query: str, k: int = 5) -> List[Dict]:
    """
    Semantic search for tools using BigQuery Vector Search.
    """
    query_embedding = get_embedding(query)

    sql = f"""
    SELECT
        id,
        name,
        description,
        cost,
        url,
        owner_id,
        embedding,
        COSINE_DISTANCE(embedding, {query_embedding}) as distance
    FROM
        `{project_id}.{dataset_id}.{table_id}`
    ORDER BY
        distance
    LIMIT {k}
    """


    try:
        query_job = client.query(sql)
        results = query_job.result()

        tools = []
        for row in results:
            tools.append({
                "id": row.id,
                "name": row.name,
                "description": row.description,
                "cost": row.cost,
                "url": row.url,
                "owner_id": row.owner_id,
                "score": 1 - row.distance  # Convert distance to similarity score
            })
        return tools
    except Exception as e:
        print(f"BigQuery search failed: {e}")
        # Optionally, you can fallback to your FAISS implementation here
        return []