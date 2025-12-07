from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_async_session
from backend.ai_services.search_engine import search_tools

router = APIRouter()

@router.get("/")
async def semantic_search(
    query: str = Query(..., description="Search query for AI tools"),
    k: int = Query(5, description="Number of results to return"),
    session: AsyncSession = Depends(get_async_session) 
) -> dict:
    """
    Semantic search for tools using embeddings + vector DB (BigQuery or FAISS fallback).
    """
    
    results = await search_tools(session, query, k=k)
    
    return {
        "query": query,
        "results": results
    }