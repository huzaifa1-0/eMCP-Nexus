from fastapi import APIRouter, Query
from ai_services.search_engine import search_tools

router = APIRouter()

@router.get("/search")
async def semantic_search(
    query: str = Query(..., description="Search query for AI tools"),
    k: int = Query(5, description="Number of results to return")
):
    """
    Semantic search for tools using embeddings + vector DB (BigQuery or FAISS fallback).
    """
    results = await search_tools(query, k=k)
    return {
        "query": query,
        "results": results
    }
