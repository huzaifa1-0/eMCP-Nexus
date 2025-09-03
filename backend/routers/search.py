from fastapi import APIRouter, Query
from google.cloud import bigquery
from backend.config import settings


router = APIRouter()
client = bigquery.Client(project=settings.GOOGLE_PROJECT)



@router.get("/")
async def semantic_search(q: str = Query(...)):
    query = f"""
        SELECT name, description, cost
        FROM `{settings.GOOGLE_PROJECT}.{settings.GOOGLE_DATASET}.tools`
        WHERE VECTOR_SEARCH(description, '{q}') LIMIT 5
    """

    results = client.query(query).result()
    return [dict(row) for row in results]


