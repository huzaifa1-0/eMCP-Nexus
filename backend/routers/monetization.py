# backend/routers/monetization.py
from fastapi import APIRouter, Depends, HTTPException
from ai_services.monetization import get_dynamic_price, get_subscription_plans
from ai_services.monitoring import get_tool_usage
from ai_services.reputation import calculate_reputation
from backend.db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.db import DBTransaction, DBRating
from sqlalchemy import select
from backend.models.db import DBTool, DBTransaction, DBRating

router = APIRouter()

@router.get("/price/{tool_id}")
async def dynamic_price(tool_id: int, session: AsyncSession = Depends(get_async_session)):
    """
    Get the dynamic price for a tool.
    """
    tool_result = await session.execute(select(DBTool).where(DBTool.id == tool_id))
    tool = tool_result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    # You'll need to fetch the necessary data to calculate the price
    txs_result = await session.execute(select(DBTransaction.amount).where(DBTransaction.tool_id == tool_id))
    txs = [row[0] for row in txs_result.all()]
    ratings_result = await session.execute(select(DBRating.rating).where(DBRating.tool_id == tool_id))
    ratings = [row[0] for row in ratings_result.all()]
    usage_logs = await get_tool_usage(session, tool_id)

    
    reputation_score = calculate_reputation(txs, ratings, usage_logs, success_rate=0.95, avg_processing_time=1.5)

    price = get_dynamic_price(tool.cost, tool_id, reputation_score, {tool_id: usage_logs})
    return {"tool_id": tool_id, "base_price": tool.cost, "dynamic_price": price}

@router.get("/subscriptions/{tool_id}")
async def subscriptions(tool_id: int):
    """
    Get available subscription plans for a tool.
    """
    plans = get_subscription_plans(tool_id)
    return {"tool_id": tool_id, "subscription_plans": plans}