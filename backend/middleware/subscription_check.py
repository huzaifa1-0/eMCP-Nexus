# backend/middleware/subscription_check.py
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.db import DBSubscription, DBUser, DBTool
from backend.db import get_async_session
from backend.security import get_current_user

async def check_subscription_access(
    tool_id: int,
    user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Check if user has an active subscription to the specified tool.
    Raises 403 if no active subscription found.
    """
    
    # Check for active subscription
    result = await session.execute(
        select(DBSubscription).where(
            DBSubscription.user_id == user.id,
            DBSubscription.tool_id == tool_id,
            DBSubscription.status == "active"
        )
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        # Get tool details for error message
        tool_result = await session.execute(select(DBTool).where(DBTool.id == tool_id))
        tool = tool_result.scalar_one_or_none()
        tool_name = tool.name if tool else "this tool"
        
        raise HTTPException(
            status_code=403,
            detail={
                "error": "subscription_required",
                "message": f"You need an active subscription to use {tool_name}",
                "tool_id": tool_id,
                "tool_name": tool_name,
                "price": tool.cost if tool else 14.99
            }
        )
    
    return subscription

async def get_user_subscriptions(
    user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get all active subscriptions for the current user"""
    
    result = await session.execute(
        select(DBSubscription, DBTool).join(
            DBTool, DBSubscription.tool_id == DBTool.id
        ).where(
            DBSubscription.user_id == user.id,
            DBSubscription.status == "active"
        )
    )
    
    subscriptions = []
    for sub, tool in result:
        subscriptions.append({
            "subscription_id": sub.id,
            "tool_id": tool.id,
            "tool_name": tool.name,
            "tool_description": tool.description,
            "tool_url": tool.url,
            "plan": sub.plan,
            "status": sub.status,
            "started_at": sub.created_at.isoformat() if sub.created_at else None
        })
    
    return subscriptions