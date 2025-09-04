from fastapi import APIRouter
from ai_services import monitoring

router = APIRouter()

@router.post("/log")
async def log_tool_usage(tool_id: int, user_id: int):
    """
    Log usage of a tool by a user.
    """
    monitoring.log_tool_usage(tool_id, user_id)
    return {"message": f"Usage logged for tool {tool_id} by user {user_id}"}

@router.get("/usage/{tool_id}")
async def get_tool_usage(tool_id: int):
    """
    Get usage history for a given tool.
    """
    history = monitoring.get_tool_usage(tool_id)
    return {"tool_id": tool_id, "usage_history": history}
