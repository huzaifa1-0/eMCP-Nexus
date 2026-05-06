from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.ai_services.monitoring import log_tool_usage as _log_tool_usage, get_tool_usage as _get_tool_usage
from backend.db import get_async_session

router = APIRouter()

@router.post("/log")
async def log_usage(
    tool_id: int, 
    user_id: int, 
    session: AsyncSession = Depends(get_async_session)
) -> dict:
    """
    Log usage of a tool by a user.
    """
    await _log_tool_usage(db=session, tool_id=tool_id, user_id=user_id, success=True, processing_time=0.0)
    return {"message": f"Usage logged for tool {tool_id} by user {user_id}"}

@router.get("/usage/{tool_id}")
async def get_usage(
    tool_id: int, 
    session: AsyncSession = Depends(get_async_session)
) -> dict:
    """
    Get usage history for a given tool.
    """
    history = await _get_tool_usage(db=session, tool_id=tool_id)
    return {
        "tool_id": tool_id, 
        "usage_history": [
            {
                "id": log.id,
                "tool_id": log.tool_id,
                "user_id": log.user_id,
                "success": log.success,
                "processing_time": log.processing_time,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None
            }
            for log in history
        ]
    }
