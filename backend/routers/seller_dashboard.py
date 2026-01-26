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

    revenue_query = select(func.sum(DBTransaction.amount)).where(DBTransaction.tool_id.in_(tool_ids))
    revenue_result = await session.execute(revenue_query)
    total_revenue = revenue_result.scalar() or 0.0

    performance_data = []
    for tool in user_tools:
        # Get runs for this specific tool
        tool_runs_res = await session.execute(
            select(func.count(DBUsageLog.id)).where(DBUsageLog.tool_id == tool.id)
        )
        tool_runs = tool_runs_res.scalar() or 0

        tool_rev_res = await session.execute(
            select(func.sum(DBTransaction.amount)).where(DBTransaction.tool_id == tool.id)
        )
        tool_revenue = tool_rev_res.scalar() or 0.0

        performance_data.append({
            "name": f"{tool.name}",
            "installs": 1, 
            "runs": tool_runs,
            "tokens": tool_runs * 150, 
            "revenue": tool_revenue,
            "date": tool.created_at.strftime("%Y-%m-%d") if hasattr(tool, 'created_at') else "2025-01-01" 
        })

    return {
        "totalInstalls": len(user_tools), 
        "totalRuns": total_runs,
        "tokensUsed": total_runs * 150, 
        "totalRevenue": total_revenue,
        "performanceData": performance_data
    }