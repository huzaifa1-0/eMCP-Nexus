from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from backend.models.db import DBTool, DBUser
from backend.models.pydantic import ToolCreate, Tool
from backend.security import get_current_user
from backend.db import get_async_session
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ai_services.search_engine import add_tool_to_faiss
from ai_services.monitoring import log_tool_usage
import random 
import time
from ..services.deployment import deploy_tool

router = APIRouter()

async def get_tool(tool_id: int, session: AsyncSession):
    result = await session.execute(select(DBTool).where(DBTool.id == tool_id))
    return result.scalar_one_or_none()



@router.post("/", response_model=Tool)
async def create_tool(
    tool_data: ToolCreate,
    background_tasks: BackgroundTasks, 
    user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> DBTool:
    
    
    deployment_info = await deploy_tool(repo_url=tool_data.repo_url)

    db_tool = DBTool(
        name = tool_data.name,
        description = tool_data.description,
        cost = tool_data.cost,
        repo_url = tool_data.repo_url,
        branch = tool_data.branch,
        url = deployment_info["url"],
        owner_id = user.id
    )
    session.add(db_tool)
    await session.commit()
    await session.refresh(db_tool)

    background_tasks.add_task(
        add_tool_to_faiss,
        tool_id=db_tool.id,
        name=db_tool.name,
        description=db_tool.description
    )
    
    
    return db_tool


@router.post("/use/{tool_id}", tags=["Tools"])
async def use_tool(
    tool_id: int, 
    background_tasks: BackgroundTasks,
    user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Simulates a user using a tool, and logs its performance."""
    
    # Check if tool exists
    tool = await get_tool(tool_id, session)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    # 1. Simulate the tool's execution
    start_time = time.time()
    # In a real-world scenario, you would call the tool's actual API here
    success = random.choice([True, False]) # Placeholder for actual success status
    processing_time = time.time() - start_time

    # 2. Log the performance in the background
    background_tasks.add_task(
        log_tool_usage,
        db=session,
        tool_id=tool_id,
        user_id=user.id,
        success=success,
        processing_time=processing_time
    )
    
    return {
        "status": "success" if success else "failure",
        "message": f"Tool {tool.name} executed.",
        "processing_time": processing_time
    }


