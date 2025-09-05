from fastapi import APIRouter, HTTPException, Depends
from backend.models.db import DBTool, DBUser
from backend.models.pydantic import ToolCreate, Tool
from backend.security import get_current_active_user 
from backend.db import get_async_session
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter()



@router.post("/", response_model=Tool)
async def create_tool(
    tool_data: ToolCreate, 
    user: DBUser = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
) -> DBTool:
    
    
    db_tool = DBTool(**tool_data.dict(), owner_id=user.id)
    session.add(db_tool)
    await session.commit()
    await session.refresh(db_tool)
    
    
    return db_tool


@router.get("/{tool_id}", response_model=Tool)
async def get_tool(tool_id: int, session: AsyncSession = Depends(get_async_session)) -> DBTool:
    query = select(DBTool).where(DBTool.id == tool_id)
    result = await session.execute(query)
    tool = result.scalars().first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool