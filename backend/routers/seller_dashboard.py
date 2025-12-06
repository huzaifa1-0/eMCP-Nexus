from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any

from backend.db import get_async_session
from backend.security import get_current_user
from backend.models.db import DBUser, DBTool, DBTransaction, DBUsageLog

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Returns aggregated metrics for the Seller Dashboard.
    """
    result = await session.execute(select(DBTool).where(DBTool.owner_id == current_user.id))
    user_tools = result.scalars().all()

    tool_ids = [t.id for t in user_tools]

    if not tool_ids:
        return {
            "totalInstalls": 0,
            "totalRuns": 0,
            "tokensUsed": 0,
            "totalRevenue": 0.0,
            "performanceData": []
        }
    
    runs_query = select(func.count(DBUsageLog.id)).where(DBUsageLog.tool_id.in_(tool_ids))
    runs_result = await session.execute(runs_query)
    total_runs = runs_result.scalar() or 0

    